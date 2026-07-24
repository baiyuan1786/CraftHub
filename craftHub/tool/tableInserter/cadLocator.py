##########################################################################################################
#   Description: CAD表格插入位置定位器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import math

from dataclasses import dataclass
from typing import Any, Iterator, List, Literal, Optional, Tuple

from ezdxf import bbox
from ezdxf.document import Drawing
from ezdxf.math import Vec2

from .data import Data


Attachment = Literal[2, 4, 6, 8]


@dataclass(frozen=True)
class _TextItem:
    '''CAD文字对象定位信息'''

    entity: Any
    text: str

    minPoint: Vec2
    maxPoint: Vec2
    centerPoint: Vec2

    blockPath: Tuple[str, ...] = ()


class CadLocator:
    '''CAD定位器'''

    ATTACHMENT_TOP = 2
    ATTACHMENT_LEFT = 4
    ATTACHMENT_RIGHT = 6
    ATTACHMENT_BOTTOM = 8

    VALID_ATTACHMENT_SET = {
        ATTACHMENT_TOP,
        ATTACHMENT_LEFT,
        ATTACHMENT_RIGHT,
        ATTACHMENT_BOTTOM
    }

    TEXT_ENTITY_TYPE_SET = {
        "TEXT",
        "MTEXT"
    }

    INSERT_ENTITY_TYPE = "INSERT"

    MAX_BLOCK_REFERENCE_DEPTH = 20

    POSITION_EPSILON = 1e-8
    DISTANCE_TIE_EPSILON = 1e-6

    def __init__(
            self,
            doc: Drawing,
            searchBlockReference: bool = True
    ) -> None:
        """初始化CAD定位器

        :param doc: DXF绘图文件
        :param searchBlockReference:
            True：搜索模型空间文字，以及块参照和嵌套块中的TEXT、MTEXT；
            False：只搜索模型空间第一层TEXT、MTEXT
        """

        if doc is None:
            raise ValueError(
                "绘图文件不能为空"
            )

        self.doc = doc

        # 当前先默认开启块参照搜索。
        # 后续GUI完成后，可以将该参数交由用户控制。
        self.searchBlockReference = bool(
            searchBlockReference
        )

        self._bboxCache = bbox.Cache()

        self._textItemList: List[
            _TextItem
        ] = []

        self.refresh()

    def setSearchBlockReference(
            self,
            enabled: bool
    ) -> None:
        '''设置是否搜索块参照中的文字并重新建立索引'''

        enabled = bool(enabled)

        if (
                self.searchBlockReference
                == enabled
        ):
            return

        self.searchBlockReference = enabled

        self.refresh()

    def refresh(self) -> None:
        '''重新建立CAD文字定位索引'''

        self._bboxCache = bbox.Cache()
        self._textItemList.clear()

        modelSpace = self.doc.modelspace()

        for entity in modelSpace:
            self._collectEntityText(
                entity=entity,
                currentDepth=0,
                blockPath=()
            )

    def _collectEntityText(
            self,
            entity: Any,
            currentDepth: int,
            blockPath: Tuple[str, ...]
    ) -> None:
        '''收集一个实体及其块参照子实体中的文字'''

        entityType = entity.dxftype()

        if (
                entityType
                in self.TEXT_ENTITY_TYPE_SET
        ):
            self._appendTextEntity(
                entity=entity,
                blockPath=blockPath
            )

            return

        if (
                entityType
                != self.INSERT_ENTITY_TYPE
        ):
            return

        if not self.searchBlockReference:
            return

        self._collectBlockReferenceText(
            insertEntity=entity,
            currentDepth=currentDepth + 1,
            blockPath=blockPath
        )

    def _collectBlockReferenceText(
            self,
            insertEntity: Any,
            currentDepth: int,
            blockPath: Tuple[str, ...]
    ) -> None:
        '''递归收集块参照中的TEXT和MTEXT'''

        if (
                currentDepth
                > self.MAX_BLOCK_REFERENCE_DEPTH
        ):
            raise ValueError(
                f"块参照递归深度超过限制: "
                f"maxDepth="
                f"{self.MAX_BLOCK_REFERENCE_DEPTH}, "
                f"blockPath="
                f"{self._formatBlockPath(blockPath)}"
            )

        for insertInstance in (
                self._iterInsertInstanceList(
                    insertEntity=insertEntity
                )
        ):
            blockName = self._readBlockName(
                insertEntity=insertInstance
            )

            if blockName in blockPath:
                circularBlockPath = (
                    blockPath
                    + (blockName,)
                )

                raise ValueError(
                    f"检测到循环块参照定义: "
                    f"{self._formatBlockPath(circularBlockPath)}"
                )

            currentBlockPath = (
                blockPath
                + (blockName,)
            )

            try:
                virtualEntityIterator = (
                    insertInstance.virtual_entities()
                )

                for virtualEntity in (
                        virtualEntityIterator
                ):
                    self._collectEntityText(
                        entity=virtualEntity,
                        currentDepth=currentDepth,
                        blockPath=currentBlockPath
                    )

            except Exception as e:
                raise RuntimeError(
                    f"读取块参照内容失败: "
                    f"blockName={blockName!r}, "
                    f"blockPath="
                    f"{self._formatBlockPath(currentBlockPath)}"
                ) from e

    def _iterInsertInstanceList(
            self,
            insertEntity: Any
    ) -> Iterator[Any]:
        '''展开普通INSERT或MINSERT阵列块参照'''

        try:
            multiInsertCount = int(
                insertEntity.mcount
            )

        except Exception:
            multiInsertCount = 1

        if multiInsertCount <= 1:
            yield insertEntity
            return

        try:
            yield from insertEntity.multi_insert()

        except Exception as e:
            blockName = self._readBlockName(
                insertEntity=insertEntity
            )

            raise RuntimeError(
                f"展开MINSERT阵列块参照失败: "
                f"blockName={blockName!r}, "
                f"count={multiInsertCount}"
            ) from e

    def _appendTextEntity(
            self,
            entity: Any,
            blockPath: Tuple[str, ...]
    ) -> None:
        '''将一个TEXT或MTEXT加入文字定位索引'''

        text = self._readEntityText(
            entity=entity
        )

        if not text:
            return

        minPoint, maxPoint = (
            self._readEntityBoundingBox(
                entity=entity
            )
        )

        centerPoint = Vec2(
            (
                minPoint.x
                + maxPoint.x
            ) / 2,
            (
                minPoint.y
                + maxPoint.y
            ) / 2
        )

        self._textItemList.append(
            _TextItem(
                entity=entity,
                text=text,
                minPoint=minPoint,
                maxPoint=maxPoint,
                centerPoint=centerPoint,
                blockPath=blockPath
            )
        )

    def locate(
            self,
            data: Data,
            sign1: Optional[str] = None,
            attachment1: Literal[2, 4, 6, 8] = 8,
            sign2: Optional[str] = None,
            attachment2: Literal[2, 4, 6, 8] = 8
    ) -> Optional[Vec2]:
        """根据提供的data和标记参数定位插入点

        :param data: 一个待插入数据
        :param sign1:
            标记1，匹配一个文字内容；
            None表示不应用标记1，此时使用固定位置插入
        :param attachment1:
            只有标记1时，决定标记1上的最终插入位置；
            存在标记2时，决定从标记1搜索标记2的方向；
            2：上，4：左，6：右，8：下
        :param sign2:
            标记2，在标记1指定方向上匹配最近的文字；
            None表示不应用标记2
        :param attachment2:
            决定标记2上的最终插入位置；
            2：上，4：左，6：右，8：下
        """

        if data is None:
            raise ValueError(
                "待定位Data不能为空"
            )

        self._validateAttachment(
            attachment1
        )

        self._validateAttachment(
            attachment2
        )

        if sign1 is None:
            return self._locateByFixedPoint(
                data=data
            )

        normalizedSign1 = self._normalizeSign(
            sign=sign1,
            signName="sign1"
        )

        sign1ItemList = self._findSign1TextItemList(
            sign=normalizedSign1
        )

        if len(sign1ItemList) == 0:
            return self._setLocateResult(
                data=data,
                insertPoint=None
            )

        if sign2 is None:
            return self._locateBySingleSign(
                data=data,
                sign=normalizedSign1,
                itemList=sign1ItemList,
                attachment=attachment1
            )

        normalizedSign2 = self._normalizeSign(
            sign=sign2,
            signName="sign2"
        )

        sign2ItemList = self._findTextItemList(
            sign=normalizedSign2
        )

        if len(sign2ItemList) == 0:
            return self._setLocateResult(
                data=data,
                insertPoint=None
            )

        return self._locateByDoubleSign(
            data=data,
            sign1=normalizedSign1,
            sign1ItemList=sign1ItemList,
            attachment1=attachment1,
            sign2=normalizedSign2,
            sign2ItemList=sign2ItemList,
            attachment2=attachment2
        )

    def _locateByFixedPoint(
            self,
            data: Data
    ) -> Optional[Vec2]:
        '''使用Data中配置的固定插入点进行定位'''

        if data.fixedInsertPoint is None:
            return self._setLocateResult(
                data=data,
                insertPoint=None
            )

        insertPoint = Vec2(
            float(
                data.fixedInsertPoint.x
            ),
            float(
                data.fixedInsertPoint.y
            )
        )

        return self._setLocateResult(
            data=data,
            insertPoint=insertPoint
        )

    def _locateBySingleSign(
            self,
            data: Data,
            sign: str,
            itemList: List[_TextItem],
            attachment: Attachment
    ) -> Optional[Vec2]:
        '''根据唯一标记文字进行定位'''

        if len(itemList) > 1:
            locationDescriptionList = [
                self._describeTextItem(
                    item=item
                )
                for item in itemList
            ]

            raise ValueError(
                f"CAD中存在多个标记1文字，"
                f"无法确定唯一位置: "
                f"sign1={sign!r}, "
                f"数量={len(itemList)}, "
                f"位置={locationDescriptionList}"
            )

        insertPoint = self._getAttachmentPoint(
            item=itemList[0],
            attachment=attachment
        )

        return self._setLocateResult(
            data=data,
            insertPoint=insertPoint
        )

    def _locateByDoubleSign(
            self,
            data: Data,
            sign1: str,
            sign1ItemList: List[_TextItem],
            attachment1: Attachment,
            sign2: str,
            sign2ItemList: List[_TextItem],
            attachment2: Attachment
    ) -> Optional[Vec2]:
        '''根据两级标记文字进行定位'''

        pairList: List[
            Tuple[
                float,
                _TextItem,
                _TextItem
            ]
        ] = []

        for sign1Item in sign1ItemList:
            for sign2Item in sign2ItemList:
                if (
                        sign1Item.entity
                        is sign2Item.entity
                ):
                    continue

                if not self._isItemInDirection(
                        originItem=sign1Item,
                        targetItem=sign2Item,
                        attachment=attachment1
                ):
                    continue

                distance = (
                    self._calculateDistance(
                        point1=sign1Item.centerPoint,
                        point2=sign2Item.centerPoint
                    )
                )

                pairList.append(
                    (
                        distance,
                        sign1Item,
                        sign2Item
                    )
                )

        if len(pairList) == 0:
            return self._setLocateResult(
                data=data,
                insertPoint=None
            )

        pairList.sort(
            key=lambda pair: pair[0]
        )

        self._validateNearestPair(
            pairList=pairList,
            sign1=sign1,
            sign2=sign2,
            attachment1=attachment1
        )

        _, _, nearestSign2Item = (
            pairList[0]
        )

        insertPoint = self._getAttachmentPoint(
            item=nearestSign2Item,
            attachment=attachment2
        )

        return self._setLocateResult(
            data=data,
            insertPoint=insertPoint
        )

    def _findSign1TextItemList(
            self,
            sign: str
    ) -> List[_TextItem]:
        '''查找与标记1匹配的文字对象

        以下两种文字均视为匹配成功：
        1. 文字内容与sign完全相同；
        2. 文字内容格式为sign(任意字符串)。

        只识别英文半角括号()。
        '''

        return [
            item
            for item in self._textItemList
            if self._isSign1TextMatched(
                text=item.text,
                sign=sign
            )
        ]

    @staticmethod
    def _isSign1TextMatched(
            text: str,
            sign: str
    ) -> bool:
        '''判断文字内容是否匹配标记1'''

        if text == sign:
            return True

        prefix = f"{sign}("

        return (
            text.startswith(prefix)
            and text.endswith(")")
        )

    def _findTextItemList(
            self,
            sign: str
    ) -> List[_TextItem]:
        '''查找文字内容与标记完全匹配的文字对象'''

        return [
            item
            for item in self._textItemList
            if item.text == sign
        ]

    def _readEntityText(
            self,
            entity: Any
    ) -> str:
        '''读取并规范化TEXT或MTEXT文字内容'''

        entityType = entity.dxftype()

        if entityType == "TEXT":
            rawText = entity.dxf.text

        elif entityType == "MTEXT":
            rawText = entity.plain_text()

        else:
            return ""

        return self._normalizeText(
            rawText=rawText
        )

    def _readEntityBoundingBox(
            self,
            entity: Any
    ) -> Tuple[Vec2, Vec2]:
        '''读取文字对象外接框，失败时退回插入点'''

        try:
            boundingBox = bbox.extents(
                [entity],
                cache=self._bboxCache
            )

            if boundingBox.has_data:
                minPoint = Vec2(
                    float(
                        boundingBox.extmin.x
                    ),
                    float(
                        boundingBox.extmin.y
                    )
                )

                maxPoint = Vec2(
                    float(
                        boundingBox.extmax.x
                    ),
                    float(
                        boundingBox.extmax.y
                    )
                )

                return minPoint, maxPoint

        except Exception:
            pass

        insertPoint = (
            self._readEntityInsertPoint(
                entity=entity
            )
        )

        return insertPoint, insertPoint

    @staticmethod
    def _readEntityInsertPoint(
            entity: Any
    ) -> Vec2:
        '''读取文字对象插入点'''

        try:
            insertPoint = (
                entity.dxf.insert
            )

            return Vec2(
                float(insertPoint.x),
                float(insertPoint.y)
            )

        except Exception as e:
            raise ValueError(
                f"无法读取文字对象插入点: "
                f"type={entity.dxftype()}"
            ) from e

    @staticmethod
    def _readBlockName(
            insertEntity: Any
    ) -> str:
        '''读取块参照名称'''

        try:
            blockName = str(
                insertEntity.dxf.name
            ).strip()

        except Exception as e:
            raise ValueError(
                "无法读取块参照名称"
            ) from e

        if not blockName:
            return "<unnamed>"

        return blockName

    def _getAttachmentPoint(
            self,
            item: _TextItem,
            attachment: Attachment
    ) -> Vec2:
        '''获取文字外接框指定方向的边缘中点'''

        centerX = item.centerPoint.x
        centerY = item.centerPoint.y

        if attachment == self.ATTACHMENT_TOP:
            return Vec2(
                centerX,
                item.maxPoint.y
            )

        if attachment == self.ATTACHMENT_LEFT:
            return Vec2(
                item.minPoint.x,
                centerY
            )

        if attachment == self.ATTACHMENT_RIGHT:
            return Vec2(
                item.maxPoint.x,
                centerY
            )

        if attachment == self.ATTACHMENT_BOTTOM:
            return Vec2(
                centerX,
                item.minPoint.y
            )

        raise ValueError(
            f"不支持的连接方向: "
            f"{attachment}"
        )

    def _isItemInDirection(
            self,
            originItem: _TextItem,
            targetItem: _TextItem,
            attachment: Attachment
    ) -> bool:
        '''判断目标文字是否位于原点文字的指定方向'''

        originPoint = (
            originItem.centerPoint
        )

        targetPoint = (
            targetItem.centerPoint
        )

        if attachment == self.ATTACHMENT_TOP:
            return (
                targetPoint.y
                > originPoint.y
                + self.POSITION_EPSILON
            )

        if attachment == self.ATTACHMENT_LEFT:
            return (
                targetPoint.x
                < originPoint.x
                - self.POSITION_EPSILON
            )

        if attachment == self.ATTACHMENT_RIGHT:
            return (
                targetPoint.x
                > originPoint.x
                + self.POSITION_EPSILON
            )

        if attachment == self.ATTACHMENT_BOTTOM:
            return (
                targetPoint.y
                < originPoint.y
                - self.POSITION_EPSILON
            )

        raise ValueError(
            f"不支持的搜索方向: "
            f"{attachment}"
        )

    def _validateNearestPair(
            self,
            pairList: List[
                Tuple[
                    float,
                    _TextItem,
                    _TextItem
                ]
            ],
            sign1: str,
            sign2: str,
            attachment1: Attachment
    ) -> None:
        '''检查最近标记组合是否存在距离相同的歧义'''

        if len(pairList) <= 1:
            return

        firstDistance = pairList[0][0]
        secondDistance = pairList[1][0]

        if (
                abs(
                    firstDistance
                    - secondDistance
                )
                <= self.DISTANCE_TIE_EPSILON
        ):
            raise ValueError(
                f"CAD定位结果不唯一，"
                f"存在距离相同的标记组合: "
                f"sign1={sign1!r}, "
                f"sign2={sign2!r}, "
                f"搜索方向={attachment1}, "
                f"最近距离="
                f"{firstDistance:.6f}"
            )

    def _validateAttachment(
            self,
            attachment: int
    ) -> None:
        '''检查方向参数是否合法'''

        if (
                attachment
                not in self.VALID_ATTACHMENT_SET
        ):
            raise ValueError(
                f"定位方向不合法: "
                f"{attachment}; "
                f"仅支持2、4、6、8"
            )

    @staticmethod
    def _calculateDistance(
            point1: Vec2,
            point2: Vec2
    ) -> float:
        '''计算两个点之间的二维直线距离'''

        return math.hypot(
            point2.x - point1.x,
            point2.y - point1.y
        )

    @staticmethod
    def _normalizeText(
            rawText: Any
    ) -> str:
        '''规范化CAD文字内容'''

        if rawText is None:
            return ""

        text = str(rawText)

        # 兼容MTEXT中的换行控制符
        text = text.replace(
            "\\P",
            "\n"
        )

        # 忽略首尾空格、连续空白以及单行和多行差异
        return " ".join(
            text.split()
        )

    def _normalizeSign(
            self,
            sign: str,
            signName: str
    ) -> str:
        '''规范化并检查标记文字'''

        normalizedSign = (
            self._normalizeText(
                rawText=sign
            )
        )

        if not normalizedSign:
            raise ValueError(
                f"{signName}不能为空字符串"
            )

        return normalizedSign

    @staticmethod
    def _describeTextItem(
            item: _TextItem
    ) -> str:
        '''生成文字对象位置描述'''

        positionDescription = (
            f"({item.centerPoint.x:.3f}, "
            f"{item.centerPoint.y:.3f})"
        )

        if not item.blockPath:
            return (
                f"模型空间"
                f"{positionDescription}"
            )

        return (
            f"块参照["
            f"{' -> '.join(item.blockPath)}"
            f"]"
            f"{positionDescription}"
        )

    @staticmethod
    def _formatBlockPath(
            blockPath: Tuple[str, ...]
    ) -> str:
        '''格式化块参照递归路径'''

        if not blockPath:
            return "<modelspace>"

        return " -> ".join(
            blockPath
        )

    @staticmethod
    def _setLocateResult(
            data: Data,
            insertPoint: Optional[Vec2]
    ) -> Optional[Vec2]:
        '''记录并返回定位结果'''

        data.insertPoint = insertPoint

        return insertPoint