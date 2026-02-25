##########################################################################################################
#   Description: craftHub主程序
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from path import *
from page import Page

from .tool import gLog, askDo, tryDo
from .tool.timestampTool import TimestampTranser
from .homePage import HomePage
from .subscript import SubscriptsMng

import os
import shutil
from functools import partial
from typing import List
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QAction, QMouseEvent, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QWidget, QLabel, QTextEdit, QMessageBox,
                            QHBoxLayout, QPushButton, QLabel, QMenu, QVBoxLayout, QToolButton, QTabWidget, QGridLayout)

WINDOW_USERMAIN_WIDTH = 950
WINDOW_USERMAIN_HEIGHT = 530
TITLE_HEIGHT = 40

class CraftHub(QMainWindow):
    '''集成GUI程序'''
    readmeTypes = (".doc", ".docx", ".txt") # 使用说明类型
    titleColor = "#dddddd"
    mainColor = "#f0f0f0"
    buttonStyle = """
            QPushButton {
                background-color: white;  /* 默认背景色 */
                color: black;             /* 文字颜色 */
                border: 1px solid #cccccc;  /* 边框 */
                border-radius: 5px;         /* 圆角 */
            }

            QPushButton:hover {
                background-color: #e6f7ff;  /* 淡蓝色背景 */
                border: 1px solid #4da6ff;  /* 蓝色边框 */
                color: black;
        }"""

    def __init__(self):

        super().__init__()

        self.resize(WINDOW_USERMAIN_WIDTH, WINDOW_USERMAIN_HEIGHT)
        self.setWindowTitle("CraftHub")
        self.setWindowIcon(QIcon(str(PATH_RESOURCE / "png" /"cycle.ico")))

        # 隐藏title栏，使用自定义title
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        # 窗口拖动相关变量
        self.dragging = False
        self.offset = QPoint()

        # 初始化选卡项
        self.TAB_main = QTabWidget(self)
        self.setCentralWidget(self.TAB_main)

        # 初始化菜单栏
        titleBar = self.customTitleBox()
        self.setMenuWidget(titleBar)

        # 初始化Home页面并打开
        HomePage(tab = self.TAB_main).open(tab = self.TAB_main)
        
        # 绑定tabWdiget右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)
        
    def _showContextMenu(self, position):     
        """显示上下文菜单"""

        currentIndex = self.TAB_main.currentIndex()

        if currentIndex >= 0:
            contextMenu = QMenu(self)
            
            closeAction = contextMenu.addAction("Close Current Page")
            
            if closeAction is not None:
                closeAction.triggered.connect(self.delCurTab)

                contextMenu.exec(self.mapToGlobal(position))

    @tryDo(title = "关闭选卡项")
    @askDo(title = "关闭选卡项", prompt = "确认要关闭该选卡项吗?")
    def delCurTab(self):
        '''删除当前选中的选卡项容器'''

        currentIndex = self.TAB_main.currentIndex()
        if currentIndex < 0:
            QMessageBox.warning(self, "WARNING", "没有选中的标签页")
            return
        
        tabTitle = self.TAB_main.tabText(currentIndex)
        widget = self.TAB_main.widget(currentIndex)
        
        if widget is not None:
            widget.remove() # type: ignore

            self.TAB_main.removeTab(currentIndex)
            gLog.logInfo(f"Remove \'{tabTitle}\' success")

    def menuBarGet(self):       
        '''自定义menuBar获取'''
        menuBar = QMenuBar(parent = self)    # 菜单栏对象

        # 创建菜单对象
        MENU_file = QMenu(title = "File", parent = self)
        MENU_page = QMenu(title = "Page", parent = self)
        MENU_tool = QMenu(title = "Tool", parent = self)
        MENU_terminal = QMenu(title = "Terminal", parent = self)
        MENU_log = QMenu(title = "Log", parent = self)
        MENU_help = QMenu(title = "Help", parent = self)

        # 创建动作
        act11 = QAction("BrowseRoot", self)
        act12 = QAction("ShortCut Creates", self)
        act13 = QAction("Initialized", self)

        act21 = QAction("Home", self)
        act22 = QAction("Close Current Page", self)
        act23 = QAction("subscript Manager", self)

        act31 = QAction("Timestamp Tool", self)
        act32 = QAction("TFTP Tool", self)
        act33 = QAction("iperf Test", self)

        act41 = QAction("Connect", self)
        act42 = QAction("Terminal Window", self)

        act51 = QMenu("hubLog", self)
        act52 = QMenu("serialLog", self)
        
        act511 = QAction("browseRoot", self)
        act512 = QAction("curLog", self)

        act521 = QAction("browseRoot", self)
        act522 = QAction("curLog", self)

        # 绑定方法
        act11.triggered.connect(partial(self._openFile, PATH_ROOT)) 
        act12.triggered.connect(self.shortCutCreate)
        act13.triggered.connect(self._initialized)
        
        act21.triggered.connect(lambda: HomePage(tab = self.TAB_main).open(tab = self.TAB_main))
        act22.triggered.connect(self.delCurTab)
        act23.triggered.connect(lambda: SubscriptsMng().open(tab = self.TAB_main))
        
        act31.triggered.connect(lambda: TimestampTranser().open(tab = self.TAB_main))

        act511.triggered.connect(partial(self._openFile, PATH_LOG_ROOT))
        act512.triggered.connect(gLog.open)
        act521.triggered.connect(partial(self._openFile, PATH_SERIAL_LOG_ROOT))
        act522.triggered.connect(partial(self._openFile, PATH_SERIAL_LOG_ROOT))

        readmeFiles = [fileName for fileName in os.listdir(PATH_README) 
                    if fileName.endswith(self.readmeTypes) and not fileName.startswith("~")]
        
        # 加载使用说明
        act6s = []
        for f in readmeFiles:
            act = QAction(f, self)
            
            filePath = PATH_README / f
            act.triggered.connect(
                partial(self._openFile, filePath=filePath)
            )
            act6s.append(act)

        # 添加菜单
        act51.addActions((act511, act512))
        act52.addActions((act521, act522))

        MENU_file.addActions((act11, act12, act13))
        MENU_page.addActions((act21, act22, act23))
        MENU_tool.addActions((act31, act32, act33))
        MENU_terminal.addActions((act41, act42))
        MENU_log.addMenu(act51)
        MENU_log.addMenu(act52)
        MENU_help.addActions(act6s)

        menuBar.addMenu(MENU_file)
        menuBar.addMenu(MENU_page)
        menuBar.addMenu(MENU_tool)
        menuBar.addMenu(MENU_terminal)
        menuBar.addMenu(MENU_log)
        menuBar.addMenu(MENU_help)

        return menuBar
    
    @staticmethod
    def _openFile(filePath: Path):
        try:
            os.startfile(str(filePath))
        except Exception as e:
            QMessageBox.critical(
                None,
                "打开文件错误",
                str(e),
                QMessageBox.StandardButton.Ok
            )

    def customTitleBox(self):
        '''为GUI专门设计的特殊的无title栏格式'''

        # 创建标题栏
        titleBar = QWidget(self)            # 容器
        titleBar.setFixedHeight(TITLE_HEIGHT)     # 设置标题栏高度
        titleBar.setStyleSheet(f"background-color: {self.titleColor};") # 设置标题栏颜色

        # 为标题栏添加布局
        LAYOUT_title = QHBoxLayout(titleBar)
        LAYOUT_title.setContentsMargins(5, 0, 5, 0) # 设置外边距
        LAYOUT_title.setSpacing(2) # 设置内间隔

        # 布局中添加一个label
        icon_label = QLabel(self)
        icon_label.setPixmap(self.windowIcon().pixmap(24, 24))
        LAYOUT_title.addWidget(icon_label)

        # 创建菜单栏并添加
        menuBar = self.menuBarGet()

        # 设置菜单栏样式
        menuBar.setStyleSheet("""
            QMenuBar::item {
                padding: 10px 20px;       /* 上下, 左右，占用空间*/
                margin: 0px 10px;          /* 上下，左右外边距*/
                background: transparent; /* 透明背景 */
            }
            
            QMenuBar::item:selected {    /* 选中状态 */
                background-color: #c6d4e0;
            }
        """)

        # 添加控制布局
        LAYOUT_ctl = QHBoxLayout()
        LAYOUT_ctl.setSpacing(2)

        BUTTON_min = QPushButton("-")
        BUTTON_max = QPushButton("口")
        BUTTON_close = QPushButton("X")

        BUTTON_min.setFixedSize(40, 30)
        BUTTON_max.setFixedSize(40, 30)
        BUTTON_close.setFixedSize(40, 30)

        BUTTON_min.setStyleSheet(self.buttonStyle)
        BUTTON_max.setStyleSheet(self.buttonStyle)
        BUTTON_close.setStyleSheet(self.buttonStyle)

        BUTTON_min.clicked.connect(self.showMinimized)
        BUTTON_max.clicked.connect(self.toggle_maximize)
        BUTTON_close.clicked.connect(self.customClose)

        LAYOUT_ctl.addWidget(BUTTON_min)
        LAYOUT_ctl.addWidget(BUTTON_max)
        LAYOUT_ctl.addWidget(BUTTON_close)

        LAYOUT_title.addWidget(menuBar)
        LAYOUT_title.addStretch(1)         # 添加弹簧，填充中间所有空白
        LAYOUT_title.addLayout(LAYOUT_ctl) # 复合布局
        return titleBar
    
    def customClose(self):
        '''自定义析构函数'''
        for i in range(self.TAB_main.count() - 1, -1, -1):
            widget = self.TAB_main.widget(i)
            if isinstance(widget, Page):
                widget.save()
                widget.remove()

        self.close()
    
    def toggle_maximize(self):
        '''切换最大化和正常的方法'''
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # 窗口拖动功能, 自动调用无需绑定
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下时记录位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在标题栏区域
            if event.position().toPoint().y() < self.menuWidget().height(): # type: ignore
                self.dragging = True
                self.offset = event.globalPosition().toPoint() - self.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动时移动窗口"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.offset)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放时停止拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    @tryDo(title = "创建快捷方式")
    def shortCutCreate(self):
        """创建工具快捷方式"""

        sourcePath = PATH_ROOT / f"main.py"
        targetPath = PATH_DESKTOP / "CraftHub.lnk"
        desktopIcoPath = PATH_ROOT / "doc" / "png" / "desktop.ico"    # 桌面图标

        # 确保源文件存在
        if not sourcePath.exists():
            raise FileNotFoundError(f"没有找到源文件: '{sourcePath}'")
        
        # 确保桌面目录存在
        PATH_DESKTOP.mkdir(parents=True, exist_ok=True)

        # 创建快捷方式
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(targetPath))
        
        # 正确设置目标和参数
        python_exe = sys.executable
        shortcut.TargetPath = python_exe
        shortcut.Arguments = f'"{sourcePath}"'
        working_dir = str(sourcePath.parent)

        # 设置工作目录（使用源文件所在目录）
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = str(desktopIcoPath)
        shortcut.Description = "CraftHub Application"
        shortcut.Save()

    @askDo(title = "初始化工具", prompt = "确认要初始化整个工具吗? \n这将还原工具到初始状态")
    @tryDo(title = "初始化工具", info = "工具初始化完毕！")
    def _initialized(self):
        '''初始化整个工具'''
        
        deletedCount = 0
        deletedLogCount = 0
        deletedSensitiveCount = 0
        deletedSetCount = 0

        sensitiveDirList: List[Path] = []
        sensitiveDirList.append(PATH_SUBSCRIPT / "_1AutoRoute" / "doc" / "image")
        sensitiveDirList.append(PATH_SUBSCRIPT / "_1AutoRoute" / "doc" / "imageTest")
        
        # 删除__pycache__文件
        gLog.logInfo("尝试删除__pycache__文件")
        for pycachePath in PATH_ROOT.rglob("__pycache__"):
            if pycachePath.is_dir():
                try:
                    shutil.rmtree(pycachePath)  # 递归删除整个文件夹
                    gLog.logInfo(f"✅ 已删除: {pycachePath}")
                    deletedCount += 1
                except Exception as e:
                    gLog.logInfo(f"❌ 删除失败 {pycachePath}: {e}")
        
        gLog.logInfo(f"总计删除了 {deletedCount} 个__pycache__文件夹\n")

        # 删除log文件
        gLog.logInfo("尝试删除log文件")
        for logDir in [PATH_LOG_ROOT, PATH_SERIAL_LOG_ROOT]:
            for logFile in logDir.iterdir():
                if logFile.stem != "readme" and logFile.stem != gLog.logPath.stem:
                    
                    logFile.unlink()
                    deletedLogCount += 1
                    
        gLog.logInfo(f"总计删除了 {deletedLogCount} 个log文件\n")
        
        # 删除敏感文件
        gLog.logInfo("尝试删除敏感文件")
        for dir in sensitiveDirList:
            if dir.exists():
                shutil.rmtree(dir)
                deletedSensitiveCount += 1
                
        gLog.logInfo(f"总计删除了 {deletedSensitiveCount} 个敏感文件夹\n")
        
        # 删除用户配置文件
        gLog.logInfo("尝试删除用户配置文件文件")
        for dataPath in PATH_ROOT.rglob("data.yaml"):
            dataPath.unlink()
            deletedSetCount += 1
            
        for dataPath in PATH_ROOT.rglob("set.yaml"):
            dataPath.unlink()
            deletedSetCount += 1
        
        gLog.logInfo(f"总计删除了 {deletedSetCount} 个用户配置文件\n")
        
        
        