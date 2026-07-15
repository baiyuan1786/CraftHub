##########################################################################################################
#   Description: 跳纤链路类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .link import LinkBase, Link
from typing import List, Optional
from pandas import DataFrame

class FiberJumpLink(Link):
    '''跳纤链路'''
    def __init__(self, 
                 substationName: str,
                 startSta: str,
                 endSta: str,
                 startStaLayer: Optional[str],
                 endStaLayer: Optional[str],
                 walkLine: str) -> None:
        """跳纤链路初始化

        :param substationName:  跳纤链路所处站
        :param startSta:        开始站
        :param endSta:          目标站
        :param startStaLayer:   开始站层级
        :param endStaLayer:     目标站层级
        """        
        
        self.substationName = substationName
        self.startSta = startSta
        self.endSta = endSta

        self.startStaLayer = startStaLayer
        self.endStaLayer = endStaLayer
        self.walkLine = walkLine
        
        if self.startStaLayer is not None and self.endStaLayer is not None:
            note = f"{self.startSta}至{self.endSta}{self.startStaLayer}与{self.endStaLayer}互联链路组网跳纤用"
        else:
            note = f"{self.startSta}至{self.endSta}互联链路组网跳纤用"

        super().__init__(3,
                         "铠装跳纤",
                         "单模FC-FC",
                         "请填写ODF屏",
                         "请填写ODF屏",
                         2,
                         note
                         )
        
    def toDF(self, substationName = None, walkLine = None):
         return super().toDF(self.substationName, self.walkLine)
        
    def __eq__(self, other: object):
        if not isinstance(other, FiberJumpLink):
            return NotImplemented
        if other.substationName == self.substationName:
            # 仅要求名称部分匹配
            if (other.startSta in self.startSta and other.endSta in self.endSta) or\
                (self.startSta in other.startSta and self.endSta in other.endSta) or\
                (other.startSta in self.endSta and other.endSta in self.startSta) or\
                (self.startSta in other.endSta and self.endSta in other.startSta):
                    return True

        return False
    
    def readExcel(self, subDF: DataFrame):
        '''读取已有表格， 尝试读取表格中已有的数据，填写线缆长度'''

        for index, row in subDF.iterrows():
            self.readRowArgs(row = row)
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
     
     
    def __str__(self) -> str:
        return f"{self.substationName}: {self.startSta}->{self.endSta}"
        
        