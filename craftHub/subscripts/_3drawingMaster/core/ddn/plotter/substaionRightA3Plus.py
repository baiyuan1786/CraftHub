##########################################################################################################
#   Description: ddn定向式绘图网络绘图器，站绘图器右图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.meta import (
    FrameA3plus,

)
from .substationRight import DDNsubplotter_right
from ...common.meta.device.autoU import AutoUcalculator
from ..reader import DataUnitDDN

class DDNsubplotter_rightA3plus(DDNsubplotter_right):
    '''ddn定向式绘图网络站绘图器_右图绘图器_A3+非扩容版本'''

    IS_EXPANSION = False

    def _buildFrame(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            PROJECTNAME: str,
            DRAWINGNAME: str
    ) -> FrameA3plus:
        '''构建A3+图框'''

        return FrameA3plus(
            doc=doc,
            **self._frameKwargs(
                data=data,
                PROJECTNAME=PROJECTNAME,
                DRAWINGNAME=DRAWINGNAME
            )
        )

    def _cabinetPoint(self) -> Vec2:
        '''获取屏柜插入点'''

        return FrameA3plus.cabinetPoint()

    def _frameCabinetPoint(self) -> Vec2:
        '''获取屏柜外框插入点'''

        return FrameA3plus.frameCabinetPoint()

    def _newDevicePanelPoint(self) -> Vec2:
        '''获取新增设备面板图插入点'''

        return FrameA3plus.newDevicePanelPoint()

    def _legendPoint(self) -> Vec2:
        '''获取图例插入点'''

        return FrameA3plus.legendPoint(t=2)

    def _introductionPoint(self) -> Vec2:
        '''获取说明插入点'''

        return FrameA3plus.introductionPoint()