##########################################################################################################
#   Description: 标题
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .link import LinkBase
import numpy as np
from pandas import DataFrame

class EmptyLink(LinkBase):
    '''空的链接'''
    
    def __init__(self) -> None:
        super().__init__()
    
    def toDF(self):
        '''转换DataFrame'''
        return DataFrame({
                "站名": np.nan,
                "序号": np.nan,
                "线缆类型": np.nan,
                "规格": np.nan,
                "起点": np.nan,
                "终点": np.nan,
                "单条长度/m": np.nan,
                "数量/条": np.nan,
                "合计/米": np.nan,
                "备注": np.nan,
                "走线": np.nan,
                "跨越机柜": np.nan,
                "跨越行": np.nan,
                "跨层": np.nan,
                "同层跨房间": np.nan,
            }, index=[0])
        
class Title(LinkBase):
    '''全站首行'''
    def __init__(self) -> None:
        super().__init__()
    
    def toDF(self):
        '''转换DataFrame'''
        return DataFrame({
                "站名": "站名",
                "序号": "序号",
                "线缆类型": "线缆类型",
                "规格": "规格",
                "起点": "起点",
                "终点": "终点",
                "单条长度/m": "单条长度/m",
                "数量/条": "数量/条",
                "合计/米": "合计/米",
                "备注": "备注",
                "走线": "走线",
                "跨越机柜": "跨越机柜",
                "跨越行": "跨越行",
                "跨层": "跨层",
                "同层跨房间": "同层跨房间",
                "参照": "参照",
                "完整线缆类型": "完整线缆类型"
            }, index=[0])
    
class SubTitle(LinkBase):
    '''单站首行'''
    def __init__(self, substationName: str) -> None:
        super().__init__()
        self.substationName = substationName
    
    
    def toDF(self):
        '''转换DataFrame'''
        return DataFrame({
                "站名": self.substationName,
                "序号": "序号",
                "线缆类型": "线缆类型",
                "规格": "规格",
                "起点": "起点",
                "终点": "终点",
                "单条长度/m": "单条长度/m",
                "数量/条": "数量/条",
                "合计/米": "合计/米",
                "备注": "备注",
                "走线": "走线",
                "跨越机柜": "跨越机柜",
                "跨越行": "跨越行",
                "跨层": "跨层",
                "同层跨房间": "同层跨房间",
                "参照": "参照",
                "完整线缆类型": "完整线缆类型"
            }, index=[0])