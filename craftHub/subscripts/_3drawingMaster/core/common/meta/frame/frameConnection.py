##########################################################################################################
#   Description: 连接图虚线外框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import 灰色边框虚线, NewBlock
from .....subPath import PATH_TEMPLATE_DIR

from ezdxf.document import Drawing
from ezdxf.math import Vec2

class FrameConnection(NewBlock):
    '''连接图虚线外框， 该外框为连接图外的灰色虚线外框'''
    def __init__(self,
                 doc:Drawing) -> None:

        super().__init__(doc = doc)
        
        points = [
            Vec2(0, 0),
            Vec2(224.3, 0),
            Vec2(224.3, 40.6),
            Vec2(224.3 + 180.4, 40.6),
            Vec2(224.3 + 180.4, 40.6 + 242.8),
            Vec2(0, 40.6 + 242.8),
            Vec2(0, 0),
        ]
        
        self.addPolyLine(points, 灰色边框虚线())
        