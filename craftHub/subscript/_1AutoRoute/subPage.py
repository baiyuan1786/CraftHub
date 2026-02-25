##########################################################################################################
#   Description: 自动路由定位工具页面创建函数
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .subPath import PATH_SUB_ROOT, PATH_TEMPSAVE, PATH_DATA
from .reader import MapReader, TransmissionSegmentReader
from .router import PowerGridGraph
from .business import Businesses

from ui.autoRoute.Ui_autoRoute import Ui_AutoRoute
from craftHub.tool import gLog, tryDo
from page import Page

import os
from pathlib import Path
from typing import Optional, List, Tuple
from PyQt6.QtWidgets import (QTabWidget, QPushButton, QWidget, QGridLayout, QLineEdit, QFileDialog,
                             QLabel, QComboBox, QMessageBox, QPlainTextEdit, QToolButton, QMenu, QSizePolicy,
                             QCheckBox)
from PyQt6.QtGui import QAction

PATH_DOC = PATH_SUB_ROOT / "doc"

class AutoRoutePage(Page, Ui_AutoRoute):
    '''自动化路由计算器页面构建'''
    
    def __init__(self, title: str):
        Page.__init__(self, title, PATH_DATA)
        Ui_AutoRoute.__init__(self)
        self.setupUi(self)
        
        self.graph: Optional[PowerGridGraph] = None   # 电力网图
        self.businesses: Optional[Businesses] = None  # 业务群
        
        # 工具按钮
        menu = QMenu()
        action1 = QAction("打开工具暂存目录", menu)
        action1.triggered.connect(lambda: os.startfile(str(PATH_TEMPSAVE))) # 打开工具暂存目录
        menu.addAction(action1)
        
        self.TOOLBUTTON_menu.setMenu(menu)
        self.COMBOBOX_counts.addItems(["1", "2", "3", "4", "5"])
        self.COMBOBOX_counts.setCurrentText("3");
        self.COMBOBOX_endSta.setEditable(True)
        self.COMBOBOX_startSta.setEditable(True)
        self.load()

    @tryDo(title = "选择源文件")
    def _selectSrc(self):
        '''选择地图'''
        self.save()
        
        # 选择文件并读进去
        fileName, _ = QFileDialog.getOpenFileName(
            parent = None,                      # 父窗口
            caption = "选择地图文件或传输段文件",            # 对话框标题
            directory = str(PATH_DOC),          # 初始目录
            filter = "表格文件 (*.xlsx);;图片文件 (*.png);;所有文件 (*.*)"  # 文件过滤器
        ) 
        
        if fileName:
            self.LINEEDIT_source.setText(fileName)
            
    @tryDo(title = "选择邻接表")
    def _selectAdjList(self):
        '''选择邻接表'''
        fileName, _ = QFileDialog.getOpenFileName(
            parent = None,                          # 父窗口
            caption = "选择邻接表文件",              # 对话框标题
            directory = str(PATH_DOC),              # 初始目录
            filter = "表格 (*.xlsx);;所有文件 (*.*)"  # 文件过滤器
        ) 
        
        if fileName:
            self.LINEEDIT_adjList.setText(fileName)
            
    @tryDo(title = "选择跳纤链路表")
    def _selectChainList(self):
        '''选择跳纤链路表'''
        fileName, _ = QFileDialog.getOpenFileName(
            parent = None,                          # 父窗口
            caption = "选择跳纤链路表",              # 对话框标题
            directory = str(PATH_DOC),              # 初始目录
            filter = "表格 (*.xlsx);;所有文件 (*.*)"  # 文件过滤器
        ) 
        
        if fileName:
            self.LINEEDIT_chainList.setText(fileName)
        
    @tryDo(title = "选择业务表")
    def _selectBusiness(self):
        '''选择业务表'''
        fileName, _ = QFileDialog.getOpenFileName(
            parent = None,                          # 父窗口
            caption = "选择业务表",              # 对话框标题
            directory = str(PATH_DOC),              # 初始目录
            filter = "表格 (*.xlsx);;所有文件 (*.*)"  # 文件过滤器
        ) 
        
        if fileName:
            self.LINEEDIT_business.setText(fileName)
            
    @tryDo(title = "转换邻接表")
    def _transToAdj(self):
        '''转换为邻接表'''

        srcPath = Path(self.LINEEDIT_source.text())
        if str(srcPath) == '.':
            raise FileNotFoundError(f"请输入地图文件或者传输段文件")
        if not srcPath.exists():
            raise FileNotFoundError(f"File \'{srcPath}\' not found")
        if srcPath.suffix not in  (".png", ".xlsx"):
            raise FileNotFoundError(f"File \'{srcPath}\' is not png file or xlsx file")

        # 调用reader获取邻接表
        if srcPath.suffix == ".png":
            raise TypeError("处理地图文件功能暂不可用")
            
            reader = MapReader(imagePath = srcPath)
            reader.statics()
            reader.plot(saveFolder = PATH_TEMPSAVE, isOpen = True)
            reader.toExcel(saveFolder = PATH_TEMPSAVE, isOpen = True)
        elif srcPath.suffix == ".xlsx":
            reader = TransmissionSegmentReader(srcPath = srcPath)
            reader.toExcel(saveFolder = PATH_TEMPSAVE, isOpen = True)

    @tryDo(title = "初始化拓扑")
    def _initGraph(self):
        '''读取邻接表'''
        if self.graph is not None:
            reply = QMessageBox.information(
                self,
                "初始化拓扑图",
                "要重新初始化拓扑图吗?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        adjFilePath = Path(self.LINEEDIT_adjList.text())
        if str(adjFilePath) == '.':
            self._selectAdjList()
            adjFilePath = Path(self.LINEEDIT_adjList.text())
            if str(adjFilePath) == '.':
                return
  
        if not adjFilePath.exists():
            raise FileNotFoundError(f"邻接表不存在 \'{adjFilePath}\'")
        if  adjFilePath.suffix != ".xlsx":
            raise FileNotFoundError(f"邻接表不是xlsx格式 \'{adjFilePath}\'")
        
        self.graph = PowerGridGraph(excelPath = adjFilePath)
        
        # 插入组合框
        names = self.graph.substationNames()
        self.COMBOBOX_endSta.clear()
        self.COMBOBOX_endSta.addItems(names)
        
        self.COMBOBOX_startSta.clear()
        self.COMBOBOX_startSta.addItems(names)
        
        QMessageBox.information(self,
                            "初始化拓扑图",
                            "初始化拓扑图完成")

    @tryDo(title = "初始化业务表")
    def _initBusiness(self):
        '''初始化业务表'''
        if self.businesses is not None:
            reply = QMessageBox.information(
                self,
                "初始化业务表",
                "要重新初始化业务表吗?",
                QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        businessPath = Path(self.LINEEDIT_business.text())
        if str(businessPath) == '.':
            self._selectAdjList()
            businessPath = Path(self.LINEEDIT_business.text())
            if str(businessPath) == '.':
                return

        if not businessPath.exists():
            raise FileNotFoundError(f"业务表不存在 \'{businessPath}\'")
        if  businessPath.suffix != ".xlsx":
            raise FileNotFoundError(f"业务表不是xlsx格式 \'{businessPath}\'")
        
        self.businesses = Businesses(filePath = businessPath)
        self.businesses.statics()

        QMessageBox.information(self,
                                "初始化业务",
                                "初始化业务表完成")

    @tryDo(title = "手动计算路由")
    def _calByHand(self):
        '''手动计算路由'''
        
        if self.graph is None:
            raise Exception("还没有初始化拓扑")
        
        gLog.enter()
        gLog.logInfo(f"Try calculate path")

        minHops, minPaths = self.graph.findSeveralPaths(startName = self.COMBOBOX_startSta.currentText().strip(),
                                                        endName = self.COMBOBOX_endSta.currentText().strip(),
                                                        forbiddenPaths = self._getForbiddenPaths(),
                                                        maxCount = int(self.COMBOBOX_counts.currentText().strip()),
                                                        onlyAson = self.CHECKBOX_onlyAson.isChecked())

        self.TEXTEDIT_outPut.clear()
        for hop, minPath in zip(minHops, minPaths):
            pathStr = self.graph.pathToStr(minPath)
            pathStrFiber = self.graph.pathToStr(minPath, True)

            self.TEXTEDIT_outPut.insertPlainText(f"Path: \'{pathStr}\', hop: {hop}\n")
            self.TEXTEDIT_outPut.insertPlainText(f"FiberPath: \'{pathStrFiber}\', hop: {hop}\n")
            gLog.logInfo(f"Get Path: \'{pathStr}\', hop: {hop}")

    @tryDo(title = "自动路由计算")
    def _calAuto(self):
        
        if self.graph is None:
            raise Exception("还没有初始化拓扑")
        if self.businesses is None:
            raise Exception("还没有初始化业务表")

        # 计算业务表
        self.businesses.calculate(graph = self.graph,
                                  forbiddenPaths = self._getForbiddenPaths(),
                                  savePath = PATH_TEMPSAVE / f"business_{gLog.date()}.xlsx")
        
        
    def _getForbiddenPaths(self):
        '''获取禁用路径'''
        forbiddenPaths: List[List[str]] = []
        rawText = self.TEXTEDIT_forbiddenPath.toPlainText()
        for line in rawText.splitlines():
            rawLineList = line.strip().split("->")
            lineList = [s.strip() for s in rawLineList]
            if lineList:
                forbiddenPaths.append(lineList)
    
        return forbiddenPaths
    
    
    
    
                        
