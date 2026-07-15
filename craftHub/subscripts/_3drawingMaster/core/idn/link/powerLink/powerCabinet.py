##########################################################################################################
#   Description: 配电屏连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import NewBlock, TextBox, CADColor
from ....common.graph import 现有设备

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal, Optional, List

class PowerCabinetConnectionPanel(NewBlock):
    '''配电屏连接面板图'''
    width1 = 46.4639    # 外框宽度
    height1 = 12.6968   # 外框高度
    
    width2 = 43.6724    # 内框宽度
    height2 = 4.9903    # 内框高度
    def __init__(self, 
                 doc: Drawing,
                 pNum: str,
                 pName: str,
                 tkNum: str,
                 tkA: Literal["10A", "16A", "20A", "32A", "63A"]
                 ) -> None:
        """配电屏连接面板图初始化

        :param doc: 文档
        :param pNum: P号, 例如10P
        :param pName: 屏名称, 例如 直流配电设备1屏
        :param tkNum: 空开编号， 例如1TK16
        :param tkA: 空开安数, 例如16A
        """        
        super().__init__(doc)
        
        self.addRectangle(self.width1, self.height1, line = 现有设备())
        self.addRectangle(self.width2, self.height2, line = 现有设备(), insertPoint = Vec2(1.4637, 0.5877))
        
        self.addMtext(
            textContent = f"{pNum} {pName}".upper(),
            textFontHeight = 2.88,
            textWidth = self.width1 * 0.8,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(23.42, 9.18),
            style = "GEDITXT",
        )
        
        self.addMtext(
            textContent = f"{tkNum}({tkA})".upper(),
            textFontHeight = 2.52,
            textWidth = self.width2 * 0.8,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(23.42, 3),
            style = "GEDITXT",
        )
