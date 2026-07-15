##########################################################################################################
#   Description: 纵向加密连接图接入交换机设备节点
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, List, Optional

from ezdxf.math import Vec2

from .cryptoCommonDev import CommonCryptoDev, CryptoChannel, CryptoDeviceType
from ..cryptoConnectionPanel import AccessSwitchConnectionPanel


class CryptoAccessSwitch(CommonCryptoDev):
    '''纵向加密连接图接入交换机设备节点'''

    DEVICE_NAME = "接入交换机"
    DEVICE_TYPE = CryptoDeviceType.ACCESS_SWITCH
    IS_NEW = False

    DEFAULT_FRONT_PORT_1 = "端口1"
    DEFAULT_FRONT_PORT_2 = "端口2"
    DEFAULT_AFTER_PORT_1 = "端口3"
    DEFAULT_AFTER_PORT_2 = "端口4"

    def __init__(
            self,
            deviceNum: str,
            frontPort1: str = DEFAULT_FRONT_PORT_1,
            frontPort2: str = DEFAULT_FRONT_PORT_2,
            afterPort1: str = DEFAULT_AFTER_PORT_1,
            afterPort2: str = DEFAULT_AFTER_PORT_2,
            isRoom2: bool = False,
            isJump: bool = False,
            isNoPhoto: bool = False
    ) -> None:
        """初始化接入交换机设备节点

        :param deviceNum:   设备号
        :param frontPort1:  前端口1
        :param frontPort2:  前端口2
        :param afterPort1:  后端口1
        :param afterPort2:  后端口2
        :param isRoom2:     是否在第二机房
        :param isJump:      是否跳过绘制
        :param isNoPhoto:   是否未拍照
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

        self.frontPort1 = frontPort1
        self.frontPort2 = frontPort2
        self.afterPort1 = afterPort1
        self.afterPort2 = afterPort2

        self.panel: Optional[AccessSwitchConnectionPanel] = None
        self.insertPoint: Optional[Vec2] = None

    def drawPanel(
            self,
            owner: Any,
            insertX: float,
            rtCurrentPoint: Vec2,
            nrtCurrentPoint: Vec2
    ) -> float:
        '''绘制设备面板，返回设备宽度'''

        self.insertPoint = AccessSwitchConnectionPanel.insertPointFromFrontPoints(
            insertX=insertX,
            rtLinkPoint=rtCurrentPoint,
            nrtLinkPoint=nrtCurrentPoint
        )

        self.panel = AccessSwitchConnectionPanel(
            doc=owner.doc,
            devNum=self.deviceNum, # type: ignore
            devName=self.deviceName,
            frontPort1=self.frontPort1,
            frontPort2=self.frontPort2,
            afterPort1=self.afterPort1,
            afterPort2=self.afterPort2,
            insertPoint=self.insertPoint
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
            return self.panel.RTPointFront(), self.frontPort1  # type: ignore

        if channel == CryptoChannel.NRT:
            return self.panel.NRTPointFront(), self.frontPort2  # type: ignore

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def afterPoint(self, channel: str):
        '''获取设备后连接点和端口名'''

        self._assertPanelDrawn()

        if channel == CryptoChannel.RT:
            return self.panel.RTPointAfter(), self.afterPort1  # type: ignore

        if channel == CryptoChannel.NRT:
            return self.panel.NRTPointAfter(), self.afterPort2  # type: ignore

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