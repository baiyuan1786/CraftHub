##########################################################################################################
#   Description: 屏柜绘图数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Dict, List

from ...common.reader import DataUnit


class DataUnitCabinet(DataUnit):
    '''屏柜绘图数据单元'''

    CABINET_TYPE_LIST = ["新增", "占用"]
    DEVICE_TYPE_LIST = ["IDN", "DDN", "PDU", "IDF"]

    DATA_KEY_DRAW_ORDER = "drawOrder"
    DATA_KEY_BUILD = "build"
    DATA_KEY_SUBSTATION_NAME = "substationName"

    DATA_KEY_CABINET_PNUM = "cabinetPnum"
    DATA_KEY_CABINET_PNAME = "cabinetPname"
    DATA_KEY_CABINET_TYPE = "cabinetType"

    DATA_KEY_PANEL_DEVICE_NAME_LIST = "panelDeviceNameList"
    DATA_KEY_PANEL_DEVICE_ALTITUDE_U_LIST = "panelDeviceAltitudeUList"
    DATA_KEY_PANEL_DEVICE_HEIGHT_U_LIST = "panelDeviceHeightUList"

    DATA_KEY_NEW_DEVICE_TYPE_LIST = "newDeviceTypeList"
    DATA_KEY_NEW_DEVICE_ALTITUDE_U_LIST = "newDeviceAltitudeUList"

    def __init__(self, rowIndex: int, dfDict: Dict) -> None:
        super().__init__(rowIndex, dfDict)

    def typeCheck(self):
        """数据有效性校验函数"""

        self.assertType(self.DATA_KEY_DRAW_ORDER, int)
        self.assertType(self.DATA_KEY_BUILD, bool)

        if not self.get(self.DATA_KEY_BUILD):
            return

        self.assertType(self.DATA_KEY_SUBSTATION_NAME, str)

        self.assertType(self.DATA_KEY_CABINET_PNUM, str)
        self.assertType(self.DATA_KEY_CABINET_PNAME, str)
        self.assertType(self.DATA_KEY_CABINET_TYPE, str)
        self.assertValue(self.DATA_KEY_CABINET_TYPE, self.CABINET_TYPE_LIST)

        self.assertType(self.DATA_KEY_PANEL_DEVICE_NAME_LIST, list)
        self.assertType(self.DATA_KEY_PANEL_DEVICE_ALTITUDE_U_LIST, list)
        self.assertType(self.DATA_KEY_PANEL_DEVICE_HEIGHT_U_LIST, list)

        self.assertType(self.DATA_KEY_NEW_DEVICE_TYPE_LIST, list)
        self.assertType(self.DATA_KEY_NEW_DEVICE_ALTITUDE_U_LIST, list)

        self._checkPanelDeviceList()
        self._checkNewDeviceList()

    def _checkPanelDeviceList(self):
        '''检查已有设备列表'''

        nameList: List = self.get(self.DATA_KEY_PANEL_DEVICE_NAME_LIST)
        altitudeList: List = self.get(self.DATA_KEY_PANEL_DEVICE_ALTITUDE_U_LIST)
        heightList: List = self.get(self.DATA_KEY_PANEL_DEVICE_HEIGHT_U_LIST)

        if len(nameList) != len(altitudeList):
            raise ValueError(
                "已有设备名称列表与安装U位列表长度不一致: "
                f"name={len(nameList)}, altitude={len(altitudeList)}"
            )

        if len(nameList) != len(heightList):
            raise ValueError(
                "已有设备名称列表与高度U数列表长度不一致: "
                f"name={len(nameList)}, height={len(heightList)}"
            )

    def _checkNewDeviceList(self):
        '''检查新增设备列表'''

        deviceTypeList: List = self.get(self.DATA_KEY_NEW_DEVICE_TYPE_LIST)
        altitudeList: List = self.get(self.DATA_KEY_NEW_DEVICE_ALTITUDE_U_LIST)

        if len(deviceTypeList) != len(altitudeList):
            raise ValueError(
                "新增设备类型列表与安装U位列表长度不一致: "
                f"type={len(deviceTypeList)}, altitude={len(altitudeList)}"
            )

        for deviceType in deviceTypeList:
            if deviceType not in self.DEVICE_TYPE_LIST:
                raise ValueError(
                    f"新增设备类型不合法: {deviceType}, "
                    f"必须是 {self.DEVICE_TYPE_LIST} 之一"
                )