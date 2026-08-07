##########################################################################################################
#   Description: ddn定向式绘图网络数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Dict

from ...common.reader import DataUnit, ParseUnit

def isNum(value: Any):
    '''判断值是否是整数'''
    try:
        intValue = int(value)
    except Exception:
        return False
    else:
        return True

class DataUnitDDN(DataUnit):
    '''地区ddn数据单元, 仅容纳一行的数据'''

    TK_A_VALUE_LIST = ["10A", "16A", "20A", "32A", "40A", "63A"]

    GCN_TARGET_STATION_NUM = 2
    GCN_LINK_BOARD_VALUE_LIST = ["电口1", "电口2", "电口3", "电口4"]

    GCN_SLOT_NUM = 2
    GCN_SLOT_MIN = 1
    GCN_SLOT_MAX = 12

    CRYPTO_TAG_ROOM2 = "r2"
    CRYPTO_TAG_JUMP = "j"
    CRYPTO_TAG_NOPHOTO = "np" # 未拍摄标记
    CRYPTO_TAG_EDGEDIDF = "e" # 旧的成端IDF标记
    CRYPTO_TAG_VALUE_LIST = [None, CRYPTO_TAG_ROOM2, CRYPTO_TAG_JUMP, CRYPTO_TAG_NOPHOTO, CRYPTO_TAG_EDGEDIDF]

    def __init__(self, rowIndex: int, dfDict: Dict) -> None:
        super().__init__(rowIndex, dfDict)

    def typeCheck(self):
        """数据有效性校验函数"""

        self._checkProjectData()

        # 未建设站点不检查详细信息
        if not self.get("build"):
            return

        self._checkRoomData()
        self._checkInstallData()
        self._checkPDUData()
        self._checkPanelDeviceData()
        self._checkPowerLinkData()
        self._checkEdgedIDFData()
        self._checkCryptoLinkData()
        self._checkGCNLinkData()
        self._checkGCNexpansionData()

    def _checkProjectData(self):
        '''检查项目基本信息'''

        self.assertType("drawOrder", int)
        self.assertType("DRAWINGNUMBER1", str)
        self.assertType("DRAWINGNUMBER2", str)
        self.assertType("build", bool)
        self.assertValue("layer", "接入层")

    def _checkRoomData(self):
        '''检查房间基本信息'''

        self.assertType("substationName", str)
        self.assertType("roomName", str)
        self.assertType("room2Name", str, allowNone = True)
        self.assertType("unify", bool)
        self.assertType("floor", str)
        self.assertValue("walkLine", ["下走线", "上走线", "电缆层走线"])

    def _checkInstallData(self):
        '''检查安装基本信息'''

        self.assertType("cabinetType", str)
        self.assertValue("cabinetType", ["新增", "占用"])

        self.assertType("DDNInstallPnum", str)
        self.assertType("DDNInstallPName", str)
        self.assertType("DDNAltitudeU", int, True)

        self.assertType("IDNInstallPnum", str)
        self.assertType("IDNInstallPName", str)
        self.assertType("IDNAltitudeU", int, True)

    def _checkPDUData(self):
        '''检查PDU信息'''

        self.assertType("DDNisNewPDU", bool)
        self.assertType("DDNisUsePDU", bool)
        self.assertType("DDNPDUAltitudeU", int, True, True)

        self.assertType("IDNisNewPDU", bool)
        self.assertType("IDNPDUAltitudeU", int, True, True)

    def _checkPanelDeviceData(self):
        '''检查面板图设备信息'''

        self.assertType("panelDeviceNameList", list)
        self.assertType("panelDeviceAltitudeUList", list)
        self.assertType("panelDeviceHeightUList", list)

        panelDeviceNameList = self.get("panelDeviceNameList")
        panelDeviceAltitudeUList = self.get("panelDeviceAltitudeUList")
        panelDeviceHeightUList = self.get("panelDeviceHeightUList")

        if len(panelDeviceNameList) != len(panelDeviceAltitudeUList):
            raise ValueError(
                "面板设备名称列表与海拔U列表长度不一致: "
                f"name={len(panelDeviceNameList)}, altitudeU={len(panelDeviceAltitudeUList)}"
            )

        if len(panelDeviceNameList) != len(panelDeviceHeightUList):
            raise ValueError(
                "面板设备名称列表与高度U列表长度不一致: "
                f"name={len(panelDeviceNameList)}, heightU={len(panelDeviceHeightUList)}"
            )

    def _checkPowerLinkData(self):
        '''检查电源连接图信息'''

        # 取电类型信息
        self.assertValue("powerType", ["独立", "DC/DC", "DC/独立"])
        self.assertType("isPowerModify", bool)
        
        # 取电屏信息
        self.assertType("powerCabinetPnum1", str)
        self.assertType("powerCabinetPname1", str)
        self.assertType("powerCabinetTknum1", str)
        self.assertType("powerCabinetTkA1", str)
        self.assertValue("powerCabinetTkA1", self.TK_A_VALUE_LIST)

        self.assertType("powerCabinetPnum2", str)
        self.assertType("powerCabinetPname2", str)
        self.assertType("powerCabinetTknum2", str)
        self.assertType("powerCabinetTkA2", str)
        self.assertValue("powerCabinetTkA2", self.TK_A_VALUE_LIST)

        if (
                self.get("powerCabinetPnum1") == self.get("powerCabinetPnum2")
                and self.get("powerCabinetPname1") != self.get("powerCabinetPname2")
        ) or (
                self.get("powerCabinetPnum1") != self.get("powerCabinetPnum2")
                and self.get("powerCabinetPname1") == self.get("powerCabinetPname2")
        ):
            raise ValueError(
                "配电屏信息矛盾: "
                f"{self.get('powerCabinetPnum1')}{self.get('powerCabinetPname1')}, "
                f"{self.get('powerCabinetPnum2')}{self.get('powerCabinetPname2')}"
            )

    def _checkEdgedIDFData(self):
        '''检查成端IDF信息'''
        
        self.assertType("edgedIDFaltitudeU", int, True, True)

    def _checkCryptoLinkData(self):
        '''检查纵向加密连接图信息'''

        self.assertType("rtcdPname", str)
        self.assertType("rtcdDevNumList", list)
        self.assertType("rtcdDevPortList", list)

        self.assertType("nrtcdPname", str)
        self.assertType("nrtcdDevNumList", list)
        self.assertType("nrtcdDevPortList", list)

        self._assertListNotEmpty("rtcdDevNumList")
        self._assertListNotEmpty("nrtcdDevNumList")

        self._assertListItemType("rtcdDevNumList", str)
        self._assertListItemType("rtcdDevPortList", str)
        self._assertListItemType("nrtcdDevNumList", str)
        self._assertListItemType("nrtcdDevPortList", str, True) # 非实时的允许填写None

        rtcdDevNumList: list = self.get("rtcdDevNumList")
        rtcdDevPortList: list = self.get("rtcdDevPortList")
        nrtcdDevNumList: list = self.get("nrtcdDevNumList")
        nrtcdDevPortList: list = self.get("nrtcdDevPortList")

        if len(rtcdDevNumList) != len(nrtcdDevNumList):
            raise ValueError(
                "实时/非实时纵向加密设备数量不一致: "
                f"rt={len(rtcdDevNumList)}, nrt={len(nrtcdDevNumList)}"
            )

        if len(rtcdDevNumList) != len(rtcdDevPortList):
            raise ValueError(
                "实时纵向加密设备数量与端口数量不一致: "
                f"dev={len(rtcdDevNumList)}, port={len(rtcdDevPortList)}"
            )

        if len(nrtcdDevNumList) != len(nrtcdDevPortList):
            raise ValueError(
                "非实时纵向加密设备数量与端口数量不一致: "
                f"dev={len(nrtcdDevNumList)}, port={len(nrtcdDevPortList)}"
            )
            
        # 重写实时链路端口号
        rtcdLen = len(rtcdDevPortList)
        newRtcdDevPortList = rtcdDevPortList.copy()
        for index, rtcdPort in enumerate(rtcdDevPortList):
            if isNum(rtcdPort) and index == rtcdLen - 1:
                newRtcdDevPortList[index] = f"ETH{rtcdPort}"
            elif isNum(rtcdPort):
                newRtcdDevPortList[index] = f"端口{rtcdPort}"
            
        self.set("rtcdDevPortList", newRtcdDevPortList)
            
        # 重写非实时链路端口号
        nrtcdLen = len(nrtcdDevPortList)
        newNrtcdDevPortList = nrtcdDevPortList.copy()
        for index, nrtcdPort in enumerate(nrtcdDevPortList):
            if isNum(nrtcdPort) and index == nrtcdLen - 1:
                newNrtcdDevPortList[index] = f"ETH{nrtcdPort}"
            elif isNum(nrtcdPort):
                newNrtcdDevPortList[index] = f"端口{nrtcdPort}"
            
        self.set("nrtcdDevPortList", newNrtcdDevPortList)
        
        # 检查现有成端IDF与新增IDF是否同时设置
        if self.get("edgedIDFaltitudeU") and self.CRYPTO_TAG_EDGEDIDF in rtcdDevNumList[0]:
            raise ValueError("不能同时设置新增成端IDF和使用利旧IDF")

        rtcdParseUnitList = [ParseUnit(devNum) for devNum in rtcdDevNumList]
        nrtcdParseUnitList = [ParseUnit(devNum) for devNum in nrtcdDevNumList]

        for rtUnit, nrtUnit in zip(rtcdParseUnitList, nrtcdParseUnitList):
            self._checkCryptoTag(rtUnit)
            self._checkCryptoTag(nrtUnit)

            if rtUnit.value != nrtUnit.value:
                raise ValueError(
                    "纵向加密实时/非实时设备号不一致: "
                    f"rt={rtUnit}, nrt={nrtUnit}"
                )

            if not rtUnit.isMatched(nrtUnit):
                raise ValueError(
                    "纵向加密实时/非实时设备tag不一致: "
                    f"rt={rtUnit}, nrt={nrtUnit}"
                )

    def _checkGCNLinkData(self):
        '''检查GCN网连接图信息'''

        self.assertType("GCNPnum", str)
        self.assertType("GCNPname", str)
        self.assertType("GCNBoardName", str)
        self.assertType("GCNareaName", str)

        self.assertType("GCNexistedEdgedIDF", str, allowNone = True)
        self.assertType("GCNTargetStationList", list)
        self.assertType("GCNLinkBoardList", list)
        self.assertType("GCNSlotList", list)

        self._assertListItemType("GCNTargetStationList", str)
        self._assertListItemType("GCNLinkBoardList", str)

        targetStationList = self.get("GCNTargetStationList")
        linkBoardList = self.get("GCNLinkBoardList")

        if len(targetStationList) != self.GCN_TARGET_STATION_NUM:
            raise ValueError(
                f"GCN网目标站数量必须为{self.GCN_TARGET_STATION_NUM}，"
                f"当前数量为{len(targetStationList)}"
            )

        if len(linkBoardList) != len(targetStationList):
            raise ValueError(
                "GCN网连接电口数量必须与目标站数量一致: "
                f"targetStation={len(targetStationList)}, linkBoard={len(linkBoardList)}"
            )

        for linkBoard in linkBoardList:
            if linkBoard not in self.GCN_LINK_BOARD_VALUE_LIST:
                raise ValueError(
                    "GCN网连接电口只能是 电口1、电口2、电口3、电口4，"
                    f"当前值为{linkBoard}"
                )

        if len(set(linkBoardList)) != len(linkBoardList):
            raise ValueError(
                "GCN网连接电口不能重复，"
                f"当前连接电口列表为{linkBoardList}"
            )

        self._checkGCNSlotList()

    def _checkGCNexpansionData(self):
        '''检查GCN扩容信息'''

        self.assertType("GCNisExpansion", bool)         # 保底网扩容参数
        self.assertType("GCNETHslotList", list)         # 保底网已存在以太网板卡列表(允许定义占用，新增)
        self.assertType("GCNnewETHslotEdgedIDF", str, allowNone = True) # 新增板卡成端IDF

    def _checkGCNSlotList(self):
        '''检查GCN网槽位列表'''

        slotList = self.get("GCNSlotList")

        if len(slotList) != self.GCN_SLOT_NUM:
            raise ValueError(
                f"GCN网槽位数量必须为{self.GCN_SLOT_NUM}，"
                f"当前槽位列表为{slotList}"
            )

        for slotValue in slotList:
            slotNum = self._parseSlotNum(slotValue)

            if slotNum < self.GCN_SLOT_MIN or slotNum > self.GCN_SLOT_MAX:
                raise ValueError(
                    f"GCN网槽位号必须在{self.GCN_SLOT_MIN}-{self.GCN_SLOT_MAX}之间，"
                    f"当前值为{slotNum}"
                )
                

    def _checkCryptoTag(self, parseUnit: ParseUnit):
        '''检查纵向加密设备tag'''

        if parseUnit.tag not in self.CRYPTO_TAG_VALUE_LIST:
            raise ValueError(
                f"纵向加密设备tag只能是\'{self.CRYPTO_TAG_VALUE_LIST}\'之一"
                f"当前值为{parseUnit.tag}, 原始数据为{parseUnit.rawStr}"
            )

    def _assertListNotEmpty(self, key: str):
        '''检查列表不能为空'''

        valueList = self.get(key)

        if len(valueList) == 0:
            raise ValueError(f"{key}不能为空")

    def _assertListItemType(self, key: str, itemType: type, allowNone: bool = False):
        '''检查列表元素类型'''

        valueList = self.get(key)

        for index, value in enumerate(valueList):
            if isinstance(value, itemType) or (value is None and allowNone):
                continue

            raise TypeError(
                f"{key}第{index + 1}个元素类型错误，"
                f"期望{itemType}，当前值={value}，类型={type(value)}"
            )

    def _parseSlotNum(self, slotValue: Any) -> int:
        '''解析槽位号'''

        if isinstance(slotValue, int):
            return slotValue

        if isinstance(slotValue, str) and slotValue.strip().isdigit():
            return int(slotValue.strip())

        raise ValueError(
            "GCNSlotList槽位号必须是数字，"
            f"当前值为{slotValue}，类型为{type(slotValue)}"
        )