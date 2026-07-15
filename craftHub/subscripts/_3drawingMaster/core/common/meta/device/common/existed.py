##########################################################################################################
#   Description: 已存在设备
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..base import Device, DeviceType
import re
from typing import List, Literal, Optional, Tuple
from ezdxf.document import Drawing

VALID_WISH_TYPE = Literal["TP", "TR"] # 可选期望替代类型
# TP: 可替代的PDU
# TR: 可替代的路由器

class ExistedDevice(Device):
    '''已存在设备'''

    # 标记类型转换设备类型
    SIGNT_TO_DEVT = {
        "TR": "replace",     # 待替代设备路由器设备
        "TP": "replace",     # 待替代PDU设备
        "R": "remove",       # 待移除设备
        "CP1": "normal",      # 连接替代PDU的设备, 使用一根线
        "CP2": "normal",     # 连接替代PDU的设备, 使用两根线
        "CP8": "normal",     # 连接替代PDU的设备, 使用两根线
        None: "normal"       # 普通存在设备
    }

    def __init__(self, 
                 rawName: str, 
                 altitudeU: int, 
                 heightU: int,
                 ) -> None:
        
        name, devType, signType, current = ExistedDevice.parseType(rawName)
        self.signType = signType
        self.current = current  # 使用电流端子，用以确定线型
        
        super().__init__(name, altitudeU, heightU, devType) # type: ignore

    def toDevicePanel(self, doc: Drawing):
        '''转换设备面板图'''
        raise Exception("普通设备没有面板图")
    

    def replacedWithNewDevice(self, other: object, wishType: VALID_WISH_TYPE = "TP"):
        """使用新设备替换此设备

        :param other: 新设备
        :param wishType: 期望替代类型, defaults to "TP"

        """

        if not isinstance(other, Device):
            raise TypeError(f"替换对象不是设备: {other}")

        if not self.isReplace:
            raise ValueError(f"当前设备不是可替换设备: {self.name}")

        if not other.isNew:
            raise TypeError(f"替换设备不是新设备: {other.name}")
        
        if not wishType == self.signType:
            raise TypeError(f"期望类型不匹配: self:{self.signType}, other:{wishType}")

        other.devType = "replaced"
        other.altitudeU = self.altitudeU    # 替代后继承位置，但不保证合法
        other.replacedDeviceName = self.name
        self.devType = "dropped"

        return other

    @classmethod
    def parseType(cls, name: str) -> Tuple[str, DeviceType, str, Optional[str]]:
        """
        解析名字，返回设备名称和类型, 标记类型。

        例：
            "25P01 直流配电设备<TP>" -> ("25P01 直流配电设备", "replace", "TP", None)
            "25P01 直流配电设备<CP1-16>" -> ("25P01 直流配电设备", "replace", "TP", "16")
            "25P01 直流配电设备" -> ("25P01 直流配电设备", "normal", None, None)
        """

        rawName = name.strip()

        match = re.fullmatch(
            r"(.*?)(?:<(.+?)>)?",
            rawName,
            flags=re.DOTALL
        )

        current = None

        if match:
            deviceName = match.group(1).strip()
            typeStr = match.group(2)

            if typeStr is not None:
                typeStr = typeStr.strip()

                if "-" in typeStr:
                    typeStr, current = typeStr.split("-", 1)

        else:
            deviceName = rawName
            typeStr = None

        if typeStr not in cls.SIGNT_TO_DEVT:
            raise ValueError(
                f"设备标记类型不符合标准: '{typeStr}', "
                f"设备标记类型必须是 {list(cls.SIGNT_TO_DEVT.keys())} 之一"
            )

        return deviceName, cls.SIGNT_TO_DEVT[typeStr], typeStr, current  # type: ignore



    
