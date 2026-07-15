##########################################################################################################
#   Description: CraftHub菜单栏构建器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import os
from functools import partial
from pathlib import Path
from typing import Callable, Tuple

from PyQt6.QtWidgets import QMessageBox, QMenuBar, QWidget, QTabWidget

from path import PATH_LOG_ROOT, PATH_README, PATH_ROOT, PATH_SERIAL_LOG_ROOT

from .homePage import HomePage
from .menu import CraftHubMenu
from ..subscript.subscriptMng import SubscriptsMng
from ..tool import GLog
from ..tool.fileCounter import FileCounterPage
from ..tool.timestampTool import TimestampTranser
from ..tool.webProxy import ProxyBrowserLauncherGUI
from ..tool.xlsxCounter import XlsxCounter
from ..tool.cadBlockPrinter import CadBlockPrinter
from ..tool.pythonLineCounter import PythonLineCounterPage

class CraftHubMenuBuilder:
    '''CraftHub菜单栏构建器'''

    MENU_FILE = "File"
    MENU_PAGE = "Page"
    MENU_TOOL = "Tool"
    MENU_TERMINAL = "Terminal"
    MENU_LOG = "Log"
    MENU_HELP = "Help"

    SUB_MENU_HUB_LOG = "hubLog"
    SUB_MENU_SERIAL_LOG = "serialLog"

    ACTION_BROWSE_ROOT = "BrowseRoot"
    ACTION_SHORTCUT_CREATE = "ShortCut Creates"
    ACTION_INITIALIZED = "Initialized"

    ACTION_HOME = "Home"
    ACTION_CLOSE_CURRENT_PAGE = "Close Current Page"
    ACTION_SUBSCRIPT_MANAGER = "subscript Manager"

    ACTION_TIMESTAMP_TOOL = "Timestamp Tool"
    ACTION_TFTP_TOOL = "TFTP Tool"
    ACTION_IPERF_TEST = "iperf Test"
    ACTION_WEB_PROXY = "WebProxy"
    ACTION_FILE_COUNTER = "FileCounter"
    ACTION_XLSX_COUNTER = "XlsxCounter"
    ACTION_CADBLOCK_PRINTER = "CadBlockPrinter"
    ACTION_PYTHON_COUNTER = "PythonCounter"

    ACTION_CONNECT = "Connect"
    ACTION_TERMINAL_WINDOW = "Terminal Window"

    ACTION_BROWSE_LOG_ROOT = "browseRoot"
    ACTION_CURRENT_LOG = "curLog"

    README_TYPES: Tuple[str, ...] = (".doc", ".docx", ".txt", ".pdf")

    MENU_NAME_LIST = [
        MENU_FILE,
        MENU_PAGE,
        MENU_TOOL,
        MENU_TERMINAL,
        MENU_LOG,
        MENU_HELP
    ]

    def __init__(
            self,
            parent: QWidget,
            tabMain: QTabWidget,
            closeCurrentPageFunc: Callable,
            shortcutCreateFunc: Callable,
            initializedFunc: Callable
    ):
        """初始化CraftHub菜单栏构建器

        :param parent:               父窗口
        :param tabMain:              主选卡项容器
        :param closeCurrentPageFunc: 关闭当前页面函数
        :param shortcutCreateFunc:   创建快捷方式函数
        :param initializedFunc:      初始化工具函数
        """
        self.parent = parent
        self.tabMain = tabMain
        self.closeCurrentPageFunc = closeCurrentPageFunc
        self.shortcutCreateFunc = shortcutCreateFunc
        self.initializedFunc = initializedFunc

        self.craftHubMenu = CraftHubMenu(
            parent=self.parent,
            menuNameList=self.MENU_NAME_LIST
        )

        self._buildMenu()

    def getMenuBar(self) -> QMenuBar:
        '''获取菜单栏'''

        return self.craftHubMenu.getMenuBar()

    def _buildMenu(self):
        '''构建菜单栏'''

        self._buildFileMenu()
        self._buildPageMenu()
        self._buildToolMenu()
        self._buildTerminalMenu()
        self._buildLogMenu()
        self._buildHelpMenu()

    def _buildFileMenu(self):
        '''构建File菜单'''

        self.craftHubMenu.addAction(
            menuName=self.MENU_FILE,
            actionName=self.ACTION_BROWSE_ROOT,
            triggerFunc=partial(self._openFile, PATH_ROOT)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_FILE,
            actionName=self.ACTION_SHORTCUT_CREATE,
            triggerFunc=self.shortcutCreateFunc
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_FILE,
            actionName=self.ACTION_INITIALIZED,
            triggerFunc=self.initializedFunc
        )

    def _buildPageMenu(self):
        '''构建Page菜单'''

        self.craftHubMenu.addAction(
            menuName=self.MENU_PAGE,
            actionName=self.ACTION_HOME,
            triggerFunc=lambda: HomePage(tab=self.tabMain).open(tab=self.tabMain)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_PAGE,
            actionName=self.ACTION_CLOSE_CURRENT_PAGE,
            triggerFunc=self.closeCurrentPageFunc
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_PAGE,
            actionName=self.ACTION_SUBSCRIPT_MANAGER,
            triggerFunc=lambda: SubscriptsMng().open(tab=self.tabMain)
        )

    def _buildToolMenu(self):
        '''构建Tool菜单'''

        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_TIMESTAMP_TOOL,
            triggerFunc=lambda: TimestampTranser().open(tab=self.tabMain)
        )

        #self.craftHubMenu.addAction(
        #    menuName=self.MENU_TOOL,
        #    actionName=self.ACTION_TFTP_TOOL
        #)
        #self.craftHubMenu.addAction(
        #    menuName=self.MENU_TOOL,
        #    actionName=self.ACTION_IPERF_TEST
        #)

        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_WEB_PROXY,
            triggerFunc=lambda: ProxyBrowserLauncherGUI().open(tab=self.tabMain)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_FILE_COUNTER,
            triggerFunc=lambda: FileCounterPage().open(tab=self.tabMain)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_XLSX_COUNTER,
            triggerFunc=lambda: XlsxCounter().open(tab=self.tabMain)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_CADBLOCK_PRINTER,
            triggerFunc=lambda: CadBlockPrinter().open(tab=self.tabMain)
        )

        self.craftHubMenu.addAction(
            menuName=self.MENU_TOOL,
            actionName=self.ACTION_PYTHON_COUNTER,
            triggerFunc=lambda: PythonLineCounterPage().open(tab=self.tabMain)
        )

    def _buildTerminalMenu(self):
        '''构建Terminal菜单'''

        self.craftHubMenu.addAction(
            menuName=self.MENU_TERMINAL,
            actionName=self.ACTION_CONNECT
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_TERMINAL,
            actionName=self.ACTION_TERMINAL_WINDOW
        )

    def _buildLogMenu(self):
        '''构建Log菜单'''

        self.craftHubMenu.addAction(
            menuName=self.MENU_LOG,
            subMenuName=self.SUB_MENU_HUB_LOG,
            actionName=self.ACTION_BROWSE_LOG_ROOT,
            triggerFunc=partial(self._openFile, PATH_LOG_ROOT)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_LOG,
            subMenuName=self.SUB_MENU_HUB_LOG,
            actionName=self.ACTION_CURRENT_LOG,
            triggerFunc=GLog.open
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_LOG,
            subMenuName=self.SUB_MENU_SERIAL_LOG,
            actionName=self.ACTION_BROWSE_LOG_ROOT,
            triggerFunc=partial(self._openFile, PATH_SERIAL_LOG_ROOT)
        )
        self.craftHubMenu.addAction(
            menuName=self.MENU_LOG,
            subMenuName=self.SUB_MENU_SERIAL_LOG,
            actionName=self.ACTION_CURRENT_LOG,
            triggerFunc=partial(self._openFile, PATH_SERIAL_LOG_ROOT)
        )

    def _buildHelpMenu(self):
        '''构建Help菜单'''

        if not PATH_README.exists():
            return

        readmeFiles = [
            fileName for fileName in os.listdir(PATH_README)
            if fileName.endswith(self.README_TYPES) and not fileName.startswith("~")
        ]

        for fileName in readmeFiles:
            filePath = PATH_README / fileName

            self.craftHubMenu.addAction(
                menuName=self.MENU_HELP,
                actionName=fileName,
                triggerFunc=partial(self._openFile, filePath)
            )

    @staticmethod
    def _openFile(filePath: Path):
        """打开文件或文件夹

        :param filePath: 文件路径
        """

        try:
            os.startfile(str(filePath))
        except Exception as error:
            QMessageBox.critical(
                None,
                "打开文件错误",
                str(error),
                QMessageBox.StandardButton.Ok
            )