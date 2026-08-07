##########################################################################################################
#   Description: 至纵向加密部分连接图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, List, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import CADColor, NewBlock
from ....common.graph import 本期新增网线, 现有互联六类电缆, 逻辑连线示意
from .cryptoCommonDev import CommonCryptoDev, CryptoChannel, CryptoDeviceType

from ...reader import DataUnitDDN
from .parser import CryptoLinkReader
from .room2FrameManager import Room2FrameManager


class LinkStyle:
    '''连接线型'''

    NEW = "new"
    LEGACY = "legacy"
    LOGIC = "logic"


class LinkDecision:
    '''连接线绘制决策'''

    LOGIC_TEXT = "利旧现有电缆"

    def __init__(self, style: str) -> None:
        """初始化连接线绘制决策

        :param style: 连接线型
        """
        self.style = style

    def line(self):
        '''创建连接线对象'''

        if self.style == LinkStyle.NEW:
            return 本期新增网线()

        if self.style == LinkStyle.LEGACY:
            return 现有互联六类电缆()

        if self.style == LinkStyle.LOGIC:
            return 逻辑连线示意()

        raise ValueError(f"未知连接线型: {self.style}")

    def arrow(self) -> bool:
        '''是否绘制箭头'''

        return self.style == LinkStyle.LOGIC

    def text(self) -> Optional[str]:
        '''连接线文字'''

        if self.style == LinkStyle.LEGACY:
            return self.LOGIC_TEXT

        if self.style == LinkStyle.LOGIC:
            return self.LOGIC_TEXT

        return None


class CryptoLink(NewBlock):
    '''至纵向加密部分连接图'''

    DEVICE_INTERVAL_X = 18
    LOGIC_LINK_EXTRA_LENGTH = 60
    NO_PHOTO_LINK_LENGTH = 60

    DATA_KEY_RTCD_PNAME = "rtcdPname"
    DATA_KEY_NRTCD_PNAME = "nrtcdPname"
    
    NO_PHOTO_LINK_LENGTH = 60
    NO_PHOTO_TEXT_OFFSET = Vec2(2, 0)
    NO_PHOTO_TEXT_FONT_HEIGHT = 3
    NO_PHOTO_TEXT_WIDTH = 60
    NO_PHOTO_TEXT_ATTACHMENT = 4  # 左中对齐
    
    FIRST_EDGED_IDF_DIRECTION = "right"

    FIRST_EDGED_IDF_NOTE_TEXT = "敷设新网线至原设备\n成端IDF配线单元后端"
    FIRST_EDGED_IDF_NOTE_FONT_HEIGHT = 3
    FIRST_EDGED_IDF_NOTE_WIDTH = 80
    FIRST_EDGED_IDF_NOTE_OFFSET = Vec2(0, -4.4)
    FIRST_EDGED_IDF_NOTE_ATTACHMENT = 2  # 上中对齐

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            insertPoint: Vec2,
            rtLinkPoint: Vec2,
            nrtLinkPoint: Vec2,
            simplified: bool = True
    ) -> None:
        """初始化至纵向加密部分连接图

        :param doc:          CAD文档
        :param data:         数据单元
        :param insertPoint:  第一个设备插入点
        :param rtLinkPoint:  实时链路接入点
        :param nrtLinkPoint: 非实时链路接入点
        :param simplified:   是否简化绘图
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.data = data
        self.simplified = simplified

        self.reader = CryptoLinkReader(data)
        self.room2FrameManager = Room2FrameManager(data.get("room2Name"))

        self.rtCurrentPoint = rtLinkPoint
        self.nrtCurrentPoint = nrtLinkPoint

        self.rtCurrentPortName: Optional[str] = "新增低端路由器实时电口"
        self.nrtCurrentPortName: Optional[str] = "新增低端路由器非实时电口"
        self.nextInsertX = insertPoint.x

        self.lastDevice: Optional[CommonCryptoDev] = None

        self._build()

    def _build(self):
        '''构建纵向加密连接图'''

        rawDeviceList = self.reader.toDeviceList()  # 获取全部设备列表
        drawDeviceList = self._toDrawDeviceList(rawDeviceList)  # 过滤NP， 简化设备处理

        for deviceIndex, device in enumerate(drawDeviceList):
            self._drawDevice(device, deviceIndex)    # 逐个绘制设备

        self.room2FrameManager.drawInto(self)   # 绘制第二房间框

    def _toDrawDeviceList(
            self,
            deviceList: List[CommonCryptoDev]
    ) -> List[CommonCryptoDev]:
        '''获取实际绘制的设备列表'''

        deviceList = self._truncateAfterNoPhotoDevice(deviceList)

        if not self.simplified:
            return deviceList

        oldDeviceIndexList = [
            index
            for index, device in enumerate(deviceList)
            if not device.isNew
        ]

        if len(oldDeviceIndexList) <= 2:
            return deviceList

        firstOldDeviceIndex = oldDeviceIndexList[0]
        lastOldDeviceIndex = oldDeviceIndexList[-1]

        return [
            device
            for index, device in enumerate(deviceList)
            if device.isNew
            or index == firstOldDeviceIndex
            or index == lastOldDeviceIndex
        ]

    def _truncateAfterNoPhotoDevice(
            self,
            deviceList: List[CommonCryptoDev]
    ) -> List[CommonCryptoDev]:
        '''遇到未拍摄设备后截断设备列表'''

        for index, device in enumerate(deviceList):
            if device.isNoPhoto:
                return deviceList[:index + 1]

        return deviceList

    def _prepareFirstEdgedIDF(
            self,
            device: CommonCryptoDev,
            deviceIndex: int
    ):
        '''准备第一个成端IDF绘制参数'''

        if deviceIndex != 0:
            return

        if not self._isEdgedIDF(device):
            return

        setattr(device, "direction", self.FIRST_EDGED_IDF_DIRECTION)


    def _isEdgedIDF(
            self,
            device: CommonCryptoDev
    ) -> bool:
        '''判断是否为成端IDF'''

        return device.deviceType in [
            CryptoDeviceType.NEW_EDGED_IDF,
            CryptoDeviceType.EXISTED_EDGED_IDF
        ]

    def _drawDevice(self, device: CommonCryptoDev, deviceIndex: int):
        '''绘制一个设备节点'''

        # 绘制未拍摄设备
        if device.isNoPhoto:
            self._drawNoPhotoDevice(device)
            self.lastDevice = device
            return

        # 绘制已拍摄设备
        linkDecision = self._getLinkDecision(device)    # 获取连线类型
        insertX = self._getDeviceInsertX(linkDecision)  # 获取插入X坐标

        self._prepareFirstEdgedIDF(device, deviceIndex)
        panelWidth = device.drawPanel(
            owner=self,
            insertX=insertX,
            rtCurrentPoint=self.rtCurrentPoint,
            nrtCurrentPoint=self.nrtCurrentPoint
        )

        for channel in device.channelList():
            self._drawChannelLine(
                device=device,
                channel=channel,
                linkDecision=linkDecision,
                deviceIndex = deviceIndex
            )

        device.recordRoom2Panel(self)

        self.lastDevice = device
        self._moveNextInsertX(panelWidth, linkDecision)

    def _drawNoPhotoDevice(self, device: CommonCryptoDev):
        '''绘制未拍摄设备逻辑连接'''

        linkDecision = LinkDecision(LinkStyle.LOGIC)

        for channel in device.channelList():
            self._drawNoPhotoChannelLine(
                device=device,
                channel=channel,
                linkDecision=linkDecision
            )

    def _drawNoPhotoChannelLine(
            self,
            device: CommonCryptoDev,
            channel: str,
            linkDecision: LinkDecision
    ):
        '''绘制未拍摄设备单通道逻辑连接'''

        if channel == CryptoChannel.RT:
            startPoint = self.rtCurrentPoint

            if startPoint is None:
                return

            endPoint = startPoint + Vec2(self.NO_PHOTO_LINK_LENGTH, 0)

            self.addLine(
                startPoint=startPoint,
                endPoint=endPoint,
                line=linkDecision.line(),
                arrow=linkDecision.arrow()
            )

            self.addMtext(
                textContent=self._getNoPhotoText(device, channel),
                textFontHeight=self.NO_PHOTO_TEXT_FONT_HEIGHT,
                textWidth=self.NO_PHOTO_TEXT_WIDTH,
                insertPoint=endPoint + self.NO_PHOTO_TEXT_OFFSET,
                attachment=self.NO_PHOTO_TEXT_ATTACHMENT,
                style = "gedi"
            )

            self.rtCurrentPoint = endPoint
            return

        if channel == CryptoChannel.NRT:
            startPoint = self.nrtCurrentPoint

            if startPoint is None:
                return

            endPoint = startPoint + Vec2(self.NO_PHOTO_LINK_LENGTH, 0)

            self.addLine(
                startPoint=startPoint,
                endPoint=endPoint,
                line=linkDecision.line(),
                arrow=linkDecision.arrow()
            )

            self.addMtext(
                textContent=self._getNoPhotoText(device, channel),
                textFontHeight=self.NO_PHOTO_TEXT_FONT_HEIGHT,
                textWidth=self.NO_PHOTO_TEXT_WIDTH,
                insertPoint=endPoint + self.NO_PHOTO_TEXT_OFFSET,
                attachment=self.NO_PHOTO_TEXT_ATTACHMENT,
                style = "gedi"
            )

            self.nrtCurrentPoint = endPoint
            return

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def _getNoPhotoText(
            self,
            device: CommonCryptoDev,
            channel: str
    ) -> str:
        '''获取未拍摄设备逻辑连接文字'''

        pName = self._getNoPhotoPname(device, channel)
        deviceNum = self._getNoPhotoDeviceNum(device, channel)

        return f"至{pName}\n{deviceNum}"
    
    def _getNoPhotoPname(
            self,
            device: CommonCryptoDev,
            channel: str
    ) -> str:
        '''获取未拍摄设备屏位名'''

        if channel == CryptoChannel.RT:
            return getattr(
                device,
                "rtPname",
                self.data.get(self.DATA_KEY_RTCD_PNAME)
            )

        if channel == CryptoChannel.NRT:
            return getattr(
                device,
                "nrtPname",
                self.data.get(self.DATA_KEY_NRTCD_PNAME)
            )

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def _getNoPhotoDeviceNum(
            self,
            device: CommonCryptoDev,
            channel: str
    ) -> str:
        '''获取未拍摄设备编号'''

        if channel == CryptoChannel.RT:
            return getattr(
                device, 
                "rtPnum",
                device.deviceNum
            ) # type: ignore

        if channel == CryptoChannel.NRT:
            return getattr(
                device,
                "nrtPnum",
                device.deviceNum
            ) # type: ignore

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def _drawChannelLine(
            self,
            device: CommonCryptoDev,
            channel: str,
            linkDecision: LinkDecision,
            deviceIndex: int
    ):
        '''绘制指定通道连接线'''
        
        # 特殊修改， 第一条线总是绘制两条线
        lineNum = 2 if deviceIndex == 0 else 1

        if channel == CryptoChannel.RT:
            startPoint = self.rtCurrentPoint
            startPortName = self.rtCurrentPortName

            frontPoint, frontPortName = device.frontPoint(channel)
            afterPoint, afterPortName = device.afterPoint(channel)

            if startPortName is not None and frontPortName is not None:
                self.addLine(
                    startPoint=startPoint,
                    endPoint=frontPoint,
                    line=linkDecision.line(),
                    arrow=linkDecision.arrow(),
                    text=linkDecision.text(),
                    num=lineNum,
                    offsetOrient="y"
                )

            self.rtCurrentPoint = afterPoint
            self.rtCurrentPortName = afterPortName
            return

        elif channel == CryptoChannel.NRT:
            startPoint = self.nrtCurrentPoint
            startPortName = self.nrtCurrentPortName

            frontPoint, frontPortName = device.frontPoint(channel)
            afterPoint, afterPortName = device.afterPoint(channel)

            if startPortName is not None and frontPortName is not None:
                self.addLine(
                    startPoint=startPoint,
                    endPoint=frontPoint,
                    line=linkDecision.line(),
                    arrow=linkDecision.arrow(),
                    text=linkDecision.text(),
                    num=lineNum,
                    offsetOrient="y"
                )

                if self._shouldDrawFirstEdgedIDFNote(device, channel, deviceIndex):
                    self._drawFirstEdgedIDFNote(
                        startPoint=startPoint,
                        endPoint=frontPoint
                    )

            self.nrtCurrentPoint = afterPoint
            self.nrtCurrentPortName = afterPortName
            return

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def _shouldDrawFirstEdgedIDFNote(
            self,
            device: CommonCryptoDev,
            channel: str,
            deviceIndex: int
    ) -> bool:
        '''是否绘制第一个成端IDF说明文字'''

        if deviceIndex != 0:
            return False

        if channel != CryptoChannel.NRT:
            return False

        return self._isEdgedIDF(device)


    def _drawFirstEdgedIDFNote(
            self,
            startPoint: Vec2,
            endPoint: Vec2
    ):
        '''绘制第一个成端IDF说明文字'''

        centerPoint = (startPoint + endPoint) / 2

        self.addMtext(
            textContent=self.FIRST_EDGED_IDF_NOTE_TEXT,
            textFontHeight=self.FIRST_EDGED_IDF_NOTE_FONT_HEIGHT,
            textWidth=self.FIRST_EDGED_IDF_NOTE_WIDTH,
            textColor=CADColor.toIndex("红色"),
            textLineSpacingDistance=1,
            insertPoint=centerPoint + self.FIRST_EDGED_IDF_NOTE_OFFSET,
            style="gedi",
            attachment=self.FIRST_EDGED_IDF_NOTE_ATTACHMENT
        )

    def _getLinkDecision(self, currentDevice: CommonCryptoDev) -> LinkDecision:
        '''获取当前设备接入线绘制决策'''

        if self._shouldUseLogicLine(currentDevice):
            return LinkDecision(LinkStyle.LOGIC)

        if self.lastDevice is None:
            return LinkDecision(LinkStyle.NEW)

        if self.lastDevice.isNew:
            return LinkDecision(LinkStyle.NEW)

        return LinkDecision(LinkStyle.LEGACY)

    def _shouldUseLogicLine(self, currentDevice: CommonCryptoDev) -> bool:
        '''是否使用逻辑连线示意'''

        if not self.simplified:
            return False

        if self.lastDevice is None:
            return False

        if self.lastDevice.isNew:
            return False

        if currentDevice.isNew:
            return False

        return True

    def _getDeviceInsertX(self, linkDecision: LinkDecision) -> float:
        '''获取设备插入点X坐标'''

        if linkDecision.style == LinkStyle.LOGIC:
            return self.nextInsertX + self.LOGIC_LINK_EXTRA_LENGTH

        return self.nextInsertX

    def _moveNextInsertX(
            self,
            panelWidth: float,
            linkDecision: LinkDecision
    ):
        '''移动下一个设备插入点X坐标'''

        self.nextInsertX += panelWidth + self.DEVICE_INTERVAL_X

        if linkDecision.style == LinkStyle.LOGIC:
            self.nextInsertX += self.LOGIC_LINK_EXTRA_LENGTH

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入至纵向加密部分连接图'''

        return super().insertInto(layout, Vec2(0, 0))