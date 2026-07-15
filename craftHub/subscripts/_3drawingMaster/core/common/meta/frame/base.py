##########################################################################################################
#   Description: 绘图图框
#                包括A3+, A3++等图框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from pathlib import Path

from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace

from ...graph import NewBlock, CustomBlock, CachedCopiedBlock
from .....subPath import PATH_TEMPLATE_DIR
from .attribute import Attribute

from ezdxf.document import Drawing
from ezdxf.enums import TextEntityAlignment
from ezdxf.entities.insert import Insert
from ezdxf.math import Vec2

from typing import Dict, Any, List, Optional
from typing import Any, List, Optional

class FrameBase(CachedCopiedBlock):
    '''图框基类'''
    def __init__(self, 
                 doc: Drawing, 
                 blockName: str,
                 sourceDocPath: Path,
                 sourceBlockName: str, 
                 attrList: Optional[List[Attribute]] = None) -> None:

        # 调用已有块, 如果不存在则复制
        super().__init__(doc, blockName, sourceDocPath, sourceBlockName)
        self.attrList = [] if attrList is None else attrList
        
        self.insertBlockList: List[CustomBlock] = []
        self.insertBlockIPList: List[Vec2] = []

    def grid(self, insertBlock: CustomBlock, insertPoint: Vec2):
        """以网格形式部署在图框中
        该部署并非插入图框中，而是随着图框一起插入最上级

        :param insertBlock: 插入块
        :param insertPoint: 块插入点
        """        

        assert isinstance(insertBlock, CustomBlock)
        assert isinstance(insertPoint, Vec2)
        
        self.insertBlockList.append(insertBlock)
        self.insertBlockIPList.append(insertPoint)

