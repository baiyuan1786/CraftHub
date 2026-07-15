##########################################################################################################
#   Description: 复杂线型类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .base import LineType, ComplexLinePattern

class SMLine(LineType):
    '''单模尾纤线'''
    def __init__(self):
        name = "单模尾纤"
        charText = "SM"
        desc = f"尾纤线---{charText}---{charText}---{charText}---"

        pattern = ComplexLinePattern(text = charText,
                                       font = "STANDARD")
        super().__init__(name, pattern, desc, pattern.length)
        
class DYLine(LineType):
    '''电源线'''
    def __init__(self):
        name = "电源线"
        charText = "DY"
        desc = f"电源线---{charText}---{charText}---{charText}---"

        pattern = ComplexLinePattern(text = charText,
                                       font = "STANDARD")
        super().__init__(name, pattern, desc, pattern.length)
        
class UTPLine(LineType):
    '''非屏蔽双绞线(网线)'''
    def __init__(self):
        name = "网线UTP"
        charText = "UTP"
        desc = f"网线---{charText}---{charText}---{charText}---"

        pattern = ComplexLinePattern(text = charText,
                                       font = "STANDARD")
        super().__init__(name, pattern, desc, pattern.length)