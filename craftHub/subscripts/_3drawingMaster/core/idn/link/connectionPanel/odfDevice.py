##########################################################################################################
#   Description: ODF屏连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import NewBlock, TextBox, CopiedBlock, CADColor
from ....common.graph import 现有设备, 本期占用机柜

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal, Optional, List

class ODFUnit:
    '''ODF单元, 仅供下面ODF连接面板图使用'''
    def __init__(self,
                 unitNum: str,
                 leftPoint: Vec2,
                 rightPoint: Vec2) -> None:
        """ODF单元

        :param unitName: 单元编号, 例如3P02
        :param leftPoint: _description_
        :param rightPoint: _description_
        """

        self.unitNum = unitNum
        self.leftPt = leftPoint
        self.rightPt = rightPoint
    
        self.isUsedLeft = False     # 左侧点被使用
        self.isUsedRight = False    # 右侧点被使用
    
    @property
    def leftPoint(self):
        '''如果未被使用，返回左侧点'''
        if not self.isUsedLeft:
            self.isUsedLeft = True
            return self.leftPt
        raise ValueError("左侧点已经被使用")
        
    @property
    def rightPoint(self):
        '''如果未被使用，返回左侧点'''
        if not self.isUsedRight:
            self.isUsedRight = True
            return self.rightPt
        raise ValueError("右侧点已经被使用")
        
class ODFPConnectionPanel(NewBlock):
    '''ODF屏连接面板图,
    一个ODF屏包含多个ODF连接单元, 
    同一个连接单元允许多次出现在连接面板图中'''
    def __init__(self, 
                 doc: Drawing,
                 odfLinkODFPfullName: str,
                 odfLinkUnitNumList: List[str],
                 ) -> None:
        """ODF屏连接面板图初始化

        :param doc: 文档
        :param odfLinkODFPfullName: ODF屏全名
        :param odfLinkUnitNumList: ODF连接单元列表 / 从上到下绘制
        """
        super().__init__(doc)
        self.name = odfLinkODFPfullName
        
        baseHeight = 6
        unitBaseHeight = 8
        unitHeight = 5
        unitWidth = 43
        
        width = 46.3
        height = baseHeight + unitBaseHeight * len(odfLinkUnitNumList)
        
        self.width = width
        self.height = height
        
        textFontHeight = 3 if len(odfLinkODFPfullName) < 20 else 2.4
        
        # ODF外框
        self.addRectangle(width = width, height = height, line = 现有设备())
        self.addMtext(
            textContent = odfLinkODFPfullName,
            textFontHeight = textFontHeight,
            textWidth = 46.4,
            textColor = CADColor.toIndex("ByBlock"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(width / 2, height - 3.3),
            style = "GEDITXT",
        )
        
        self.unitList: List[ODFUnit] = []
        
        # ODFunit绘制
        for index, unitNum in enumerate(odfLinkUnitNumList):
            basePoint = Vec2((width - unitWidth) / 2, height - baseHeight - (index + 1) * unitBaseHeight + (unitBaseHeight - unitHeight) / 2)
            
            TextBox(doc = doc, 
                    boxWidth = unitWidth, 
                    boxHeight = unitHeight,
                    textFontHeight = 2.16,
                    textContent = f"{unitNum} ODF配线单元" if "ODF" not in unitNum and "设备" not in unitNum else unitNum,
                    textStyle = "GEDITXT").insertInto(self.block, basePoint)
            
            # 记录连接点和连接次数
            self.unitList.append(ODFUnit(unitNum = unitNum, 
                                         leftPoint = basePoint + Vec2(0, unitHeight / 2), 
                                         rightPoint = basePoint + Vec2(unitWidth, unitHeight / 2)))

    def unitPoint(self, 
                  unitNum: str, 
                  leftRight: Literal["left", "right"],
                  offSet: Vec2 = Vec2(0, 0)):
        """搜索ODF单元左右连接点, 同一个ODF单元只可被搜索一次

        :param unitNum: 单元名
        :param leftRight: 左点或者右点
        :param offSet: 基点偏置
        """        
        # 搜索左点
        if leftRight == "left":
            for unit in self.unitList:
                if unit.unitNum == unitNum and not unit.isUsedLeft:
                    return unit.leftPoint + offSet
            else:
                raise ValueError(f"未搜索到可用ODF单元: \'{unitNum}\'")
        # 搜索右点
        elif leftRight == "right":
            for unit in self.unitList:
                if unit.unitNum == unitNum and not unit.isUsedRight:
                    return unit.rightPoint + offSet
            else:
                raise ValueError(f"未搜索到可用ODF单元: \'{unitNum}\'")
            
        else:
            raise ValueError(f"错误的指定: \'{leftRight}\'")
        

class ODFJumpUnit(NewBlock):
    '''ODF跳纤单元'''
    def __init__(self, 
                 doc: Drawing,
                 odfPName: str,
                 odfUnitName: str,
                 height: int):
        """ODF跳纤单元初始化

        :param doc: 文档
        :param odfPName: ODF屏名称
        :param odfUnitName: ODF单元名称
        :param height: _description_
        """        
        
        super().__init__(doc)
        
        offsety1 = 3.2 # 从下到内框偏置
        offsety2 = 6.8 # 从上到内框偏置
        
        self.lineNum = 1 if len(odfUnitName) < 15 else 2
        
        self.line1Height = 5 # 单行文本框高度
        self.width = 46
        self.height = height
        self.heightInter = height - offsety1 - offsety2
        
        # ODF屏
        self.addRectangle(width = self.width, height = self.height, line = 现有设备())
        self.addMtext(textContent = odfPName,
                      textFontHeight = 2.88,
                      textWidth = self.width * 0.8,
                      insertPoint = Vec2(self.width / 2, self.height - 2.36),
                      attachment = 2,
                      style = "GEDITXT")
        
        # ODF单元
        unitBox = TextBox(doc = doc, 
                    boxWidth = 43, 
                    boxHeight = self.heightInter,
                    textFontHeight = 2.16,
                    textContent = odfUnitName,
                    textStyle = "GEDITXT")
        
        unitBox.insertInto(self.block, insertPoint  = Vec2(1.58, offsety1))
        
    def left2right(self, point: Vec2):
        '''左侧点转换右侧点'''
        return point + Vec2(self.width, 0)
    
    @staticmethod
    def getWidth():
        return 46
        
        