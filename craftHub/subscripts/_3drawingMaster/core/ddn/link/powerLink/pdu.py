##########################################################################################################
#   Description: pdu连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.graph import TextBox, NewBlock, CADColor
from ....common.graph import 现有设备, 本期占用机柜

from ezdxf.document import Drawing
from ezdxf.math import Vec2
    
class PDUConnectionPanel(TextBox):
    '''PDU连接面板图'''
    width = 50.0591
    height = 19.72
    
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
        textContentList = ["in", "A路", "out", "in", "B路", "out"]
        textInsertList = [Vec2(4.45, 16.4), Vec2(2.91, 9.8), Vec2(4.45, 2.75), 
                          Vec2(4.45 + 40.58, 16.4), Vec2(2.91 + 44.11, 9.8), Vec2(4.45 + 40.58, 2.75)]
        
        for content, ip in zip(textContentList, textInsertList):
            self.addMtext(
                textContent = content.upper(),
                textFontHeight = 2.16,
                textWidth = 2.8,
                textColor = CADColor.toIndex("ByBlock"),
                textLineSpacingDistance = 1,
                insertPoint = ip,
                style = "gedi",
            )

    @classmethod
    def inPoint(cls, powerPoint: Vec2, insertPoint: Vec2):
        '''in口位置'''
        return powerPoint + Vec2(0, (insertPoint - powerPoint).y + cls.height - 1.47)
    
    @classmethod
    def outPoint(cls, powerPoint: Vec2, insertPoint: Vec2):
        '''out口位置'''

        return powerPoint + Vec2(0, (insertPoint - powerPoint).y + 1.47)