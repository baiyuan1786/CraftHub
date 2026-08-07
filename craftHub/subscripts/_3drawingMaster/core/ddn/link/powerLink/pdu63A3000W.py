##########################################################################################################
#   Description: 包含具体取电端子的pdu连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import TextBox, NewBlock, CADColor
from ....common.graph import 现有设备, 本期占用机柜

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Dict, List, Tuple, Literal
from .pduBase import PDUConnectionPanel

class PDU_63A3000W(PDUConnectionPanel):
    "63A输入，3000W标准PDU, 需要63A输入时可以考虑"
    
    IN_MOD_WIDTH = 3.87
    IN_MOD_HEIGHT = 3.78
    IN_MOD_TEXT = "63A"
    IN_MOD_STYLE = "geditxt"
    
    OUT_MOD_WIDTH = 1.93
    OUT_MOD_HEIGHT = 3.78
    OUT_MOD_STYLE = "geditxt"
    OUT_MOD32_TEXT = "32A"
    OUT_MOD10_TEXT = "10A"
    
    IN_MOD_INTERVAL_X = 8.9
    IN_MOD_INTERVAL_Y = PDUConnectionPanel.IN_INTERVAL_Y
    
    OUT_MOD_INTERVAL_X = 8.07
    OUT_MOD_INTERVAL_Y = PDUConnectionPanel.IN_INTERVAL_Y
    
    TERMINAL_FONT_HEIGHT = 1.44

    def __init__(self, doc: Drawing, installPnum: str, isNew: bool) -> None:
        super().__init__(doc, installPnum, isNew)
        
        # 端子属性， 先默认使用32APDU
        in32 = TextBox(doc = doc, 
                       boxWidth= self.IN_MOD_WIDTH, 
                       boxHeight = self.IN_MOD_HEIGHT, 
                       textContent = self.IN_MOD_TEXT, 
                       textStyle = self.IN_MOD_STYLE,
                       textFontHeight = self.TERMINAL_FONT_HEIGHT) # 输入32A端子

        # 插入左右两个In接口
        in32.insertIntoMid(self, Vec2(self.IN_MOD_INTERVAL_X, self.height - self.IN_INTERVAL_Y))
        in32.insertIntoMid(self, Vec2(self.width - self.IN_MOD_INTERVAL_X, self.height - self.IN_INTERVAL_Y))
        
        # 插入输出接口阵列
        LEFT_X_LIST = [self.OUT_MOD_INTERVAL_X + i * self.OUT_MOD_WIDTH for i in range(4)]
        RIGHT_X_LIST = [self.width - self.OUT_MOD_INTERVAL_X + (i - 3) * self.OUT_MOD_WIDTH for i in range(4)]
        
        for insertList in [LEFT_X_LIST, RIGHT_X_LIST]:
            for index, x in enumerate(insertList, start = 1):
                if index < 3:
                    self._addTerminal(x=x, y=self.OUT_MOD_INTERVAL_Y, index=index, a="32A")
                else:
                    self._addTerminal(x=x, y=self.OUT_MOD_INTERVAL_Y, index=index, a="10A")

        # 插入接地线
        self._addGL()
                
                
    def _addTerminal(self, x: float, y: float, index: int, a: Literal["32A", "10A"]):
        '''插入某个安数的端子，使用正中点插入'''
        
        if a == "32A":
            outTer =  TextBox(doc = self.doc, 
                       boxWidth= self.OUT_MOD_WIDTH, 
                       boxHeight = self.OUT_MOD_HEIGHT, 
                       textContent = self.OUT_MOD32_TEXT, 
                       textStyle = self.OUT_MOD_STYLE,
                       textFontHeight = self.TERMINAL_FONT_HEIGHT,
                       textRotation = 90) # 输出32A端子
        elif a == "10A":
            outTer =  TextBox(doc = self.doc, 
                       boxWidth= self.OUT_MOD_WIDTH, 
                       boxHeight = self.OUT_MOD_HEIGHT, 
                       textContent = self.OUT_MOD10_TEXT, 
                       textStyle = self.OUT_MOD_STYLE,
                       textFontHeight = self.TERMINAL_FONT_HEIGHT,
                       textRotation = 90) # 输出10A端子
        else:
            raise ValueError(f"非法端子安数: {a}")
        
        outTer.insertIntoMid(self, Vec2(x, self.OUT_MOD_INTERVAL_Y))
        
        # 插入上方蓝色文本
        self.addMtext(
            textContent = str(index),
            textColor = CADColor.toIndex("深蓝色"),
            textWidth = self.OUT_MOD_WIDTH,
            textFontHeight = 1.55,
            style = "gedi",
            attachment = 8,
            insertPoint = Vec2(x, y + self.OUT_MOD_HEIGHT / 2)
        )
        
        
    @classmethod
    def inPoint(cls, insertPoint: Vec2, direction: Literal["left", "right"]):
        '''返回输入点绝对坐标(相对上一级基点)'''
        if direction == "left":
            return insertPoint + Vec2(cls.IN_MOD_INTERVAL_X, cls.height - cls.IN_INTERVAL_Y + cls.IN_MOD_HEIGHT / 2)
        elif direction == "right":
            return insertPoint + Vec2(cls.width - cls.IN_MOD_INTERVAL_X, cls.height - cls.IN_INTERVAL_Y + cls.IN_MOD_HEIGHT / 2)
        else:
            raise ValueError(f"非法的方向: {direction}")
    
    @classmethod
    def outPoint(cls, insertPoint: Vec2, direction: Literal["left", "right"]):
        '''返回输出点绝对坐标(相对上一级基点)'''
        
        # 使用最右侧10A端子
        if direction == "left":
            return insertPoint + Vec2(cls.OUT_MOD_INTERVAL_X + cls.OUT_MOD_WIDTH * 3, cls.OUT_MOD_INTERVAL_Y - cls.OUT_MOD_HEIGHT / 2)
        elif direction == "right":
            return insertPoint + Vec2(cls.width - cls.OUT_MOD_INTERVAL_X, cls.OUT_MOD_INTERVAL_Y - cls.OUT_MOD_HEIGHT / 2)
        else:
            raise ValueError(f"非法的方向: {direction}")
        

