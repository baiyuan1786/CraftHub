##########################################################################################################
#   Description: 绘图大师底层图形化接口
#                提供与底层dxf文件交互的接口
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .color import CADColor                     # 颜色接口
from .line import LineTypeMnger, Line, LineType # 线条接口
from .line.line import *                        # 具体线接口
from .shape import NewBlock, ExistedBlock, CopiedBlock, TextBox, CustomBlock, CachedCopiedBlock  # 抽象形状接口