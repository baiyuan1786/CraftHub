##########################################################################################################
#   Description: 组网链路表说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock, CADColor, 红色下划线

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal

class NetWorkLinkIntroduction(NewBlock):
    '''组网链路表说明'''
    def __init__(self, doc: Drawing) -> None:
        super().__init__(doc)
        
        textContent = "组网链路需求表"
        # 添加文字
        self.addMtext(
            textContent = textContent,
            textFontHeight = 9.3,
            textWidth = 75,
            textColor = CADColor.toIndex("白色"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(0, 0),
            style = "GEDITXT",
            attachment = 8
        )