##########################################################################################################
#   Description: 新增设备
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....graph import CADColor
from ..base import Device
from ezdxf.document import Drawing

class NewPDU(Device):
    '''新增PDU'''
    def __init__(self, 
                 name: str, 
                 altitudeU: int) -> None:
        heightU = 3
        super().__init__(name, altitudeU, heightU, "new")

    def toDevicePanel(self, doc: Drawing):
        '''转换设备面板图'''
        raise Exception("PDU没有面板图")
    
class EdgedIDF(Device):
    '''成端使用的IDF'''
    def __init__(self, 
                 altitudeU: int) -> None:

        # name = "本期新增路由器成端IDF"
        name = "另外立项建设IDF"
        heightU = 1
        super().__init__(name, altitudeU, heightU, "nobuild")

    def toDevicePanel(self, doc: Drawing):
        '''转换设备面板图'''
        raise Exception("IDF没有面板图")