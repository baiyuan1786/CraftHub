##########################################################################################################
#   Description: 基本通用属性
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import Optional
from ezdxf.document import Drawing
from ezdxf.math import Vec2

U = 4.45 # CM
def U2CM(valueU: int):
    """将U为单位的值转换为CM为单位

    :param valueU: U为单位的值
    """        
    return valueU * U