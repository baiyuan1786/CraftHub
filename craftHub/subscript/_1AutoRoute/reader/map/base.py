##########################################################################################################
#   Description: 提供完整的图像处理器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from pathlib import Path
from .builder import MapedSubstations
from .hander import MapHander

class MapReader(MapHander, MapedSubstations):
    '''图像处理器， 输入图像完成邻接表初始化'''
    
    def __init__(self, imagePath: Path):
        MapHander.__init__(self, imagePath)
        positions = self.substationNodes()
        ocrResults = self.substationOCR()
        connections = self.connectionDet()
        MapedSubstations.__init__(self, positions, ocrResults, connections)
        