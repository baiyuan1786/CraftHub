##########################################################################################################
#   Description: IDN集成式绘图模块，站绘图器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Dict, List

from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.graph import CADColor
from ...common.meta import FrameA3plus, FrameA3plusplus
from ..reader.reader import DataUnitIDN
from .substationLeft import IDNsubPlotter_left
from .substationRight import IDNsubPlotter_right

class IDNsubPlotter:
    '''idn站绘图器'''

    LEFT_FRAME_OFFSET = Vec2(370, 0)
    RIGHT_FRAME_OFFSET = Vec2(841, 0) + Vec2(38.4559, 0) + LEFT_FRAME_OFFSET
    SUBSTATION_NAME_OFFSET_Y = Vec2(0, 142)

    CABLELAY_INSERT_POINT = LEFT_FRAME_OFFSET + Vec2(193, 33)

    CONFIG_KEY_DATE = "date"

    CONFIG_KEY_APPROVE = "approve"
    CONFIG_KEY_REVIEW1 = "review1"
    CONFIG_KEY_CHECK = "check"
    CONFIG_KEY_DESIGN = "design"
    CONFIG_KEY_DRAW = "draw"

    CONFIG_KEY_APPROVE_NUM = "approveNum"
    CONFIG_KEY_REVIEW1_NUM = "review1Num"
    CONFIG_KEY_CHECK_NUM = "checkNum"
    CONFIG_KEY_DESIGN_NUM = "designNum"
    CONFIG_KEY_DRAW_NUM = "drawNum"

    DEFAULT_CONFIG_TEXT = ""

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitIDN,
            config: Dict[str, Any],
            PROJECTNAME: str
    ) -> None:
        """IDN集成式网络站绘图器

        :param doc:         文档
        :param data:        数据单元
        :param config:      配置
        :param PROJECTNAME: 项目名
        """

        self.doc = doc
        self.data = data
        self.config = config
        self.substationName: str = data.get("substationName")
        self.PROJECTNAME = PROJECTNAME
        self.DATE = self._getConfigStr(self.CONFIG_KEY_DATE)

    def plot(self):
        '''绘图'''

        if self.data.get("build"):
            self._buildStation(self.data)
        else:
            self._notBuildStation(self.data)

    def _buildStation(self, data: DataUnitIDN):
        '''已建设站点构建'''

        self.roomName: str = data.get("roomName")
        self.walkLine: str = data.get("walkLine")

        if data.get("DDNInstallPnum") != data.get("installPnum"):
            data.set("DDNAltitudeU", None)
            data.set("DDNisNewPDU", False)
            data.set("DDNPDUAltitudeU", None)

        if not data.get("DDNisNewPDU"):
            data.set("DDNPDUAltitudeU", None)

        if not data.get("isNewPDU"):
            data.set("PDUAltitudeU", None)

        odfLinkTerminateStrList = self.odfLinkTerminateStrListHandled(data=data)
        data.set("odfLinkTerminateStrList", odfLinkTerminateStrList)

        self.rightPlotter = IDNsubPlotter_right(
            doc=self.doc,
            data=data,
            config=self.config,
            PROJECTNAME=self.PROJECTNAME,
            DRAWINGNAME=f"{self.substationName}{self.roomName}新增设备/板卡安装图",
        )

        self.leftPlotter = IDNsubPlotter_left(
            doc=self.doc,
            data=data,
            config=self.config,
            PROJECTNAME=self.PROJECTNAME,
            DRAWINGNAME=f"{self.substationName}{self.roomName}平面布置图及设备连接图",
        )

    def _notBuildStation(self, data: DataUnitIDN):
        '''未建设站点构建'''

        self.rightPlotter = FrameA3plus(
            doc=self.doc,

            APPROVE=self._getConfigStr(self.CONFIG_KEY_APPROVE),
            APPROVENUM=self._getConfigStr(self.CONFIG_KEY_APPROVE_NUM),
            REVIEW1=self._getConfigStr(self.CONFIG_KEY_REVIEW1),
            REVIEW1NUM=self._getConfigStr(self.CONFIG_KEY_REVIEW1_NUM),
            CHECK=self._getConfigStr(self.CONFIG_KEY_CHECK),
            CHECKNUM=self._getConfigStr(self.CONFIG_KEY_CHECK_NUM),
            DESIGN=self._getConfigStr(self.CONFIG_KEY_DESIGN),
            DESIGNNUM=self._getConfigStr(self.CONFIG_KEY_DESIGN_NUM),
            DRAW=self._getConfigStr(self.CONFIG_KEY_DRAW),
            DRAWNUM=self._getConfigStr(self.CONFIG_KEY_DRAW_NUM),

            PROJECTNAME=self.PROJECTNAME,
            DRAWINGNAME=f"{self.substationName}XX室新增设备/板卡安装图",
            DRAWINGNUMBER=data.get("DRAWINGNUMBER1"),
            DATE=self._getConfigStr(self.CONFIG_KEY_DATE)
        )

        self.leftPlotter = FrameA3plusplus(
            doc=self.doc,

            APPROVE=self._getConfigStr(self.CONFIG_KEY_APPROVE),
            APPROVENUM=self._getConfigStr(self.CONFIG_KEY_APPROVE_NUM),
            REVIEW1=self._getConfigStr(self.CONFIG_KEY_REVIEW1),
            REVIEW1NUM=self._getConfigStr(self.CONFIG_KEY_REVIEW1_NUM),
            CHECK=self._getConfigStr(self.CONFIG_KEY_CHECK),
            CHECKNUM=self._getConfigStr(self.CONFIG_KEY_CHECK_NUM),
            DESIGN=self._getConfigStr(self.CONFIG_KEY_DESIGN),
            DESIGNNUM=self._getConfigStr(self.CONFIG_KEY_DESIGN_NUM),
            DRAW=self._getConfigStr(self.CONFIG_KEY_DRAW),
            DRAWNUM=self._getConfigStr(self.CONFIG_KEY_DRAW_NUM),

            PROJECTNAME=self.PROJECTNAME,
            DRAWINGNAME=f"{self.substationName}XX室平面布置图及设备连接图",
            DRAWINGNUMBER=data.get("DRAWINGNUMBER2"),
            DATE=self._getConfigStr(self.CONFIG_KEY_DATE)
        )

    def odfLinkTerminateStrListHandled(self, data: DataUnitIDN):
        '''计算ODF连接终点字符串'''

        odfLinkTerminateStrListHandled = []

        for terminaterStr, fiberJump in zip(data.get("odfLinkTerminateStrList"), data.get("fiberJumpList")):
            newStr = f"至{terminaterStr}"

            if fiberJump is not None:
                staList = fiberJump.split("/")
                staList = [
                    sta + "变" if not sta.endswith(("局", "变", "站", "所")) else sta
                    for sta in staList
                ]

                staList = [self.substationName.split("kV")[-1]] + staList + [terminaterStr.split("kV")[-1]]
                linkStr = "->".join(staList)

                newStr += "\n"
                newStr += f"({linkStr}, 光缆跳纤)"

            elif not terminaterStr.endswith("(GCN网专线)"):
                newStr += "\n"
                newStr += "(光纤直连)"

            else:
                newStr = newStr.replace("(GCN网专线)", "\n(GCN网 MSTP GE传输专线)")

            odfLinkTerminateStrListHandled.append(newStr)

        return odfLinkTerminateStrListHandled

    def _addSubstationNameText(self, layout: Modelspace, insertPoint: Vec2):
        '''添加站名文字信息'''

        headNote = self.data.get("headNote")
        text = self.substationName

        if headNote is not None:
            text += f"({CADColor.colored(headNote)})"

        if not self.data.get("build"):
            planText = CADColor.colored("规划建设中", "黄色")
            text += f"({planText})"

        layout.add_mtext(
            text=text,
            dxfattribs={
                "insert": insertPoint,
                "char_height": 67.6225,
                "width": 370,
                "attachment_point": 4,
                "layer": "文本",
                "style": "GEDITXT",
                "line_spacing_factor": 0.7625,
                "line_spacing_style": 1,
            }
        )

    def insertInto(self, layout: Modelspace, insertPoint: Vec2):
        '''将两个图框插入到模型空间'''

        self._addSubstationNameText(
            layout=layout,
            insertPoint=insertPoint + self.SUBSTATION_NAME_OFFSET_Y,
        )

        self.leftPlotter.insertInto(layout, insertPoint + self.LEFT_FRAME_OFFSET)
        self.rightPlotter.insertInto(layout, insertPoint + self.RIGHT_FRAME_OFFSET)

    def _getFrameConfigDict(self) -> Dict[str, str]:
        '''获取图框配置字典'''

        return {
            "APPROVE": self._getConfigStr(self.CONFIG_KEY_APPROVE),
            "APPROVENUM": self._getConfigStr(self.CONFIG_KEY_APPROVE_NUM),
            "REVIEW1": self._getConfigStr(self.CONFIG_KEY_REVIEW1),
            "REVIEW1NUM": self._getConfigStr(self.CONFIG_KEY_REVIEW1_NUM),
            "CHECK": self._getConfigStr(self.CONFIG_KEY_CHECK),
            "CHECKNUM": self._getConfigStr(self.CONFIG_KEY_CHECK_NUM),
            "DESIGN": self._getConfigStr(self.CONFIG_KEY_DESIGN),
            "DESIGNNUM": self._getConfigStr(self.CONFIG_KEY_DESIGN_NUM),
            "DRAW": self._getConfigStr(self.CONFIG_KEY_DRAW),
            "DRAWNUM": self._getConfigStr(self.CONFIG_KEY_DRAW_NUM),
        }

    def _getConfigStr(self, key: str) -> str:
        '''从配置中读取字符串参数'''

        value = self.config.get(key, self.DEFAULT_CONFIG_TEXT)

        if value is None:
            return self.DEFAULT_CONFIG_TEXT

        return str(value)