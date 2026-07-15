##########################################################################################################
#   Description: GCN网传输设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Iterable, List

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import CADColor, NewBlock, 现有设备, 逻辑连线示意


class GCNBoardSlotConnectionPanel(NewBlock):
    '''GCN网板卡槽位连接面板图'''

    WIDTH = 48.0
    HEIGHT = 12.0

    PORT_BOX_WIDTH = 12.8
    PORT_BOX_HEIGHT = 5.2
    PORT_BOX_OFFSET_X = 0.0
    PORT_BOX_OFFSET_Y = 0.0

    SLOT_TEXT_HEIGHT = 5
    SLOT_TEXT_WIDTH = 14.0
    SLOT_TEXT_STYLE = "gedi"

    PORT_TEXT = "电口"
    PORT_TEXT_HEIGHT = 2.8
    PORT_TEXT_WIDTH = 8.0
    PORT_TEXT_STYLE = "gedi"

    SLOT_CENTER_OFFSET_X = 24.0
    SLOT_CENTER_OFFSET_Y = 6.8

    DASH_LINE_START_OFFSET_X = PORT_BOX_WIDTH
    DASH_LINE_END_OFFSET_X = WIDTH
    DASH_LINE_OFFSET_Y = PORT_BOX_OFFSET_Y + PORT_BOX_HEIGHT / 2

    def __init__(
            self,
            doc: Drawing,
            slotNum: int,
            insertPoint: Vec2
    ) -> None:
        """初始化GCN网板卡槽位连接面板图

        :param doc: 文档
        :param slotNum: 槽位号
        :param insertPoint: 插入点
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.slotNum = slotNum
        self.insertPoint = insertPoint

        self._build()

    @classmethod
    def frontPointLocal(cls) -> Vec2:
        '''返回电口框前连接点局部坐标'''

        return Vec2(
            cls.PORT_BOX_OFFSET_X,
            cls.PORT_BOX_OFFSET_Y + cls.PORT_BOX_HEIGHT / 2
        )

    @classmethod
    def afterPointLocal(cls) -> Vec2:
        '''返回电口框后连接点局部坐标'''

        return Vec2(
            cls.PORT_BOX_OFFSET_X + cls.PORT_BOX_WIDTH,
            cls.PORT_BOX_OFFSET_Y + cls.PORT_BOX_HEIGHT / 2
        )

    def _build(self):
        '''构建槽位面板图'''

        self._drawOuterFrame()
        self._drawPortBox()
        self._drawSlotText()
        self._drawSlotDashLine()

    def _drawOuterFrame(self):
        '''绘制槽位外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawPortBox(self):
        '''绘制电口小框及其文字'''

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(self.PORT_BOX_OFFSET_X, self.PORT_BOX_OFFSET_Y)
        )

        self.addMtext(
            textContent=self.PORT_TEXT,
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(
                self.PORT_BOX_OFFSET_X + self.PORT_BOX_WIDTH / 2,
                self.PORT_BOX_OFFSET_Y + self.PORT_BOX_HEIGHT / 2
            ),
            style=self.PORT_TEXT_STYLE,
            attachment=5
        )

    def _drawSlotText(self):
        '''绘制槽位文字'''

        self.addMtext(
            textContent=f"{self.slotNum}槽",
            textFontHeight=self.SLOT_TEXT_HEIGHT,
            textWidth=self.SLOT_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.SLOT_CENTER_OFFSET_X, self.SLOT_CENTER_OFFSET_Y),
            style=self.SLOT_TEXT_STYLE,
            attachment=5
        )

    def _drawSlotDashLine(self):
        '''绘制槽位内部逻辑线'''

        self.addLine(
            startPoint=Vec2(self.DASH_LINE_START_OFFSET_X, self.DASH_LINE_OFFSET_Y),
            endPoint=Vec2(self.DASH_LINE_END_OFFSET_X, self.DASH_LINE_OFFSET_Y),
            line=逻辑连线示意()
        )

    def frontPoint(self) -> Vec2:
        '''返回电口框前连接点，即左中点绝对坐标'''

        return self.insertPoint + self.frontPointLocal()

    def afterPoint(self) -> Vec2:
        '''返回电口框后连接点，即右中点绝对坐标'''

        return self.insertPoint + self.afterPointLocal()

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入到布局中'''

        return super().insertInto(layout, self.insertPoint)

class GCNDeviceConnectionPanel(NewBlock):
    '''GCN网传输设备连接面板图'''

    WIDTH = 55.8
    HEIGHT = 64.0

    TEXT_STYLE = "gedi"
    TEXT_HEIGHT = 4
    TEXT_WIDTH = 52.0
    TEXT_LINE_SPACING_DISTANCE = 1

    TITLE_INSERT_Y = 61.0
    AREA_INSERT_Y = 55.0
    BOARD_INSERT_Y = 49.0

    SLOT_INSERT_X = 2.2
    SLOT1_INSERT_Y = 26.0
    SLOT2_INSERT_Y = 8.5

    SLOT_NUM_MIN = 1
    SLOT_NUM_MAX = 12

    DEFAULT_SLOT_NUM_LIST = [1, 3]

    ALIGN_TOLERANCE = 0.1

    def __init__(
            self,
            doc: Drawing,
            pNum: str,
            pName: str,
            boardName: str,
            areaName: str,
            insertPoint: Vec2,
            slotNumList: Iterable[int] | None = None
    ) -> None:
        """初始化GCN网传输设备连接面板图

        :param doc: 文档
        :param pNum: 屏号
        :param pName: 屏名
        :param boardName: 板卡名
        :param areaName: 所属域名称
        :param insertPoint: 插入点
        :param slotNumList: 槽位号列表，允许1-12槽，默认绘制1槽和3槽
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.pNum = str(pNum)
        self.pName = str(pName)
        self.boardName = str(boardName)
        self.areaName = str(areaName)
        self.insertPoint = insertPoint

        self.slotNumList: List[int] = list(
            self.DEFAULT_SLOT_NUM_LIST if slotNumList is None else slotNumList
        )

        self._checkSlotNumList()

        self.slotPanelList: List[GCNBoardSlotConnectionPanel] = []

        self._build()

    @classmethod
    def slotFrontPointGapY(cls) -> float:
        '''获取两块板卡电口前连接点的纵向间隔'''

        return abs(
            cls._slotFrontPointLocal(0).y
            - cls._slotFrontPointLocal(1).y
        )

    @classmethod
    def insertPointFromSlotFrontPoints(
            cls,
            insertX: float,
            frontPointList: List[Vec2]
    ) -> Vec2:
        '''根据两个槽位前连接点反算设备插入点'''

        if len(frontPointList) != 2:
            raise ValueError(f"GCN网传输设备接入点数量必须为2，当前数量为{len(frontPointList)}")

        insertYList = [
            frontPoint.y - cls._slotFrontPointLocal(index).y
            for index, frontPoint in enumerate(frontPointList)
        ]

        if abs(insertYList[0] - insertYList[1]) > cls.ALIGN_TOLERANCE:
            raise ValueError(
                "无法保证GCN网传输设备两个槽位同时水平连接: "
                f"insertYList={insertYList}, frontPointList={frontPointList}"
            )

        return Vec2(insertX, sum(insertYList) / len(insertYList))

    @classmethod
    def _slotFrontPointLocal(cls, index: int) -> Vec2:
        '''获取指定槽位前连接点局部坐标'''

        return cls._slotInsertPoint(index) + GCNBoardSlotConnectionPanel.frontPointLocal()

    @classmethod
    def _slotInsertPoint(cls, index: int) -> Vec2:
        '''获取指定槽位插入点局部坐标'''

        slotInsertPointList = [
            Vec2(cls.SLOT_INSERT_X, cls.SLOT1_INSERT_Y),
            Vec2(cls.SLOT_INSERT_X, cls.SLOT2_INSERT_Y)
        ]

        if index < 0 or index >= len(slotInsertPointList):
            raise IndexError(f"槽位索引越界: {index}")

        return slotInsertPointList[index]

    def _build(self):
        '''构建设备面板图'''

        self._drawOuterFrame()
        self._drawHeaderTexts()
        self._buildSlots()

    def _checkSlotNumList(self):
        '''检查槽位号列表'''

        if len(self.slotNumList) != 2:
            raise ValueError(f"GCN网传输设备槽位数量必须为2，当前为{self.slotNumList}")

        for slotNum in self.slotNumList:
            if not isinstance(slotNum, int):
                raise TypeError(f"槽位号必须是int类型，当前值为{slotNum}，类型为{type(slotNum)}")

            if slotNum < self.SLOT_NUM_MIN or slotNum > self.SLOT_NUM_MAX:
                raise ValueError(
                    f"槽位号必须在{self.SLOT_NUM_MIN}-{self.SLOT_NUM_MAX}之间，"
                    f"当前值为{slotNum}"
                )

    def _drawOuterFrame(self):
        '''绘制设备外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawHeaderTexts(self):
        '''绘制顶部三行说明文字'''

        self.addMtext(
            textContent=self._titleText(),
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.TITLE_INSERT_Y),
            style=self.TEXT_STYLE,
            attachment=2
        )

        self.addMtext(
            textContent=self._areaText(),
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.AREA_INSERT_Y),
            style=self.TEXT_STYLE,
            attachment=2
        )

        self.addMtext(
            textContent=self._boardText(),
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.BOARD_INSERT_Y),
            style=self.TEXT_STYLE,
            attachment=2
        )

    def _buildSlots(self):
        '''构建两个槽位面板'''

        slotInsertPointList = [
            Vec2(self.SLOT_INSERT_X, self.SLOT1_INSERT_Y),
            Vec2(self.SLOT_INSERT_X, self.SLOT2_INSERT_Y)
        ]

        for slotNum, slotInsertPoint in zip(self.slotNumList, slotInsertPointList):
            slotPanel = GCNBoardSlotConnectionPanel(
                doc=self.doc,
                slotNum=slotNum,
                insertPoint=slotInsertPoint
            )

            slotPanel.insertInto(self.block)
            self.slotPanelList.append(slotPanel)

    def _titleText(self) -> str:
        '''获取第一行标题'''

        return f"{CADColor.colored(self.pNum)} {CADColor.colored(self.pName)}"

    def _areaText(self) -> str:
        '''获取第二行所属域文字'''

        return f"传输新网B({CADColor.colored(self.areaName)})设备"

    def _boardText(self) -> str:
        '''获取第三行板卡说明'''

        return f"({self.boardName}以太网板卡)"

    def slotFrontPoint(self, index: int) -> Vec2:
        '''获取指定板卡电口前连接点绝对坐标'''

        self._checkSlotIndex(index)
        return self.insertPoint + self.slotPanelList[index].frontPoint()

    def slotAfterPoint(self, index: int) -> Vec2:
        '''获取指定板卡电口后连接点绝对坐标'''

        self._checkSlotIndex(index)
        return self.insertPoint + self.slotPanelList[index].afterPoint()

    def _checkSlotIndex(self, index: int):
        '''检查板卡索引合法性'''

        if index < 0 or index >= len(self.slotPanelList):
            raise IndexError(f"板卡索引越界: {index}")

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入到布局中'''

        return super().insertInto(layout, self.insertPoint)