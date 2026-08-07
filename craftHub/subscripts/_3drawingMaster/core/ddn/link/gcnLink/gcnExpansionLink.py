##########################################################################################################
#   Description: GCN网扩容连接图
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
from .gcnData import GCNDeviceData
from .gcnDev import GCNDeviceConnectionPanel
from .gcnIDF import GCNIDFConnectionPanel
from .gcnLinkData import GCNLinkData


class GCNExpansionLink(NewBlock):
    '''GCN网扩容连接图'''

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

    FIRST_LINE_LEN1 = 23.5
    FIRST_LINE_LEN2 = 32.7

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            insertPoint: Vec2,
            linkPoint1: Vec2,
            linkPoint2: Vec2,
            linkData: GCNLinkData | None = None
    ) -> None:
        """初始化GCN网扩容连接图

        :param doc: CAD文档
        :param data: DDN数据单元
        :param insertPoint: 插入点
        :param linkPoint1: 新增路由器GCN网电口1接入点
        :param linkPoint2: 新增路由器GCN网电口2接入点
        :param linkData: GCN连接数据
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.data = data
        self.insertPoint = insertPoint
        self.linkData = GCNLinkData(data) if linkData is None else linkData

        self.currentPointList: List[Vec2] = [
            linkPoint1,
            linkPoint2
        ]

        self._checkLinkPointList()
        self._build()

    def _build(self):
        '''构建GCN网扩容连接图'''

        deviceData = self.linkData.getDeviceData()
        devicePanel = self._buildGCNDevice(deviceData)

        for index, linkItemData in enumerate(self.linkData.getLinkItemDataList()):
            self._connectExpansionSlot(
                devicePanel=devicePanel,
                index=index,
                targetStation=linkItemData.targetStation
            )

    def _buildGCNDevice(
            self,
            deviceData: GCNDeviceData
    ) -> GCNDeviceConnectionPanel:
        '''构建扩容模式下的GCN网传输设备'''

        deviceInsertPoint = Vec2(
            self._gcnDeviceInsertX(deviceData),
            self.insertPoint.y
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

        return devicePanel

    def _gcnDeviceInsertX(
            self,
            deviceData: GCNDeviceData
    ) -> float:
        '''获取扩容模式下GCN网传输设备X坐标'''

        maxIDFLevel = 0

        if self.linkData.hasEdgedIDF():
            maxIDFLevel += 1

        hasBranchIDF = False

        for slotNum in deviceData.slotNumList:
            ethSlotData = deviceData.getETHSlotDataBySlotNum(slotNum)

            if ethSlotData.isOccupied() and deviceData.hasExistedEdgedIDF():
                hasBranchIDF = True

            if ethSlotData.isNew() and deviceData.hasNewETHslotEdgedIDF():
                hasBranchIDF = True

        if hasBranchIDF:
            maxIDFLevel += 1

        return (
            self.insertPoint.x
            + maxIDFLevel * (GCNIDFConnectionPanel.WIDTH + self.IDF_INTERVAL_X)
            + self.DEVICE_INTERVAL_X
        )

    def _connectExpansionSlot(
            self,
            devicePanel: GCNDeviceConnectionPanel,
            index: int,
            targetStation: str
    ):
        '''连接扩容模式下的单个槽位'''

        deviceData = self.linkData.getDeviceData()

        slotNum = deviceData.slotNumList[index]
        ethSlotData = deviceData.getETHSlotDataBySlotNum(slotNum)

        currentPoint = self.currentPointList[index]
        slotFrontPoint = devicePanel.slotFrontPoint(index)
        slotAfterPoint = devicePanel.slotAfterPoint(index)

        nextIDFX = self.insertPoint.x
        isFirstDevice = True

        currentPoint, nextIDFX, isFirstDevice = self._connectFrontEdgedIDF(
            currentPoint=currentPoint,
            nextIDFX=nextIDFX,
            index=index,
            slotFrontPoint=slotFrontPoint,
            isFirstDevice=isFirstDevice
        )

        # 占用槽位连接
        if ethSlotData.isOccupied():
            self._connectOccupiedSlot(
                currentPoint=currentPoint,
                nextIDFX=nextIDFX,
                slotFrontPoint=slotFrontPoint,
                slotAfterPoint=slotAfterPoint,
                index=index,
                targetStation=targetStation,
                isFirstDevice=isFirstDevice
            )
            return

        # 新增槽位连接
        if ethSlotData.isNew():
            self._connectNewSlot(
                currentPoint=currentPoint,
                nextIDFX=nextIDFX,
                slotFrontPoint=slotFrontPoint,
                slotAfterPoint=slotAfterPoint,
                index=index,
                targetStation=targetStation,
                isFirstDevice=isFirstDevice
            )
            return

        raise ValueError(f"{slotNum}槽未标记<o>或<n>，不能参与扩容连接")

    def _connectFrontEdgedIDF(
            self,
            currentPoint: Vec2,
            nextIDFX: float,
            index: int,
            slotFrontPoint: Vec2,
            isFirstDevice: bool
    ):
        '''连接扩容模式下的前置成端IDF'''

        edgedIDFData = self.linkData.getEdgedIDF()

        if edgedIDFData is None:
            return currentPoint, nextIDFX, isFirstDevice

        idfPanel = self._buildIDFPanel(
            devNum=edgedIDFData.devNum,
            devName=edgedIDFData.devName,
            insertX=nextIDFX,
            alignPoint=slotFrontPoint
        )

        self._drawInputLink(
            startPoint=currentPoint,
            endPoint=idfPanel.frontPoint(),
            index=index,
            isFirstDevice=isFirstDevice,
            line=本期新增网线()
        )

        return (
            idfPanel.afterPoint(),
            nextIDFX + GCNIDFConnectionPanel.WIDTH + self.IDF_INTERVAL_X,
            False
        )

    def _connectOccupiedSlot(
            self,
            currentPoint: Vec2,
            nextIDFX: float,
            slotFrontPoint: Vec2,
            slotAfterPoint: Vec2,
            index: int,
            targetStation: str,
            isFirstDevice: bool
    ):
        '''连接扩容模式下的占用板卡'''

        deviceData = self.linkData.getDeviceData()

        if deviceData.hasExistedEdgedIDF():
            idfPanel = self._buildIDFPanel(
                devNum=deviceData.existedEdgedIDF, # type: ignore
                devName=GCNIDFConnectionPanel.DEVICE_NAME,
                insertX=nextIDFX,
                alignPoint=slotFrontPoint
            )

            # 前一个设备 → GCN旧有成端IDF
            # 这段是本项目新增连接，所以用本期新增网线
            self._drawInputLink(
                startPoint=currentPoint,
                endPoint=idfPanel.frontPoint(),
                index=index,
                isFirstDevice=isFirstDevice,
                line=本期新增网线()
            )

            # GCN旧有成端IDF → GCN设备占用板卡
            # 这段是已有跳接关系，所以用现有互联六类电缆
            self.addLine(
                startPoint=idfPanel.afterPoint(),
                endPoint=slotFrontPoint,
                line=现有互联六类电缆(),
                text="利旧现有电缆"
            )

        else:
            self._drawInputLink(
                startPoint=currentPoint,
                endPoint=slotFrontPoint,
                index=index,
                isFirstDevice=isFirstDevice,
                line=本期新增网线()
            )

        self._drawTargetLogicLink(
            startPoint=slotAfterPoint,
            targetStation=targetStation
        )

    def _connectNewSlot(
            self,
            currentPoint: Vec2,
            nextIDFX: float,
            slotFrontPoint: Vec2,
            slotAfterPoint: Vec2,
            index: int,
            targetStation: str,
            isFirstDevice: bool
    ):
        '''连接扩容模式下的新增板卡'''

        deviceData = self.linkData.getDeviceData()

        if deviceData.hasNewETHslotEdgedIDF():
            idfPanel = self._buildIDFPanel(
                devNum=deviceData.newETHslotEdgedIDF, # type: ignore
                devName=GCNIDFConnectionPanel.DEVICE_NAME,
                insertX=nextIDFX,
                alignPoint=slotFrontPoint
            )

            self._drawInputLink(
                startPoint=currentPoint,
                endPoint=idfPanel.frontPoint(),
                index=index,
                isFirstDevice=isFirstDevice,
                line=本期新增网线()
            )

            self.addLine(
                startPoint=idfPanel.afterPoint(),
                endPoint=slotFrontPoint,
                line=本期新增网线()
            )

        else:
            self._drawInputLink(
                startPoint=currentPoint,
                endPoint=slotFrontPoint,
                index=index,
                isFirstDevice=isFirstDevice,
                line=本期新增网线()
            )

        self._drawTargetLogicLink(
            startPoint=slotAfterPoint,
            targetStation=targetStation
        )

    def _buildIDFPanel(
            self,
            devNum: str,
            devName: str,
            insertX: float,
            alignPoint: Vec2
    ) -> GCNIDFConnectionPanel:
        '''构建扩容模式下的IDF面板'''

        insertPoint = GCNIDFConnectionPanel.insertPointFromFrontPoint(
            insertX=insertX,
            frontPoint=alignPoint
        )

        idfPanel = GCNIDFConnectionPanel(
            doc=self.doc,
            devNum=devNum,
            devName=devName,
            insertPoint=insertPoint
        )

        idfPanel.insertInto(self.block)

        return idfPanel

    def _drawInputLink(
            self,
            startPoint: Vec2,
            endPoint: Vec2,
            index: int,
            isFirstDevice: bool,
            line
    ):
        '''绘制扩容模式设备输入线'''

        if isFirstDevice:
            self.addLine(
                startPoint=startPoint,
                endPoint=endPoint,
                line=line,
                polyLine=True,
                text=self.FIRST_LINK_TEXT,
                polyLineFirstLineLen=self._getFirstLineLen(index)
            )
            return

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=line,
            text="利旧现有电缆" if isinstance(line, 现有互联六类电缆) else None
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

    def _getFirstLineLen(self, index: int) -> float:
        '''获取第一个设备折线中点偏移'''

        if index == 0:
            return self.FIRST_LINE_LEN1

        return self.FIRST_LINE_LEN2

    def _checkLinkPointList(self):
        '''检查接入点数量'''

        if len(self.currentPointList) != self.LINE_NUM:
            raise ValueError(
                f"GCN网连接图必须输入{self.LINE_NUM}个接入点，"
                f"当前数量为{len(self.currentPointList)}"
            )

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入GCN网扩容连接图'''

        return super().insertInto(layout, Vec2(0, 0))