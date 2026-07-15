##########################################################################################################
#   Description: IDN设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from ....common.graph import NewBlock, ExistedBlock, CADColor


class IDN设备连接面板图(NewBlock):
    '''IDN设备连接面板图'''

    WIDTH = 50.0591
    HEIGHT = 59.0225

    # 保留旧变量名，避免外部代码引用 width / height 出错
    width = WIDTH
    height = HEIGHT

    BLOCK_NAME = "ZX-DDLYQ-LJMB"

    DEVICE_TEXT = (
        "新增低端路由器\n"
        "(中兴ZXR10 6800-6X)"
    )

    TEXT_FONT_HEIGHT = 2.88
    TEXT_WIDTH = 50
    TEXT_INSERT_POINT = Vec2(25.56, 28.75)
    TEXT_STYLE = "GEDITXT"
    TEXT_LINE_SPACING_DISTANCE = 1

    def __init__(
            self,
            doc: Drawing,
            installPnum: str
    ) -> None:
        """初始化IDN设备连接面板图

        :param doc: CAD文档
        :param installPnum: 安装屏号
        """

        super().__init__(doc=doc)

        connectionPanelBlock = ExistedBlock(
            doc=doc,
            blockName=self.BLOCK_NAME
        )
        connectionPanelBlock.insertInto(self)

        self.addMtext(
            textContent=self._deviceText(installPnum),
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByLayer"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=self.TEXT_INSERT_POINT,
            style=self.TEXT_STYLE
        )

    @classmethod
    def setBlockName(cls, blockName: str):
        '''设置连接面板图块名'''

        if not isinstance(blockName, str) or blockName.strip() == "":
            raise ValueError(f"IDN设备连接面板图块名不能为空，当前值为{blockName}")

        cls.BLOCK_NAME = blockName.strip()

    @classmethod
    def setDeviceText(cls, deviceText: str):
        '''设置设备说明文字'''

        if not isinstance(deviceText, str) or deviceText.strip() == "":
            raise ValueError(f"IDN设备连接面板图设备说明文字不能为空，当前值为{deviceText}")

        cls.DEVICE_TEXT = deviceText.strip()

    @classmethod
    def setDeviceName(cls, deviceName: str):
        '''设置设备名称，等价于设置设备说明文字'''

        cls.setDeviceText(deviceName)

    @classmethod
    def setDeviceSize(
            cls,
            width: float,
            height: float
    ):
        '''设置连接面板图尺寸'''

        if not isinstance(width, int | float):
            raise TypeError(f"IDN设备连接面板图宽度必须是数字，当前类型为{type(width)}")

        if not isinstance(height, int | float):
            raise TypeError(f"IDN设备连接面板图高度必须是数字，当前类型为{type(height)}")

        if width <= 0 or height <= 0:
            raise ValueError(f"IDN设备连接面板图尺寸必须大于0，当前值为{width}x{height}")

        cls.WIDTH = width
        cls.HEIGHT = height

        # 同步旧变量名
        cls.width = width
        cls.height = height

    @classmethod
    def setDeviceConfig(
            cls,
            blockName: str | None = None,
            deviceText: str | None = None,
            width: float | None = None,
            height: float | None = None
    ):
        '''批量设置连接面板图配置'''

        if blockName is not None:
            cls.setBlockName(blockName)

        if deviceText is not None:
            cls.setDeviceText(deviceText)

        if width is not None or height is not None:
            if width is None or height is None:
                raise ValueError("设置IDN设备连接面板图尺寸时，width和height必须同时提供")

            cls.setDeviceSize(width, height)

    @classmethod
    def _deviceText(cls, installPnum: str) -> str:
        '''获取完整设备说明文字'''

        return f"{installPnum} {cls.DEVICE_TEXT}"

    @staticmethod
    def power1Point():
        '''电源模块1连接点'''
        return Vec2(8.62, 59.0225)
    
    @staticmethod
    def power2Point():
        '''电源模块2连接点'''
        return Vec2(42.13, 59.0225)
    
    @staticmethod
    def board1Point():
        '''板卡1连接点(8端口 FE/GE电接口板)
        连接三区业务'''
        return Vec2(48.5, 12)
        
    @staticmethod
    def board2Point():
        '''板卡2连接点(8端口 FE/GE电接口板)
        一般什么也不接'''
        return Vec2(48.5, 7.16)
        
    @staticmethod
    def board3Point():
        '''板卡3连接点(4端口 10GE光接口板)
        连接ODF可用'''
        return Vec2(48.5, 46.91)
        
    @staticmethod
    def board4Point():
        '''板卡4连接点(4端口 10GE光接口板)
        连接ODF可用'''
        return Vec2(48.5, 42)

    @staticmethod
    def board6Point(lineNum: int = 0):
        '''板卡6连接点(10端口 FE/GE光接口板)下侧接口
        连接四区业务'''
        return Vec2(7.6, 1.5) + Vec2(1 * lineNum, 0)
    
    @staticmethod
    def board6PointRight():
        '''板卡6连接点(10端口 FE/GE光接口板)右侧接口
        连接四区业务'''
        return Vec2(49, 2.4)