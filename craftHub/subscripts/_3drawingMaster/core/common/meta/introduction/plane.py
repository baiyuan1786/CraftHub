##########################################################################################################
#   Description: 平面图说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock, CADColor, 红色下划线

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Dict

class PlaneIntroduction(NewBlock):
    """平面图说明"""
    
    # 定义常量：6.114高度时的字符宽度参考值
    REFERENCE_HEIGHT = 6.114
    REFERENCE_CHAR_WIDTHS: Dict[str, float] = {
        "chinese": 4.28,      # 汉字
        "digit": 2.77,        # 阿拉伯数字
        "lowercase": 2.27,    # 小写英文字母
        "uppercase": 2.64,    # 大写英文字母
        "other": 2.5          # 其他字符
    }
    
    def __init__(self,
                 doc: Drawing,
                 substationName: str,
                 roomName: str):
        """平面图说明初始化

        :param doc: 文档
        :param substationName: 站名
        :param roomName: 房间名称
        """        
        super().__init__(doc)
        textContent = f"{substationName}{roomName}平面布置图"
        textFontHeight = 6.114
        
        # 添加文字
        self.addMtext(
            textContent = textContent,
            textFontHeight = textFontHeight,
            textWidth = 100,
            textColor = CADColor.toIndex("红色"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(0, 0),
            style = "GEDITXT",
            attachment = 8
        )
        
        # 添加横线
        textLen = self._textLen(textContent, textFontHeight)
        self.addLine(
            startPoint = Vec2(textLen * -0.5, -0.3),
            endPoint = Vec2(textLen * 0.5, -0.3),
            line = 红色下划线()
        )
    
    def _isChinese(self, char: str) -> bool:
        """判断字符是否为汉字
        
        :param char: 单个字符
        :return: True如果是汉字，否则False
        """
        # 检查是否为中文字符（包括中文标点）
        charCode = ord(char)
        return (
            (0x4E00 <= charCode <= 0x9FFF) or      # 基本汉字
            (0x3400 <= charCode <= 0x4DBF) or      # 扩展A
            (0x20000 <= charCode <= 0x2A6DF) or    # 扩展B
            (0x2A700 <= charCode <= 0x2B73F) or    # 扩展C
            (0x2B740 <= charCode <= 0x2B81F) or    # 扩展D
            (0x2B820 <= charCode <= 0x2CEAF) or    # 扩展E
            (0x2CEB0 <= charCode <= 0x2EBEF) or    # 扩展F
            (0xF900 <= charCode <= 0xFAFF) or      # 兼容汉字
            (0x2F800 <= charCode <= 0x2FA1F)       # 兼容扩展
        )
    
    def _getCharType(self, char: str) -> str:
        """获取字符类型
        
        :param char: 单个字符
        :return: 字符类型名称
        """
        if self._isChinese(char):
            return "chinese"
        elif char.isdigit():
            return "digit"
        elif char.islower():
            return "lowercase"
        elif char.isupper():
            return "uppercase"
        else:
            return "other"
    
    def _textLen(self, textContent: str, textFontHeight: float) -> float:
        """计算文本总宽度

        :param textContent: 文本内容
        :param textFontHeight: 字体高度
        :return: 文本总宽度
        """
        if not textContent:
            return 0.0
        
        # 计算缩放比例
        scaleRatio = textFontHeight / self.REFERENCE_HEIGHT
        
        totalWidth = 0.0
        
        for char in textContent:
            # 获取字符类型
            charType = self._getCharType(char)
            
            # 计算字符宽度
            referenceWidth = self.REFERENCE_CHAR_WIDTHS.get(charType, self.REFERENCE_CHAR_WIDTHS["other"])
            charWidth = referenceWidth * scaleRatio
            
            totalWidth += charWidth
        
        return round(totalWidth, 4)  # 保留4位小数
