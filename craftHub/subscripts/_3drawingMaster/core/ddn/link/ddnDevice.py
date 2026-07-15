##########################################################################################################
#   Description: ddn设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Literal

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from ...common.graph import ExistedBlock, NewBlock, CADColor
from ...common.graph import 现有设备, 本期占用机柜
from ....subPath import PATH_TEMPLATE_DIR


class DDN设备连接面板图(NewBlock):
    '''DDN设备连接面板图'''

    WIDTH = 64.89
    HEIGHT = 93.50
    BOARD_HEIGHT = 10

    # 保留旧变量名，避免外部已有代码引用 width / height 出错
    width = WIDTH
    height = HEIGHT
    boardHeight = BOARD_HEIGHT

    BLOCK_NAME = "DDSJW-LJMB"

    DEVICE_TEXT = (
        "新增地区ddnA平面\n"
        "接入层路由器/低端路由器\n"
        f"{CADColor.colored('(地调A-低端-厂家型号)')}"
    )

    TEXT_FONT_HEIGHT = 4
    TEXT_WIDTH = 50
    TEXT_INSERT_POINT = Vec2(33, 81)
    TEXT_STYLE = "gedi"
    TEXT_ATTACHMENT = 2
    TEXT_LINE_SPACING_DISTANCE = 1

    def __init__(
            self,
            doc: Drawing,
            installPnum: str
    ) -> None:
        """初始化DDN设备连接面板图

        :param doc: CAD文档
        :param installPnum: 安装屏号
        """

        super().__init__(doc=doc)

        ExistedBlock(
            doc=doc,
            blockName=self.BLOCK_NAME
        ).insertInto(self)

        self.addMtext(
            textContent=self._deviceText(installPnum),
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByLayer"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=self.TEXT_INSERT_POINT,
            style=self.TEXT_STYLE,
            attachment=self.TEXT_ATTACHMENT
        )

    @classmethod
    def setBlockName(cls, blockName: str):
        '''设置连接面板图块名'''

        if not isinstance(blockName, str) or blockName.strip() == "":
            raise ValueError(f"DDN设备连接面板图块名不能为空，当前值为{blockName}")

        cls.BLOCK_NAME = blockName.strip()

    @classmethod
    def setDeviceText(cls, deviceText: str):
        '''设置设备说明文字'''

        if not isinstance(deviceText, str) or deviceText.strip() == "":
            raise ValueError(f"DDN设备连接面板图设备说明文字不能为空，当前值为{deviceText}")

        cls.DEVICE_TEXT = deviceText.strip()

    @classmethod
    def setDeviceName(cls, deviceName: str):
        '''设置设备名称，等价于设置设备说明文字'''

        cls.setDeviceText(deviceName)

    @classmethod
    def setDeviceConfig(
            cls,
            blockName: str | None = None,
            deviceText: str | None = None
    ):
        '''批量设置连接面板图配置'''

        if blockName is not None:
            cls.setBlockName(blockName)

        if deviceText is not None:
            cls.setDeviceText(deviceText)

    @classmethod
    def _deviceText(cls, installPnum: str) -> str:
        '''获取完整设备说明文字'''

        return f"{CADColor.colored(installPnum)} {cls.DEVICE_TEXT}"

    @staticmethod
    def power1Point():
        '''电源模块1连接点'''
        return Vec2(12.67, 91.6)
    
    @staticmethod
    def power2Point():
        '''电源模块2连接点'''
        return Vec2(52.27, 91.6)
    
    @classmethod
    def board1Point(cls, t: Literal["电", "光"] = "电"):
        '''千兆以太网光/电接口板1'''
        assert t in ["电", "光"], f"选择的类型不支持: \'{t}\'"
        
        if t == "电":
            return Vec2(cls.width, 49.08)
        else:
            return Vec2(cls.width, 49.08 + cls.boardHeight)
        
    @classmethod
    def board2Point(cls, t: Literal["电", "光"] = "电"):
        '''千兆以太网光/电接口板2'''
        assert t in ["电", "光"], f"选择的类型不支持: \'{t}\'"
        
        if t == "电":
            return Vec2(cls.width, 35.9)
        else:
            return Vec2(cls.width, 35.9 + cls.boardHeight)
        
    @classmethod
    def board3Point(cls, t: Literal["电", "光"] = "电"):
        '''千兆以太网光/电接口板3'''
        assert t in ["电", "光"], f"选择的类型不支持: \'{t}\'"
        
        if t == "电":
            return Vec2(cls.width, 21.7)
        else:
            return Vec2(cls.width, 21.7 + cls.boardHeight)
        
    @classmethod
    def board4Point(cls, t: Literal["电", "光"] = "电"):
        '''千兆以太网光/电接口板4'''
        assert t in ["电", "光"], f"选择的类型不支持: \'{t}\'"
        
        if t == "电":
            return Vec2(cls.width, 9.2)
        else:
            return Vec2(cls.width, 9.2 + cls.boardHeight)
