##########################################################################################################
#   Description: 线型管理器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog

from .lineType.complex import SMLine, UTPLine, DYLine
from .lineType.simple import DASH, DASHDOT, Continuous
from .lineType.base import LineType

from typing import List
from ezdxf.document import Drawing
from functools import wraps

class LineTypeMnger:
    '''线型管理器'''
    def __init__(self):
        self.lineTypeList: List[LineType] = []
        self.lineTypeList.append(DASH())
        self.lineTypeList.append(DASHDOT())
        self.lineTypeList.append(SMLine())
        self.lineTypeList.append(UTPLine())
        self.lineTypeList.append(DYLine())
        self.lineTypeList.append(Continuous())
        
        self.nameList: List[str] = [lt.name for lt in self.lineTypeList]
        
        GLog.logInfo(f"线型管理器获取到 \'{len(self.lineTypeList)}\' 种线型")
        
    def addToDoc(self, doc: Drawing):
        '''添加所有线型至文件
        注意每个文件都必须添加一次'''

        for lt in self.lineTypeList:
            lt.addToDoc(doc)