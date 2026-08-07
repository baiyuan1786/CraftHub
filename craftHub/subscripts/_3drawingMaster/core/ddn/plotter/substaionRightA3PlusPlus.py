##########################################################################################################
#   Description: ddn定向式绘图网络绘图器，站绘图器右图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import Any, Dict, List

from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.meta import (
    FrameA3plusplus,
)
from .substationRight import DDNsubplotter_right
from ..gcnPanel import GCNpanel
from ..reader import DataUnitDDN

class DDNsubplotter_rightA3plusplus(DDNsubplotter_right):
    '''ddn定向式绘图网络站绘图器_右图绘图器_A3++扩容版本'''

    IS_EXPANSION = True
    GCN_BOARD_BLOCK_NAME = "GCN_BOARD"

    def __init__(self, doc: Drawing, data: DataUnitDDN, config: Dict[str, Any], PROJECTNAME: str, DRAWINGNAME: str) -> None:
        super().__init__(doc, data, config, PROJECTNAME, DRAWINGNAME)
        assert isinstance(self.frame, FrameA3plusplus)
        self._addGCNexpansion()

    def _buildFrame(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            PROJECTNAME: str,
            DRAWINGNAME: str
    ) -> FrameA3plusplus:
        '''构建A3++图框'''

        return FrameA3plusplus(
            doc=doc,
            **self._frameKwargs(
                data=data,
                PROJECTNAME=PROJECTNAME,
                DRAWINGNAME=DRAWINGNAME
            )
        )
        
    def _addGCNexpansion(self):
        '''增加GCN扩容内容'''
        self.frame.grid(
            GCNpanel(doc=self.doc, data=self.data),
            self._GCNpanelPoint()
        )
        
    def _GCNpanelPoint(self)-> Vec2:
        '''获取GCN面板图插入点'''
        return FrameA3plusplus.GCNpanelPoint()

    def _cabinetPoint(self) -> Vec2:
        '''获取屏柜插入点'''
        return FrameA3plusplus.cabinetPoint()

    def _frameCabinetPoint(self) -> Vec2:
        '''获取屏柜外框插入点'''

        return FrameA3plusplus.frameCabinetPoint()

    def _newDevicePanelPoint(self) -> Vec2:
        '''获取新增设备面板图插入点'''

        return FrameA3plusplus.newDevicePanelPoint()

    def _legendPoint(self) -> Vec2:
        '''获取图例插入点'''

        return FrameA3plusplus.legendPoint(t=2)

    def _introductionPoint(self) -> Vec2:
        '''获取说明插入点'''

        return FrameA3plusplus.introductionPoint(t=2)