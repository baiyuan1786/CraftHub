##########################################################################################################
#   Description: A3+图框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .....subPath import PATH_TEMPLATE_DIR
from .base import FrameBase, Attribute
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.document import Drawing
from ezdxf.math import Vec2
from typing import Dict, Any, List, Optional

class FrameA3plusplus(FrameBase):
    '''A3++图框'''
    count = 0
    DEFAULT_FRAME_NAME = "GEDI_A3++"    # 默认图框名
    FRAME_NAME = DEFAULT_FRAME_NAME             # 定义图框名
    
    @classmethod
    def setFrameName(cls, newName: str):
        assert isinstance(newName, str), f"新图框名不是字符串"
        cls.FRAME_NAME = newName
    
    def __init__(self, 
                 doc:Drawing,
                 APPROVE: str = "批准人",
                 APPROVENUM: str = "批准人号",
                 
                 REVIEW1: str = "审核人",
                 REVIEW1NUM: str = "审核人号",
                 
                 CHECK: str = "校核人",
                 CHECKNUM: str = "校核人号",
                 
                 DESIGN: str = "主设人",
                 DESIGNNUM: str = "主设人号",
                 
                 DRAW: str = "制图人",
                 DRAWNUM: str = "制图人号",
                 
                 DATE: str = "2026.5",
                 PROJECTNAME: str = "项目名",
                 PHASE: str = "施工图",
                 DRAWINGNAME: str = "绘图号",
                 DRAWINGNUMBER: str = "ABCD-000-000",
                 VERSION: str = "A"
                 ) -> None:
        
        # 增强属性列表
        attrList: List[Attribute] = [
            Attribute("APPROVE", APPROVE, 3.5, 0.8),
            Attribute("APPROVENUM", APPROVENUM, 3.5, 0.8),
            Attribute("REVIEW1", REVIEW1, 3.5, 0.8),
            Attribute("REVIEW1NUM", REVIEW1NUM, 3.5, 0.8),
            Attribute("CHECK", CHECK, 3.5, 0.8),
            Attribute("CHECKNUM", CHECKNUM, 3.5, 0.8),
            Attribute("DESIGN", DESIGN, 3.5, 0.8),
            Attribute("DESIGNNUM", DESIGNNUM, 3.5, 0.8),
            Attribute("DRAW", DRAW, 3.5, 0.8),
            Attribute("DRAWNUM", DRAWNUM, 3.5, 0.8),
            
            Attribute("DATE", DATE, 3.5, 0.8),
            Attribute("PHASE", PHASE, 4, 0.8, 1, offset = Vec2(0, 0)),
            Attribute("DRAWINGNAME", DRAWINGNAME, 3.5, 0.85, 1, "TK", offset = Vec2(0, 0)), # 此属性特别指定为TK
            Attribute("DRAWINGNUMBER", DRAWINGNUMBER, 4, 0.8),
            Attribute("VERSION", VERSION, 3.5, 0.8),            
        ]

        # 文字过长处理
        if len(PROJECTNAME) > 37:
            attrList.append(Attribute("PROJECTNAME", PROJECTNAME, 2.6, 0.65, 2, offset = Vec2(33, 0)))
        else:
            attrList.append(Attribute("PROJECTNAME", PROJECTNAME, 2.8, 0.65, 2, offset = Vec2(33, 0)))
        

        super().__init__(doc = doc,
                         blockName = self.FRAME_NAME,
                         sourceDocPath = PATH_TEMPLATE_DIR / "frame.dxf",
                         sourceBlockName = self.DEFAULT_FRAME_NAME,
                         attrList = attrList)
        FrameA3plusplus.count += 1
    
    @staticmethod
    def legendPoint(t: int = 1):
        '''图例点'''
        if t == 1:
            return Vec2(787.6417, 120.9943)
        else:
            return Vec2(787.6417, 183) # 右上角
    
    @staticmethod
    def connectionPoint(t: int = 1):
        '''连接图点'''
        if t == 1:
            return Vec2(460, 146)
        else:
            return Vec2(469, 101)

    @staticmethod
    def frameConnectionPoint():
        '''连接图外框点'''

        return Vec2(430, 6.5)
    
    @staticmethod
    def introductionPoint(t: int = 1):
        '''主要介绍点(左下角)/次要介绍点(右下角)'''
        if t == 1:
            # 主要介绍点
            return Vec2(34.38, 10)
        else:
            # 次要介绍点
            return Vec2(507, 7.5)
    
    @staticmethod
    def planePoint():
        '''平面图点'''
        return Vec2(155, 137)
    
    @staticmethod
    def netWorkLinkIntroPoint(t: int = 1):
        '''组网链路需求表文字插入点'''
        if t == 1:
            return Vec2(721, 273)
        else:
            return Vec2(543, 44.4)
    
    @staticmethod
    def cableLayIntroPoint(t: int = 1):
        '''线缆敷设表文字插入点1'''
        if t == 1:
            return Vec2(306, 122)
        else:
            return Vec2(310, 106)
        
    @staticmethod
    def connectionIntroPoint(t: int = 1):
        '''设备连接图文字插入点'''
        if t == 1:
            return Vec2(569.7, 22.69)
        else:
            return Vec2(569.7, 22.69)
        
    @staticmethod
    def GCNpanelPoint():
        '''GCN面板图插入点'''
        return Vec2(517.2, 49.5)
        
    @staticmethod
    def cabinetPoint():
        '''屏柜插入点'''
        return Vec2(107, 31.5)
    
    @staticmethod
    def newDevicePanelPoint():
        '''设备面板图插入点'''
        return Vec2(265, 11.4)
    
    @staticmethod
    def frameCabinetPoint():
        '''屏柜外框插入点'''
        return Vec2(32.7, 11.4)
        
    def insertInto(self, layout: BlockLayout | Modelspace | Any, insertPoint: Vec2 | None = None):
        
        if insertPoint is None:
            insertPoint = Vec2(0, 0)
        
        # 插入图框并设置增强属性
        frameInsert = super().insertInto(layout, insertPoint)
        
        for a in self.attrList:
            a.add_attrib_autoLocate(insert = frameInsert)
            
        # 将存储的块插入上级
        for b, ip in zip(self.insertBlockList, self.insertBlockIPList):
            b.insertInto(layout, insertPoint + ip)
        
        return frameInsert
        