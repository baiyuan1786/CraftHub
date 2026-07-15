##########################################################################################################
#   Description: 线条类基类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .lineType import LineType

class Line:
    '''线条基类'''
    def __init__(self,
                 lineName: str,
                 lineType: LineType,
                 color: int,
                 lineWeight: float = -1,
                 ltscale: float = 1.0,
                 const_width:float = 0.0):
        """线基类初始化

        :param lineName: 线的名字
        :param lineType: 线型, 主要是用到线型的名字
        :param color: 线颜色, 根据CADIndex定义
        :param lineWeight: 线宽, 单位mm*100, -3: default, -2 byblock, -1 bylayer
        :param ltscale: 线型比例, defaults to 1.0
        :param const_width: 全局宽度, defaults to 0.0
        """        
        
        self.lineName = lineName
        self.lineType = lineType
        self.color = color
        self.lineWeight = lineWeight
        self.ltscale = ltscale
        self.const_width = const_width
        
    @property
    def attributes(self):
        '''转换为DXF线条属性格式'''
        return {
            "linetype": self.lineType.name,         # 线型名
            "ltscale": self.ltscale,                # 线型比例
            "lineweight": self.lineWeight,		    # 线宽
            "color": self.color,                    # 颜色
            "const_width": self.const_width         # 全局宽度
        }