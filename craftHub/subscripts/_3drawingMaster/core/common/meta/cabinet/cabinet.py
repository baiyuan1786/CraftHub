##########################################################################################################
#   Description: 绘图大师屏柜
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .cabinetPanel import CabinetPanel
from ..device import Device

from typing import Literal, List
from ezdxf.document import Drawing

class Cabinet:
    '''屏柜类实体，如果一个屏柜被使用，则使用本类描述'''
    def __init__(self,
                 pNum: str,
                 name: str, 
                 height: int = 220,
                 width: int = 60,
                 depth: Literal[60, 80] = 60,
                 cabinetType: Literal["新增", "占用"] = "新增"
                 ) -> None:
        """屏柜初始化

        :param pNum:    P号, 例如1P
        :param name:    屏柜名, 例如路由器1屏
        :param height:  高, cm
        :param width:   宽, cm
        :param depth:   深, cm
        :param cabinetType: 屏柜类型，影响平面图绘图线型
        """
        
        self.pNum = pNum
        self.name = name
        self.height = height
        self.width = width
        self.depth = int(depth)
        self.cabinetType = cabinetType
        self.deviceList: List[Device] = [] # 设备实体列表

    def toPanel(self, doc:Drawing):
        '''转换面板图'''
        cabinetPanel = CabinetPanel(
            doc = doc,
            pNum = self.pNum,
            name = self.name,
            height = self.height,
            width = self.width,
            isNew = (self.cabinetType == "新增")
        )
        
        # 插入设备面板图
        for device in self.deviceList:
            cabinetPanel.addDevice(device.toDeviceInCabinet(doc = doc))
        
        return cabinetPanel

    def addDevice(self, device: Device):
        """插入设备实体到屏柜中

        :param device: 设备实体
        """        

        assert isinstance(device, Device)
        self.deviceList.append(device)