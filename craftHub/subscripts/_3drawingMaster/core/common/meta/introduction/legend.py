##########################################################################################################
#   Description: 绘图图例
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import ExistedBlock, CachedCopiedBlock
from .....subPath import PATH_TEMPLATE_DIR

from ezdxf.document import Drawing

class Legend(CachedCopiedBlock):
    '''绘图图例, 支持自定义名称'''
    DEFAULT_BLOCK_NAME = "Legend"
    BLOCK_NAME = "Legend"
    
    @classmethod
    def setBlockName(cls, name: str):
        cls.BLOCK_NAME = name
    
    def __init__(self, 
                 doc:Drawing) -> None:
        
        # 此图框尝试复制
        super().__init__(doc = doc,
                         blockName = self.BLOCK_NAME,
                         sourceDocPath = PATH_TEMPLATE_DIR / "legend.dxf",
                         sourceBlockName = self.DEFAULT_BLOCK_NAME
                         )