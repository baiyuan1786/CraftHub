##########################################################################################################
#   Description: 具体链接
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .link import Link
from typing import List, Literal, Optional

class 直流电源线_阻燃导线(Link):
    def __init__(self, 
                 startPos: str, 
                 endPos: str,
                 current: Optional[str],
                 num: int = 1) -> None:
        
        if current is not None and current.endswith("A"):
            current = current.split("A")[0]

        if current is None or current == "10":
            specification = "ZA-RVV-2*4mm2,红蓝各半"
        elif current == "16" or current == "20":
            specification = "ZA-RVV-2*6mm2,红蓝各半"
        elif current == "32" or current == "40":
            specification = "ZA-RVV-2*10mm2,红蓝各半"
        elif current == "63":
            specification = "ZA-RVV-2*16mm2,红蓝各半"
            
        else:
            raise ValueError(f"{startPos}->{endPos} | 电流端子错误: {current} | 电流端子不合法")
        
        super().__init__(1, 
                         "直流电源线", 
                         specification, 
                         startPos, 
                         endPos, 
                         num)
        
class 直流电源线_原厂配套(Link):
    def __init__(self, 
                 startPos: str, 
                 endPos: str, 
                 ) -> None:
        super().__init__(1, 
                         "直流电源线", 
                         "原厂配套", 
                         startPos, 
                         endPos, 
                         1)
        
class 接地线(Link):
    '''设备接地线'''
    def __init__(self,
                 startPos: str, 
                 endPos: str, 
                 ) -> None:
        super().__init__(2, 
                         "接地线", 
                         "原厂配套", 
                         startPos, 
                         endPos, 
                         1)
        
class 机柜接地线(Link):
    def __init__(self,
                 startPos: str, 
                 endPos: str, 
                 ) -> None:
        super().__init__(2, 
                         "机柜接地线", 
                         "原厂配套", 
                         startPos, 
                         endPos, 
                         1)
        
class 铠装跳纤(Link):
    def __init__(self, 
                 specification: Literal["单模LC-FC", "单模LC-LC", "单模FC-FC"],
                 startPos: str, 
                 endPos: str, 
                 num: int,
                 note: str) -> None:
        super().__init__(3, 
                         "铠装跳纤", 
                         specification, 
                         startPos, 
                         endPos, 
                         num, 
                         note)

class 光速寻线以太网线缆(Link):
    def __init__(self, 
                 startPos: str, 
                 endPos: str, 
                 note: str,
                 num: int = 1
                 ) -> None:
        super().__init__(4, 
                         "光速寻线以太网线缆", 
                         "六类非屏蔽双绞线", 
                         startPos, 
                         endPos, 
                         num, 
                         note)    
        
class 普通网线(Link):
    def __init__(self, 
                 startPos: str, 
                 endPos: str, 
                 note: str,
                 num: int  = 1
                 ) -> None:
        super().__init__(4, 
                         "普通网线", 
                         "六类非屏蔽双绞线", 
                         startPos, 
                         endPos, 
                         num, 
                         note
                         )
        
class 复合网线(Link):
    def __init__(self, 
                 startPos: str, 
                 endPos: str, 
                 note: str,
                 type: Literal["普通网线", "光速寻线以太网线缆"],
                 ) -> None:
        super().__init__(4, 
                         type, 
                         "六类非屏蔽双绞线", 
                         startPos, 
                         endPos, 
                         1, 
                         note
                         )
        
        