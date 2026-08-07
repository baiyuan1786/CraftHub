##########################################################################################################
#   Description: 屏柜图框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock
from ...graph.line import 灰色边框虚线
from .....subPath import PATH_TEMPLATE_DIR

from ezdxf.document import Drawing
from ezdxf.math import Vec2

class FrameCabinetA3plus(NewBlock):
    '''屏柜外框A3+, 该外框由A3框直接管理
    该外框为屏柜外的灰色外框'''

    WIDTH = 216.1274
    HEIGHT = 267.0965
    def __init__(self,
                 doc:Drawing) -> None:
        '''A3+图框'''

        # 此图框尝试复制
        super().__init__(doc = doc)
        
        points = [
            Vec2(0, 0),
            Vec2(self.WIDTH, 0),
            Vec2(self.WIDTH, self.HEIGHT),
            Vec2(0, self.HEIGHT),
            Vec2(0, 0)
        ]
        
        
        self.addPolyLine(points, 灰色边框虚线())
        
        
