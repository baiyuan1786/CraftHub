##########################################################################################################
#   Description: GCN网设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace

from ....common.graph import NewBlock, TextBox, CADColor
from ....common.graph import 现有设备

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Any, Literal, Optional, List

class GCNUnitConnectionPanel(NewBlock):
    '''GCN网设备单元连接面板图'''
    
    width = 46       # 单元宽度
    widthInter = 43  # 内部框宽度
    heightInter = 5 # 内部框高度
    offsetY1 = 3     # 内部框纵向偏置
    heightALine = 5.5  # 单行字符串高度
    
    def __init__(self, 
                 doc: Drawing,
                 pFullName: str,
                 unitName: str,
                 portName: str,
                 insertPoint: Vec2,
                 boardName: Optional[str] = None,
                 GCNareaName: Optional[str] = None,
                 ) -> None:
        """GCN网连接单元初始化

        :param doc: 文档
        :param pFullName: 屏柜完整名称
        :param unitName: 单元名称
        :param portName: 端口名称
        :param insertPoint: 插入点
        :param boardName: 以太网板卡名称, defaults to None
        :param GCNareaName: GCN网所属域名称, defaults to None
        """        
        super().__init__(doc)
        self.insertPoint = insertPoint # 记录偏置
        
        pString = pFullName
        if boardName is not None and GCNareaName is not None:
            pString += f"\n传输新网B(\\C1;{GCNareaName}\\C0;)设备"
            pString += f"\n({CADColor.colored(boardName, "红色")})以太网板卡"
            
        unitString = f"{unitName} {portName}"
            
        textLineNum = len(pString.split("\n"))
        height = self.offsetY1 + self.heightInter + textLineNum * self.heightALine
        if textLineNum == 1:
            height += 3
        
        # 添加外框
        self.addRectangle(width = self.width, 
                          height = height, 
                          line = 现有设备(),
                          insertPoint = Vec2(0, 0))
        
        # 添加内框
        self.addRectangle(width = self.widthInter, 
                          height = self.heightInter, 
                          line = 现有设备(),
                          insertPoint = Vec2((self.width - self.widthInter) / 2, self.offsetY1))
            
        # 添加外文本
        self.addMtext(
            textContent = pString,
            textFontHeight = 2.88,
            textWidth = self.width * 0.9,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(self.width / 2, height - 2),
            style = "GEDITXT",
            attachment = 2
        )
        
        # 添加内文本
        self.addMtext(
            textContent = unitString,
            textFontHeight = 2.16,
            textWidth = self.widthInter * 0.9,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(self.width / 2, self.offsetY1 + self.heightInter / 2),
            style = "GEDITXT",
            attachment = 5
        )
        

    def leftPoint(self):
        '''返回左接口绝对坐标'''
        return self.insertPoint + Vec2((self.width - self.widthInter) / 2, self.offsetY1 + self.heightInter / 2)
    
    def rightPoint(self):
        '''返回右接口绝对坐标'''
        return self.leftPoint() + Vec2(self.widthInter, 0)
    
    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        return super().insertInto(layout, self.insertPoint)
        