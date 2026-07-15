##########################################################################################################
#   Description: DDN设备
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from ezdxf.document import Drawing

from ....graph import CADColor, ExistedBlock
from ..base import Device


class DDN设备(Device):
    '''DDN设备'''

    DEVICE_NAME = (
        "本期新增地区ddnA平面\n"
        "接入层路由器/低端路由器\n"
        f"{CADColor.colored('(地调A-低端-厂家型号)')}"
    )
    DEVICE_HEIGHT_U = 4
    DEVICE_TYPE = "new"

    PANEL_BLOCK_NAME = "DDSJWLYQ-MB"

    def __init__(self, altitudeU: int) -> None:
        """初始化DDN设备

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
            raise ValueError(f"DDN设备面板图块名不能为空，当前值为{blockName}")

        cls.PANEL_BLOCK_NAME = blockName.strip()

    @classmethod
    def setDeviceName(cls, deviceName: str):
        '''设置设备名称'''

        if not isinstance(deviceName, str) or deviceName.strip() == "":
            raise ValueError(f"DDN设备名称不能为空，当前值为{deviceName}")

        cls.DEVICE_NAME = deviceName.strip()

    @classmethod
    def setDeviceHeightU(cls, heightU: int):
        '''设置设备高度U数'''

        if not isinstance(heightU, int):
            raise TypeError(f"DDN设备高度必须是int类型，当前类型为{type(heightU)}")

        if heightU <= 0:
            raise ValueError(f"DDN设备高度必须大于0，当前值为{heightU}")

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