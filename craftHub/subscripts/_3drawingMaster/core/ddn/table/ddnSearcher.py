##########################################################################################################
#   Description: DDN层级搜索器，表格导出用
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import List, Optional, Any

from ...common.reader.dataUnit import DataUnit


class DDNSearcher:
    '''DDN搜索器'''

    KEY_SUBSTATION_NAME = "substationName"
    KEY_LAYER = "layer"

    CORE_LAYER = "核心层"
    ACCESS_LAYER = "接入层"
    AGGREGATION_LAYER = "汇聚层"

    CORE_KEYWORD_LIST = ["备调", "地调"]
    ACCESS_PREFIX_LIST = ["110kV", "35kV", "10kV"]
    AGGREGATION_PREFIX_LIST = ["220kV", "500kV"]

    STATION_SUFFIX = "变"

    def __init__(self, dataUnitFullList: List[DataUnit]) -> None:
        self.dataUnitFullList = dataUnitFullList

    def searchLayer(self, substationName: str) -> Optional[str]:
        """搜索某个站的层级

        :param substationName: 搜索站名
        """

        layer = self.search(substationName, self.KEY_LAYER)

        if layer is not None:
            return layer

        return self._inferLayer(substationName)

    def searchName(self, substationSubName: str) -> str:
        """搜索站完整名称

        :param substationSubName: 站部分名称
        """

        for data in self.dataUnitFullList:
            substationName = data.get(self.KEY_SUBSTATION_NAME)

            if (substationSubName + self.STATION_SUFFIX) in substationName:
                return substationName

        return substationSubName

    def search(self, substationName: str, valueName: str) -> Optional[Any]:
        """搜索某个站的某个值

        :param substationName: 搜索站名
        :param valueName:      搜索字段名
        """

        for data in self.dataUnitFullList:
            if data.get(self.KEY_SUBSTATION_NAME) == substationName:
                return data.get(valueName)

        return None

    def _inferLayer(self, substationName: str) -> Optional[str]:
        '''根据站名推断层级'''

        if any(keyword in substationName for keyword in self.CORE_KEYWORD_LIST):
            return self.CORE_LAYER

        if any(substationName.startswith(prefix) for prefix in self.ACCESS_PREFIX_LIST):
            return self.ACCESS_LAYER

        if any(substationName.startswith(prefix) for prefix in self.AGGREGATION_PREFIX_LIST):
            return self.AGGREGATION_LAYER

        return None