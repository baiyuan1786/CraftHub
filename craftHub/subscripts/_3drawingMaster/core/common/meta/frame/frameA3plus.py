##########################################################################################################
#   Description: A3+图框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .base import FrameBase, Attribute
from .....subPath import PATH_TEMPLATE_DIR

from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.document import Drawing
from ezdxf.math import Vec2
from typing import Dict, Any, List, Optional

class FrameA3plus(FrameBase):
    '''A3+图框'''
    count = 0
    DEFAULT_FRAME_NAME = "GEDI_A3+"    # 默认图框名
    FRAME_NAME = DEFAULT_FRAME_NAME            # 定义图框名
    
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
                 DATE: str = "2026.2",
                 PROJECTNAME: str = "项目名",
                 PHASE: str = "施工图",
                 DRAWINGNAME: str = "绘图号",
                 DRAWINGNUMBER: str = "ABCD-000-000",
                 VERSION: str = "A",
                 ) -> None:
        '''A3+图框'''

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
            Attribute("DRAWINGNAME", DRAWINGNAME, 4.75, 0.8, 1, offset = Vec2(0, 0)),
            Attribute("DRAWINGNUMBER", DRAWINGNUMBER, 4, 0.8),
            Attribute("VERSION", VERSION, 3.5, 0.8),            
        ]

        # 文字过长处理
        if len(PROJECTNAME) > 37:
            attrList.append(Attribute("PROJECTNAME", PROJECTNAME, 2.4, 0.7, 1, offset = Vec2(0, 0)))
        else:
            attrList.append(Attribute("PROJECTNAME", PROJECTNAME, 2.8, 0.7, 1, offset = Vec2(0, 0)))

        super().__init__(doc = doc,
                         blockName = self.FRAME_NAME,
                         sourceDocPath = PATH_TEMPLATE_DIR / "frame.dxf",
                         sourceBlockName = self.DEFAULT_FRAME_NAME,
                         attrList = attrList)
        FrameA3plus.count += 1

    @staticmethod
    def legendPoint():
        '''图例点'''
        return Vec2(581.4463, 194.8077)
    
    @staticmethod
    def introductionPoint():
        '''介绍点(右下角)'''
        return Vec2(458.1526, 47.5593)
    
    @staticmethod
    def cabinetPoint():
        '''屏柜插入点'''
        return Vec2(133.13, 40.6)
    
    @staticmethod
    def newDevicePanelPoint():
        '''设备面板图插入点'''
        return Vec2(304.8596, 14.54)
    
    @staticmethod
    def frameCabinetPoint():
        '''屏柜外框插入点'''
        return Vec2(58.7598, 11.4225)
        
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