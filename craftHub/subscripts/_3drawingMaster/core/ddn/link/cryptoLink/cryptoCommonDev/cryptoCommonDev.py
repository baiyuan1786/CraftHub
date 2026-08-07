##########################################################################################################
#   Description: 纵向加密连接图通用设备基类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from ezdxf.math import Vec2


class CryptoChannel:
    '''纵向加密链路通道'''

    RT = "rt"
    NRT = "nrt"

    BOTH = (RT, NRT)


class CryptoDeviceType:
    '''纵向加密连接图设备类型'''

    NONE = "none"
    NEW_EDGED_IDF = "newEdgedIDF"
    EXISTED_EDGED_IDF = "existedEdgedIDF"
    NORMAL_IDF = "normalIDF"
    ROOM_CONNECTED_IDF = "roomConnectedIDF"
    ACCESS_SWITCH = "accessSwitch"
    CD_PAIR = "cdPair"


class CommonCryptoDev(ABC):
    '''纵向加密连接图通用设备节点'''

    def __init__(
            self,
            deviceNum: Optional[str],
            deviceName: str,
            deviceType: str,
            isNew: bool = False,
            isRoom2: bool = False,
            isJump: bool = False,
            isNoPhoto: bool = False
    ) -> None:
        """初始化通用设备节点

        :param deviceType: 设备类型
        :param deviceNum: 设备号
        :param deviceName: 设备名
        :param isNew:      是否视作新设备
        :param isRoom2:    是否在第二机房
        :param isJump:     是否跳过绘制
        :param isNoPhoto:  是否未拍照
        """

        self.deviceNum = deviceNum
        self.deviceName = deviceName
        self.deviceType = deviceType
        self.isNew = isNew
        self.isRoom2 = isRoom2
        self.isJump = isJump
        self.isNoPhoto = isNoPhoto

    @abstractmethod
    def drawPanel(
            self,
            owner: Any,
            insertX: float,
            rtCurrentPoint: Vec2,
            nrtCurrentPoint: Vec2
    ) -> float:
        '''绘制设备面板，返回设备宽度'''

    @abstractmethod
    def channelList(self) -> List[str]:
        '''返回该设备参与连接的通道'''

    @abstractmethod
    def frontPoint(self, channel: str) -> Tuple[Vec2, Optional[str]]:
        '''获取设备前连接点和端口名'''

    @abstractmethod
    def afterPoint(self, channel: str) -> Tuple[Vec2, Optional[str]]:
        '''获取设备后连接点和端口名'''

    @abstractmethod
    def recordRoom2Panel(self, owner: Any):
        '''记录第二机房边界'''