##########################################################################################################
#   Description: CAD表格OLE对象尺寸调整器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal, Optional, Tuple

import win32com.client
from ezdxf.math import Vec2

from craftHub.tool import GLog

from .data import Data


Attachment = Literal[2, 4, 6, 8]

SizeAdjustMode = Literal[
    "fixedWidth",
    "fixedHeight",
    "maxSize"
]


class SizeAdjuster:
    '''CAD表格OLE对象尺寸调整器'''

    MODE_FIXED_WIDTH = "fixedWidth"
    MODE_FIXED_HEIGHT = "fixedHeight"
    MODE_MAX_SIZE = "maxSize"

    ATTACHMENT_TOP = 8
    ATTACHMENT_BOTTOM = 2
    ATTACHMENT_LEFT = 4
    ATTACHMENT_RIGHT = 6

    VALID_MODE_SET = {
        MODE_FIXED_WIDTH,
        MODE_FIXED_HEIGHT,
        MODE_MAX_SIZE
    }

    VALID_ATTACHMENT_SET = {
        ATTACHMENT_TOP,
        ATTACHMENT_BOTTOM,
        ATTACHMENT_LEFT,
        ATTACHMENT_RIGHT
    }

    COM_POINT_VARIANT_TYPE = 8197

    SIZE_EPSILON = 1e-8
    SCALE_EPSILON = 1e-8
    MOVE_EPSILON = 1e-8

    def __init__(
            self,
            mode: Optional[SizeAdjustMode] = None,
            attachment: Attachment = ATTACHMENT_TOP,
            width: Optional[float] = None,
            height: Optional[float] = None,
            maxWidth: Optional[float] = None,
            maxHeight: Optional[float] = None
    ) -> None:
        """初始化OLE对象尺寸调整器

        :param mode:
            None: 不调整尺寸；
            fixedWidth: 固定宽度，高度等比例变化；
            fixedHeight: 固定高度，宽度等比例变化；
            maxSize: 在最大宽度和最大高度范围内取最大等比例尺寸
        :param attachment:
            缩放时保持不变的锚点；
            8: 上中点；
            2: 下中点；
            4: 左中点；
            6: 右中点
        :param width: fixedWidth模式下的目标宽度
        :param height: fixedHeight模式下的目标高度
        :param maxWidth: maxSize模式下允许的最大宽度
        :param maxHeight: maxSize模式下允许的最大高度
        """

        self.mode = mode
        self.attachment = attachment

        self.width = width
        self.height = height

        self.maxWidth = maxWidth
        self.maxHeight = maxHeight

        self._validateConfig()

    def adjust(
            self,
            cadObject: Any,
            data: Optional[Data] = None,
            attachment: Optional[Attachment] = None
    ) -> Tuple[float, float]:
        """调整已插入CAD表格对象的尺寸

        调整过程中会保持指定锚点的坐标不变。

        :param cadObject: 已插入AutoCAD中的OLE或图片对象
        :param data: 当前待插入表格数据，仅用于输出日志
        :param attachment:
            临时覆盖初始化时设置的锚点；
            8: 上中点；
            2: 下中点；
            4: 左中点；
            6: 右中点
        :return: 调整后的实际宽度和高度
        """

        if cadObject is None:
            raise ValueError("待调整的CAD对象不能为空")

        currentAttachment = (
            self.attachment
            if attachment is None
            else attachment
        )

        self._validateAttachment(
            currentAttachment
        )

        minPoint, maxPoint = self._getBoundingBox(
            cadObject=cadObject
        )

        currentWidth, currentHeight = self._getSize(
            minPoint=minPoint,
            maxPoint=maxPoint
        )

        tag = (
            data.tag
            if data is not None
            else "未知"
        )

        GLog.logInfo(
            f"读取表格原始尺寸: "
            f"TAG={tag}, "
            f"width={currentWidth:.4f}, "
            f"height={currentHeight:.4f}"
        )

        # mode=None时保持原始尺寸，
        # 用于兼容尚未启用尺寸调整功能的调用。
        if self.mode is None:
            return currentWidth, currentHeight

        scaleFactor = self._calculateScaleFactor(
            currentWidth=currentWidth,
            currentHeight=currentHeight
        )

        if scaleFactor <= 0:
            raise ValueError(
                f"OLE缩放比例必须大于0: {scaleFactor}"
            )

        # 记录缩放前必须保持不变的锚点。
        originalAnchorPoint = self._getAttachmentPoint(
            minPoint=minPoint,
            maxPoint=maxPoint,
            attachment=currentAttachment # type: ignore
        )

        if (
                abs(scaleFactor - 1.0)
                > self.SCALE_EPSILON
        ):
            self._scaleObject(
                cadObject=cadObject,
                basePoint=originalAnchorPoint,
                scaleFactor=scaleFactor
            )

            self._updateObject(
                cadObject=cadObject
            )

        # ScaleEntity原则上会保持缩放基点不变，
        # 但OLE对象的实际外接框可能出现细微偏差，
        # 所以缩放后重新测量并执行一次位置纠正。
        newMinPoint, newMaxPoint = self._getBoundingBox(
            cadObject=cadObject
        )

        currentAnchorPoint = self._getAttachmentPoint(
            minPoint=newMinPoint,
            maxPoint=newMaxPoint,
            attachment=currentAttachment # type: ignore
        )

        self._restoreAnchorPoint(
            cadObject=cadObject,
            currentAnchorPoint=currentAnchorPoint,
            targetAnchorPoint=originalAnchorPoint
        )

        self._updateObject(
            cadObject=cadObject
        )

        finalMinPoint, finalMaxPoint = self._getBoundingBox(
            cadObject=cadObject
        )

        finalWidth, finalHeight = self._getSize(
            minPoint=finalMinPoint,
            maxPoint=finalMaxPoint
        )

        GLog.logInfo(
            f"{GLog.GREEN}"
            f"表格尺寸调整完成: "
            f"TAG={tag}, "
            f"mode={self.mode}, "
            f"scale={scaleFactor:.6f}, "
            f"width={finalWidth:.4f}, "
            f"height={finalHeight:.4f}, "
            f"attachment={currentAttachment}"
            f"{GLog.END}"
        )

        return finalWidth, finalHeight

    def _calculateScaleFactor(
            self,
            currentWidth: float,
            currentHeight: float
    ) -> float:
        '''根据尺寸调整模式计算等比例缩放系数'''

        if self.mode == self.MODE_FIXED_WIDTH:
            assert self.width is not None

            return (
                self.width
                / currentWidth
            )

        if self.mode == self.MODE_FIXED_HEIGHT:
            assert self.height is not None

            return (
                self.height
                / currentHeight
            )

        if self.mode == self.MODE_MAX_SIZE:
            assert self.maxWidth is not None
            assert self.maxHeight is not None

            widthScaleFactor = (
                self.maxWidth
                / currentWidth
            )

            heightScaleFactor = (
                self.maxHeight
                / currentHeight
            )

            # 取较小的比例，保证宽度和高度均不超过限制。
            # 不限制比例小于1，因此原对象较小时允许放大到最大可用尺寸。
            return min(
                widthScaleFactor,
                heightScaleFactor
            )

        raise ValueError(
            f"未知尺寸调整模式: {self.mode}"
        )

    def _getBoundingBox(
            self,
            cadObject: Any
    ) -> Tuple[Vec2, Vec2]:
        '''读取CAD对象二维外接框'''

        try:
            minPointRaw, maxPointRaw = (
                cadObject.GetBoundingBox()
            )

        except Exception as e:
            raise RuntimeError(
                "无法读取CAD表格对象外接框"
            ) from e

        minPoint = Vec2(
            float(minPointRaw[0]),
            float(minPointRaw[1])
        )

        maxPoint = Vec2(
            float(maxPointRaw[0]),
            float(maxPointRaw[1])
        )

        return minPoint, maxPoint

    def _getSize(
            self,
            minPoint: Vec2,
            maxPoint: Vec2
    ) -> Tuple[float, float]:
        '''根据外接框计算对象宽度和高度'''

        width = (
            maxPoint.x
            - minPoint.x
        )

        height = (
            maxPoint.y
            - minPoint.y
        )

        if width <= self.SIZE_EPSILON:
            raise ValueError(
                f"CAD表格对象宽度无效: {width}"
            )

        if height <= self.SIZE_EPSILON:
            raise ValueError(
                f"CAD表格对象高度无效: {height}"
            )

        return width, height

    def _getAttachmentPoint(
            self,
            minPoint: Vec2,
            maxPoint: Vec2,
            attachment: Attachment
    ) -> Vec2:
        '''获取外接框指定方向的边缘中点'''

        centerX = (
            minPoint.x
            + maxPoint.x
        ) / 2

        centerY = (
            minPoint.y
            + maxPoint.y
        ) / 2

        if attachment == self.ATTACHMENT_TOP:
            return Vec2(
                centerX,
                maxPoint.y
            )

        if attachment == self.ATTACHMENT_BOTTOM:
            return Vec2(
                centerX,
                minPoint.y
            )

        if attachment == self.ATTACHMENT_LEFT:
            return Vec2(
                minPoint.x,
                centerY
            )

        if attachment == self.ATTACHMENT_RIGHT:
            return Vec2(
                maxPoint.x,
                centerY
            )

        raise ValueError(
            f"不支持的锚点方向: {attachment}"
        )

    def _scaleObject(
            self,
            cadObject: Any,
            basePoint: Vec2,
            scaleFactor: float
    ) -> None:
        '''以指定锚点为基点等比例缩放CAD对象'''

        try:
            cadObject.ScaleEntity(
                self._toVariantPoint(
                    basePoint
                ),
                float(scaleFactor)
            )

        except Exception as e:
            raise RuntimeError(
                f"缩放CAD表格对象失败: "
                f"scaleFactor={scaleFactor}, "
                f"basePoint={basePoint}"
            ) from e

    def _restoreAnchorPoint(
            self,
            cadObject: Any,
            currentAnchorPoint: Vec2,
            targetAnchorPoint: Vec2
    ) -> None:
        '''将缩放后的锚点移动回缩放前的位置'''

        xOffset = (
            targetAnchorPoint.x
            - currentAnchorPoint.x
        )

        yOffset = (
            targetAnchorPoint.y
            - currentAnchorPoint.y
        )

        if (
                abs(xOffset) <= self.MOVE_EPSILON
                and abs(yOffset) <= self.MOVE_EPSILON
        ):
            return

        try:
            # Move方法按照两个点之间的向量移动对象。
            cadObject.Move(
                self._toVariantPoint(
                    currentAnchorPoint
                ),
                self._toVariantPoint(
                    targetAnchorPoint
                )
            )

        except Exception as e:
            raise RuntimeError(
                f"恢复CAD表格锚点失败: "
                f"currentPoint={currentAnchorPoint}, "
                f"targetPoint={targetAnchorPoint}"
            ) from e

    @staticmethod
    def _updateObject(
            cadObject: Any
    ) -> None:
        '''请求AutoCAD刷新对象'''

        try:
            cadObject.Update()
        except Exception:
            # 部分粘贴对象不提供Update，
            # 不影响后续重新读取外接框。
            pass

    def _validateConfig(self) -> None:
        '''检查尺寸调整配置是否合法'''

        self._validateAttachment(
            self.attachment
        )

        if self.mode is None:
            return

        if self.mode not in self.VALID_MODE_SET:
            raise ValueError(
                f"尺寸调整模式不合法: {self.mode}; "
                f"仅支持"
                f"{self.MODE_FIXED_WIDTH}、"
                f"{self.MODE_FIXED_HEIGHT}、"
                f"{self.MODE_MAX_SIZE}"
            )

        if self.mode == self.MODE_FIXED_WIDTH:
            self._validatePositiveNumber(
                value=self.width,
                name="width"
            )

            return

        if self.mode == self.MODE_FIXED_HEIGHT:
            self._validatePositiveNumber(
                value=self.height,
                name="height"
            )

            return

        if self.mode == self.MODE_MAX_SIZE:
            self._validatePositiveNumber(
                value=self.maxWidth,
                name="maxWidth"
            )

            self._validatePositiveNumber(
                value=self.maxHeight,
                name="maxHeight"
            )

    def _validateAttachment(
            self,
            attachment: int
    ) -> None:
        '''检查锚点参数是否合法'''

        if attachment not in self.VALID_ATTACHMENT_SET:
            raise ValueError(
                f"表格锚点方向不合法: {attachment}; "
                f"仅支持"
                f"{self.ATTACHMENT_TOP}、"
                f"{self.ATTACHMENT_BOTTOM}、"
                f"{self.ATTACHMENT_LEFT}、"
                f"{self.ATTACHMENT_RIGHT}"
            )

    @staticmethod
    def _validatePositiveNumber(
            value: Optional[float],
            name: str
    ) -> None:
        '''检查参数是否为大于0的数字'''

        if value is None:
            raise ValueError(
                f"尺寸参数不能为空: {name}"
            )

        try:
            numberValue = float(value)

        except (TypeError, ValueError) as e:
            raise ValueError(
                f"尺寸参数必须是数字: "
                f"{name}={value}"
            ) from e

        if numberValue <= 0:
            raise ValueError(
                f"尺寸参数必须大于0: "
                f"{name}={value}"
            )

    @classmethod
    def _toVariantPoint(
            cls,
            point: Vec2
    ):
        '''将Vec2转换为AutoCAD COM三维点'''

        return win32com.client.VARIANT(
            cls.COM_POINT_VARIANT_TYPE,
            (
                float(point.x),
                float(point.y),
                0.0
            )
        )