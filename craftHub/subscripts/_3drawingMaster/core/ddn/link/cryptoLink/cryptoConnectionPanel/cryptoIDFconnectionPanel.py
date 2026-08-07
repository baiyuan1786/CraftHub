##########################################################################################################
#   Description: 纵向加密IDF连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from .....common.graph import CADColor, NewBlock
from .....common.graph import 现有设备, 本期新增网线

class CDIDFConnectionPanel(NewBlock):
    '''纵向加密IDF连接面板图'''

    DIRECTION_LEFT = "left"
    DIRECTION_RIGHT = "right"

    WIDTH = 42
    HEIGHT = 21

    PORT_BOX_WIDTH = 14
    PORT_BOX_HEIGHT = 8.5

    PORT_BOX_BOTTOM_Y = 0
    PORT_BOX_TOP_Y = HEIGHT - PORT_BOX_HEIGHT

    PORT_TEXT_HEIGHT = 3
    DEVICE_TEXT_HEIGHT = 3

    PORT_TEXT_WIDTH_RATE = 0.9
    DEVICE_TEXT_WIDTH_RATE = 0.9

    CUT_BUSINESS_LINE_LENGTH = 18
    CUT_BUSINESS_TEXT_HEIGHT = 3
    CUT_BUSINESS_TEXT_WIDTH = 90
    CUT_BUSINESS_TEXT_OFFSET_Y = 2
    CUT_BUSINESS_TEXT_OFFSET_X = 13
    CUT_BUSINESS_TEXT = "业务割接时断开与旧A网路由器的链路"

    ALIGN_TOLERANCE = 0.5

    @classmethod
    def insertPointFromFrontPoints(
            cls,
            insertX: float,
            rtLinkPoint: Vec2,
            nrtLinkPoint: Vec2,
            direction: Literal["left", "right"] = "left"
    ) -> Vec2:
        '''根据实时/非实时接入点反算IDF插入点'''

        cls._checkDirection(direction)

        rtInsertY = rtLinkPoint.y - cls._rtPointFrontLocalStatic(direction).y
        nrtInsertY = nrtLinkPoint.y - cls._nrtPointFrontLocalStatic(direction).y

        if abs(rtInsertY - nrtInsertY) > cls.ALIGN_TOLERANCE:
            raise ValueError(
                "无法保证IDF两个接入点同时水平连接: "
                f"rtInsertY={rtInsertY}, nrtInsertY={nrtInsertY}, "
                f"rtLinkPoint={rtLinkPoint}, nrtLinkPoint={nrtLinkPoint}"
            )

        return Vec2(insertX, (rtInsertY + nrtInsertY) / 2)

    @classmethod
    def _checkDirection(
            cls,
            direction: Literal["left", "right"]
    ):
        '''检查端口朝向'''

        if direction not in [cls.DIRECTION_LEFT, cls.DIRECTION_RIGHT]:
            raise ValueError(f"未知IDF端口朝向: {direction}")

    @classmethod
    def _rtPointFrontLocalStatic(
            cls,
            direction: Literal["left", "right"] = "left"
    ) -> Vec2:
        '''获取实时纵向加密端口前点局部坐标'''

        return Vec2(
            cls._portBoxFrontXStatic(direction),
            cls.PORT_BOX_TOP_Y + cls.PORT_BOX_HEIGHT / 2
        )

    @classmethod
    def _nrtPointFrontLocalStatic(
            cls,
            direction: Literal["left", "right"] = "left"
    ) -> Vec2:
        '''获取非实时纵向加密端口前点局部坐标'''

        return Vec2(
            cls._portBoxFrontXStatic(direction),
            cls.PORT_BOX_BOTTOM_Y + cls.PORT_BOX_HEIGHT / 2
        )

    @classmethod
    def _portBoxInsertXStatic(
            cls,
            direction: Literal["left", "right"]
    ) -> float:
        '''获取端口框插入点X坐标'''

        cls._checkDirection(direction)

        if direction == cls.DIRECTION_LEFT:
            return 0

        return cls.WIDTH - cls.PORT_BOX_WIDTH

    @classmethod
    def _portBoxFrontXStatic(
            cls,
            direction: Literal["left", "right"]
    ) -> float:
        '''获取端口前点X坐标'''

        cls._checkDirection(direction)

        if direction == cls.DIRECTION_LEFT:
            return 0

        return cls.WIDTH - cls.PORT_BOX_WIDTH

    @classmethod
    def _portBoxAfterXStatic(
            cls,
            direction: Literal["left", "right"]
    ) -> float:
        '''获取端口后点X坐标'''

        cls._checkDirection(direction)

        if direction == cls.DIRECTION_LEFT:
            return cls.PORT_BOX_WIDTH

        return cls.WIDTH

    def __init__(
            self,
            doc: Drawing,
            devNum: str,
            devName: str,
            portR: Optional[str],
            portNR: Optional[str],
            insertPoint: Vec2,
            isCutBusiness: bool = False,
            direction: Literal["left", "right"] = "left"
    ) -> None:
        """纵向加密IDF连接面板图初始化

        :param doc: CAD文档
        :param devNum: 设备号，例如40P10
        :param devName: 设备名，例如IDF配线单元
        :param portR: 实时纵向加密使用端口
        :param portNR: 非实时纵向加密使用端口
        :param insertPoint: 插入点
        :param isCutBusiness: 是否绘制业务断开标记
        :param direction: 端口朝向，left为左侧端口，right为右侧端口
        """

        super().__init__(doc)

        self._checkDirection(direction)

        self.insertPoint = insertPoint

        self.devNum = devNum
        self.devName = devName
        self.portR = portR
        self.portNR = portNR
        self.isCutBusiness = isCutBusiness
        self.direction = direction

        self._drawOuterFrame()
        self._drawPortBox()
        self._drawPortText()
        self._drawDeviceText()

        if self.isCutBusiness:
            self._drawCutBusiness()

    def _drawOuterFrame(self):
        '''绘制外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawPortBox(self):
        '''绘制端口框'''

        portBoxInsertX = self._portBoxInsertX()

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(portBoxInsertX, self.PORT_BOX_TOP_Y)
        )

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(portBoxInsertX, self.PORT_BOX_BOTTOM_Y)
        )

    def _drawPortText(self):
        '''绘制端口文字'''

        self._drawPortMtext(
            textContent=self.portR,
            insertPoint=Vec2(self._portBoxCenterX(), self._rtCenterY())
        )

        self._drawPortMtext(
            textContent=self.portNR,
            insertPoint=Vec2(self._portBoxCenterX(), self._nrtCenterY())
        )

    def _drawPortMtext(
            self,
            textContent: Optional[str],
            insertPoint: Vec2
    ):
        '''绘制单个端口文字'''

        if textContent is None:
            return

        self.addMtext(
            textContent=CADColor.colored(textContent),
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_BOX_WIDTH * self.PORT_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=insertPoint,
            style="gedi",
            attachment=5
        )

    def _drawDeviceText(self):
        '''绘制设备文字'''

        deviceText = f"{CADColor.colored(self.devNum)} {self.devName}"

        self.addMtext(
            textContent=deviceText,
            textFontHeight=self.DEVICE_TEXT_HEIGHT,
            textWidth=(self.WIDTH - self.PORT_BOX_WIDTH) * self.DEVICE_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self._deviceTextCenterX(), self.HEIGHT / 2),
            style="gedi",
            attachment=5
        )

    def _drawCutBusiness(self):
        '''绘制业务断开标记'''

        if self.portR:
            self._drawCutBusinessTop()

        if self.portNR:
            self._drawCutBusinessBottom()

    def _drawCutBusinessTop(self):
        '''绘制上方业务断开标记'''

        startPoint = self._rtPortTopCenterLocal()
        endPoint = startPoint + Vec2(0, self.CUT_BUSINESS_LINE_LENGTH)

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=本期新增网线(),
            fork=True
        )

        self.addMtext(
            textContent=self.CUT_BUSINESS_TEXT,
            textFontHeight=self.CUT_BUSINESS_TEXT_HEIGHT,
            textWidth=self.CUT_BUSINESS_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=endPoint + Vec2(self._cutBusinessTextOffsetX(), self.CUT_BUSINESS_TEXT_OFFSET_Y),
            style="gedi",
            attachment=8
        )

    def _drawCutBusinessBottom(self):
        '''绘制下方业务断开标记'''

        startPoint = self._nrtPortBottomCenterLocal()
        endPoint = startPoint + Vec2(0, -self.CUT_BUSINESS_LINE_LENGTH)

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=本期新增网线(),
            fork=True
        )

        self.addMtext(
            textContent=self.CUT_BUSINESS_TEXT,
            textFontHeight=self.CUT_BUSINESS_TEXT_HEIGHT,
            textWidth=self.CUT_BUSINESS_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=endPoint + Vec2(self._cutBusinessTextOffsetX(), -1 * self.CUT_BUSINESS_TEXT_OFFSET_Y),
            style="gedi",
            attachment=2
        )

    def _portBoxInsertX(self) -> float:
        '''获取端口框插入点X坐标'''

        return self._portBoxInsertXStatic(self.direction) # type: ignore

    def _portBoxCenterX(self) -> float:
        '''获取端口框中心X坐标'''

        return self._portBoxInsertX() + self.PORT_BOX_WIDTH / 2

    def _deviceTextCenterX(self) -> float:
        '''获取设备文字中心X坐标'''

        if self.direction == self.DIRECTION_LEFT:
            return (self.PORT_BOX_WIDTH + self.WIDTH) / 2

        return (self.WIDTH - self.PORT_BOX_WIDTH) / 2

    def _cutBusinessTextOffsetX(self) -> float:
        '''获取业务割接文字X方向偏移'''

        if self.direction == self.DIRECTION_LEFT:
            return self.CUT_BUSINESS_TEXT_OFFSET_X

        return -self.CUT_BUSINESS_TEXT_OFFSET_X

    def _rtPortTopCenterLocal(self) -> Vec2:
        '''获取实时纵向加密端口框上中点局部坐标'''

        return Vec2(
            self._portBoxCenterX(),
            self.PORT_BOX_TOP_Y + self.PORT_BOX_HEIGHT
        )

    def _nrtPortBottomCenterLocal(self) -> Vec2:
        '''获取非实时纵向加密端口框下中点局部坐标'''

        return Vec2(
            self._portBoxCenterX(),
            self.PORT_BOX_BOTTOM_Y
        )

    def _rtCenterY(self) -> float:
        '''获取实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_TOP_Y + self.PORT_BOX_HEIGHT / 2

    def _nrtCenterY(self) -> float:
        '''获取非实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_BOTTOM_Y + self.PORT_BOX_HEIGHT / 2

    def _rtPointFrontLocal(self) -> Vec2:
        '''获取实时纵向加密端口前点局部坐标'''

        return Vec2(
            self._portBoxFrontXStatic(self.direction), # type: ignore
            self._rtCenterY()
        )

    def _rtPointAfterLocal(self) -> Vec2:
        '''获取实时纵向加密端口后点局部坐标'''

        return Vec2(
            self._portBoxAfterXStatic(self.direction), # type: ignore
            self._rtCenterY()
        )

    def _nrtPointFrontLocal(self) -> Vec2:
        '''获取非实时纵向加密端口前点局部坐标'''

        return Vec2(
            self._portBoxFrontXStatic(self.direction), # type: ignore
            self._nrtCenterY()
        )

    def _nrtPointAfterLocal(self) -> Vec2:
        '''获取非实时纵向加密端口后点局部坐标'''

        return Vec2(
            self._portBoxAfterXStatic(self.direction), # type: ignore
            self._nrtCenterY()
        )

    def RTPointFront(self) -> Vec2:
        '''返回实时纵向加密端口前点绝对坐标'''

        return self.insertPoint + self._rtPointFrontLocal()

    def RTPointAfter(self) -> Vec2:
        '''返回实时纵向加密端口后点绝对坐标'''

        return self.insertPoint + self._rtPointAfterLocal()

    def NRTPointFront(self) -> Vec2:
        '''返回非实时纵向加密端口前点绝对坐标'''

        return self.insertPoint + self._nrtPointFrontLocal()

    def NRTPointAfter(self) -> Vec2:
        '''返回非实时纵向加密端口后点绝对坐标'''

        return self.insertPoint + self._nrtPointAfterLocal()

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''插入纵向加密IDF连接面板图'''

        return super().insertInto(layout, self.insertPoint)