##########################################################################################################
#   Description: ddn定向式绘图网络数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.subscripts._3drawingMaster.core.common.reader.reader import ExcelValueType
from craftHub.tool import GLog
from ...common.reader import DataUnit, Reader, ExcelValueType
from .dataUnit import DataUnitDDN

import pandas as pd
from pathlib import Path

class ReaderDDN(Reader):
    COL_WISH_TYPES = [
        ("站名称", ExcelValueType.STR),
        ("substationName", ExcelValueType.STR),
        ("layer", ExcelValueType.STR),
        ("drawOrder", ExcelValueType.INT),
        ("DRAWINGNUMBER1", ExcelValueType.STR),
        ("DRAWINGNUMBER2", ExcelValueType.STR),
        ("build", ExcelValueType.BOOL),
        ("roomName", ExcelValueType.STR),
        ("room2Name", ExcelValueType.STR),
        ("unify", ExcelValueType.BOOL),
        ("walkLine", ExcelValueType.STR),
        # ("edgedIDFaltitudeU", ExcelValueType.STR),
        ("floor", ExcelValueType.STR),
        ("IDNInstallPnum", ExcelValueType.STR),
        ("IDNInstallPName", ExcelValueType.STR),
        # ("IDNAltitudeU", ExcelValueType.MIXED),
        ("DDNInstallPnum", ExcelValueType.STR),
        ("DDNInstallPName", ExcelValueType.STR),
        # ("DDNAltitudeU", ExcelValueType.STR),
        ("cabinetType", ExcelValueType.STR),
        ("panelDeviceNameList", ExcelValueType.LIST_STR),
        ("panelDeviceAltitudeUList", ExcelValueType.LIST_INT),
        ("panelDeviceHeightUList", ExcelValueType.LIST_INT),
        ("IDNisNewPDU", ExcelValueType.BOOL),
        # ("IDNPDUAltitudeU", ExcelValueType.MIXED),
        ("DDNisNewPDU", ExcelValueType.BOOL),
        ("DDNisUsePDU", ExcelValueType.BOOL),
        # ("DDNPDUAltitudeU", ExcelValueType.STR),
        ("powerCabinetPnum1", ExcelValueType.STR),
        ("powerCabinetPname1", ExcelValueType.STR),
        ("powerCabinetTknum1", ExcelValueType.STR),
        ("powerCabinetTkA1", ExcelValueType.STR),
        ("powerCabinetPnum2", ExcelValueType.STR),
        ("powerCabinetPname2", ExcelValueType.STR),
        ("powerCabinetTknum2", ExcelValueType.STR),
        ("powerCabinetTkA2", ExcelValueType.STR),
        ("rtcdPname", ExcelValueType.STR),
        ("rtcdDevNumList", ExcelValueType.LIST_STR),
        ("rtcdDevPortList", ExcelValueType.LIST_STR),
        ("nrtcdPname", ExcelValueType.STR),
        ("nrtcdDevNumList", ExcelValueType.LIST_STR),
        ("nrtcdDevPortList", ExcelValueType.LIST_STR),
        ("GCNPnum", ExcelValueType.STR),
        ("GCNPname", ExcelValueType.STR),
        ("GCNexistedEdgedIDF", ExcelValueType.STR),
        ("GCNTargetStationList", ExcelValueType.LIST_STR),
        ("GCNLinkBoardList", ExcelValueType.LIST_STR),
        ("GCNSlotList", ExcelValueType.LIST_INT),
        ("GCNBoardName", ExcelValueType.STR),
        ("GCNareaName", ExcelValueType.STR),
        ("GCNisExpansion", ExcelValueType.BOOL),
        # ("GCNETHslotList", ExcelValueType.STR),
    ]
    
    def __init__(self, excelPath: Path, sheetName: str) -> None:
        super().__init__(excelPath, sheetName)
        self.assertColTypes()
        
    def __iter__(self):
        return iter([DataUnitDDN(index, self.dfDict) for index in range(len(self))])
    
    def assertColTypes(self):
        GLog.logInfo(f"{GLog.BLUE}开始表格类型校验{GLog.END}")
        for (col, wishType) in self.COL_WISH_TYPES:
            self.assertColType(col, wishType)
            
        GLog.logInfo(f"{GLog.GREEN}表格类型检查通过{GLog.END}")
