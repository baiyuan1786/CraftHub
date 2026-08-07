##########################################################################################################
#   Description: 文本框类
#                暂时不支持配置字体样式和线形，后面再修改
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import Any

from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace

from .block import CustomBlock

from ..line import 现有设备
from ..line import Line
from ..color import CADColor

from ezdxf.math import Vec2
from ezdxf.document import Drawing

DEFAULT_TEXT_WIDTH_FACTOR = 0.9

class TextBox(CustomBlock):
    """
    带有多行文本框的矩形框类, 该矩形框使用一个块来维护
    """

    def __init__(self,
                 doc: Drawing,
                 boxWidth: float = 48.2,
                 boxHeight: float = 4.45,
                 boxLine: Line = 现有设备(),
    
                 textContent: str = "",
                 textFontHeight: float = 1.98,
                 textLineSpacingDistance: float = 1,
                 textColor: int = CADColor.toIndex("白色"),
                 textStyle: str = "天联",
                 textRotation: int = 0,
                 textAttachment: int = 5
                 ):
        """初始化BoxWithText对象
        该块创建之后以块来维护对象

        :param doc:             DXF文档对象
        :param boxWidth:        文本框宽度, defaults to 48.2
        :param boxHeight:       文本框高度, defaults to 4.45
        :param boxLine:         文本框线型, 

        :param textContent:             文本框内容, defaults to ""
        :param textFontHeight:          文本框文字高度, defaults to 1.98
        :param textLineSpacingDistance: 行间距, defaults to 1
        :param textColor:               文本框颜色
        :param textStyle                字体样式， 必须选择存在的字体样式, 否则报错
        :param textRotation:            文本框旋转角度
        """         
        super().__init__(doc)
        insertPoint = Vec2(0, 0)
        # 插入矩形
        self.addRectangle(
            width = boxWidth,
            height = boxHeight,
            line = boxLine,
            insertPoint = insertPoint
        )
        
        self.boxWidth = boxWidth
        self.boxHeight = boxHeight
        
        # 插入文本框
        self.addMtext(
            textContent = textContent,
            textFontHeight = textFontHeight,
            textWidth = boxWidth * DEFAULT_TEXT_WIDTH_FACTOR,
            textColor = textColor,
            textLineSpacingDistance = textLineSpacingDistance,
            style = textStyle, # 默认使用天联字体
            insertPoint = insertPoint + Vec2(boxWidth / 2, boxHeight / 2),
            rotation = textRotation,
            attachment = textAttachment
        )
        
    def insertIntoMid(self, layout: BlockLayout | Modelspace | Any, insertPoint: Vec2 | None = None):
        '''使用中心点插入'''
        insertPoint -= Vec2(self.boxWidth / 2, self.boxHeight / 2)
        return super().insertInto(layout, insertPoint)
