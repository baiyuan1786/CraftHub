##########################################################################################################
#   Description: A3+图纸说明, 右下角的那个小说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock, CADColor
from ezdxf.document import Drawing
from ezdxf.math import Vec2

from .....subPath import PATH_TEMPLATE_DIR

class A3plusIntroduction(NewBlock):
    '''A3+图纸说明, 右下角的那个小说明'''
    def __init__(self, 
                 doc:Drawing) -> None:
        
        # 不使用复制块了
        super().__init__(doc)

        textContent = "说明:\n"
        textContent += "1. 本站新增设备具体面板安装如图所示,设备安装高度可根据现场施工调整。\n"
        textContent += "2. 各设备接地线由设备供应商提供。新增带电设备需可靠接地,经机房接地条连接至接地网。\n"
        textContent += "3. 具体线缆敷设以现场施工为准；具体使用端口号以调度中心批复为准。"

        self.addMtext(
            textContent = textContent,
            textFontHeight = 4,
            textWidth = 140,
            textColor = CADColor.toIndex("白色"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(0, 0),
            style = "GEDITXT",
            attachment = 7
        )