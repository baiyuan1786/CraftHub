##########################################################################################################
#   Description: IDN集成式绘图模块， 主绘图器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .substation import IDNsubPlotter
from ..reader import ReaderIDN, DataUnitIDN, PowerStaLinksReader
from ...common.meta import IDN设备
from ..link import IDN设备连接面板图

from craftHub.tool import GLog

from pathlib import Path
from ezdxf.document import Drawing
from typing import List, Optional, Dict

class IDNmainPlotter:
    '''idn主绘图器'''
    
    def __init__(self,
                 doc: Drawing,
                 config: Dict        
                 ) -> None:
        """初始化主绘图控制器

        :param doc:             文档
        :param config:          配置字典
        """
        self.doc = doc
        self.config = config
        self.excelPath = config["src"]
        self.sheetName = config["srcSheet"]
        self.PROJECTNAME = config["project"]
        self.DATE = config["date"]
        
        self.powerLinkExcelPath = config["powerLink"]
        self.powerLinkSheetName = config["powerLinkSheet"]

        self.dataUnitList: List[DataUnitIDN] = []
        self.dataUnitFullList: List[DataUnitIDN] = []
        self.drawerList: List[IDNsubPlotter] = []
        errorList = []

        # 加载读取器
        try:
            reader = ReaderIDN(excelPath = self.excelPath, sheetName = self.sheetName)
        except Exception as e:
            raise ValueError(f"读取器 | 加载错误: {e}")

        # 校验数据
        for index, data in enumerate(reader):
            try:
                self.dataUnitFullList.append(data)
                data.typeCheck()
                self.dataUnitList.append(data)
            except Exception as e:
                errorList.append(f"解析表格 | 解析第{int(index) + 2}行 {data.get("substationName")}时出错: {str(e)}") # type: ignore
                continue

        # 输出错误信息
        for err in errorList:
            GLog.logInfo(f"{GLog.RED}{err}{GLog.END}")

        # 供电所相关接入
        if self.powerLinkExcelPath and self.powerLinkSheetName:
            self._appendPowerLinks(self.powerLinkExcelPath, self.powerLinkSheetName)

        self.dataUnitList.sort(key = lambda a:a.get("drawOrder"))               # type: ignore
        self.dataUnitFullList.sort(key = lambda a:a.get("drawOrder"))           # type: ignore
        GLog.logInfo(f"{GLog.GREEN}共解析成功 {len(self.dataUnitList)} 条数据{GLog.END}")
        
        
    def _appendPowerLinks(self,
                          powerLinkExcelPath: Path,
                          powerLinkSheetName: str):
        '''附加供电所信息到数据中'''
        
        powerLinks = PowerStaLinksReader(excelPath = Path(powerLinkExcelPath), sheetName = powerLinkSheetName)
        success = 0
        for powerLink in powerLinks:
            for data in self.dataUnitList:
                if powerLink != data:
                    continue

                # 继承ODF屏数据
                if powerLink.accessPanel == "继承" or powerLink.accessPanel == "":
                    powerLink.inheritODFP(data)

                data.append("odfLinkODFPfullNameList", powerLink.accessPanel)
                data.append("odfLinkBoardList", 6)                          # 使用FE/GE口
                data.append("odfLinkUnitNumList", powerLink.accessODF)      # 连接ODF单元
                data.append("odfLinkTerminateStrList", powerLink.powerName) # 目标供电所名 
                data.append("fiberJumpList", powerLink.jumper)              # 跳纤站

                data.typeCheck()
                success += 1
                break
            else:
                GLog.logInfo(f"{GLog.YELLOW}附加供电所 | {powerLink} | 匹配失败， 跳过{GLog.END}")
        
        GLog.logInfo(f"{GLog.GREEN}共附加了 {success} 条供电所数据{GLog.END}")
    
    def plot(self) -> None:
        """执行批量绘图， 逐个绘制接入层站点， 按照drawOrder进行绘图布局"""
        
        success = 0
        errorList = []
        self.drawerList = []
        
        if not self.dataUnitList:
            GLog.logInfo("没有数据可绘制")
            return
        
        GLog.logInfo(f"{GLog.BLUE}idn绘图器 | 共{len(self.dataUnitList)}个站{GLog.END}")

        # 逐个绘图
        for index, data in enumerate(self.dataUnitList, start=1):
            try:                
                GLog.logInfo(f"{GLog.BLUE}绘制第 \'{index}/{len(self.dataUnitList)}\' 个站: {data.get("substationName")}{GLog.END}")
                
                drawer = IDNsubPlotter(doc = self.doc,
                                               data = data,
                                               config = self.config,
                                               PROJECTNAME = self.PROJECTNAME)
                self.drawerList.append(drawer)
                drawer.plot()
                drawer.insertInto(self.doc.modelspace(), data.drawOrderToOffset()) # 按照绘图顺序布局
                success += 1
                
                GLog.logInfo(f"第{index}个站绘制完成")
            except Exception as e:
                errorList.append(f"{data.get("substationName")} | {str(e)}")
            
        # 输出绘制信息
        if len(errorList) > 0:    
            GLog.logInfo(f"{GLog.RED}idn绘图器 | 共产生了{len(errorList)}个错误{GLog.END}")
            for err in errorList:
                GLog.logInfo(f"{GLog.RED}idn绘图器 | {err}{GLog.END}")
        else:
            GLog.logInfo(f"{GLog.GREEN}idn绘图器 | 没有发生错误{GLog.END}")
        
        if success == 0:
            raise ValueError("没有站被绘制，请检查输入数据库")
        
        GLog.logInfo(f"{GLog.BLUE}idn绘图器 | 绘制完成, 共完成 {success} 个站绘制{GLog.END}")

    @classmethod
    def setBlockConfig(cls, doc: Drawing, devName: str, heightU: int, panelBlockName: str, connectionBlockName: str):
        '''设置块信息'''
        if panelBlockName not in doc.blocks:
            raise ValueError(f"idn绘图器 | 设备面板图块未找到: {panelBlockName}")
        if connectionBlockName not in doc.blocks:
            raise ValueError(f"idn绘图器 | 连接面板图块未找到: {connectionBlockName}")
        
        IDN设备.setDeviceConfig(
            deviceName = devName,
            heightU = heightU,
            blockName = panelBlockName
        )
        IDN设备连接面板图.setDeviceConfig(
            blockName = connectionBlockName,
            deviceText = devName
        )
    
        
        