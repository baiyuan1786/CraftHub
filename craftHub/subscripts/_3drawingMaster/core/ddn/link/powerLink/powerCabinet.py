##########################################################################################################
#   Description: 配电屏连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import NewBlock, TextBox, CADColor
from ....common.graph import 现有设备

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal, Optional, List

        
class PowerCabinetConnectionPanel2(NewBlock):
    '''配电屏连接面板图2'''
    width1 = 49.73    # 外框宽度
    height1 = 13.34   # 外框高度
    
    width2 = 32.91    # 内框宽度
    height2 = 5.24    # 内框高度
    def __init__(self, 
                 doc: Drawing,
                 roomName: str,
                 pNum: str,
                 pName: str,
                 tkNum: str,
                 tkA: Literal["10A", "16A", "20A", "32A", "63A"],
                 orient: Literal["left", "right"] = "left"
                 ) -> None:
        """配电屏连接面板图初始化

        :param doc: 文档
        :param roomName: 房间名, 如主控室
        :param pNum: P号, 例如10P
        :param pName: 屏名称, 例如 直流配电设备1屏
        :param tkNum: 空开编号， 例如1TK16
        :param tkA: 空开安数, 例如16A
        :param orient: 方向, 可选左边和右边
        """        
        super().__init__(doc)
        
        if orient == "left":
            ipInterMtext = Vec2(14.47 + self.width2 / 2, 3)
            ipInterBox = Vec2(14.31, 0.5877)
        else:
            ipInterMtext = Vec2(self.width1 - self.width2 / 2 - 14.47, 3)
            ipInterBox = Vec2(self.width1 - self.width2 - 14.31, 0.5877)
        
        
        self.addRectangle(self.width1, self.height1, line = 现有设备())
        self.addRectangle(self.width2, self.height2, line = 现有设备(), insertPoint = ipInterBox)
        
        cabinetStr = f"{roomName} {pNum} {pName}".upper()
        
        # 屏柜文字
        self.addMtext(
            textContent = CADColor.colored(cabinetStr),
            textFontHeight = 3.2, # if len(cabinetStr) < 19 else 2.5,
            textWidth = self.width1 * 0.99,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(23.42, 9.18),
            style = "gedi",
        )

        # 空开文字
        self.addMtext(
            textContent = f"{CADColor.colored(tkNum)}({tkA})".upper(),
            textFontHeight = 2.8,
            textWidth = self.width2 * 0.99,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = ipInterMtext,
            style = "gedi",
        )
        
        