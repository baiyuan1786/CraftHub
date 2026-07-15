##########################################################################################################
#   Description: 设备类，存储设备所有信息，并可从设备类导出设备面板图、设备屏柜面板图、设备单板说明图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import CustomBlock
from .deviceInCabinet import DeviceInCabinet
from abc import ABC, abstractmethod

from typing import Literal, Tuple, Optional
from ezdxf.document import Drawing

DeviceType = Literal[
    "normal",
    "new",
    "remove",
    "replace",
    "replaced",
    "dropped"
]

class Device(ABC):
    '''设备基类'''

    VALID_DEV_TYPES = {
        "normal",
        "new",
        "remove",
        "replace",
        "replaced",
        "dropped"
    }

    def __init__(self,
                 name: str,
                 altitudeU: int,
                 heightU: int,
                 devType: DeviceType = "normal",
                 replacedDeviceName: Optional[str] = None
                 ) -> None:
        """设备基类

        :param name: 设备名称
        :param altitudeU: 设备所处屏柜位置
        :param heightU: 设备高度
        :param devType: 设备类型
        :param replacedDeviceName: 已被替代的设备名字
        """
        super().__init__()

        if devType not in self.VALID_DEV_TYPES:
            raise ValueError(f"不支持的设备类型: {devType}")

        self.name = name
        self.altitudeU = altitudeU
        self.heightU = heightU
        self.devType = devType
        self.replacedDeviceName = replacedDeviceName
        
    def setDevType(self, devType: DeviceType):
        '''设置设备类型'''
        self.devType = devType

    @property
    def isNew(self) -> bool:
        return self.devType == "new"

    @property
    def isNormal(self) -> bool:
        return self.devType == "normal"

    @property
    def isRemove(self) -> bool:
        return self.devType == "remove"

    @property
    def isReplace(self) -> bool:
        return self.devType == "replace"

    @property
    def isReplaced(self) -> bool:
        return self.devType == "replaced"

    @property
    def isDropped(self) -> bool:
        return self.devType == "dropped"

    @property
    def isVisibleInCabinet(self) -> bool:
        """是否需要显示在屏柜中"""
        return not self.isDropped

    @abstractmethod
    def toDevicePanel(self, doc: Drawing) -> CustomBlock:
        '''转换设备面板图'''
        pass

    def toDeviceInCabinet(self, doc: Drawing) -> DeviceInCabinet:
        """输出屏柜中设备"""

        return DeviceInCabinet(
            doc=doc,
            name=self.name,
            heightU=self.heightU,
            altitudeU=self.altitudeU,
            devType=self.devType, # type: ignore
            replacedDeviceName=self.replacedDeviceName
        )
