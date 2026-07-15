##########################################################################################################
#   Description: 纵向加密连接图普通IDF设备节点
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, List, Optional

from ezdxf.math import Vec2

from .cryptoCommonDev import CommonCryptoDev, CryptoChannel, CryptoDeviceType
from ..cryptoConnectionPanel import CDIDFConnectionPanel


class CryptoNormalIDF(CommonCryptoDev):
    '''纵向加密连接图普通IDF设备节点'''

    DEVICE_NAME = "IDF配线单元"
    DEVICE_TYPE = CryptoDeviceType.NORMAL_IDF
    IS_NEW = False

    def __init__(
            self,
            deviceNum: str,
            portR: str,
            portNR: str,
            isRoom2: bool = False,
            isJump: bool = False,
            isNoPhoto: bool = False,
            isCutBusiness: bool = False
    ) -> None:
        """初始化普通IDF设备节点

        :param deviceNum:      设备号
        :param portR:          实时业务端口
        :param portNR:         非实时业务端口
        :param isRoom2:        是否在第二机房
        :param isJump:         是否跳过绘制
        :param isNoPhoto:      是否未拍照
        :param isCutBusiness:  是否绘制断开业务标记
        """

        super().__init__(
            deviceNum=deviceNum,
            deviceName=self.DEVICE_NAME,
            deviceType=self.DEVICE_TYPE,
            isNew=self.IS_NEW,
            isRoom2=isRoom2,
            isJump=isJump,
            isNoPhoto=isNoPhoto
        )

        self.portR = portR
        self.portNR = portNR
        self.isCutBusiness = isCutBusiness

        self.panel: Optional[CDIDFConnectionPanel] = None
        self.insertPoint: Optional[Vec2] = None

    def drawPanel(
            self,
            owner: Any,
            insertX: float,
            rtCurrentPoint: Vec2,
            nrtCurrentPoint: Vec2
    ) -> float:
        '''绘制设备面板，返回设备宽度'''

        self.insertPoint = CDIDFConnectionPanel.insertPointFromFrontPoints(
            insertX=insertX,
            rtLinkPoint=rtCurrentPoint,
            nrtLinkPoint=nrtCurrentPoint
        )

        self.panel = CDIDFConnectionPanel(
            doc=owner.doc,
            devNum=self.deviceNum, # type: ignore
            devName=self.deviceName,
            portR=self.portR,
            portNR=self.portNR,
            insertPoint=self.insertPoint,
            isCutBusiness=self.isCutBusiness
        )

        self.panel.insertInto(owner.block)

        return self.panel.WIDTH

    def channelList(self) -> List[str]:
        '''返回该设备参与连接的通道'''

        return [
            CryptoChannel.RT,
            CryptoChannel.NRT
        ]

    def frontPoint(self, channel: str):
        '''获取设备前连接点和端口名'''

        self._assertPanelDrawn()

        if channel == CryptoChannel.RT:
            return self.panel.RTPointFront(), self.portR  # type: ignore

        if channel == CryptoChannel.NRT:
            return self.panel.NRTPointFront(), self.portNR  # type: ignore

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def afterPoint(self, channel: str):
        '''获取设备后连接点和端口名'''

        self._assertPanelDrawn()

        if channel == CryptoChannel.RT:
            return self.panel.RTPointAfter(), self.portR  # type: ignore

        if channel == CryptoChannel.NRT:
            return self.panel.NRTPointAfter(), self.portNR  # type: ignore

        raise ValueError(f"未知纵向加密链路通道: {channel}")


    def recordRoom2Panel(self, owner: Any):
        '''记录第二机房边界'''

        if not self.isRoom2:
            return

        self._assertPanelDrawn()

        owner.room2FrameManager.recordPanel(
            insertPoint=self.insertPoint,
            width=self.panel.WIDTH,   # type: ignore
            height=self.panel.HEIGHT  # type: ignore
        )

    def _assertPanelDrawn(self):
        '''检查设备面板是否已经绘制'''

        if self.panel is None or self.insertPoint is None:
            raise ValueError(f"{self.deviceNum} {self.deviceName} 尚未绘制，无法获取连接点")