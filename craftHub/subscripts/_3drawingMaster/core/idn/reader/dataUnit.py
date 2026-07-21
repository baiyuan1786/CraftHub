##########################################################################################################
#   Description: IDN集成式网络数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog
from ...common.reader import DataUnit
from typing import Dict, Any, List

class DataUnitIDN(DataUnit):
    '''地区idn数据单元, 仅容纳一行的数据'''
    
    def __init__(self, rowIndex: int, dfDict: Dict) -> None:
        super().__init__(rowIndex, dfDict)
        
    def typeCheck(self):
        """数据有效性校验函数"""
        
        # 项目基本信息
        assert isinstance(self.get("drawOrder"), int), f"绘图顺序不是整数, 其值为{self.get('drawOrder')}"
        assert self.get("layer") in ["接入层", "汇聚层", "核心层"], f"层级不是接入层, 汇聚层, 核心层之一, 其值为{self.get('layer')}"
        assert isinstance(self.get("DRAWINGNUMBER1"), str), f"DRAWINGNUMBER1必须是字符串类型，实际类型为{type(self.get('DRAWINGNUMBER1')).__name__}"
        assert isinstance(self.get("DRAWINGNUMBER2"), str), f"DRAWINGNUMBER2必须是字符串类型，实际类型为{type(self.get('DRAWINGNUMBER2')).__name__}"
        assert isinstance(self.get("build"), bool), f"notBuild必须是字符串类型，实际类型为{type(self.get('build')).__name__}"
        
        # 未建设站点不检查详细信息
        if not self.get("build"):
            return
        
        # 房间基本信息
        assert isinstance(self.get("substationName"), str), f"substationName必须是字符串类型，实际类型为{type(self.get('substationName')).__name__}"
        assert isinstance(self.get("roomName"), str) and bool(self.get("roomName")), f"roomName必须是非空字符串，实际值为{repr(self.get('roomName'))}"
        assert isinstance(self.get("room2Name"), str) or self.get("room2Name") is None, f"room2Name必须是字符串类型或None，实际类型为{type(self.get('room2Name')).__name__}"
        assert isinstance(self.get("unify"), bool), f"unify必须是布尔类型，实际类型为{type(self.get('unify')).__name__}"
        assert self.get("walkLine") in ["下走线", "上走线", "电缆层走线"], f"walkLine必须是['下走线', '上走线', '电缆层走线']之一，实际值为{repr(self.get('walkLine'))}"
        assert isinstance(self.get("floor"), str), f"floor必须是字符串类型，实际类型为{type(self.get('floor')).__name__}"
        
        # 安装基本信息
        assert isinstance(self.get("installPnum"), str), f"installPnum必须是字符串类型，实际类型为{type(self.get('installPnum')).__name__}"
        assert isinstance(self.get("installPName"), str), f"installPName必须是字符串类型，实际类型为{type(self.get('installPName')).__name__}"
        assert isinstance(self.get("altitudeU"), int) or self.get("altitudeU") == "auto", f"installAltitudeU必须是整数类型或'auto'，实际值类型为{type(self.get('altitudeU')).__name__}"
        assert self.get("installCabinetType") in ["新增", "占用"], f"installCabinetType必须是['新增', '占用']之一，实际值为{repr(self.get('installCabinetType'))}"
        assert isinstance(self.get("PDUAltitudeU"), int) or self.get("PDUAltitudeU") == "auto" or self.get("PDUAltitudeU") is None, f"installPDUAltitudeU必须是整数、'auto'或None，实际值类型为{type(self.get('PDUAltitudeU')).__name__}"
        assert isinstance(self.get("DDNInstallPnum"), str), f"DDNdevInstallPnum必须是字符串类型，实际类型为{type(self.get('DDNInstallPnum')).__name__}"
        assert isinstance(self.get("DDNAltitudeU"), int) or self.get("DDNAltitudeU") == "auto" or self.get("DDNAltitudeU") is None, f"DDNdevAltitudeU必须是整数、'auto'或None，实际值类型为{type(self.get('DDNAltitudeU')).__name__}"
        
        # 面板图信息
        if self.get("panelDeviceNameList") is None:
            self.set("panelDeviceNameList", [])  # 允许面板图是空的设备
        if not self.get("panelDeviceNameList") and not self.get("panelDeviceAltitudeUList"):
            self.set("panelDeviceAltitudeUList", [])
        if not self.get("panelDeviceNameList") and not self.get("panelDeviceHeightUList"):
            self.set("panelDeviceHeightUList", [])
        
        assert isinstance(self.get("panelDeviceNameList"), list), f"panelDeviceNameList必须是列表类型，实际类型为{type(self.get('panelDeviceNameList')).__name__}"
        assert isinstance(self.get("panelDeviceAltitudeUList"), list), f"panelDeviceAltitudeUList必须是列表类型，实际类型为{type(self.get('panelDeviceAltitudeUList')).__name__}"
        assert isinstance(self.get("panelDeviceHeightUList"), list), f"panelDeviceHeightUList必须是列表类型，实际类型为{type(self.get('panelDeviceHeightUList')).__name__}"
        
        # PDU信息
        assert isinstance(self.get("isUsePDU"), bool), f"isUsePDU必须是布尔类型，实际类型为{type(self.get('isUsePDU')).__name__}"
        assert isinstance(self.get("isNewPDU"), bool), f"isNewPDU必须是布尔类型，实际类型为{type(self.get('isNewPDU')).__name__}"

        # 电源信息处理
        assert isinstance(self.get("powerCabinetPnum1"), str), f"powerCabinetPnum1必须是字符串类型，实际类型为{type(self.get('powerCabinetPnum1')).__name__}"
        assert isinstance(self.get("powerCabinetPname1"), str), f"powerCabinetPname1必须是字符串类型，实际类型为{type(self.get('powerCabinetPname1')).__name__}"
        assert isinstance(self.get("powerCabinetTknum1"), str), f"powerCabinetTknum1必须是字符串类型，实际类型为{type(self.get('powerCabinetTknum1')).__name__}"

        assert isinstance(self.get("powerCabinetPnum2"), str), f"powerCabinetPnum2必须是字符串类型，实际类型为{type(self.get('powerCabinetPnum2')).__name__}"
        assert isinstance(self.get("powerCabinetPname2"), str), f"powerCabinetPname2必须是字符串类型，实际类型为{type(self.get('powerCabinetPname2')).__name__}"
        assert isinstance(self.get("powerCabinetTknum2"), str), f"powerCabinetTknum2必须是字符串类型，实际类型为{type(self.get('powerCabinetTknum2')).__name__}"

        if (self.get("powerCabinetPnum1") == self.get("powerCabinetPnum2") and self.get("powerCabinetPname1") != self.get("powerCabinetPname2")) or (
            self.get("powerCabinetPnum1") != self.get("powerCabinetPnum2") and self.get("powerCabinetPname1") == self.get("powerCabinetPname2")
        ):
            raise ValueError(f"配电屏信息矛盾: {self.get('powerCabinetPnum1')}{self.get('powerCabinetPname1')}, {self.get('powerCabinetPnum2')}{self.get('powerCabinetPname2')}")
        
        area3DevPortList = self.get("area3DevPortList")
        area3DevNumList = self.get("area3DevNumList")
        area3DevNameList = self.get("area3DevNameList")
        
        assert isinstance(area3DevPortList, list), f"area3DevPortList必须是列表类型，实际类型为{type(self.get('area3DevPortList')).__name__}"
        assert isinstance(area3DevNumList, list), f"area3DevNumList必须是列表类型，实际类型为{type(self.get('area3DevNumList')).__name__}"
        assert isinstance(area3DevNameList, list), f"area3DevNameList必须是列表类型，实际类型为{type(self.get('area3DevNameList')).__name__}"
        
        lenArea3 = len(area3DevPortList) 
        if not self.get("area3pNumList"):
            self.set("area3pNumList", [None] * lenArea3)
        if not self.get("area3pNameList"):
            self.set("area3pNameList", [None] * lenArea3)
        
        # 使用元组检查所有列表长度一致，并添加详细错误信息
        lenDevPort = len(area3DevPortList)
        lenDevNum = len(area3DevNumList)
        lenDevName = len(area3DevNameList)
        lenPNum = len(self.get("area3pNumList")) # type: ignore
        lenPName = len(self.get("area3pNameList")) # type: ignore
        
        assert lenDevPort == lenArea3, f"area3DevPortList长度应为{lenArea3}，实际为{lenDevPort}"
        assert lenDevNum == lenArea3, f"area3DevNumList长度应为{lenArea3}，实际为{lenDevNum}"
        assert lenDevName == lenArea3, f"area3DevNameList长度应为{lenArea3}，实际为{lenDevName}"
        assert lenPNum == lenArea3, f"area3pNumList长度应为{lenArea3}，实际为{lenPNum}"
        assert lenPName == lenArea3, f"area3pNameList长度应为{lenArea3}，实际为{lenPName}"
        assert lenArea3 >= 1, f"area3DevPortList必须至少包含1个元素，实际长度为{lenArea3}"
        
        if self.get("area3InRoom2Num") is None:
            self.set("area3InRoom2Num", 0)
        
        assert isinstance(self.get("area3InRoom2Num"), int), f"area3InRoom2Num必须是整数类型，实际类型为{type(self.get('area3InRoom2Num')).__name__}"
        assert isinstance(self.get("area3Room2Photo"), bool), f"area3Room2Photo必须是布尔类型，实际类型为{type(self.get('area3Room2Photo')).__name__}"
        
        # ODF链路信息
        assert isinstance(self.get("odfLinkBoardList"), list), f"odfLinkBoardList必须是列表类型，实际类型为{type(self.get('odfLinkBoardList')).__name__}"
        
        lenODF = len(self.get("odfLinkBoardList")) # type: ignore
        if not self.get("fiberJumpList"):
            self.set("fiberJumpList", [None] * lenODF)
        
        assert isinstance(self.get("odfLinkUnitNumList"), list), f"odfLinkUnitNumList必须是列表类型，实际类型为{type(self.get('odfLinkUnitNumList')).__name__}"
        assert isinstance(self.get("odfLinkODFPfullNameList"), list), f"odfLinkODFPfullNameList必须是列表类型，实际类型为{type(self.get('odfLinkODFPfullNameList')).__name__}"
        assert isinstance(self.get("odfLinkTerminateStrList"), list), f"odfLinkTerminateStrList必须是列表类型，实际类型为{type(self.get('odfLinkTerminateStrList')).__name__}"
        assert isinstance(self.get("fiberJumpList"), list), f"fiberJumpList必须是列表类型，实际类型为{type(self.get('fiberJumpList')).__name__}"
        
        lenODFunit = len(self.get("odfLinkUnitNumList")) # type: ignore
        lenODFfullname = len(self.get("odfLinkODFPfullNameList")) # type: ignore
        lenODFterstr = len(self.get("odfLinkTerminateStrList")) # type: ignore
        lenfiberJump = len(self.get("fiberJumpList")) # type: ignore
        
        assert lenODFunit == lenODF, f"odfLinkUnitNumList长度应为{lenODF}，实际为{lenODFunit}"
        assert lenODFfullname == lenODF, f"odfLinkODFPfullNameList长度应为{lenODF}，实际为{lenODFfullname}"
        assert lenODFterstr == lenODF, f"odfLinkTerminateStrList长度应为{lenODF}，实际为{lenODFterstr}"
        assert lenfiberJump == lenODF, f"fiberJumpList长度应为{lenODF}，实际为{lenfiberJump}"
        
        # ODF跳纤信息
        assert isinstance(self.get("jump1stIDF"), bool), f"jump1stIDF必须是bool类型，实际类型为{type(self.get('jump1stIDF')).__name__}"
        
        if not self.get("odfJumpPList"):
            self.set("odfJumpPList", [])
        if not self.get("odfJumpUnitList"):
            self.set("odfJumpUnitList", [])
            
        assert isinstance(self.get("odfJumpPList"), list), f"area3ODFjumpPList必须是列表类型，实际类型为{type(self.get('odfJumpPList')).__name__}"
        assert isinstance(self.get("odfJumpUnitList"), list), f"area3ODFUnitList必须是列表类型，实际类型为{type(self.get('odfJumpUnitList')).__name__}"

        assert len(self.get("odfJumpPList")) == len(self.get("odfJumpUnitList")), f"3区ODF跳纤信息长度不匹配,odfJumpPList: {self.get('odfJumpPList')}, odfJumpUnitList: {self.get('odfJumpUnitList')}" # type: ignore

        # GCN网信息
        GCNPnameList: List = self.get("GCNPnameList")
        GCNDevList: List = self.get("GCNDevList")
        GCNPortList: List = self.get("GCNPortList")
    
        assert isinstance(GCNPnameList, list), f"GCNPnameList必须是列表类型，实际类型为{type(self.get('GCNPnameList')).__name__}"
        assert isinstance(GCNDevList, list), f"GCNPnameList必须是列表类型，实际类型为{type(self.get('GCNDevList')).__name__}"
        assert isinstance(GCNPortList, list), f"GCNPnameList必须是列表类型，实际类型为{type(self.get('GCNPortList')).__name__}"
        
        lenGCN = len(GCNPnameList)
        lenGCNPnameList = len(GCNPnameList)
        lenGCNDevList = len(GCNDevList)
        lenGCNPortList = len(GCNPortList)
        
        assert lenGCNPnameList == lenGCN, f"GCNPnameList长度应为{lenGCN}，实际为{lenGCNPnameList}"
        assert lenGCNDevList == lenGCN, f"GCNDevList长度应为{lenGCN}，实际为{lenGCNDevList}"
        assert lenGCNPortList == lenGCN, f"GCNPortList长度应为{lenGCN}，实际为{lenGCNPortList}"
            
        # 禁用同屏安装
        if self.get("installPnum") == self.get("DDNInstallPnum"):
            pass
            #raise ValueError(f"禁止ddn和idn设备同屏安装，idn:{self.get("installPnum")}, ddn:{self.get("DDNInstallPnum")}")
            
        # 四区链路信息
        try:
            self.assertType("area4DevNumList", list)
            self.assertType("area4DevNameList", list)
            self.assertType("area4DevPortList", list)
        except Exception:
            GLog.logInfo("四区链路类型错误， 重置为空")
            self.set("area4DevNumList", [])
            self.set("area4DevNameList", [])
            self.set("area4DevPortList", [])
        
        area4Len = len(self.get("area4DevNumList"))
        self.assertLen("area4DevNumList", area4Len)
        self.assertLen("area4DevNameList", area4Len)
        self.assertLen("area4DevPortList", area4Len)

     