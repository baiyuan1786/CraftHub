##########################################################################################################
#   Description: ddn定向式绘图网络绘图器，站绘图器右图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ezdxf.document import Drawing
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ...common.meta import (
    A3plusIntroduction,
    Cabinet,
    ExistedDevice,
    FrameCabinetA3plus,
    FrameA3plusplus,
    FrameA3plus,
    Legend,
    DDN设备,
)
from ...common.meta.device.autoU import AutoUcalculator
from ..reader import DataUnitDDN

class DDNsubplotter_right(ABC):
    '''ddn定向式绘图网络站绘图器_右图绘图器基类'''

    CONFIG_KEY_DATE = "date"

    CONFIG_KEY_APPROVE = "approve"
    CONFIG_KEY_REVIEW1 = "review1"
    CONFIG_KEY_CHECK = "check"
    CONFIG_KEY_DESIGN = "design"
    CONFIG_KEY_DRAW = "draw"

    CONFIG_KEY_APPROVE_NUM = "approveNum"
    CONFIG_KEY_REVIEW1_NUM = "review1Num"
    CONFIG_KEY_CHECK_NUM = "checkNum"
    CONFIG_KEY_DESIGN_NUM = "designNum"
    CONFIG_KEY_DRAW_NUM = "drawNum"

    DEFAULT_CONFIG_TEXT = ""

    IS_EXPANSION = False

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            config: Dict[str, Any],
            PROJECTNAME: str,
            DRAWINGNAME: str,
    ) -> None:
        """ddn定向式绘图网络站绘图器_右图绘图器初始化

        :param doc:         CAD文档
        :param data:        数据单元
        :param config:      绘图配置字典
        :param PROJECTNAME: 项目名称
        :param DRAWINGNAME: 图纸名称
        """

        self.doc = doc
        self.data = data
        self.config = config
        self.GCNisExpansion = self.IS_EXPANSION

        self._checkPanelDeviceData(data)

        self.frame = self._buildFrame(
            doc=doc,
            data=data,
            PROJECTNAME=PROJECTNAME,
            DRAWINGNAME=DRAWINGNAME
        )

        self.addUsedCabinet(data)
        self.addFrameCabinet()
        self.addNewDevicePanel(data)
        self.addLegend()
        self.addIntroduction()

    @abstractmethod
    def _buildFrame(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            PROJECTNAME: str,
            DRAWINGNAME: str
    )->Any:
        '''构建图框'''

        pass

    @abstractmethod
    def _cabinetPoint(self) -> Vec2:
        '''获取屏柜插入点'''

        pass

    @abstractmethod
    def _frameCabinetPoint(self) -> Vec2:
        '''获取屏柜外框插入点'''

        pass

    @abstractmethod
    def _newDevicePanelPoint(self) -> Vec2:
        '''获取新增设备面板图插入点'''

        pass

    @abstractmethod
    def _legendPoint(self) -> Vec2:
        '''获取图例插入点'''

        pass

    @abstractmethod
    def _introductionPoint(self) -> Vec2:
        '''获取说明插入点'''

        pass

    def addUsedCabinet(self, data: DataUnitDDN):
        '''增加被使用的屏柜类到图框中'''

        deviceNameList: List = data.get("panelDeviceNameList")
        deviceAltitudeUList: List = data.get("panelDeviceAltitudeUList")
        deviceHeightUList: List = data.get("panelDeviceHeightUList")

        cabinet = Cabinet(
            pNum=data.get("DDNInstallPnum"),
            name=data.get("DDNInstallPName"),
            cabinetType=data.get("cabinetType"),
            withGroudLine=True  # 绘制接地线
        )

        existedDeviceList: List[ExistedDevice] = [
            ExistedDevice(rawName, altitude, height)
            for rawName, altitude, height in zip(
                deviceNameList,
                deviceAltitudeUList,
                deviceHeightUList
            )
        ]

        calculator = AutoUcalculator(existedDeviceList=existedDeviceList)

        calculator.installPDU(altitudeU=data.get("DDNPDUAltitudeU"))
        calculator.installPDU(altitudeU=data.get("IDNPDUAltitudeU"))
        calculator.installDDN(altitudeU=data.get("DDNAltitudeU"))
        calculator.installIDN(altitudeU=data.get("IDNAltitudeU"))
        calculator.installIDF(altitudeU=data.get("edgedIDFaltitudeU"))

        deviceList = calculator.calculate()

        for device in deviceList:
            cabinet.addDevice(device)

        self.frame.grid(
            cabinet.toPanel(doc=self.doc),
            self._cabinetPoint()
        )

    def addFrameCabinet(self):
        '''增加屏柜外框'''

        self.frame.grid(
            FrameCabinetA3plus(doc=self.doc),
            self._frameCabinetPoint()
        )

    def addNewDevicePanel(self, data: DataUnitDDN):
        '''增加新增设备面板图到图框中'''

        device = DDN设备(
            altitudeU=data.get("DDNAltitudeU")
        )

        self.frame.grid(
            device.toDevicePanel(
                doc=self.doc,
                isExpansion=self.GCNisExpansion
            ),
            self._newDevicePanelPoint()
        )

    def addLegend(self):
        '''增加图例'''

        self.frame.grid(
            Legend(doc=self.doc),
            self._legendPoint()
        )

    def addIntroduction(self):
        '''增加说明'''

        self.frame.grid(
            A3plusIntroduction(doc=self.doc, board=True),
            self._introductionPoint()
        )

    def insertInto(self, layout: Modelspace, insertPoint: Vec2):
        '''将图框插入到模型空间'''

        self.frame.insertInto(layout, insertPoint)

    def _frameKwargs(
            self,
            data: DataUnitDDN,
            PROJECTNAME: str,
            DRAWINGNAME: str
    ) -> Dict[str, Any]:
        '''获取图框通用参数'''

        return {
            "APPROVE": self._getConfigStr(self.CONFIG_KEY_APPROVE),
            "APPROVENUM": self._getConfigStr(self.CONFIG_KEY_APPROVE_NUM),
            "REVIEW1": self._getConfigStr(self.CONFIG_KEY_REVIEW1),
            "REVIEW1NUM": self._getConfigStr(self.CONFIG_KEY_REVIEW1_NUM),
            "CHECK": self._getConfigStr(self.CONFIG_KEY_CHECK),
            "CHECKNUM": self._getConfigStr(self.CONFIG_KEY_CHECK_NUM),
            "DESIGN": self._getConfigStr(self.CONFIG_KEY_DESIGN),
            "DESIGNNUM": self._getConfigStr(self.CONFIG_KEY_DESIGN_NUM),
            "DRAW": self._getConfigStr(self.CONFIG_KEY_DRAW),
            "DRAWNUM": self._getConfigStr(self.CONFIG_KEY_DRAW_NUM),
            "PROJECTNAME": PROJECTNAME,
            "DRAWINGNAME": DRAWINGNAME,
            "DRAWINGNUMBER": data.get("DRAWINGNUMBER2"),
            "DATE": self._getConfigStr(self.CONFIG_KEY_DATE),
        }

    def _checkPanelDeviceData(self, data: DataUnitDDN):
        '''检查设备描述参数'''

        deviceNameList: List = data.get("panelDeviceNameList")
        deviceAltitudeUList: List = data.get("panelDeviceAltitudeUList")
        deviceHeightUList: List = data.get("panelDeviceHeightUList")

        if (
                len(deviceNameList) != len(deviceAltitudeUList)
                or len(deviceAltitudeUList) != len(deviceHeightUList)
        ):
            raise ValueError(
                "输入的设备描述参数长度不一致: "
                f"deviceNameList:{len(deviceNameList)}, "
                f"deviceAltitudeUList:{len(deviceAltitudeUList)}, "
                f"deviceHeightUList:{len(deviceHeightUList)}"
            )

    def _getConfigStr(self, key: str) -> str:
        '''从配置中读取字符串参数'''

        value = self.config.get(key, self.DEFAULT_CONFIG_TEXT)

        if value is None:
            return self.DEFAULT_CONFIG_TEXT

        return str(value)

