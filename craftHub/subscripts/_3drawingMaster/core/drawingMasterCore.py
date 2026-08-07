##########################################################################################################
#   Description: 绘图大师类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Type

import ezdxf
import win32com.client
from ezdxf.math import Vec2

from craftHub.tool import GLog

from .common.graph import NewBlock, CADColor
from .common.graph.line import LineTypeMnger
from .common.table import TableInserter
from .common.reader import DataUnit
from .common.meta import Legend, FrameA3plus, FrameA3plusplus
from .common.meta import IDN设备, DDN设备
from .idn import IDNTableExporter, IDNmainPlotter
from .ddn import DDNTableExporter, DDNmainPlotter
from .cabinet import Cabinet_mainplt

@dataclass(frozen=True)
class OleTableConfig:
    '''OLE表格插入配置'''

    enableConfigKey: str    # 使动键
    logText: str
    excelConfigKey: str     # excel键
    sheetConfigKey: str     # sheet键
    startCol: str           # 开始列
    endCol: str             # 结束列
    oleInsertPointOffset: Vec2 # 插入偏移： 上中相对左下
    oleWidth: float            # 宽度
    maxHeight: float           # 最大高度


@dataclass(frozen=True)
class PlotterProfile:
    '''绘图器配置档案'''

    plotterClass: Type[Any]                                 # 绘图器类
    tableExporterClass: Optional[Type[Any]] = None          # 表格导出器类
    oleTableConfigList: tuple[OleTableConfig, ...] = ()     # 导出表格参数列表


class DrawingMasterCore:
    '''绘图大师内核'''

    CONFIG_KEY_PLOTTER = "plotter"
    CONFIG_KEY_CONVAS = "convas"
    CONFIG_KEY_BLOCK_COUNT = "blockCount"
    CONFIG_KEY_DEST = "dest"
    CONFIG_KEY_OLE_TYPE = "oleType"

    DXF_SUFFIX = ".dxf"
    DWG_SUFFIX = ".dwg"

    SAVE_FILE_PREFIX = "DrawingMaster"

    AUTOCAD_DISPATCH_NAME = "AutoCAD.Application"
    AUTOCAD_SAVE_WAIT_SECOND = 5

    OLE_TYPE_EMBED = "OLE_EMBED"
    OLE_TYPE_BITMAP = "xlBitmap"
    OLE_TYPE_PICTURE = "xlPicture"
    OLE_TYPES = (OLE_TYPE_EMBED, OLE_TYPE_BITMAP, OLE_TYPE_PICTURE)
    
    EXPORT_FORMAT_DXF = "dxf"
    EXPORT_FORMAT_DWG = "dwg"
    EXPORT_FORMATS = (EXPORT_FORMAT_DXF, EXPORT_FORMAT_DWG)

    LAYOUT_FORMATS = DataUnit.LAYOUT_FORMATS

    # idn配置
    IDN_NET_LINK_TABLE_CONFIG = OleTableConfig(
        enableConfigKey="insertNetLink",
        logText="idn集成式绘图网络 | 尝试插入组网链路表",
        excelConfigKey="netLink",
        sheetConfigKey="netLinkSheet",
        startCol="B",
        endCol="J",
        oleInsertPointOffset=Vec2(1100, 270),
        oleWidth=200,
        maxHeight=44
    )

    IDN_CABLE_LAY_TABLE_CONFIG = OleTableConfig(
        enableConfigKey="insertCableLay",
        logText="idn集成式绘图网络 | 尝试插入线缆敷设表",
        excelConfigKey="cableLay",
        sheetConfigKey="cableLaySheet",
        startCol="B",
        endCol="J",
        oleInsertPointOffset=Vec2(684, 118),
        oleWidth=244,
        maxHeight=112
    )

    # ddn配置
    DDN_NET_LINK_TABLE_CONFIG = OleTableConfig(
        enableConfigKey="insertNetLink",
        logText="ddn定向式绘图网络 | 尝试插入组网链路表",
        excelConfigKey="netLink",
        sheetConfigKey="netLinkSheet",
        startCol="B",
        endCol="J",
        oleInsertPointOffset=Vec2(914, 41),
        oleWidth=215,
        maxHeight=33
    )

    DDN_CABLE_LAY_TABLE_CONFIG = OleTableConfig(
        enableConfigKey="insertCableLay",
        logText="ddn定向式绘图网络 | 尝试插入线缆敷设表",
        excelConfigKey="cableLay",
        sheetConfigKey="cableLaySheet",
        startCol="B",
        endCol="K",
        oleInsertPointOffset=Vec2(675, 118),
        oleWidth=229,
        maxHeight=112
    )

    # 参数字典， 新的绘图器在此注册
    PLOTTER_PROFILE_DICT = {
        "idn集成式绘图网络绘图器": PlotterProfile(
            plotterClass=IDNmainPlotter,
            tableExporterClass=IDNTableExporter,
            oleTableConfigList=(
                IDN_NET_LINK_TABLE_CONFIG,
                IDN_CABLE_LAY_TABLE_CONFIG,
            )
        ),

        "ddn定向式绘图网络绘图器": PlotterProfile(
            plotterClass=DDNmainPlotter,
            tableExporterClass=DDNTableExporter,
            oleTableConfigList=(
                DDN_NET_LINK_TABLE_CONFIG,
                DDN_CABLE_LAY_TABLE_CONFIG,
            )
        ),
        "屏柜绘图器": PlotterProfile(
            plotterClass=Cabinet_mainplt,
            tableExporterClass=None,
            oleTableConfigList=()
        )
        
    }

    def __init__(self, config: dict):
        '''加载核心，将所有配置进行加载'''

        self.config = config
        self.lineTypeMnger = LineTypeMnger()

        self.plotterName = self._getPlotterName()
        self.plotterProfile = self._getPlotterProfile(self.plotterName)

        self._resetBlockCount()
        DataUnit.setLayoutFormat(config["layout"])
        self.doc = self._loadDoc()
        self._initLineType()
        self.setBlockConfig(config)

        self.plotter = self._createPlotter()
        
        #for key, value in config.items():
            #GLog.logInfoWithNoTime(f"key: {key}, value: {value}")

        GLog.logInfo(f"{GLog.GREEN}绘图器 '{self.plotterName}' 初始化成功{GLog.END}")

    def plot(self):
        '''绘制图形'''

        savePath = self._getSavePath()
        self._checkSavePath(savePath)
        self._checkPlotter()

        self.plotter.plot()
        self.doc.saveas(savePath)

        if self.config["exportFormat"] == self.EXPORT_FORMAT_DWG:
            savePath = self.dxfToDwg(savePath)
        else:
            pass

        GLog.logInfo(f"{GLog.GREEN}绘图文件已保存至 '{savePath}'{GLog.END}")

        self._insertOleTables(savePath)
        self._openResultFile(savePath)

    def toTable(self):
        '''导出所有表格'''

        if self.plotterProfile.tableExporterClass is None:
            GLog.logInfo(f"{GLog.YELLOW}当前绘图器未配置表格导出器，跳过表格导出{GLog.END}")
            return

        exporter = self.plotterProfile.tableExporterClass(
            dataUnitFullList=self._getPlotterDataUnitFullList(),
            dataUnitList=self._getPlotterDataUnitList(),
            config=self.config
        )
        exporter.export()
        
    def setBlockConfig(self, config: dict):
        '''设置所有块属性'''

        # 绘图器定义
        if config[self.CONFIG_KEY_PLOTTER] in ["idn集成式绘图网络绘图器", "ddn定向式绘图网络绘图器"]:
            IDNmainPlotter.setBlockConfig(doc = self.doc, 
                                devName = config["idnName"], 
                                heightU = config["idnHeightU"], 
                                panelBlockName = config["idnPanel"], 
                                connectionBlockName = config["idnConnection"])
            
            # DDN属性
            DDNmainPlotter.setBlockConfig(doc = self.doc, 
                                devName = config["ddnName"], 
                                heightU = config["ddnHeightU"], 
                                panelBlockName = config["ddnPanel"], 
                                connectionBlockName = config["ddnConnection"])
            
            # 图框属性
            FrameA3plusplus.setFrameName(config["frameLeft"])
            FrameA3plus.setFrameName(config["frameRight"])
            
            # 其他属性
            Legend.setBlockName(config["legend"])

        elif config[self.CONFIG_KEY_PLOTTER] in ["屏柜绘图器"]:
            IDN设备.setDeviceConfig(
                deviceName = config["idnName"],
                heightU = config["idnHeightU"],
                blockName = None
            )
            DDN设备.setDeviceConfig(
                deviceName = config["ddnName"],
                heightU = config["ddnHeightU"],
                blockName = None
            )
        

    @staticmethod
    def dxfToDwg(dxfPath: Path) -> Path:
        '''DXF转换DWG'''

        GLog.logInfo(f"{GLog.BLUE}导出为DWG格式 | '{dxfPath}'{GLog.END}")

        acad = win32com.client.Dispatch(DrawingMasterCore.AUTOCAD_DISPATCH_NAME)
        acadDoc = acad.Documents.Open(str(dxfPath))

        dwgPath = dxfPath.with_suffix(DrawingMasterCore.DWG_SUFFIX)

        try:
            time.sleep(DrawingMasterCore.AUTOCAD_SAVE_WAIT_SECOND)
            acadDoc.SaveAs(str(dwgPath))
            time.sleep(DrawingMasterCore.AUTOCAD_SAVE_WAIT_SECOND)
        finally:
            acadDoc.Close(False)

        GLog.logInfo(f"{GLog.GREEN}转换成功 | '{dwgPath}'{GLog.END}")

        if dxfPath.exists():
            dxfPath.unlink()

        return dwgPath

    def _getPlotterName(self) -> str:
        '''获取绘图器名称'''

        plotterName = self.config[self.CONFIG_KEY_PLOTTER]

        if plotterName not in self.PLOTTER_PROFILE_DICT:
            raise ValueError(f"{plotterName} 暂不支持")

        return plotterName

    def _getPlotterProfile(self, plotterName: str) -> PlotterProfile:
        '''获取绘图器配置档案'''

        return self.PLOTTER_PROFILE_DICT[plotterName]

    def _resetBlockCount(self):
        '''重置块计数器'''

        blockCount = self.config[self.CONFIG_KEY_BLOCK_COUNT]
        NewBlock.setBlockCount(blockCount)

    def _loadDoc(self):
        '''加载DXF画布'''

        convas = self.config[self.CONFIG_KEY_CONVAS]
        doc = ezdxf.readfile(convas)  # type: ignore

        self._clearModelspaceEntities(doc)

        return doc

    def _clearModelspaceEntities(self, doc):
        '''清空模型空间实体，但保留块定义'''

        modelspace = doc.modelspace()
        entityList = list(modelspace)

        entityTypeCountDict = {}

        for entity in entityList:
            entityType = entity.dxftype()
            entityTypeCountDict[entityType] = entityTypeCountDict.get(entityType, 0) + 1

            modelspace.delete_entity(entity)

        if len(entityList) == 0:
            GLog.logInfo(f"{GLog.BLUE}DXF画布模型空间无实体，无需清理{GLog.END}")
            return

        GLog.logInfo(f"{GLog.YELLOW}已清空DXF画布模型空间实体，共 {len(entityList)} 个{GLog.END}")

        for entityType, count in entityTypeCountDict.items():
            GLog.logInfo(f"    - {entityType}: {count}")

    def _initLineType(self):
        '''初始化线型'''

        self.lineTypeMnger.addToDoc(doc=self.doc)

    def _createPlotter(self):
        '''创建绘图器'''

        return self.plotterProfile.plotterClass(
            doc=self.doc,
            config=self.config
        )

    def _getSavePath(self) -> Path:
        '''获取保存路径'''

        destFolder = Path(self.config[self.CONFIG_KEY_DEST])
        saveName = f"{self.SAVE_FILE_PREFIX}_{GLog.date()}{self.DXF_SUFFIX}"

        return destFolder / saveName

    def _checkSavePath(self, savePath: Path):
        '''检查保存路径'''

        if not savePath.parent.is_dir():
            raise ValueError("输入的目标路径不是文件夹")

        if savePath.exists():
            raise FileExistsError(f"保存路径已存在 '{savePath}'")

        if not savePath.parent.exists():
            raise FileNotFoundError(f"保存路径文件夹不存在 '{savePath.parent}'")

    def _checkPlotter(self):
        '''检查绘图器是否合法'''

        if not hasattr(self.plotter, "plot"):
            raise AttributeError("绘图器没有实现方法plot")

    def _insertOleTables(self, savePath: Path):
        '''插入所有OLE表格'''

        for oleTableConfig in self.plotterProfile.oleTableConfigList:
            if not self.config.get(oleTableConfig.enableConfigKey, False):
                continue

            self._insertOleTable(savePath, oleTableConfig)

    def _insertOleTable(self, savePath: Path, oleTableConfig: OleTableConfig):
        '''插入单个OLE表格'''

        GLog.logInfo(f"{GLog.YELLOW}警告 | 你正在使用OLE插入功能，运行期间请勿操作电脑, 请关闭多余程序， CAD响应过慢将导致插入失败！{GLog.END}")
        GLog.logInfo(f"{GLog.BLUE}{oleTableConfig.logText}{GLog.END}")

        inserter = TableInserter(
            DXFpath=savePath,
            insertExcel=self.config[oleTableConfig.excelConfigKey],
            insertSheet=self.config[oleTableConfig.sheetConfigKey],
            dataList=self._getPlotterDataUnitList(),
            startCol=oleTableConfig.startCol,
            endCol=oleTableConfig.endCol,
            oleInsertPointOffset=oleTableConfig.oleInsertPointOffset,
            oleWidth=oleTableConfig.oleWidth
        )

        inserter.insertOLE(
            MaxHeight=oleTableConfig.maxHeight, # type: ignore
            insertType=self.config[self.CONFIG_KEY_OLE_TYPE]
        )

    def _getPlotterDataUnitList(self):
        '''获取绘图器有效数据单元列表'''

        if not hasattr(self.plotter, "dataUnitList"):
            raise AttributeError("当前绘图器没有 dataUnitList 属性，无法执行表格相关操作")

        return self.plotter.dataUnitList

    def _getPlotterDataUnitFullList(self):
        '''获取绘图器完整数据单元列表'''

        if not hasattr(self.plotter, "dataUnitFullList"):
            raise AttributeError("当前绘图器没有 dataUnitFullList 属性，无法执行表格导出操作")

        return self.plotter.dataUnitFullList

    @staticmethod
    def _openResultFile(savePath: Path):
        '''打开绘图结果文件'''

        os.startfile(savePath)