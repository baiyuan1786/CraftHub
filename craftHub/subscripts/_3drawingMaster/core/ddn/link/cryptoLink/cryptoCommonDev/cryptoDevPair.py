##########################################################################################################
#   Description: 纵向加密连接图加密设备对节点
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, List, Optional

from ezdxf.math import Vec2

from .cryptoCommonDev import CommonCryptoDev, CryptoChannel, CryptoDeviceType
from ..cryptoConnectionPanel import CDConnectionPanel


class CryptoDevPair(CommonCryptoDev):
    '''纵向加密连接图加密设备对节点'''

    DEVICE_NAME = "纵向加密设备对"
    DEVICE_TYPE = CryptoDeviceType.CD_PAIR
    IS_NEW = False

    def __init__(
            self,
            rtPnum: str,
            rtPname: str,
            nrtPnum: str,
            nrtPname: str,
            rtIsRoom2: bool = False,
            nrtIsRoom2: bool = False,
            rtIsJump: bool = False,
            nrtIsJump: bool = False,
            rtIsNoPhoto: bool = False,
            nrtIsNoPhoto: bool = False
    ) -> None:
        """初始化加密设备对节点

        :param rtPnum:       实时纵向加密设备所在屏位号
        :param rtPname:      实时纵向加密设备所在屏位名
        :param nrtPnum:      非实时纵向加密设备所在屏位号
        :param nrtPname:     非实时纵向加密设备所在屏位名
        :param rtIsRoom2:    实时纵向加密设备是否在第二机房
        :param nrtIsRoom2:   非实时纵向加密设备是否在第二机房
        :param rtIsJump:     实时纵向加密设备是否跳过绘制
        :param nrtIsJump:    非实时纵向加密设备是否跳过绘制
        :param rtIsNoPhoto:  实时纵向加密设备是否未拍照
        :param nrtIsNoPhoto: 非实时纵向加密设备是否未拍照
        """

        super().__init__(
            deviceNum=None,
            deviceName=self.DEVICE_NAME,
            deviceType=self.DEVICE_TYPE,
            isNew=self.IS_NEW,
            isRoom2=rtIsRoom2 or nrtIsRoom2,
            isJump=rtIsJump and nrtIsJump,
            isNoPhoto=rtIsNoPhoto or nrtIsNoPhoto
        )

        self.rtPnum = rtPnum
        self.rtPname = rtPname
        self.rtIsRoom2 = rtIsRoom2
        self.rtIsJump = rtIsJump
        self.rtIsNoPhoto = rtIsNoPhoto

        self.nrtPnum = nrtPnum
        self.nrtPname = nrtPname
        self.nrtIsRoom2 = nrtIsRoom2
        self.nrtIsJump = nrtIsJump
        self.nrtIsNoPhoto = nrtIsNoPhoto

        self.rtPanel: Optional[CDConnectionPanel] = None
        self.nrtPanel: Optional[CDConnectionPanel] = None

    def drawPanel(
            self,
            owner: Any,
            insertX: float,
            rtCurrentPoint: Vec2,
            nrtCurrentPoint: Vec2
    ) -> float:
        '''绘制设备面板，返回设备宽度'''

        if self.rtIsJump and self.nrtIsJump:
            return 0

        if not self.rtIsJump:
            rtInsertPoint = CDConnectionPanel.insertPointFromFrontPoint(
                frontPoint=Vec2(insertX, rtCurrentPoint.y),
                crypoType=CryptoChannel.RT
            )

            self.rtPanel = CDConnectionPanel(
                doc=owner.doc,
                devPnum=self.rtPnum,
                devPname=self.rtPname,
                crypoType=CryptoChannel.RT,
                insertPoint=rtInsertPoint
            )

            self.rtPanel.insertInto(owner.block)

        if not self.nrtIsJump:
            nrtInsertPoint = CDConnectionPanel.insertPointFromFrontPoint(
                frontPoint=Vec2(insertX, nrtCurrentPoint.y),
                crypoType=CryptoChannel.NRT
            )

            self.nrtPanel = CDConnectionPanel(
                doc=owner.doc,
                devPnum=self.nrtPnum,
                devPname=self.nrtPname,
                crypoType=CryptoChannel.NRT,
                insertPoint=nrtInsertPoint
            )

            self.nrtPanel.insertInto(owner.block)

        return CDConnectionPanel.WIDTH

    def channelList(self) -> List[str]:
        '''返回该设备参与连接的通道'''

        channelList: List[str] = []

        if not self.rtIsJump:
            channelList.append(CryptoChannel.RT)

        if not self.nrtIsJump:
            channelList.append(CryptoChannel.NRT)

        return channelList

    def frontPoint(self, channel: str):
        '''获取设备前连接点和端口名'''

        if channel == CryptoChannel.RT:
            self._assertRTPanelDrawn()
            return self.rtPanel.frontPoint(), self.rtPnum  # type: ignore

        if channel == CryptoChannel.NRT:
            self._assertNRTPanelDrawn()
            return self.nrtPanel.frontPoint(), self.nrtPnum  # type: ignore

        raise ValueError(f"未知纵向加密链路通道: {channel}")

    def afterPoint(self, channel: str):
        '''获取设备后连接点'''

        return self.frontPoint(channel)

    def recordRoom2Panel(self, owner: Any):
        '''记录第二机房边界'''

        if self.rtIsRoom2:
            self._assertRTPanelDrawn()

            owner.room2FrameManager.recordPanel(
                insertPoint=self.rtPanel.insertPoint,  # type: ignore
                width=self.rtPanel.WIDTH,             # type: ignore
                height=self.rtPanel.HEIGHT            # type: ignore
            )

        if self.nrtIsRoom2:
            self._assertNRTPanelDrawn()

            owner.room2FrameManager.recordPanel(
                insertPoint=self.nrtPanel.insertPoint,  # type: ignore
                width=self.nrtPanel.WIDTH,             # type: ignore
                height=self.nrtPanel.HEIGHT            # type: ignore
            )

    def _assertRTPanelDrawn(self):
        '''检查实时纵向加密设备面板是否已经绘制'''

        if self.rtPanel is None:
            raise ValueError(f"{self.rtPnum} {self.rtPname} 尚未绘制，无法获取连接点")

    def _assertNRTPanelDrawn(self):
        '''检查非实时纵向加密设备面板是否已经绘制'''

        if self.nrtPanel is None:
            raise ValueError(f"{self.nrtPnum} {self.nrtPname} 尚未绘制，无法获取连接点")