##########################################################################################################
#   Description: 纵向加密连接图机房互联IDF设备节点
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from typing import Any, Literal, Optional

from ezdxf.math import Vec2

from .cryptoCommonDev import CryptoDeviceType
from .cryptoNormalIDF import CryptoNormalIDF
from ..cryptoConnectionPanel import CDroomConnectedIDFConnectionPanel


class CryptoRoomConnectedIDF(CryptoNormalIDF):
    '''纵向加密连接图机房互联IDF设备节点'''

    DEVICE_NAME = "机房互联IDF配线单元"
    DEVICE_TYPE = CryptoDeviceType.ROOM_CONNECTED_IDF

    DIRECTION_LEFT = "left"
    DIRECTION_RIGHT = "right"

    def __init__(
            self,
            deviceNum: str,
            portR: Optional[str],
            portNR: Optional[str],
            direction: Literal["left", "right"],
            isRoom2: bool = False,
            isJump: bool = False,
            isNoPhoto: bool = False,
            isCutBusiness: bool = False
    ) -> None:
        """初始化机房互联IDF设备节点

        :param deviceNum: 设备号
        :param portR: 实时纵向加密端口
        :param portNR: 非实时纵向加密端口
        :param direction: 端口朝向，left为左侧IDF，right为右侧IDF
        :param isRoom2: 是否在第二机房
        :param isJump: 是否跳过绘制
        :param isNoPhoto: 是否未拍照
        :param isCutBusiness: 是否绘制业务断开标记
        """

        super().__init__(
            deviceNum=deviceNum,
            portR=portR, # type: ignore
            portNR=portNR, # type: ignore
            isRoom2=isRoom2,
            isJump=isJump,
            isNoPhoto=isNoPhoto,
            isCutBusiness=isCutBusiness
        )

        self.deviceName = self.DEVICE_NAME
        self.deviceType = self.DEVICE_TYPE
        self.direction = direction

        self.panel: Optional[CDroomConnectedIDFConnectionPanel] = None

    def drawPanel(
            self,
            owner: Any,
            insertX: float,
            rtCurrentPoint: Vec2,
            nrtCurrentPoint: Vec2
    ) -> float:
        '''绘制设备面板，返回设备宽度'''

        self.insertPoint = CDroomConnectedIDFConnectionPanel.insertPointFromFrontPoints(
            insertX=insertX,
            rtLinkPoint=rtCurrentPoint,
            nrtLinkPoint=nrtCurrentPoint,
            direction=self.direction # type: ignore
        )

        self.panel = CDroomConnectedIDFConnectionPanel(
            doc=owner.doc,
            devNum=self.deviceNum, # type: ignore
            portR=self.portR,
            portNR=self.portNR,
            insertPoint=self.insertPoint,
            isCutBusiness=self.isCutBusiness,
            direction=self.direction # type: ignore
        )

        self.panel.insertInto(owner.block)

        return self.panel.WIDTH