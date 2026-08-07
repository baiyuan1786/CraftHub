##########################################################################################################
#   Description: pdu连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import TextBox, NewBlock, CADColor
from ....common.graph import 现有设备, 本期占用机柜, 普通白色粗实线

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Dict, List, Tuple, Literal
    
class PDUConnectionPanel(TextBox):
    '''PDU连接面板图'''
    width = 50
    height = 12.7
    
    IN_INTERVAL_X = 4.5
    IN_INTERVAL_Y = 2.87
    
    LU_INTERVAL_X = 2.5
    LU_INTERVAL_Y = height / 2
    
    GROUND_LINE_POINT = Vec2(width / 2, 2.5) # 接地线插入点
    
    def __init__(self, 
                 doc:Drawing,
                 installPnum: str,
                 isNew: bool) -> None:
        """PDU连接面板图2初始化

        :param doc: 文档
        :param installPnum: 安装 / 所在P号
        :param isNew: 是否是新增的PDU
        """        
        
        # 文本框初始化
        super().__init__(doc = doc,
                         boxHeight = self.height,
                         boxWidth = self.width,
                         boxLine = 本期占用机柜() if isNew else 现有设备(),
                         textContent = f"{CADColor.colored(installPnum)} 新增直流PDU" if isNew else f"{installPnum} 利旧直流PDU",
                         textFontHeight = 3.2,
                         textStyle = "gedi",
                         )
        
        # 插入常规属性
        textList: List[Tuple[str, Vec2]] = [
            ("in", Vec2(self.IN_INTERVAL_X, self.height - self.IN_INTERVAL_Y)),   # 左侧
            ("A路", Vec2(self.LU_INTERVAL_X, self.LU_INTERVAL_Y)),
            ("out", Vec2(self.IN_INTERVAL_X, self.IN_INTERVAL_Y)),

            ("in", Vec2(self.width - self.IN_INTERVAL_X, self.height - self.IN_INTERVAL_Y)),   # 右侧
            ("A路", Vec2(self.width - self.LU_INTERVAL_X, self.LU_INTERVAL_Y)),
            ("out", Vec2(self.width - self.IN_INTERVAL_X, self.IN_INTERVAL_Y)),
        ]
        
        
        for content, ip in textList:
            self.addMtext(
                textContent = content.upper(),
                textFontHeight = 2.16,
                textWidth = 2.8,
                textColor = CADColor.toIndex("ByBlock"),
                textLineSpacingDistance = 1,
                insertPoint = ip,
                style = "gedi",
                attachment = 5  # 使用正中对齐
            )
            
    @classmethod
    def inPoint(cls, insertPoint: Vec2, direction: Literal["left", "right"]) -> Vec2: # type: ignore
        '''in口位置'''
        pass
    
    @classmethod
    def outPoint(cls, insertPoint: Vec2, direction: Literal["left", "right"])-> Vec2: # type: ignore
        '''out口位置'''

        pass

    def _addGL(self):
        """添加设备接地线"""
        
        # 一根竖线三根横线组成
        basePoint = self.GROUND_LINE_POINT
        self.addLine(startPoint = basePoint, endPoint = basePoint - Vec2(0, 6), line = 普通白色粗实线())
        basePoint -= Vec2(0, 6)
        self.addLine(startPoint = basePoint - Vec2(2.7, 0), endPoint = basePoint + Vec2(2.7, 0), line = 普通白色粗实线())
        basePoint -= Vec2(0, 1)
        self.addLine(startPoint = basePoint - Vec2(2.1, 0), endPoint = basePoint + Vec2(2.1, 0), line = 普通白色粗实线())
        basePoint -= Vec2(0, 1)
        self.addLine(startPoint = basePoint - Vec2(1.3, 0), endPoint = basePoint + Vec2(1.3, 0), line = 普通白色粗实线())