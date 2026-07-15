##########################################################################################################
#   Description: IDN设备
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ezdxf.document import Drawing

from ..base import Device
from ....graph import ExistedBlock

class IDN设备(Device):
    '''IDN设备'''

    DEVICE_NAME = "新增低端路由器\n(中兴ZXR10 6800-6X)"
    DEVICE_HEIGHT_U = 4
    DEVICE_TYPE = "new"

    PANEL_BLOCK_NAME = "ZX-DDLYQ-DC-MB"

    def __init__(self, altitudeU: int) -> None:
        """初始化IDN设备

        :param altitudeU: 设备安装U位
        """

        super().__init__(
            name=self.DEVICE_NAME,
            altitudeU=altitudeU,
            heightU=self.DEVICE_HEIGHT_U,
            devType=self.DEVICE_TYPE
        )

    @classmethod
    def setBlockName(cls, blockName: str):
        '''设置面板图块名'''

        if not isinstance(blockName, str) or blockName.strip() == "":
            raise ValueError(f"IDN设备面板图块名不能为空，当前值为{blockName}")

        cls.PANEL_BLOCK_NAME = blockName.strip()

    @classmethod
    def setDeviceName(cls, deviceName: str):
        '''设置设备名称'''

        if not isinstance(deviceName, str) or deviceName.strip() == "":
            raise ValueError(f"IDN设备名称不能为空，当前值为{deviceName}")

        cls.DEVICE_NAME = deviceName.strip()

    @classmethod
    def setDeviceHeightU(cls, heightU: int):
        '''设置设备高度U数'''

        if not isinstance(heightU, int):
            raise TypeError(f"IDN设备高度必须是int类型，当前类型为{type(heightU)}")

        if heightU <= 0:
            raise ValueError(f"IDN设备高度必须大于0，当前值为{heightU}")

        cls.DEVICE_HEIGHT_U = heightU

    @classmethod
    def setDeviceConfig(
            cls,
            deviceName: str | None = None,
            heightU: int | None = None,
            blockName: str | None = None
    ):
        '''批量设置设备配置'''

        if deviceName is not None:
            cls.setDeviceName(deviceName)

        if heightU is not None:
            cls.setDeviceHeightU(heightU)

        if blockName is not None:
            cls.setBlockName(blockName)

    def toDevicePanel(self, doc: Drawing):
        '''转换设备面板图'''

        return ExistedBlock(
            doc=doc,
            blockName=self.PANEL_BLOCK_NAME
        )