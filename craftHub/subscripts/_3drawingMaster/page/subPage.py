##########################################################################################################
#   Description: 页面创建函数
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..subPath import PATH_DATA
from ..ui.Ui_drawingMaster import Ui_Form
from ..core import DrawingMasterCore
from .setPage import DrawingMasterSetPage, DrawingMasterConfig
from .plotWorker import PlotWorker

from craftHub.tool import GLog, tryDo
from page import Page

from pathlib import Path
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QButtonGroup)
import os
from typing import Optional

class DrawingMasterPage(Page, Ui_Form):
    '''绘图大师主页面'''
    
    def __init__(self, title: str):
        # 初始化
        Page.__init__(self, title, PATH_DATA)   # 页面
        Ui_Form.__init__(self)                  # UI
        self.setupUi(self)                      # 加载UI
        
        self.core = None                        # 绘图核心
        self.load()
        
    @tryDo(title = "初始化绘图器", info = "初始化绘图器成功")
    def _init(self):
        '''初始化绘图器'''
        self.core = DrawingMasterCore(config = self.getConfig()) 
    
    @property
    def drawcore(self):
        '''获取绘图核心'''
        if self.core is None:
            raise ValueError("绘图器还未初始化")
        return self.core
        
    def getConfig(self):
        '''获取所有参数组成的字典'''
        
        # 源文件
        srcFile: Optional[Path] = self.readPara(self.lineEdit_src, True, True, "源文件不存在") # type: ignore
        if srcFile is None:
            raise FileNotFoundError("请输入数据库文件")
        if not srcFile.suffix in (".xlsx", ".xlsm"):
            raise ValueError("源文件夹必须使用xlsx或者xlsm表格")
        
        srcSheet: Optional[str] = self.readPara(self.lineEdit_sheetName, False, False) # type: ignore
        
        # 参考文件
        try:
            cableLayExcel = self.readPara(self.lineEdit_cablelay, True, True, "参考线缆敷设表未找到")
            cableLaySheet = self.readPara(self.lineEdit_cablelaySheet, False, False)
        except FileNotFoundError:
            GLog.logInfo("线缆敷设表路径不存在, 将路径设置为None")
            cableLayExcel = None
            cableLaySheet = None

        try:
            netJumpExcel = self.readPara(self.lineEdit_netJump, True, True, "参考跳纤链路表未找到")
            netJumpSheet = self.readPara(self.lineEdit_netJumpSheet, False, False)
        except FileNotFoundError:
            GLog.logInfo("线缆敷设表_跳纤链路路径不存在, 将路径设置为None")
            netJumpExcel = None
            netJumpSheet = None
            
        try:
            netLinkExcel = self.readPara(self.lineEdit_netLink, True, True, "参考组网链路表未找到")
            netLinkSheet = self.readPara(self.lineEdit_netLinkSheet, False, False)
        except FileNotFoundError:
            GLog.logInfo("组网链路表路径不存在, 将路径设置为None")
            netLinkExcel = None
            netLinkSheet = None
            
        try:
            powerLinkExcel = self.readPara(self.lineEdit_powerLink, True, True, "供电所接入表未找到")
            powerLinkSheet = self.readPara(self.lineEdit_powerLinkSheet, False, False)
        except FileNotFoundError:
            GLog.logInfo("组网链路表路径不存在, 将路径设置为None")
            powerLinkExcel = None
            powerLinkSheet = None
        
        # 输出路径
        dest: Optional[Path] = self.readPara(self.lineEdit_dst, True, True, "输出路径不存在") # type: ignore
        if dest is None:
            raise FileNotFoundError("请输入输出路径")
        elif not dest.is_dir():
            raise ValueError(f"输出路径不是一个文件夹: \'{dest}\'")

        # 其他设置
        setConfig = DrawingMasterConfig.getConfig()
        setConfig["convas"] = Path(setConfig["convas"]) # 转换为路径对象
        convas = setConfig["convas"]
        
        if str(convas) == ".":
            raise FileNotFoundError("请输入画布文件！")
        if not convas.exists():
            raise FileNotFoundError("画布不存在")
        if not convas.suffix == ".dxf":
            raise ValueError("绘图画布必须使用dxf文件")

        myConfig = {
            "src": srcFile,
            "srcSheet": srcSheet,
            "dest": dest,
            "cableLay": cableLayExcel,
            "cableLaySheet": cableLaySheet,
            "netJump": netJumpExcel,
            "netJumpSheet": netJumpSheet,
            "netLink": netLinkExcel,
            "netLinkSheet": netLinkSheet,
            "powerLink": powerLinkExcel,
            "powerLinkSheet": powerLinkSheet,
        }
        myConfig.update(setConfig)
        
        if myConfig["exportFormat"] == "dxf" and (myConfig["insertCableLay"] or myConfig["insertNetLink"]):
            raise ValueError("导出格式设置为dxf时无法插入表格， 请修改导出格式")
        
        return myConfig 

    @tryDo(title = "选择源文件夹")
    def _selectSrc(self):
        '''选择源文件夹'''
        filePath, _ = QFileDialog.getSaveFileName(
            parent = None,                      # 父窗口
            caption = "选择数据库表格",          # 对话框标题
            directory = "",                     # 初始目录
        ) 
        
        if filePath:
            self.lineEdit_src.setText(filePath)

    @tryDo(title = "选择输出路径")
    def _selectOutput(self):
        '''选择输出路径'''
        folderName = QFileDialog.getExistingDirectory(
            parent = None,                      # 父窗口
            caption = "选择输出路径",            # 对话框标题
            directory = "",                     # 初始目录
            options = QFileDialog.Option.ShowDirsOnly
        ) 
        
        if folderName:
            self.lineEdit_dst.setText(folderName)
    
    @tryDo(title = "打开源文件夹")
    def _openSrc(self):
        srcDir = self.lineEdit_src.text()
        os.startfile(srcDir)
        
    @tryDo(title = "打开目标文件夹")
    def _openDst(self):
        dstDir = self.lineEdit_dst.text()
        os.startfile(dstDir)    
            
    @tryDo(title = "打开设置")   
    def _set(self):
        '''调整工具设置'''
        DrawingMasterSetPage(parent = self).exec()

    def _onPlotFinished(self):
        self.pushButton_trans.setEnabled(True)
        GLog.logInfo(f"{GLog.GREEN}绘图完成{GLog.END}")

    def _onPlotError(self, errMsg: str):
        self.pushButton_trans.setEnabled(True)
        GLog.logInfo(f"绘图失败: {errMsg}")

    @tryDo(title = "DrawingMaster转换CADW文件")
    def _trans(self):
        '''表格转换DXF'''

        destFolder = Path(self.lineEdit_dst.text())
        if str(destFolder) == ".":
            raise FileNotFoundError("请输入输出目录")
        if not destFolder.exists():
            raise FileNotFoundError("目标目录不存在")

        # 禁用按钮，防止重复点击
        self.pushButton_trans.setEnabled(False)

        self.plotWorker = PlotWorker(self.drawcore)
        self.plotWorker.finishedSignal.connect(self._onPlotFinished)
        self.plotWorker.errorSignal.connect(self._onPlotError)
        self.plotWorker.start()

    @tryDo(title = "导出表格")
    def _toTable(self):
        '''导出表格'''
        self.drawcore.toTable()