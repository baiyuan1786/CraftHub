##########################################################################################################
#   Description: 单条链接
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog
import numpy as np
import math
import pandas as pd
from pandas import DataFrame
from pandas import Series
from typing import List, Literal, Optional
from abc import ABC, abstractmethod

class LinkBase(ABC):
    '''连接基类'''
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def toDF(self)->DataFrame:
        pass

class Link(LinkBase):
    '''单条链接基类'''
    baseLen = 3  # 基础长度

    armoredJumperLineType = "铠装跳纤"
    armoredJumperLenTuple = (
        1, 3, 5, 8, 10, 15, 20, 25,
        30, 35, 40, 45, 50, 60, 80, 100
    ) # 铠装跳纤允许长度

    def __init__(self, 
                 order: int,
                 lineType: str,
                 specification: str,
                 startPos: str,
                 endPos: str,
                 num: int,
                 note: str = "",

                 crossingCabinet: int = 0,
                 crossingRow: int = 0,
                 crossingFloor: bool = False,
                 crossingRoom: bool = False
                )-> None:    
        """单链接初始化
        :param order: 序号
        :param lineType: 线缆类型
        :param specification: 规格
        :param startPos: 起点
        :param endPos: 终点
        :param num: 数量
        :param note: 备注
        
        :param crossingCabinet: 跨机柜
        :param crossingRow: 跨行
        :param crossingFloor: 跨层
        :param crossingRoom: 同层跨房间
        """
        self.order = order
        self.lineType = lineType
        self.specification = specification
        self.startPos = startPos
        self.endPos = endPos
        self.num = num
        self.note = note
        
        self.crossingCabinet = crossingCabinet
        self.crossingRow = crossingRow
        self.crossingFloor = crossingFloor
        self.crossingRoom = crossingRoom
        
        self.isReferrenced = False

    def convergeArmoredJumperLen(self, rawLen: float) -> int:
        """铠装跳纤长度收敛"""

        for standardLen in self.armoredJumperLenTuple:
            if rawLen <= standardLen:
                return standardLen
        else:
            raise ValueError(f"铠装跳纤长度超过上限: \'{rawLen}\' m")

    def oneLineLen(self, walkLine: str, startPos: Optional[str] = None, endPos: Optional[str] = None):
        '''单条长度/m'''

        for pos in [startPos, endPos]:
            if pos is not None and ("未知" in pos or "请填" in pos):
                return "未知"

        if self.crossingFloor:
            wholeLen = 70
        elif self.crossingRoom:
            wholeLen = 50
        else:
            wholeLen = self.baseLen
            wholeLen += self.crossingCabinet * 0.8
            wholeLen += self.crossingRow * 1.6

            # 电缆层跨屏加六米
            if walkLine == "电缆层走线" and (self.crossingCabinet > 0 or self.crossingRow > 0):
                wholeLen += 6

        # 铠装跳纤长度收敛
        if self.lineType.strip() == self.armoredJumperLineType:
            return self.convergeArmoredJumperLen(wholeLen)

        return math.ceil(wholeLen)
    
    def wholeLineLen(self, walkLine: str, startPos: Optional[str] = None, endPos: Optional[str] = None):
        '''全部线长度'''
        oneLen = self.oneLineLen(walkLine, startPos, endPos)
        return oneLen * self.num if isinstance(oneLen, float) or isinstance(oneLen, int) else "未知"

    def toDF(self, substationName: str, walkLine: str):
        '''转换DataFrame'''
        return DataFrame({
                "站名": substationName,
                "序号": self.order,
                "线缆类型": self.lineType,
                "规格": self.specification,
                "起点": self.startPos,
                "终点": self.endPos,
                "单条长度/m": self.oneLineLen(walkLine, self.startPos, self.endPos),
                "数量/条": self.num,
                "合计/米": self.wholeLineLen(walkLine, self.startPos, self.endPos),
                "备注": self.note,
                "走线": walkLine,
                "跨越机柜": int(self.crossingCabinet),
                "跨越行": int(self.crossingRow),
                "跨层": int(self.crossingFloor),
                "同层跨房间": int(self.crossingRoom),
                "参照": int(self.isReferrenced),
                "完整线缆类型": f"{self.lineType} + {self.specification}",
            }, index=[0])
        
    def isRowMatched(self, row: Series):
        '''连接是否和一行匹配'''

        # 四项必须匹配
        if pd.isna(row["备注"]):
            row["备注"] = ""
        
        if (self.order == row["序号"]
              and self.lineType == row["线缆类型"]
              and self.specification == row["规格"]
              and (self.note == row["备注"])
              ):
            
            # 起止点匹配
            if (self.startPos == row["起点"]
              and self.endPos == row["终点"]):
                return True
            elif ("请填写" in self.startPos
                  or "请填写" in self.endPos):
                return True
            
        return False

    def readRowArgs(self, row: Series):
        '''读取一行的参数， 如果找到匹配行，立即填写，否则什么也不做'''
        if not self.isRowMatched(row):
            return
        
        # 如果找到匹配行，参照匹配行填写
        self.crossingCabinet = row["跨越机柜"] if not pd.isna(row["跨越机柜"]) else 0
        self.crossingRow = row["跨越行"] if not pd.isna(row["跨越行"]) else 0
        self.crossingFloor = row["跨层"] if not pd.isna(row["跨层"]) else 0
        self.crossingRoom = row["同层跨房间"] if not pd.isna(row["同层跨房间"]) else 0
        
        # 读取ROW的值
        if "请填写" in self.startPos:
            self.startPos = row["起点"] if not pd.isna(row["起点"]) else "请填写起点"
        if "请填写" in self.endPos:
            self.endPos = row["终点"] if not pd.isna(row["终点"]) else "请填写终点"
            
        self.isReferrenced = True # 参照标记
                   

