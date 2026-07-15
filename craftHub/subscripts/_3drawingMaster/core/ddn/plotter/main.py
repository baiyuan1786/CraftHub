##########################################################################################################
#   Description: ddn定向式绘图网络， 主绘图器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Dict, List

from ezdxf.document import Drawing

from craftHub.tool import GLog

from ..reader import DataUnitDDN, ReaderDDN
from .substation import DDNsubplotter
from ...common.meta import DDN设备
from ...common.graph import CADColor
from ..link.ddnDevice import DDN设备连接面板图

class DDNmainPlotter:
    '''ddn接入层主绘图器'''

    def __init__(
            self,
            doc: Drawing,
            config: Dict
    ) -> None:
        """初始化主绘图控制器

        :param doc: 文档
        :param config: 配置字典
        """

        self.doc = doc
        self.config = config

        self.excelPath: Path = config["src"]
        self.sheetName: str = config["srcSheet"]
        self.PROJECTNAME = self.PROJECTNAME = config["project"]
        self.DATE = config["date"]

        self.dataUnitList: List[DataUnitDDN] = []
        self.dataUnitFullList: List[DataUnitDDN] = []
        self.drawerList: List[DDNsubplotter] = []

        self._loadData()

    def _loadData(self):
        '''加载ddn绘图数据'''

        errorList = []

        try:
            reader = ReaderDDN(
                excelPath=self.excelPath,
                sheetName=self.sheetName
            )
        except Exception as error:
            raise ValueError(f"读取器 | 加载错误: {error}")

        for index, data in enumerate(reader):
            try:
                self.dataUnitFullList.append(data)
                data.typeCheck()
                self.dataUnitList.append(data)

            except Exception as error:
                errorList.append(
                    f"解析表格 | 解析第{int(index) + 2}行 "
                    f"{data.get('substationName')}时出错: {str(error)}"
                )
                continue

        for error in errorList:
            GLog.logInfo(f"{GLog.RED}{error}{GLog.END}")

        self.dataUnitList.sort(key=lambda data: data.get("drawOrder"))          # type: ignore
        self.dataUnitFullList.sort(key=lambda data: data.get("drawOrder"))      # type: ignore

        GLog.logInfo(f"{GLog.GREEN}共解析成功 {len(self.dataUnitList)} 条数据{GLog.END}")

    def plot(self) -> None:
        '''执行批量绘图，逐个绘制接入层站点，按照drawOrder进行绘图布局'''

        success = 0
        errorList = []
        self.drawerList = []

        if not self.dataUnitList:
            GLog.logInfo("没有数据可绘制")
            return

        GLog.logInfo(f"{GLog.BLUE}ddn绘图器 | 共{len(self.dataUnitList)}个站{GLog.END}")

        for index, data in enumerate(self.dataUnitList, start=1):
            try:
                GLog.logInfo(
                    f"{GLog.BLUE}绘制第 '{index}/{len(self.dataUnitList)}' 个站: "
                    f"{data.get('substationName')}{GLog.END}"
                )

                drawer = DDNsubplotter(
                    doc=self.doc,
                    data=data,
                    config=self.config,
                    PROJECTNAME=self.PROJECTNAME
                )

                self.drawerList.append(drawer)

                drawer.plot()

                drawer.insertInto(
                    self.doc.modelspace(),
                    data.drawOrderToOffset()
                )

                success += 1

                GLog.logInfo(f"第{index}个站绘制完成")

            except Exception as error:
                errorList.append(f"{data.get('substationName')} | {str(error)}")

        if len(errorList) > 0:
            GLog.logInfo(f"{GLog.RED}ddn绘图器 | 共产生了{len(errorList)}个错误{GLog.END}")

            for error in errorList:
                GLog.logInfo(f"{GLog.RED}ddn绘图器 | {error}{GLog.END}")

        else:
            GLog.logInfo(f"{GLog.GREEN}ddn绘图器 | 没有发生错误{GLog.END}")

        if success == 0:
            raise ValueError("没有站被绘制，请检查输入数据库")

        GLog.logInfo(f"{GLog.BLUE}ddn绘图器 | 绘制完成, 共完成 {success} 个站绘制{GLog.END}")
        
    @classmethod
    def setBlockConfig(cls, doc: Drawing, devName: str, heightU: int, panelBlockName: str, connectionBlockName: str):
        '''设置块信息'''
        if panelBlockName not in doc.blocks:
            raise ValueError(f"ddn绘图器 | 设备面板图块未找到: {panelBlockName}")
        if connectionBlockName not in doc.blocks:
            raise ValueError(f"ddn绘图器 | 连接面板图块未找到: {connectionBlockName}")
        
        DDN设备.setDeviceConfig(
            deviceName = devName,
            heightU = heightU,
            blockName = panelBlockName
        )
        DDN设备连接面板图.setDeviceConfig(
            blockName = connectionBlockName,
            deviceText = devName
        )
        