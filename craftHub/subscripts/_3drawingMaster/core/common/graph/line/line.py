##########################################################################################################
#   Description: 线条类定义
#                目前共计定义了十种线缆，分别是
#                本期新增机柜
#                本期占用机柜
#                本期新增设备
#                现有设备
#                本期新增电源线
#                本期新增跳纤
#                本期新增网线
#                现有互联六类电缆
#                现有互联光缆
#                逻辑连线示意
#
#                下面是绘图模板部分使用的线型
#                普通黄色线
#                
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .base import Line
from .lineType import LineType, DYLine, SMLine, UTPLine, DASH, DASHDOT, Continuous

from ..color import CADColor

class 本期新增机柜(Line):
    '''红色虚线加粗'''
    def __init__(self):
        super().__init__(lineName = "本期新增机柜",
                         lineType = DASH(),
                         color = CADColor.toIndex("红色"),
                         const_width = 0.8,
                         ltscale = 5,
                         lineWeight = 30)
        
class 本期新增机柜Panel(Line):
    '''红色虚线加粗面板图版本, 比上一个版本的更粗'''
    def __init__(self):
        super().__init__(lineName = "本期新增机柜",
                         lineType = DASH(),
                         color = CADColor.toIndex("红色"),
                         const_width = 1.5,
                         ltscale = 5,
                         lineWeight = 30)
        
class 本期占用机柜(Line):
    '''红色直线加粗'''
    def __init__(self):
        super().__init__(lineName = "本期占用机柜",
                         lineType = Continuous(),
                         color = CADColor.toIndex("红色"),
                         const_width = 0.8,
                         ltscale = 1,
                         lineWeight = -3)
        
class 本期新增设备(Line):
    '''红色直线加粗, 和本期占用机柜线型相同'''
    def __init__(self):
        super().__init__(lineName = "本期新增设备",
                         lineType = Continuous(),
                         color = CADColor.toIndex("红色"),
                         const_width = 0.8,
                         ltscale = 1,
                         lineWeight = -3)
        
class 现有设备(Line):
    '''普通白色直线'''
    def __init__(self):
        super().__init__(lineName = "现有设备",
                         lineType = Continuous(),
                         color = CADColor.toIndex("白色"),
                         const_width = 0,
                         ltscale = 1,
                         lineWeight = -3)


class 本期新增电源线(Line):
    '''红色DY线'''
    def __init__(self):
        super().__init__(lineName = "本期新增电源线",
                         lineType = DYLine(),
                         color = CADColor.toIndex("红色"),
                         const_width = 0.5)
        
class 本期新增跳纤(Line):
    '''洋红色SM线'''
    def __init__(self):
        super().__init__(lineName = "本期新增跳纤",
                         lineType = SMLine(),
                         color = CADColor.toIndex("洋红色"),
                         const_width = 0.3
                         )
        
class 本期新增网线(Line):
    '''青色UTP线'''
    def __init__(self):
        super().__init__(lineName = "本期新增网线",
                         lineType = UTPLine(),
                         color = CADColor.toIndex("青色"),
                         const_width = 0.3
                        )
        
class 现有互联六类电缆(Line):
    '''青色UTP线加粗'''
    def __init__(self):
        super().__init__(lineName = "现有互联六类电缆",
                         lineType = UTPLine(),
                         color = CADColor.toIndex("青色"),
                         const_width = 1.5
                        )

class 现有互联光缆(Line):
    '''洋红色虚线加粗'''
    def __init__(self):
        super().__init__(lineName = "现有互联光缆",
                         lineType = DASH(),
                         color = CADColor.toIndex("洋红色"),
                         ltscale = 20,
                         const_width = 1.5
                         )
        
class 逻辑连线示意(Line):
    '''蓝色点画线'''
    def __init__(self):
        super().__init__(lineName = "逻辑连线示意",
                         lineType = DASHDOT(),
                         color = CADColor.toIndex("蓝色"),
                         ltscale = 5.0,
                         const_width = 0.2)
        
class 普通黄色线(Line):
    '''普通黄色线'''
    def __init__(self):
        super().__init__(lineName = "普通黄色线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("黄色"),
                            const_width = 0,
                            ltscale = 1,
                            lineWeight = -3)
        
class 普通红色线(Line):
    '''普通红色线'''
    def __init__(self):
        super().__init__(lineName = "普通红色线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("红色"),
                            const_width = 0,
                            ltscale = 1,
                            lineWeight = -3)
        
class 普通红色线02(Line):
    '''普通红色线'''
    def __init__(self):
        super().__init__(lineName = "普通红色线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("红色"),
                            const_width = 0.2,
                            ltscale = 1,
                            lineWeight = -3)
        
class 红色下划线(Line):
    '''红色下划线'''
    def __init__(self):
        super().__init__(lineName = "红色下划线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("红色"),
                            const_width = 0.83,
                            ltscale = 500,
                            lineWeight = -3)
        
class 白色下划线(Line):
    '''白色下划线'''
    def __init__(self):
        super().__init__(lineName = "白色下划线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("白色"),
                            const_width = 0.83,
                            ltscale = 500,
                            lineWeight = -3)
        
class 普通白色粗实线(Line):
    '''普通白色线, 画设备面板图会用到'''
    def __init__(self):
        super().__init__(lineName = "普通白色线",
                            lineType = Continuous(),
                            color = CADColor.toIndex("白色"),
                            const_width = 0.5,
                            ltscale = 2,
                            lineWeight = 0.3 * 100)

class 灰色边框虚线(Line):
    '''灰色边框虚线，画屏柜面板图外框会用到'''
    def __init__(self):
        super().__init__(lineName = "灰色边框虚线",
                            lineType = DASH(),
                            color = 252,
                            const_width = 0,
                            ltscale = 10,
                            lineWeight = -1)
        
class 非建设设备(Line):
    '''普通灰色直线'''
    def __init__(self):
        super().__init__(lineName = "非建设设备",
                         lineType = Continuous(),
                         color = CADColor.toIndex("灰色"),
                         const_width = 0,
                         ltscale = 1,
                         lineWeight = -3)