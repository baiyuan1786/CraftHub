##########################################################################################################
#   Description: 派生块
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .block import CustomBlock
from ezdxf.document import Drawing
from typing import Optional


class NewBlock(CustomBlock):
    '''只允许创建新块'''

    def __init__(
            self,
            doc: Drawing,
            blockName: Optional[str] = None
    ) -> None:
        """创建新块

        :param doc: 文档
        :param blockName: 块名，设置为None表示自动命名
        """

        super().__init__(
            doc=doc,
            blockName=blockName,
            allowExisted=False,
            allowCreate=True
        )
        
class ExistedBlock(CustomBlock):
    '''只允许调用已存在块'''

    def __init__(
            self,
            doc: Drawing,
            blockName: str
    ) -> None:
        """调用已存在块

        :param doc: 文档
        :param blockName: 已存在块名
        """

        super().__init__(
            doc=doc,
            blockName=blockName,
            allowExisted=True,
            allowCreate=False
        )