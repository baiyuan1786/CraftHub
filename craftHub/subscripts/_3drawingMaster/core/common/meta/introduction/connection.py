##########################################################################################################
#   Description: 设备连接图说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock, CADColor, 白色下划线

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal

class ConnectionIntroduction(NewBlock):
    '''设备连接图说明'''
    def __init__(self, doc: Drawing) -> None:
        super().__init__(doc)
        
        textContent = "设备连接图"
        textFontHeight = 8
        
        self.addMtext(textContent = textContent,
                        textFontHeight = textFontHeight,
                        textWidth = 75,
                        style = "GEDI",
                        insertPoint = Vec2(0, 0),
                        attachment = 8)
        
        textLine = self._textLen(textContent, textFontHeight)
        
        
        # 添加横线
        self.addLine(
            startPoint = Vec2(textLine * -0.5, -0.3),
            endPoint = Vec2(textLine * 0.5, -0.3),
            line = 白色下划线()
        )
        
    def _textLen(self, 
                  textContent: str, 
                  textFontHeight: float):
        """文本长度

        :param textContent: 文本
        :param textFontHeight: 文本高度
        """      
        
        return (textFontHeight / 8) * 6 * len(textContent)
    