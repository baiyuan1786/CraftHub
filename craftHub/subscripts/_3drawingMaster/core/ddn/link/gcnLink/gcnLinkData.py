##########################################################################################################
#   Description: GCN网连接数据读取器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import List, Optional

from ....common.reader import ParseUnit
from ...reader import DataUnitDDN
from .gcnData import EdgedIDFData, GCNDeviceData, GCNLinkItemData


class GCNLinkData:
    '''GCN网连接数据读取器'''

    DATA_KEY_GCN_PNUM = "GCNPnum"
    DATA_KEY_GCN_PNAME = "GCNPname"
    DATA_KEY_GCN_EXISTED_EDGED_IDF = "GCNexistedEdgedIDF"

    DATA_KEY_GCN_IS_EXPANSION = "GCNisExpansion"
    DATA_KEY_GCN_ETH_SLOT_LIST = "GCNETHslotList"
    DATA_KEY_GCN_NEW_ETH_SLOT_EDGED_IDF = "GCNnewETHslotEdgedIDF"
    DATA_KEY_GCN_TARGET_STATION_LIST = "GCNTargetStationList"
    DATA_KEY_GCN_LINK_BOARD_LIST = "GCNLinkBoardList"
    DATA_KEY_GCN_BOARD_NAME = "GCNBoardName"
    DATA_KEY_GCN_AREA_NAME = "GCNareaName"
    DATA_KEY_GCN_SLOT_LIST = "GCNSlotList"

    DATA_KEY_DDN_INSTALL_PNUM = "DDNInstallPnum"
    DATA_KEY_EDGED_IDF_ALTITUDE_U = "edgedIDFaltitudeU"

    DATA_KEY_RTCD_DEV_NUM_LIST = "rtcdDevNumList"

    TAG_REUSED_EDGED_IDF = "e"

    NEW_EDGED_IDF_DEV_NAME = "本期新增成端IDF"
    REUSED_EDGED_IDF_DEV_NAME = "利旧成端IDF"

    def __init__(self, data: DataUnitDDN) -> None:
        """初始化GCN网连接数据读取器

        :param data: ddn数据单元
        """

        self.data = data

        self.deviceData = self._buildDeviceData()
        self.edgedIDFData = self._buildEdgedIDFData()

    def _buildDeviceData(self) -> GCNDeviceData:
        '''构建保底通信网传输设备数据'''

        return GCNDeviceData(
            pNum=self.data.get(self.DATA_KEY_GCN_PNUM),
            pName=self.data.get(self.DATA_KEY_GCN_PNAME),
            boardName=self.data.get(self.DATA_KEY_GCN_BOARD_NAME),
            areaName=self.data.get(self.DATA_KEY_GCN_AREA_NAME),

            existedEdgedIDF=self.data.get(self.DATA_KEY_GCN_EXISTED_EDGED_IDF),

            targetStationList=self.data.get(self.DATA_KEY_GCN_TARGET_STATION_LIST),
            linkBoardList=self.data.get(self.DATA_KEY_GCN_LINK_BOARD_LIST),
            slotNumList=self.data.get(self.DATA_KEY_GCN_SLOT_LIST),

            isExpansion=self.data.get(self.DATA_KEY_GCN_IS_EXPANSION),
            ethSlotRawList=self.data.get(self.DATA_KEY_GCN_ETH_SLOT_LIST),
            newETHslotEdgedIDF=self.data.get(self.DATA_KEY_GCN_NEW_ETH_SLOT_EDGED_IDF)
        )

    def _buildEdgedIDFData(self) -> Optional[EdgedIDFData]:
        '''构建成端IDF数据'''

        reusedEdgedIDFData = self._buildReusedEdgedIDFData()
        newEdgedIDFData = self._buildNewEdgedIDFData()

        if reusedEdgedIDFData is not None and newEdgedIDFData is not None:
            raise ValueError("不能同时设置利旧成端IDF和本期新增成端IDF")

        if reusedEdgedIDFData is not None:
            return reusedEdgedIDFData

        if newEdgedIDFData is not None:
            return newEdgedIDFData

        return None

    def _buildReusedEdgedIDFData(self) -> Optional[EdgedIDFData]:
        '''构建利旧成端IDF数据'''

        rtcdDevNumList = self.data.get(self.DATA_KEY_RTCD_DEV_NUM_LIST)

        if not rtcdDevNumList:
            return None

        if not isinstance(rtcdDevNumList, list):
            raise TypeError(
                f"{self.DATA_KEY_RTCD_DEV_NUM_LIST}期望为list类型，"
                f"当前类型为{type(rtcdDevNumList)}"
            )

        if len(rtcdDevNumList) == 0:
            return None

        firstDevNum = rtcdDevNumList[0]

        if firstDevNum is None:
            return None

        firstDevNumParsed = ParseUnit(str(firstDevNum))

        if not firstDevNumParsed.isMatched(self.TAG_REUSED_EDGED_IDF):
            return None

        return EdgedIDFData(
            devNum=firstDevNumParsed.value,
            devName=self.REUSED_EDGED_IDF_DEV_NAME,
            altitudeU=None,
            isNew=False
        )

    def _buildNewEdgedIDFData(self) -> Optional[EdgedIDFData]:
        '''构建本期新增成端IDF数据'''

        edgedIDFAltitudeU = self.data.get(self.DATA_KEY_EDGED_IDF_ALTITUDE_U)

        if edgedIDFAltitudeU is None:
            return None

        ddnInstallPnum = self.data.get(self.DATA_KEY_DDN_INSTALL_PNUM)

        if ddnInstallPnum is None:
            raise ValueError("存在本期新增成端IDF需求，但未找到DDNInstallPnum")

        return EdgedIDFData(
            devNum=ddnInstallPnum,
            devName=self.NEW_EDGED_IDF_DEV_NAME,
            altitudeU=edgedIDFAltitudeU,
            isNew=True
        )

    def getSlotNumList(self) -> List[int]:
        '''获取GCN网传输设备槽位号列表'''

        return self.deviceData.slotNumList

    def getLinkBoardList(self) -> List[str]:
        '''获取GCN网连接电口列表'''

        return self.deviceData.linkBoardList

    def getDeviceData(self) -> GCNDeviceData:
        '''获取GCN网传输设备数据'''

        return self.deviceData

    def getEdgedIDF(self) -> Optional[EdgedIDFData]:
        '''获取成端IDF数据'''

        return self.edgedIDFData

    def hasEdgedIDF(self) -> bool:
        '''判断是否存在成端IDF'''

        return self.edgedIDFData is not None

    def iterIDFUnit(self):
        '''遍历IDF跳接单元'''

        return self.deviceData.iterIDFUnit()

    def iterLinkItem(self):
        '''遍历GCN网出局链路'''

        return self.deviceData.iterLinkItem()

    def getIDFUnitList(self) -> List[str]:
        '''获取已有GCN设备成端IDF列表'''

        if not self.deviceData.hasExistedEdgedIDF():
            return []

        return [self.deviceData.existedEdgedIDF] # type: ignore

    def getLinkItemDataList(self) -> List[GCNLinkItemData]:
        '''获取GCN网出局链路数据列表'''

        return self.deviceData.linkItemDataList

    def hasIDFUnit(self) -> bool:
        '''判断是否存在IDF跳接单元'''

        return self.deviceData.hasIDFUnit()
    
    def isExpansion(self) -> bool:
        '''判断是否为保底网扩容'''

        return self.deviceData.isExpansion

    def getExistedEdgedIDF(self) -> str:
        '''获取已有GCN设备成端IDF'''

        return self.deviceData.existedEdgedIDF # type: ignore

    def getNewETHslotEdgedIDF(self) -> str:
        '''获取新增以太网板卡成端IDF'''

        return self.deviceData.newETHslotEdgedIDF # type: ignore