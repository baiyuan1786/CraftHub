##########################################################################################################
#   Description: 屏柜绘图读取器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path

from craftHub.tool import GLog

from ...common.reader import Reader, ExcelValueType
from .dataUnit import DataUnitCabinet


class ReaderCabinet(Reader):
    '''屏柜绘图读取器'''

    COL_WISH_TYPES = [
        ("substationName", ExcelValueType.STR),
        ("drawOrder", ExcelValueType.INT),
        ("build", ExcelValueType.BOOL),

        ("cabinetPnum", ExcelValueType.STR),
        ("cabinetPname", ExcelValueType.STR),
        ("cabinetType", ExcelValueType.STR),

        ("panelDeviceNameList", ExcelValueType.LIST_STR),
        ("panelDeviceAltitudeUList", ExcelValueType.LIST_INT),
        ("panelDeviceHeightUList", ExcelValueType.LIST_INT),

        ("newDeviceTypeList", ExcelValueType.LIST_STR),
        #("newDeviceAltitudeUList", ExcelValueType.LIST_INT),
    ]

    def __init__(self, excelPath: Path, sheetName: str) -> None:
        super().__init__(excelPath, sheetName)
        self.assertColTypes()

    def __iter__(self):
        return iter([
            DataUnitCabinet(index, self.dfDict)
            for index in range(len(self))
        ])

    def assertColTypes(self):
        '''校验表格列类型'''

        GLog.logInfo(f"{GLog.BLUE}开始表格类型校验{GLog.END}")

        for col, wishType in self.COL_WISH_TYPES:
            self.assertColType(col, wishType)

        GLog.logInfo(f"{GLog.GREEN}表格类型检查通过{GLog.END}")