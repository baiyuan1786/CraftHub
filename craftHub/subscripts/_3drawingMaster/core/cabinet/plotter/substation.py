##########################################################################################################
#   Description: 屏柜绘图器，单站绘图器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from typing import List

from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.graph import CustomBlock, CADColor
from ...common.meta import Cabinet, ExistedDevice
from ...common.meta.device.autoU import AutoUcalculator
from ..reader import DataUnitCabinet


class Cabinet_subplt(CustomBlock):
    '''单站屏柜绘图器'''

    STATION_TEXT_INSERT_POINT = Vec2(0, 80)
    STATION_TEXT_WIDTH = 370
    STATION_TEXT_HEIGHT = 67

    CABINET_INSERT_POINT = Vec2(130, 0)

    DEVICE_TYPE_IDN = "IDN"
    DEVICE_TYPE_DDN = "DDN"
    DEVICE_TYPE_PDU = "PDU"
    DEVICE_TYPE_IDF = "IDF"

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitCabinet
    ) -> None:
        """初始化单站屏柜绘图器

        :param doc: CAD文档
        :param data: 屏柜数据单元
        """

        super().__init__(doc=doc, blockName=None, allowExisted=False)

        self.doc = doc
        self.data = data
        self.substationName: str = data.get("substationName")

    def plot(self):
        '''绘制单站屏柜图'''

        self._addSubstationNameText()
        self._addCabinetPanel()

    def _addSubstationNameText(self):
        '''添加站名多行文本框'''

        text = (
            f"{self.data.get('substationName')}"
        )

        self.addMtext(
            textContent=text,
            textFontHeight=self.STATION_TEXT_HEIGHT,
            textWidth=self.STATION_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByLayer"),
            textLineSpacingDistance=1,
            insertPoint=self.STATION_TEXT_INSERT_POINT,
            style="GEDITXT",
            attachment=6
        )

    def _addCabinetPanel(self):
        '''添加屏柜面板图'''

        cabinet = Cabinet(
            pNum=self.data.get("cabinetPnum"),
            name=self.data.get("cabinetPname"),
            cabinetType=self.data.get("cabinetType")
        )

        calculator = AutoUcalculator(
            existedDeviceList=self._existedDeviceList()
        )

        self._installNewDeviceList(calculator)

        for device in calculator.calculate():
            cabinet.addDevice(device)

        cabinet.toPanel(doc=self.doc).insertInto(
            self.block,
            self.CABINET_INSERT_POINT
        )

    def _existedDeviceList(self) -> List[ExistedDevice]:
        '''获取已有设备列表'''

        deviceNameList: List = self.data.get("panelDeviceNameList")
        deviceAltitudeUList: List = self.data.get("panelDeviceAltitudeUList")
        deviceHeightUList: List = self.data.get("panelDeviceHeightUList")

        return [
            ExistedDevice(rawName, altitudeU, heightU)
            for rawName, altitudeU, heightU in zip(
                deviceNameList,
                deviceAltitudeUList,
                deviceHeightUList
            )
        ]

    def _installNewDeviceList(self, calculator: AutoUcalculator):
        '''安装新增设备列表'''

        deviceTypeList: List = self.data.get("newDeviceTypeList")
        deviceAltitudeUList: List = self.data.get("newDeviceAltitudeUList")

        for deviceType, altitudeU in zip(deviceTypeList, deviceAltitudeUList):
            self._installNewDevice(
                calculator=calculator,
                deviceType=deviceType,
                altitudeU=altitudeU
            )

    def _installNewDevice(
            self,
            calculator: AutoUcalculator,
            deviceType: str,
            altitudeU: int
    ):
        '''安装单个新增设备'''

        if deviceType == self.DEVICE_TYPE_IDN:
            calculator.installIDN(altitudeU=altitudeU)
            return

        if deviceType == self.DEVICE_TYPE_DDN:
            calculator.installDDN(altitudeU=altitudeU)
            return

        if deviceType == self.DEVICE_TYPE_PDU:
            calculator.installPDU(altitudeU=altitudeU)
            return

        if deviceType == self.DEVICE_TYPE_IDF:
            calculator.installIDF(altitudeU=altitudeU)
            return

        raise ValueError(f"未知新增设备类型: {deviceType}")

    def insertInto(
            self,
            layout: Modelspace,
            insertPoint: Vec2
    ):
        '''插入到模型空间'''

        return super().insertInto(layout, insertPoint)