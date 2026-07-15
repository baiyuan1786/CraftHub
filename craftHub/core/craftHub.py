##########################################################################################################
#   Description: CraftHub主窗口
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtWidgets import QMainWindow, QMenu, QMessageBox, QTabWidget

from page import Page
from path import PATH_RESOURCE

from .craftHubInitializer import CraftHubInitializer
from .craftHubMenuBuilder import CraftHubMenuBuilder
from .craftHubTitleBar import CraftHubTitleBar
from .homePage import HomePage
from .shortcutCreator import ShortcutCreator
from ..tool import askDo, GLog, tryDo


class CraftHub(QMainWindow):
    '''CraftHub集成GUI程序'''

    WINDOW_WIDTH = 950
    WINDOW_HEIGHT = 530
    WINDOW_TITLE = "CraftHub"
    WINDOW_ICON_PATH = PATH_RESOURCE / "png" / "cycle.ico"

    def __init__(self):
        '''初始化CraftHub主窗口'''

        super().__init__()

        self.isDragging = False
        self.dragOffset = QPoint()
        self.tabMain = QTabWidget(self)

        self._initWindow()
        self._initCentralWidget()
        self._initTitleBar()
        self._openHomePage()
        self._bindContextMenu()

    def _initWindow(self):
        '''初始化窗口基础属性'''

        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowIcon(QIcon(str(self.WINDOW_ICON_PATH)))
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

    def _initCentralWidget(self):
        '''初始化中心页面容器'''

        self.setCentralWidget(self.tabMain)

    def _initTitleBar(self):
        '''初始化自定义标题栏'''

        menuBuilder = CraftHubMenuBuilder(
            parent=self,
            tabMain=self.tabMain,
            closeCurrentPageFunc=self.delCurTab,
            shortcutCreateFunc=self.shortCutCreate,
            initializedFunc=self._initialized
        )

        titleBar = CraftHubTitleBar(
            parent=self,
            menuBar=menuBuilder.getMenuBar(),
            minimizeFunc=self.showMinimized,
            maximizeFunc=self.toggleMaximize,
            closeFunc=self.customClose
        )

        self.setMenuWidget(titleBar)

    def _openHomePage(self):
        '''打开主页'''

        HomePage(tab=self.tabMain).open(tab=self.tabMain)

    def _bindContextMenu(self):
        '''绑定右键菜单'''

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)

    def _showContextMenu(self, position: QPoint):
        """显示上下文菜单

        :param position: 鼠标位置
        """

        currentIndex = self.tabMain.currentIndex()

        if currentIndex < 0:
            return

        currentPage = self.tabMain.widget(currentIndex)

        if not isinstance(currentPage, Page):
            return

        contextMenu = QMenu(self)

        closeAction = contextMenu.addAction("Close")

        contextMenu.addSeparator()

        exportDataAction = contextMenu.addAction("ExportConfig")
        importDataAction = contextMenu.addAction("ImportConfig")

        if (closeAction is None
            or exportDataAction is None
            or importDataAction is None):
            return

        closeAction.triggered.connect(self.delCurTab)
        exportDataAction.triggered.connect(currentPage.exportData)
        importDataAction.triggered.connect(currentPage.importData)

        contextMenu.exec(self.mapToGlobal(position))

    @tryDo(title="关闭选卡项")
    @askDo(title="关闭选卡项", prompt="确认要关闭该选卡项吗?")
    def delCurTab(self):
        '''删除当前选中的选卡项'''

        currentIndex = self.tabMain.currentIndex()

        if currentIndex < 0:
            QMessageBox.warning(self, "WARNING", "没有选中的标签页")
            return

        tabTitle = self.tabMain.tabText(currentIndex)
        tabWidget = self.tabMain.widget(currentIndex)

        if isinstance(tabWidget, Page):
            tabWidget.remove()

        self.tabMain.removeTab(currentIndex)
        GLog.logInfo(f"Remove '{tabTitle}' success")

    def customClose(self):
        '''自定义关闭函数'''

        for index in range(self.tabMain.count() - 1, -1, -1):
            tabWidget = self.tabMain.widget(index)

            if isinstance(tabWidget, Page):
                tabWidget.save()
                tabWidget.remove()

        self.close()

    def toggleMaximize(self):
        '''切换最大化和正常窗口'''

        if self.isMaximized():
            self.showNormal()
            return

        self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件

        :param event: 鼠标事件
        """

        if event.button() != Qt.MouseButton.LeftButton:
            return

        menuWidget = self.menuWidget()

        if menuWidget is None:
            return

        if event.position().toPoint().y() < menuWidget.height():
            self.isDragging = True
            self.dragOffset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件

        :param event: 鼠标事件
        """

        if self.isDragging:
            self.move(event.globalPosition().toPoint() - self.dragOffset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件

        :param event: 鼠标事件
        """

        if event.button() == Qt.MouseButton.LeftButton:
            self.isDragging = False

    @tryDo(title="创建快捷方式")
    def shortCutCreate(self):
        '''创建工具快捷方式'''

        ShortcutCreator.createCraftHubShortcut()

    @askDo(title="初始化工具", prompt="确认要初始化整个工具吗? \n这将还原工具到初始状态")
    @tryDo(title="初始化工具", info="工具初始化完毕！")
    def _initialized(self):
        '''初始化整个工具'''

        CraftHubInitializer.initialize()