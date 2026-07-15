##########################################################################################################
#   Description: GCN网连接图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, List, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import CADColor, NewBlock
from ....common.graph import 本期新增网线, 逻辑连线示意, 现有互联六类电缆

from ...reader import DataUnitDDN

from .gcnData import EdgedIDFData, GCNDeviceData, GCNLinkItemData
from .gcnDev import GCNDeviceConnectionPanel
from .gcnIDF import GCNIDFConnectionPanel
from .gcnLinkData import GCNLinkData


class GCNLink(NewBlock):
    '''GCN网连接图'''

    LINE_NUM = 2

    IDF_INTERVAL_X = 12
    DEVICE_INTERVAL_X = 18

    FIRST_LINK_TEXT = "MSTP FE传输专线"

    TARGET_LOGIC_LINE_LENGTH = 48
    TARGET_TEXT_OFFSET_X = 3
    TARGET_TEXT_HEIGHT = 3
    TARGET_TEXT_WIDTH = 45
    TARGET_TEXT_STYLE = "gedi"

    TARGET_TEXT_TEMPLATE = "至{}\n汇聚层路由器设备"

    DEVICE_TYPE_NONE = "none"
    DEVICE_TYPE_EDGED_IDF = "edgedIDF"
    DEVICE_TYPE_NORMAL_IDF = "normalIDF"
    DEVICE_TYPE_GCN_DEVICE = "gcnDevice"
    
    FIRST_LINK_MIDDLE_OFFSET = Vec2(5, 0)

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            insertPoint: Vec2,
            linkPoint1: Vec2,
            linkPoint2: Vec2,
    ) -> None:
        """初始化GCN网连接图

        :param doc: CAD文档
        :param data: ddn数据单元
        :param insertPoint: 插入点
        :param linkPoint1: 新增路由器GCN网电口1接入点
        :param linkPoint2: 新增路由器GCN网电口2接入点
        :param slotNumList: 传输设备两块以太网板卡槽位号，允许1-12槽，默认1槽和3槽
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.data = data
        self.insertPoint = insertPoint

        self.linkData = GCNLinkData(data)

        self.currentPointList: List[Vec2] = [
            linkPoint1,
            linkPoint2
        ]

        self.nextInsertX = insertPoint.x
        self.hasDrawnFirstDevice = False
        self.lastDeviceType = self.DEVICE_TYPE_NONE
        self._checkLinkPointList()
        self._build()

    def _build(self):
        '''构建GCN网连接图'''

        self._buildEdgedIDF()
        self._buildIDFList()
        self._buildGCNDevice()

    def _buildEdgedIDF(self):
        '''构建成端IDF'''

        edgedIDFData = self.linkData.getEdgedIDF()

        if edgedIDFData is None:
            return

        self._addIDFPair(
            devNum=edgedIDFData.devNum,
            devName=edgedIDFData.devName,
            deviceType=self.DEVICE_TYPE_EDGED_IDF
        )

    def _buildIDFList(self):
        '''构建普通IDF跳接链路'''

        for idfUnit in self.linkData.iterIDFUnit():
            self._addIDFPair(
                devNum=idfUnit,
                devName=GCNIDFConnectionPanel.DEVICE_NAME,
                deviceType=self.DEVICE_TYPE_NORMAL_IDF
            )
            
    def _buildGCNDevice(self):
        '''构建GCN网传输设备'''

        deviceData = self.linkData.getDeviceData()
        linkItemDataList = self.linkData.getLinkItemDataList()

        isFirstDevice = not self.hasDrawnFirstDevice
        previousDeviceType = self.lastDeviceType

        if isFirstDevice:
            deviceInsertPoint = Vec2(
                self.nextInsertX,
                self.insertPoint.y
            )
        else:
            deviceInsertPoint = GCNDeviceConnectionPanel.insertPointFromSlotFrontPoints(
                insertX=self.nextInsertX + self.DEVICE_INTERVAL_X,
                frontPointList=self.currentPointList
            )

        devicePanel = GCNDeviceConnectionPanel(
            doc=self.doc,
            pNum=deviceData.pNum,
            pName=deviceData.pName,
            boardName=deviceData.boardName,
            areaName=deviceData.areaName,
            insertPoint=deviceInsertPoint,
            slotNumList=deviceData.slotNumList
        )

        devicePanel.insertInto(self.block)

        # 连接到GCN网设备
        for index, linkItemData in enumerate(linkItemDataList):
            self._connectToGCNDeviceSlot(
                devicePanel=devicePanel,
                linkItemData=linkItemData,
                index=index,
                isFirstDevice=isFirstDevice,
                previousDeviceType=previousDeviceType
            )

        self._markDeviceDrawn(self.DEVICE_TYPE_GCN_DEVICE)
    
    def _addIDFPair(
            self,
            devNum: str,
            devName: str,
            deviceType: str
    ):
        '''添加一组IDF设备，两条线各绘制一个'''

        isFirstDevice = not self.hasDrawnFirstDevice
        previousDeviceType = self.lastDeviceType

        insertPointList = (
            self._firstIDFInsertPointList()
            if isFirstDevice
            else self._normalIDFInsertPointList()
        )

        idfPanelList: List[GCNIDFConnectionPanel] = []

        # 插入两个IDF
        for index, (currentPoint, insertPoint) in enumerate(zip(self.currentPointList, insertPointList)):
            idfPanel = self._addSingleIDF(
                devNum=devNum,
                devName=devName,
                currentPoint=currentPoint,
                insertPoint=insertPoint,
                isFirstDevice=isFirstDevice,
                previousDeviceType=previousDeviceType,
                middleOffset=self._getFirstLinkMiddleOffset(index)
            )

            idfPanelList.append(idfPanel)

        self.currentPointList = [
            idfPanel.afterPoint()
            for idfPanel in idfPanelList
        ]

        self.nextInsertX += GCNIDFConnectionPanel.WIDTH + self.IDF_INTERVAL_X
        self._markDeviceDrawn(deviceType)

    def _addSingleIDF(
            self,
            devNum: str,
            devName: str,
            currentPoint: Vec2,
            insertPoint: Vec2,
            isFirstDevice: bool,
            previousDeviceType: str,
            middleOffset: Optional[Vec2]
    ) -> GCNIDFConnectionPanel:
        '''添加单个IDF设备并连接'''

        idfPanel = GCNIDFConnectionPanel(
            doc=self.doc,
            devNum=devNum,
            devName=devName,
            insertPoint=insertPoint
        )

        idfPanel.insertInto(self.block)

        self._drawInputLink(
            startPoint=currentPoint,
            endPoint=idfPanel.frontPoint(),
            isFirstDevice=isFirstDevice,
            previousDeviceType=previousDeviceType,
            middleOffset=middleOffset
        )

        return idfPanel

    def _connectToGCNDeviceSlot(
            self,
            devicePanel: GCNDeviceConnectionPanel,
            linkItemData: GCNLinkItemData,
            index: int,
            isFirstDevice: bool,
            previousDeviceType: str
    ):
        '''连接到GCN网传输设备槽位'''

        slotFrontPoint = devicePanel.slotFrontPoint(index)
        slotAfterPoint = devicePanel.slotAfterPoint(index)

        self._drawInputLink(
            startPoint=self.currentPointList[index],
            endPoint=slotFrontPoint,
            isFirstDevice=isFirstDevice,
            previousDeviceType=previousDeviceType,
            middleOffset=self._getFirstLinkMiddleOffset(index)
        )

        self._drawTargetLogicLink(
            startPoint=slotAfterPoint,
            targetStation=linkItemData.targetStation
        )

        self.currentPointList[index] = slotAfterPoint

    def _drawInputLink(
            self,
            startPoint: Vec2,
            endPoint: Vec2,
            isFirstDevice: bool,
            previousDeviceType: str,
            middleOffset: Optional[Vec2] = None
    ):
        '''绘制设备前接入线'''

        if isFirstDevice:
            self.addLine(
                startPoint=startPoint,
                endPoint=endPoint,
                line=本期新增网线(),
                polyLine=True,
                text=self.FIRST_LINK_TEXT,
                polyLineMiddleOffset=middleOffset
            )
            return

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=self._getInputLinkLine(previousDeviceType)
        )

    def _drawTargetLogicLink(
            self,
            startPoint: Vec2,
            targetStation: str
    ):
        '''绘制至目标站汇聚层路由器设备逻辑线'''

        endPoint = startPoint + Vec2(self.TARGET_LOGIC_LINE_LENGTH, 0)

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=逻辑连线示意(),
            arrow=True
        )

        self.addMtext(
            textContent=self.TARGET_TEXT_TEMPLATE.format(targetStation),
            textFontHeight=self.TARGET_TEXT_HEIGHT,
            textWidth=self.TARGET_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=endPoint + Vec2(self.TARGET_TEXT_OFFSET_X, 0),
            style=self.TARGET_TEXT_STYLE,
            attachment=4
        )

    def _getInputLinkLine(self, previousDeviceType: str):
        '''获取设备前接入线线型'''

        if previousDeviceType == self.DEVICE_TYPE_EDGED_IDF:
            return 本期新增网线()

        return 现有互联六类电缆()

    def _getFirstLinkMiddleOffset(self, index: int) -> Optional[Vec2]:
        '''获取第一个设备折线中点偏移'''

        if index == 0:
            return None

        return self.FIRST_LINK_MIDDLE_OFFSET 

    def _markDeviceDrawn(self, deviceType: str):
        '''标记设备已经绘制'''

        self.hasDrawnFirstDevice = True
        self.lastDeviceType = deviceType

    def _checkLinkPointList(self):
        '''检查接入点数量'''

        if len(self.currentPointList) != self.LINE_NUM:
            raise ValueError(
                f"GCN网连接图必须输入{self.LINE_NUM}个接入点，"
                f"当前数量为{len(self.currentPointList)}"
            )

    def _firstIDFInsertPointList(self) -> List[Vec2]:
        '''获取第一组IDF插入点列表'''

        sourceGapY = self.currentPointList[1].y - self.currentPointList[0].y
        direction = 1 if sourceGapY >= 0 else -1

        idfGapY = GCNDeviceConnectionPanel.slotFrontPointGapY() * direction

        return [
            Vec2(self.nextInsertX, self.insertPoint.y),
            Vec2(self.nextInsertX, self.insertPoint.y + idfGapY)
        ]

    def _normalIDFInsertPointList(self) -> List[Vec2]:
        '''获取普通IDF组插入点列表'''

        return [
            GCNIDFConnectionPanel.insertPointFromFrontPoint(
                insertX=self.nextInsertX,
                frontPoint=currentPoint
            )
            for currentPoint in self.currentPointList
        ]

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入GCN网连接图'''

        return super().insertInto(layout, Vec2(0, 0))