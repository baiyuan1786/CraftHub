##########################################################################################################
#   Description: 绘图大师子脚本主程序
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .page.subPage import DrawingMasterPage
from .subPath import PATH_INFO, PATH_DESC

from ...subscript import Subscript

class DrawingMaster(Subscript):
    '''绘图大师'''
    def __init__(self):
        super().__init__(name = "DrawingMaster",
                         pageCls = DrawingMasterPage,
                         infoPath = PATH_INFO,
                         descPath = PATH_DESC)