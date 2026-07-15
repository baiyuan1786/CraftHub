##########################################################################################################
#   Description: IDN集成式绘图模块，站绘图器左图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Dict

from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.graph import ExistedBlock
from ...common.meta import (
    CableLayIntroduction,
    ConnectionIntroduction,
    FrameA3plusplus,
    Legend,
    LocalIDNLayer1Introduction,
    NetWorkLinkIntroduction,
    PlaneIntroduction,
)
from ..link import ConnectionMap
from ..reader.reader import DataUnitIDN


class IDNsubPlotter_left:
    '''IDN站绘图器_左图绘图器'''

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
            PROJECTNAME: str,
            DRAWINGNAME: str,
    ) -> None:
        """IDN集成式网络站绘图器_左图绘图器初始化

        :param doc:         CAD文档
        :param data:        数据单元
        :param config:      绘图配置字典
        :param PROJECTNAME: 项目名称
        :param DRAWINGNAME: 图纸名称
        """

        self.doc = doc
        self.config = config

        self.substationName: str = data.get("substationName")
        self.roomName: str = data.get("roomName")
        self.walkLine: str = data.get("walkLine")

        self.frame = FrameA3plusplus(
            doc=doc,

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

            PROJECTNAME=PROJECTNAME,
            DRAWINGNAME=DRAWINGNAME,
            DRAWINGNUMBER=data.get("DRAWINGNUMBER1"),
            DATE=self._getConfigStr(self.CONFIG_KEY_DATE),
        )

        self.addLegend()
        self.addIntroduction(data)

        self.frame.grid(ConnectionMap(doc=self.doc, data=data), self.frame.connectionPoint())
        self.frame.grid(ConnectionIntroduction(doc=doc), self.frame.connectionIntroPoint())
        self.frame.grid(NetWorkLinkIntroduction(doc=doc), self.frame.netWorkLinkIntroPoint())
        self.frame.grid(CableLayIntroduction(doc=doc), self.frame.cableLayIntroPoint())

        try:
            self.addPlane()
        except Exception:
            pass

    def addLegend(self):
        '''增加图例'''

        self.frame.grid(Legend(doc=self.doc), self.frame.legendPoint())

    def addIntroduction(self, data: DataUnitIDN):
        '''插入IDN集成式网络说明'''

        introduction = LocalIDNLayer1Introduction(
            doc=self.doc,
            walkLine=data.get("walkLine"),
            isNewPDU=data.get("isNewPDU"),
            installPnum=data.get("installPnum"),
            installCabinetType=data.get("installCabinetType"),
        )

        self.frame.grid(introduction, self.frame.introductionPoint())

    def addPlane(self):
        '''增加平面图'''

        if self.substationName in self.doc.blocks:
            blockName = self.substationName
        else:
            blockName = self.substationName.replace("(", "（").replace(")", "）")

        if blockName in self.doc.blocks:
            plane = ExistedBlock(
                doc=self.doc,
                blockName=blockName,
            )

            self.frame.grid(plane, self.frame.planePoint())
        else:
            raise ValueError("没有找到平面图块")

        planeIntro = PlaneIntroduction(
            doc=self.doc,
            substationName=self.substationName,
            roomName=self.roomName,
        )

        self.frame.grid(planeIntro, self.frame.planePoint() + Vec2(0, -10))

    def insertInto(self, layout: Modelspace, insertPoint: Vec2):
        '''将被图框插入到模型空间'''

        self.frame.insertInto(layout, insertPoint)

    def _getConfigStr(self, key: str) -> str:
        '''从配置中读取字符串参数'''

        value = self.config.get(key, self.DEFAULT_CONFIG_TEXT)

        if value is None:
            return self.DEFAULT_CONFIG_TEXT

        return str(value)