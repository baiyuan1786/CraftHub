##########################################################################################################
#   Description: 简单线型类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .base import LineType, SimpleLinePattern
    
class DASH(LineType):
    '''虚线类型'''
    def __init__(self):
        name = "DASH"
        pattern = SimpleLinePattern(patternList = [0.35, 0.26, -0.9])
        desc = "--------------------------"
        super().__init__(name, pattern, desc, pattern.length)
        
class DASHDOT(LineType):
    '''点画线类型'''
    def __init__(self):
        name = "DASHDOT"
        pattern = SimpleLinePattern(patternList = [6, 3.5, -1.25, 0, -1.25])
        desc = "—— . —— . —— . —— . —— . —— . "
        super().__init__(name, pattern, desc, pattern.length)
        
class Continuous(LineType):
    '''默认连续直线'''
    def __init__(self):
        name = "Continuous"
        pattern = SimpleLinePattern(patternList = [1, 1])
        desc = "——————————————————————————————"
        super().__init__(name, pattern, desc, pattern.length)