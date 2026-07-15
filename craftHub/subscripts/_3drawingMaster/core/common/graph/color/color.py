##########################################################################################################
#   Description: CAD颜色类, 将颜色映射为CAD索引
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import Union, Dict, Optional

class CADColor:
    """AutoCAD 颜色管理类
    
    提供汉字颜色名到CAD颜色Index的转换
    """
    
    # CAD标准颜色Index映射表
    COLOR_MAPPING: Dict[str, int] = {
        "bylayer": 256,      # 随图层
        "byblock": 0,        # 随块
        
        # 标准颜色 (AutoCAD Index 1-7)
        "红色": 1,
        "红": 1,
        "red": 1,
        "黄色": 2,
        "黄": 2,
        "yellow": 2,
        "绿色": 3,
        "绿": 3,
        "green": 3,
        "青色": 4,
        "青": 4,
        "cyan": 4,
        "蓝色": 5,
        "蓝": 5,
        "blue": 5,
        "洋红色": 6,
        "洋红": 6,
        "magenta": 6,
        "purple": 6,
        "白色": 7,
        "白": 7,
        "white": 7,
        "黑色": 7,            # 注意：7 为黑白混合， 在白色背景上显示黑，黑色背景上显示白
        "黑": 7,
        "black": 7,
        
        # 扩展常用颜色 (AutoCAD Index 10-249)
        "灰色": 8,
        "灰": 8,
        "gray": 8,
        "浅灰色": 9,
        "浅灰": 9,
        "lightgray": 9,
        "棕色": 40,
        "棕": 40,
        "brown": 40,
        "粉红色": 12,
        "粉红": 12,
        "pink": 12,
        "橙色": 30,
        "橙": 30,
        "orange": 30,
        "金色": 51,
        "金": 51,
        "gold": 51,
        "银色": 8,
        "银": 8,
        "silver": 8,
        "橄榄色": 59,
        "橄榄": 59,
        "olive": 59,
        "紫色": 180,
        "紫": 180,
        "深红色": 12,
        "深红": 12,
        "darkred": 12,
        "墨绿色": 62,
        "墨绿": 62,
        "darkgreen": 62,
        "深蓝色": 140,
        "深蓝": 140,
        "darkblue": 140,
        "浅蓝色": 151,
        "浅蓝": 151,
        "lightblue": 151,
        "浅绿色": 92,
        "浅绿": 92,
        "lightgreen": 92,
        
        # ACI默认值
        "none": 0,           # 无颜色/Byblock
        "normal": 1,         # 默认红色
        "default": 1,
    }
    
    @classmethod
    def toIndex(cls, colorName: str) -> int:
        """将颜色名转换为CAD颜色Index
        
        :param colorName: 颜色名称（中文/英文）
        """

        colorName = str(colorName).strip().lower()
        
        if colorName in cls.COLOR_MAPPING:
            return cls.COLOR_MAPPING[colorName]
        else:
            raise ValueError(f"未定义的颜色: \'{colorName}\'")
        
    @classmethod
    def colored(cls, text: Optional[str], colorName: str = "红色"):
        """文本染色

        :param text:        文本
        :param colorName:   颜色名称， 默认染红色
        """        
        if text is None:
            return ""
        
        colorIndex = cls.toIndex(colorName)
        return f"\\C{colorIndex};{text}\\C0;"
