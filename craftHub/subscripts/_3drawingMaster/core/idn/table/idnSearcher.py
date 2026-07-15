##########################################################################################################
#   Description: IDN层级搜索器，表格导出用
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...common.reader.dataUnit import DataUnit
from typing import List

class IDNSearcher:
    '''IDN搜索器'''
    def __init__(self, dataUnitFullList: List[DataUnit]) -> None:
        self.dataUnitFullList = dataUnitFullList
    
    def searchLayer(self, substationName: str):
        """搜索某个站的层级

        :param substationName: 搜索站名
        """    
        
        # 从满表中搜索
        for data in self.dataUnitFullList:
            if data.get("substationName") == substationName:
                return data.get("layer")
            
        # 使用默认逻辑查找
        else:
            if "备调" in substationName or "地调" in substationName:
                return "核心层"
            elif substationName.startswith("110kV") or substationName.startswith("35kV") or substationName.startswith("10kV"):
                return "接入层"
            elif substationName.startswith("220kV") or substationName.startswith("500kV"):
                return "汇聚层"

        return None
    
    def searchName(self, substationSubName: str):
        """搜索站完整名称

        :param substationSubName: 站部分名称
        """        
        
        for data in self.dataUnitFullList:
            if (substationSubName + "变") in data.get("substationName"):
                return data.get("substationName")
            
        return substationSubName
    
    def search(self, substationName: str, valueName: str):
        """搜索某个站的某个值

        :param substationName: 搜索站名
        """    
        # 从满表中搜索
        for data in self.dataUnitFullList:
            if data.get("substationName") == substationName:
                return data.get(valueName)
            
        return None