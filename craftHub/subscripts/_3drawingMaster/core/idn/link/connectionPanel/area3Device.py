##########################################################################################################
#   Description: 三区普通设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import NewBlock, TextBox, CADColor

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal, Optional, List

class Area3DeviceConnectionPanel(NewBlock):
    '''带有一个端口的普通设备连接面板图(3区连接用)'''
    
    @classmethod
    def getWidth(cls):
        return 30.4
    
    def __init__(self, 
                 doc: Drawing,
                 port: Optional[str],
                 devNum: Optional[str],
                 devName: Optional[str],
                 pNum: Optional[str] = None,
                 pName: Optional[str] = None,
                 textLine: int = 1
                 
                 ) -> None:
        """配电屏连接面板图初始化

        :param doc: 文档
        :param port: 端口名
        :param devNum: 设备号, 例如 3P03
        :param devName: 设备名, 例如 idn交换机
        :param pNum: 屏名称, 例如 直流配电设备1屏, 如果屏和设备数字相同可不填
        :param pName: 设备名称, 例如 "IDF配线单元", 可不填
        :param textLine: 文本行数
        """
        super().__init__(doc)
        
        pFullName = f"{pNum}{pName}" if pNum is not None and pName is not None else None 
        self.fullName = ""
        if pFullName is not None:
            self.fullName += pFullName + "\n"
        if devNum is not None:
            self.fullName += devNum + "\n"
        if devName is not None:
            self.fullName += devName
        
        self.port = port if port is not None else "未知口"
        self.devNum = devNum
        self.devName = devName
        self.width = 30.4
        
        # 插入双文本框
        textBoxPort = TextBox(doc = doc, 
                              boxWidth = self.width, 
                              boxHeight = 7.27,
                              textFontHeight = 2.16,
                              textContent = self.port,
                              textStyle = "GEDITXT")
        
        textBoxName = TextBox(doc = doc, 
                              boxWidth = self.width, 
                              boxHeight = 14.5,
                              textFontHeight = 2.88,
                              textContent = self.fullName,
                              textStyle = "GEDITXT")
        
        textBoxPort.insertInto(self.block, Vec2(0, 14.5))
        textBoxName.insertInto(self.block, Vec2(0, 0))
        
        
    @staticmethod
    def leftPoint(offset: Vec2 = Vec2(0, 0)):
        '''左接口点'''
        return Vec2(2, 17.4) + offset
    
    @staticmethod
    def rightPoint(offset: Vec2 = Vec2(0, 0)):
        '''右接口点'''
        return Vec2(27.7, 17.4) + offset
    
    @staticmethod
    def downPoint(offset: Vec2 = Vec2(0, 0)):
        '''下接口点'''
        return Vec2(30.4 / 2, 1.5) + offset
        
    @staticmethod
    def upPoint(offset: Vec2 = Vec2(0, 0)):
        '''上接口点'''
        return Vec2(30.4 / 2, 19.6) + offset
    
    def portNum(self):
        '''返回端口数量'''
        return self.port.count(",") + 1 # 以逗号分隔计算端口数量
    
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Area3DeviceConnectionPanel):
            return NotImplemented
        
        return (self.devNum == other.devNum
                and self.devName == other.devName
                and self.port == other.port)
        
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)