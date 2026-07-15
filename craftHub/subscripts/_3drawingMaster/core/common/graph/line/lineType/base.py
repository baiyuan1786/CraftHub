##########################################################################################################
#   Description: 线型基类 + pattern基类
#                注意线型不包括线的weight和颜色信息
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog
from ezdxf.document import Drawing
from typing import Optional, List

class LineType:
    '''线型基类,
    规定线型的同时也规定颜色'''
    def __init__(self,
                 name: str,
                 pattern,
                 desc: Optional[str],
                 length: int | float
                 ):
        """线型基类

        :param name: 线型名称，例如 "单模尾纤"
        :param pattern: 线型模式，线型有简单线型和复杂线型之分
        :param desc: 线型描述，例如 ---SM---SM---SM---
        :param length: 线型总长度, 复杂线型需要此参数
        """
        if isinstance(pattern, ComplexLinePattern):
            pattern = pattern.pattern
        elif isinstance(pattern, SimpleLinePattern):
            pattern = pattern.pattern
        
        self.name = name
        self.pattern = pattern
        self.desc = desc
        self.length = length
        
    def addToDoc(self, doc: Drawing):
        """添加该线型到文件中

        :param doc: 绘图文件
        """        
        assert isinstance(doc, Drawing)
        
        if self.name in doc.linetypes:
            GLog.logInfo(f"线型管理器 | 线型已存在 \'{self.name}\'")
            return

        try:
            doc.linetypes.add(
                name = self.name,
                pattern = self.pattern,
                description = self.desc,
                length = self.length
            )
        except Exception as e:
            GLog.logInfo(f"线型管理器 | 添加线型 \'{self.name}\' 错误: {str(e)}")
        else:
            GLog.logInfo(f"线型管理器 | 已添加线型 \'{self.name}\'")

class SimpleLinePattern:
    '''简单线型模式类'''
    def __init__(self, patternList: List[int] | List[float]):
        """简单线型模式由列表定义

        :param patternList: [total_pattern_length, elem1, elem2, ...]
        """
        # 检查空 
        if not patternList:
            raise ValueError("Pattern is Empty")
        
        # 检查总长
        if (patternList[0] - sum([abs(num) for num in patternList[1:]])) > 1e-9:
            raise ValueError("Pattern 的总长与各个部分长度之和不匹配")
        
        self.patternList = patternList
        
    @property
    def length(self):
        '''模式线段总长'''
        return self.patternList[0]
        
    @property
    def pattern(self):
        '''线型模式'''
        return self.patternList
        
class ComplexLinePattern:
    '''复杂线型模式类'''
    def __init__(self,
                 text: str,
                 font: str = "STANDARD",
                 lineLength: float = 3,
                 textGap: float = 2.5,
                 textSize: float = 1.2,
                 textXoffset: float = -1,
                 textYoffset: float = -0.6):
        """复杂线型模式

        :param text: 复杂线型文本, 例如SM
        :param font: 复杂线型文字样式
        :param lineLength: 线长, defaults to 3
        :param textGap: 文本间隔, defaults to 2.5
        :param textSize: 文本大小, defaults to 1.2
        :param textXoffset: 文本X轴偏移, defaults to -1
        :param textYoffset: 文本Y轴偏移, defaults to -0.6
        """        

        self.text = text
        self.font = font
        self.lineLength = lineLength
        self.textGap = textGap
        self.textSize = textSize
        self.textXoffset = textXoffset
        self.textYoffset = textYoffset
           
    @property
    def length(self):
        '''模式线段总长'''
        return self.lineLength + self.textGap * 2 + self.textSize * 1.2
        
    @property
    def pattern(self):
        '''线型模式'''
        return f'A,{self.lineLength},-{self.textGap},' \
            f'[\"{self.text}\",{self.font},S={self.textSize},U=0.0,X={self.textXoffset * 0.8},Y={self.textYoffset}],' \
            f'-{self.textGap}'