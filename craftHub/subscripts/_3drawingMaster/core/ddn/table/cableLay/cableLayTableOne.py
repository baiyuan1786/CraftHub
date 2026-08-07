##########################################################################################################
#   Description: 地区ddn单站线缆敷设表
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Dict, List, Optional

import pandas as pd
from pandas import DataFrame

from ....common.meta import ExistedDevice
from ....common.reader import DataUnit, ParseUnit

from .link import (
    Link,
    SubTitle,
    接地线,
    机柜接地线,
    普通网线,
    直流电源线_原厂配套,
    直流电源线_阻燃导线,
    光速寻线以太网线缆
)

class CableLayTableOne:
    '''单个站的线缆敷设表'''

    DATA_KEY_SUBSTATION_NAME = "substationName"
    DATA_KEY_WALK_LINE = "walkLine"

    DATA_KEY_DDN_INSTALL_PNUM = "DDNInstallPnum"
    DATA_KEY_DDN_IS_NEW_PDU = "DDNisNewPDU"
    DATA_KEY_DDN_IS_USE_PDU = "DDNisUsePDU"
    DATA_KEY_CABINET_TYPE = "cabinetType"

    DATA_KEY_POWER_CABINET_PNUM1 = "powerCabinetPnum1"
    DATA_KEY_POWER_CABINET_PNAME1 = "powerCabinetPname1"
    DATA_KEY_POWER_CABINET_TK_A1 = "powerCabinetTkA1"
    DATA_KEY_POWER_CABINET_PNUM2 = "powerCabinetPnum2"
    DATA_KEY_POWER_CABINET_PNAME2 = "powerCabinetPname2"
    DATA_KEY_POWER_CABINET_TK_A2 = "powerCabinetTkA2"

    DATA_KEY_PANEL_DEVICE_NAME_LIST = "panelDeviceNameList"
    DATA_KEY_PANEL_DEVICE_ALTITUDE_U_LIST = "panelDeviceAltitudeUList"
    DATA_KEY_PANEL_DEVICE_HEIGHT_U_LIST = "panelDeviceHeightUList"

    DATA_KEY_EDGED_IDF_ALTITUDE_U = "edgedIDFaltitudeU"

    DATA_KEY_RTCD_DEV_NUM_LIST = "rtcdDevNumList"
    DATA_KEY_NRTCD_DEV_NUM_LIST = "nrtcdDevNumList"

    DATA_KEY_GCN_PNUM = "GCNPnum"
    DATA_KEY_GCN_PNAME = "GCNPname"
    DATA_KEY_GCN_EXISTED_EDGED_IDF = "GCNexistedEdgedIDF"
    DATA_KEY_GCN_NEW_ETH_SLOT_EDGED_IDF = "GCNnewETHslotEdgedIDF"
    DATA_KEY_GCN_TARGET_STATION_LIST = "GCNTargetStationList"
    DATA_KEY_GCN_SLOT_LIST = "GCNSlotList"
    DATA_KEY_GCN_ETH_SLOT_LIST = "GCNETHslotList"
    DATA_KEY_GCN_IS_EXPANSION = "GCNisExpansion"

    CABINET_TYPE_NEW = "新增"

    ROUTER_DEV_NAME = "新增低端路由器"
    NEW_PDU_DEV_NAME = "新增直流PDU"
    EXISTED_PDU_A_NAME = "本屏现有PDU A路"
    EXISTED_PDU_B_NAME = "本屏现有PDU B路"
    IDF_DEV_NAME = "IDF配线单元"
    GCN_DEVICE_NAME = "保底网设备"

    POWER_MODULE_1 = "电源模块1"
    POWER_MODULE_2 = "电源模块2"
    POWER_MODULE = "电源模块"

    GROUND_BAR_NAME = "本机柜接地排"

    EDGED_IDF_CABLE_NUM = 16
    CRYPTO_CABLE_NUM = 2
    GCN_CABLE_NUM = 2

    MAX_LIGHT_LINE_NUM = 2
    MAX_PDU_LINE_NUM = 8

    TAG_JUMP = "j"
    TAG_EXISTED_EDGED_IDF = "e"
    TAG_GCN_SLOT_OCCUPIED = "o"
    TAG_GCN_SLOT_NEW = "n"

    NEW_EDGED_IDF_DEV_NAME = "新增路由器成端IDF"
    EXISTED_EDGED_IDF_DEV_NAME = "利旧成端IDF"
    
    CD_NUM = 2  # 加密设备连线数量

    def __init__(self, data: DataUnit) -> None:
        """初始化单站线缆敷设表

        :param data: 单站数据单元
        """

        self.substationName: str = data.get(self.DATA_KEY_SUBSTATION_NAME)
        self.walkLine = data.get(self.DATA_KEY_WALK_LINE)
        self.data = data
        self.room2 = data.get("room2Name")

        self.linkList: List[Link] = []
        self.lightLineUsedNum = 0
        self.PDULineUsedNum = 0

        self._buildPowerLink(data)
        self._buildOldDevPowerLink(data)
        self._buildGroundLink(data)
        self._buildEdgedIDFLink(data)
        self._buildCryptoLink(data)
        self._buildGCNLink(data)

    def newLink(self, link: Link):
        '''新增一条连接'''

        if isinstance(link, 直流电源线_原厂配套):
            self.PDULineUsedNum += 1

            if self.PDULineUsedNum > self.MAX_PDU_LINE_NUM:
                raise ValueError("使用了超过8根PDU出线！！")

        self.linkList.append(link)

    def _buildPowerLink(self, data: DataUnit):
        '''构建新增设备电源线连接'''

        installPnum = self._installPnum(data)

        if data.get(self.DATA_KEY_DDN_IS_NEW_PDU):
            self.newLink(
                直流电源线_阻燃导线(
                    startPos=f"{data.get(self.DATA_KEY_POWER_CABINET_PNUM1)} {data.get(self.DATA_KEY_POWER_CABINET_PNAME1)}",
                    endPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} A路",
                    current=data.get(self.DATA_KEY_POWER_CABINET_TK_A1)
                )
            )

            self.newLink(
                直流电源线_阻燃导线(
                    startPos=f"{data.get(self.DATA_KEY_POWER_CABINET_PNUM2)} {data.get(self.DATA_KEY_POWER_CABINET_PNAME2)}",
                    endPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} B路",
                    current=data.get(self.DATA_KEY_POWER_CABINET_TK_A2)
                )
            )

            self.newLink(
                直流电源线_原厂配套(
                    startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} A路",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_1}"
                )
            )

            self.newLink(
                直流电源线_原厂配套(
                    startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} B路",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_2}"
                )
            )

        elif data.get(self.DATA_KEY_DDN_IS_USE_PDU):
            self.newLink(
                直流电源线_原厂配套(
                    startPos=f"{installPnum} {self.EXISTED_PDU_A_NAME}",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_1}"
                )
            )

            self.newLink(
                直流电源线_原厂配套(
                    startPos=f"{installPnum} {self.EXISTED_PDU_B_NAME}",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_2}"
                )
            )

        else:
            self.newLink(
                直流电源线_阻燃导线(
                    startPos=f"{data.get(self.DATA_KEY_POWER_CABINET_PNUM1)} {data.get(self.DATA_KEY_POWER_CABINET_PNAME1)}",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_1}",
                    current=data.get(self.DATA_KEY_POWER_CABINET_TK_A1)
                )
            )

            self.newLink(
                直流电源线_阻燃导线(
                    startPos=f"{data.get(self.DATA_KEY_POWER_CABINET_PNUM2)} {data.get(self.DATA_KEY_POWER_CABINET_PNAME2)}",
                    endPos=f"{installPnum} {self.ROUTER_DEV_NAME} {self.POWER_MODULE_2}",
                    current=data.get(self.DATA_KEY_POWER_CABINET_TK_A2)
                )
            )

    def _buildOldDevPowerLink(self, data: DataUnit):
        '''构建旧设备与新增PDU的电源线连接'''

        panelDeviceNameList: List = data.get(self.DATA_KEY_PANEL_DEVICE_NAME_LIST)
        panelDeviceAltitudeUList: List = data.get(self.DATA_KEY_PANEL_DEVICE_ALTITUDE_U_LIST)
        panelDeviceHeightUList: List = data.get(self.DATA_KEY_PANEL_DEVICE_HEIGHT_U_LIST)

        oldDevList: List[ExistedDevice] = [
            ExistedDevice(name, altitude, height)
            for name, altitude, height in zip(
                panelDeviceNameList,
                panelDeviceAltitudeUList,
                panelDeviceHeightUList
            )
        ]

        if not oldDevList:
            return

        if not data.get(self.DATA_KEY_DDN_IS_NEW_PDU):
            return

        installPnum = self._installPnum(data)
        oldDevCPList = [
            dev
            for dev in oldDevList
            if dev.signType in ["CP1", "CP2", "CP8"]
        ]

        for oldDevCP in oldDevCPList:
            if oldDevCP.signType == "CP2":
                self.newLink(
                    直流电源线_阻燃导线(
                        startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} A路",
                        endPos=f"现有设备 {oldDevCP.name} {self.POWER_MODULE_1}",
                        current=oldDevCP.current
                    )
                )

                self.newLink(
                    直流电源线_阻燃导线(
                        startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} B路",
                        endPos=f"现有设备 {oldDevCP.name} {self.POWER_MODULE_2}",
                        current=oldDevCP.current
                    )
                )

            elif oldDevCP.signType == "CP1":
                self.newLink(
                    直流电源线_阻燃导线(
                        startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME}",
                        endPos=f"现有设备 {oldDevCP.name} {self.POWER_MODULE}",
                        current=oldDevCP.current
                    )
                )

            elif oldDevCP.signType == "CP8":
                self.newLink(
                    直流电源线_阻燃导线(
                        startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} A路",
                        endPos=f"现有设备 {oldDevCP.name} {self.POWER_MODULE_1}",
                        current=oldDevCP.current,
                        num=4
                    )
                )

                self.newLink(
                    直流电源线_阻燃导线(
                        startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME} B路",
                        endPos=f"现有设备 {oldDevCP.name} {self.POWER_MODULE_2}",
                        current=oldDevCP.current,
                        num=4
                    )
                )

    def _buildGroundLink(self, data: DataUnit):
        '''构建接地线连接'''

        installPnum = self._installPnum(data)

        if data.get(self.DATA_KEY_DDN_IS_NEW_PDU):
            self.newLink(
                接地线(
                    startPos=f"{installPnum} {self.NEW_PDU_DEV_NAME}",
                    endPos=self.GROUND_BAR_NAME
                )
            )

        self.newLink(
            接地线(
                startPos=f"{installPnum} {self.ROUTER_DEV_NAME}",
                endPos=self.GROUND_BAR_NAME
            )
        )

        if data.get(self.DATA_KEY_CABINET_TYPE) == self.CABINET_TYPE_NEW:
            self.newLink(
                机柜接地线(
                    startPos=f"{installPnum} 新增机柜",
                    endPos=self.GROUND_BAR_NAME
                )
            )

    def _buildEdgedIDFLink(self, data: DataUnit):
        '''构建新增路由器至成端IDF接线'''

        if not self._hasEdgedIDF(data):
            return

        if self._hasNewEdgedIDF(data):
            self.newLink(
                普通网线(
                    startPos=self._routerPos(data),
                    endPos=self._edgedIDFPos(data),
                    note="路由器电口成端(另外立项建设)",
                    num=self.EDGED_IDF_CABLE_NUM
                )
            )
        else:
            self.newLink(
                普通网线(
                    startPos=self._routerPos(data),
                    endPos=self._edgedIDFPos(data),
                    note="路由器电口成端(利旧)",
                    num=self.EDGED_IDF_CABLE_NUM
                )
            )

    def _buildCryptoLink(self, data: DataUnit):
        '''构建至纵向加密连接的新增网线'''

        # 只计算了IDF
        targetPos = self._firstCryptoIDFPos(data)
        if targetPos is None:
            targetPos = self._cryptoDevPos(data)  # 仅纵向加密

        if targetPos is None:
            return

        if data.get("rtcdDevPortList")[0] is not None and data.get("nrtcdDevPortList")[0] is not None:
            self._addNormalNetLinkIfDifferent(
                startPos=self._newCableStartPos(data),
                endPos=targetPos,
                note="至纵向加密认证装置(A平面实时), 其中一条作备用",
                num=self.CD_NUM
            )
            self._addNormalNetLinkIfDifferent(
                startPos=self._newCableStartPos(data),
                endPos=targetPos,
                note="至纵向加密认证装置(A平面非实时), 其中一条作备用",
                num=self.CD_NUM
            )
        elif data.get("rtcdDevPortList")[0] is not None:
            self._addNormalNetLinkIfDifferent(
                startPos=self._newCableStartPos(data),
                endPos=targetPos,
                note="至纵向加密认证装置(A平面实时和非实时), 其中一条作备用",
                num=self.CD_NUM
            )
        else:
            return

    def _buildGCNLink(self, data: DataUnit):
        '''构建至GCN网连接的新增网线'''

        targetStationList = data.get(self.DATA_KEY_GCN_TARGET_STATION_LIST)
        gcnSlotList = data.get(self.DATA_KEY_GCN_SLOT_LIST)

        if not targetStationList:
            return

        self._checkGCNLinkData(
            targetStationList=targetStationList,
            gcnSlotList=gcnSlotList
        )

        for targetSta, gcnSlot in zip(targetStationList, gcnSlotList):
            targetPos = self._gcnTargetPosBySlot(
                data=data,
                gcnSlot=gcnSlot
            )

            self._addNormalNetLinkIfDifferent(
                startPos=self._newCableStartPos(data),
                endPos=targetPos,
                note=f"至{targetSta}, 保底网链路",
            )

    def _checkGCNLinkData(
            self,
            targetStationList: List,
            gcnSlotList: List
    ):
        '''检查GCN链路数据'''

        if gcnSlotList is None:
            raise ValueError("GCNTargetStationList存在数据，但GCNSlotList为空")

        if len(targetStationList) != len(gcnSlotList):
            raise ValueError(
                "GCN目标站点数量与使用板卡数量不一致: "
                f"GCNTargetStationList={targetStationList}, "
                f"GCNSlotList={gcnSlotList}"
            )

    def _gcnTargetPosBySlot(
            self,
            data: DataUnit,
            gcnSlot
    ) -> str:
        '''根据GCN板卡类型获取新增线缆终点'''

        if self._isGCNOccupiedSlot(data, gcnSlot):
            existedEdgedIDF = data.get(self.DATA_KEY_GCN_EXISTED_EDGED_IDF)

            if existedEdgedIDF is not None:
                return self._gcnEdgedIDFPos(existedEdgedIDF)

            return self._gcnDevicePos(data)

        newETHSlotEdgedIDF = data.get(self.DATA_KEY_GCN_NEW_ETH_SLOT_EDGED_IDF)

        if newETHSlotEdgedIDF is not None:
            return self._gcnEdgedIDFPos(newETHSlotEdgedIDF)

        return self._gcnDevicePos(data)

    def _isGCNOccupiedSlot(
            self,
            data: DataUnit,
            gcnSlot
    ) -> bool:
        '''判断GCN使用板卡是否为占用板卡'''

        if not data.get(self.DATA_KEY_GCN_IS_EXPANSION):
            return True

        gcnETHSlotUnitDict = self._gcnETHSlotUnitDict(data)
        slotKey = self._slotKey(gcnSlot)

        if slotKey not in gcnETHSlotUnitDict:
            raise ValueError(
                "GCNisExpansion为True，但GCNSlotList中的板卡未在GCNETHslotList中找到: "
                f"slot={gcnSlot}, GCNETHslotList={data.get(self.DATA_KEY_GCN_ETH_SLOT_LIST)}"
            )

        slotUnit = gcnETHSlotUnitDict[slotKey]

        if slotUnit.tag == self.TAG_GCN_SLOT_OCCUPIED:
            return True

        if slotUnit.tag == self.TAG_GCN_SLOT_NEW:
            return False

        raise ValueError(
            "GCNisExpansion为True时，GCNSlotList涉及的板卡必须在GCNETHslotList中标记<o>或<n>: "
            f"slot={gcnSlot}, slotUnit={slotUnit}"
        )

    def _gcnETHSlotUnitDict(self, data: DataUnit) -> Dict[str, ParseUnit]:
        '''获取GCN以太网板卡解析字典'''

        gcnETHSlotList = data.get(self.DATA_KEY_GCN_ETH_SLOT_LIST)

        if gcnETHSlotList is None:
            raise ValueError("GCNisExpansion为True，但GCNETHslotList为空")

        resultDict: Dict[str, ParseUnit] = {}

        for rawSlot in gcnETHSlotList:
            slotUnit = ParseUnit(str(rawSlot).strip())
            slotKey = str(slotUnit.value).strip()

            if slotKey in resultDict:
                raise ValueError(
                    "GCNETHslotList中存在重复板卡编号: "
                    f"slot={slotKey}, GCNETHslotList={gcnETHSlotList}"
                )

            resultDict[slotKey] = slotUnit

        return resultDict

    def _slotKey(self, rawSlot) -> str:
        '''获取板卡编号比较键'''

        return str(ParseUnit(str(rawSlot).strip()).value).strip()
    
    def _gcnEdgedIDFPos(self, idfUnit) -> str:
        '''获取GCN成端IDF位置'''

        return self._idfPos(
            ParseUnit(str(idfUnit).strip()).value
        )
        
    def _gcnDevicePos(self, data: DataUnit) -> str:
        '''获取GCN设备位置'''

        gcnPnum = data.get(self.DATA_KEY_GCN_PNUM)
        gcnPname = data.get(self.DATA_KEY_GCN_PNAME)

        return f"{gcnPnum} {gcnPname} {self.GCN_DEVICE_NAME}"

    def _addNormalNetLinkIfDifferent(
            self,
            startPos: str,
            endPos: str,
            note: str,
            num: int = 1
    ):
        '''起点终点不一致时新增普通网线'''

        self.newLink(
            光速寻线以太网线缆(
                startPos=startPos,
                endPos=endPos,
                note=note,
                num=num
            )
        )
        
    def _cryptoDevPos(self, data: DataUnit) -> Optional[str]:
        '''获取纵向加密设备位置'''
        rtcdDevNumList: list = data.get(self.DATA_KEY_RTCD_DEV_NUM_LIST)
        nrtcdDevNumList: list = data.get(self.DATA_KEY_NRTCD_DEV_NUM_LIST)

        if len(rtcdDevNumList) == 0 or len(nrtcdDevNumList) == 0:
            return None
        
        pUnit = ParseUnit(rtcdDevNumList[-1])
        
        if pUnit.isMatched("r2"):
            if self.room2 is not None:
                return f"{pUnit.value} 纵向加密装置({self.room2})"
            else:
                raise ValueError("设置了r2参数但是room2Name未填写")
        else:
            return f"{pUnit.value} 纵向加密装置"
        

    def _firstCryptoIDFPos(self, data: DataUnit) -> Optional[str]:
        '''获取纵向加密连接的第一个实际IDF位置'''

        rtcdDevNumList = data.get(self.DATA_KEY_RTCD_DEV_NUM_LIST)
        nrtcdDevNumList = data.get(self.DATA_KEY_NRTCD_DEV_NUM_LIST)

        if len(rtcdDevNumList) == 0 or len(nrtcdDevNumList) == 0:
            return None

        rtcdIDFUnitList = [
            ParseUnit(devNum)
            for devNum in rtcdDevNumList[:-1]
        ]

        nrtcdIDFUnitList = [
            ParseUnit(devNum)
            for devNum in nrtcdDevNumList[:-1]
        ]

        for rtUnit, nrtUnit in zip(rtcdIDFUnitList, nrtcdIDFUnitList):
            if self._isJump(rtUnit) or self._isJump(nrtUnit):
                continue

            if self._isExistedEdgedIDF(rtUnit) or self._isExistedEdgedIDF(nrtUnit):
                continue

            if rtUnit.value != nrtUnit.value:
                raise ValueError(
                    "纵向加密实时/非实时第一个IDF设备号不一致，"
                    f"rt={rtUnit}, nrt={nrtUnit}"
                )

            return self._idfPos(rtUnit.value)

        return None

    def _firstGCNTargetPos(self, data: DataUnit) -> Optional[str]:
        '''获取GCN网第一个新增线缆终点
        如果GCN成端IDF存在，使用对应成端IDF，否则使用保底网屏'''

        idfUnit = data.get(self.DATA_KEY_GCN_EXISTED_EDGED_IDF)

        if idfUnit is not None:
            return self._idfPos(idfUnit)

        gcnPnum = data.get(self.DATA_KEY_GCN_PNUM)
        gcnPname = data.get(self.DATA_KEY_GCN_PNAME)

        return f"{gcnPnum} {gcnPname} {self.GCN_DEVICE_NAME}"

    def _newCableStartPos(self, data: DataUnit) -> str:
        '''获取新增网线起点'''

        # 如果有成端IDF，起点使用成端IDF，否则使用路由器
        if self._hasEdgedIDF(data):
            return self._edgedIDFPos(data)

        return self._routerPos(data)

    def _hasEdgedIDF(self, data: DataUnit) -> bool:
        '''是否存在成端IDF'''

        return self._hasNewEdgedIDF(data) or self._hasExistedEdgedIDF(data)

    def _hasNewEdgedIDF(self, data: DataUnit) -> bool:
        '''是否存在本期新增成端IDF'''

        return data.get(self.DATA_KEY_EDGED_IDF_ALTITUDE_U) is not None


    def _hasExistedEdgedIDF(self, data: DataUnit) -> bool:
        '''是否存在利旧成端IDF'''

        return self._existedEdgedIDFUnit(data) is not None

    def _existedEdgedIDFUnit(self, data: DataUnit) -> Optional[ParseUnit]:
        '''获取利旧成端IDF单元'''

        rtcdDevNumList = data.get(self.DATA_KEY_RTCD_DEV_NUM_LIST)
        nrtcdDevNumList = data.get(self.DATA_KEY_NRTCD_DEV_NUM_LIST)

        if len(rtcdDevNumList) == 0:
            return None

        rtUnit = ParseUnit(rtcdDevNumList[0])

        if not self._isExistedEdgedIDF(rtUnit):
            return None

        if len(nrtcdDevNumList) == 0:
            raise ValueError("实时纵向加密存在利旧成端IDF，但非实时纵向加密设备列表为空")

        nrtUnit = ParseUnit(nrtcdDevNumList[0])

        if not self._isExistedEdgedIDF(nrtUnit):
            raise ValueError(
                "实时纵向加密存在利旧成端IDF，但非实时纵向加密第一个设备未标记<e>: "
                f"rt={rtUnit}, nrt={nrtUnit}"
            )

        if rtUnit.value != nrtUnit.value:
            raise ValueError(
                "实时/非实时利旧成端IDF设备号不一致: "
                f"rt={rtUnit}, nrt={nrtUnit}"
            )

        return rtUnit

    def _isExistedEdgedIDF(self, parseUnit: ParseUnit) -> bool:
        '''判断是否为利旧成端IDF'''

        return parseUnit.tag == self.TAG_EXISTED_EDGED_IDF

    def _routerPos(self, data: DataUnit) -> str:
        '''获取新增低端路由器位置'''

        return f"{self._installPnum(data)} {self.ROUTER_DEV_NAME}"

    def _edgedIDFPos(self, data: DataUnit) -> str:
        '''获取成端IDF位置'''

        if self._hasNewEdgedIDF(data):
            return f"{self._installPnum(data)} {self.NEW_EDGED_IDF_DEV_NAME}"

        existedEdgedIDFUnit = self._existedEdgedIDFUnit(data)

        if existedEdgedIDFUnit is not None:
            return f"{existedEdgedIDFUnit.value} {self.EXISTED_EDGED_IDF_DEV_NAME}"

        raise ValueError("不存在成端IDF，无法获取成端IDF位置")

    def _idfPos(self, devNum: str) -> str:
        '''获取IDF位置'''

        return f"{devNum} {self.IDF_DEV_NAME}"

    def _installPnum(self, data: DataUnit) -> str:
        '''获取DDN安装屏号'''

        return data.get(self.DATA_KEY_DDN_INSTALL_PNUM)

    def _isJump(self, parseUnit: ParseUnit) -> bool:
        '''是否跳过该设备'''

        return parseUnit.tag == self.TAG_JUMP

    def readExcel(self, subDF: DataFrame):
        '''读取已有表格，尝试继承已有线缆长度和跨越参数'''

        for index, row in subDF.iterrows():
            for link in self.linkList:
                link.readRowArgs(row=row)

    def toDF(self):
        '''转换为DataFrame'''

        dfList = [SubTitle(substationName=self.substationName).toDF()]
        dfList += [
            link.toDF(
                substationName=self.substationName,
                walkLine=self.walkLine
            )
            for link in self.linkList
        ]

        return pd.concat(dfList)


# 兼容旧命名风格，如果上层代码仍然使用 cableLayTableOne，可以保留这一行
cableLayTableOne = CableLayTableOne