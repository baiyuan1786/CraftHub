##########################################################################################################
#   Description: CraftHub自定义标题栏
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMenuBar, QPushButton, QWidget


class CraftHubTitleBar(QWidget):
    '''CraftHub自定义标题栏'''

    TITLE_HEIGHT = 40
    TITLE_MARGIN_LEFT = 5
    TITLE_MARGIN_TOP = 0
    TITLE_MARGIN_RIGHT = 5
    TITLE_MARGIN_BOTTOM = 0

    TITLE_SPACING = 2
    CONTROL_SPACING = 2

    ICON_WIDTH = 24
    ICON_HEIGHT = 24

    BUTTON_WIDTH = 40
    BUTTON_HEIGHT = 30

    TITLE_COLOR = "#dddddd"

    BUTTON_STYLE = """
        QPushButton {
            background-color: white;
            color: black;
            border: 1px solid #cccccc;
            border-radius: 5px;
        }

        QPushButton:hover {
            background-color: #e6f7ff;
            border: 1px solid #4da6ff;
            color: black;
        }
    """

    MENU_BAR_STYLE = f"""
        QMenuBar {{
            background-color: {TITLE_COLOR};
        }}

        QMenuBar::item {{
            padding: 10px 20px;
            margin: 0px 10px;
            background-color: {TITLE_COLOR};
        }}

        QMenuBar::item:selected {{
            background-color: #c6d4e0;
        }}
    """

    def __init__(
            self,
            parent: QWidget,
            menuBar: QMenuBar,
            minimizeFunc: Callable,
            maximizeFunc: Callable,
            closeFunc: Callable
    ):
        """初始化CraftHub自定义标题栏

        :param parent:       父窗口
        :param menuBar:      菜单栏
        :param minimizeFunc: 最小化函数
        :param maximizeFunc: 最大化函数
        :param closeFunc:    关闭函数
        """
        super().__init__(parent)

        self.parentWindow = parent
        self.menuBar = menuBar
        self.minimizeFunc = minimizeFunc
        self.maximizeFunc = maximizeFunc
        self.closeFunc = closeFunc

        self._initTitleBar()

    def _initTitleBar(self):
        '''初始化标题栏'''

        self.setFixedHeight(self.TITLE_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("craftHubTitleBar")
        self.setStyleSheet(f"""
            QWidget#craftHubTitleBar {{
                background-color: {self.TITLE_COLOR};
            }}
        """)

        titleLayout = QHBoxLayout(self)
        titleLayout.setContentsMargins(
            self.TITLE_MARGIN_LEFT,
            self.TITLE_MARGIN_TOP,
            self.TITLE_MARGIN_RIGHT,
            self.TITLE_MARGIN_BOTTOM
        )
        titleLayout.setSpacing(self.TITLE_SPACING)

        iconLabel = self._createIconLabel()
        controlLayout = self._createControlLayout()

        self.menuBar.setStyleSheet(self.MENU_BAR_STYLE)

        titleLayout.addWidget(iconLabel)
        titleLayout.addWidget(self.menuBar)
        titleLayout.addStretch(1)
        titleLayout.addLayout(controlLayout)

    def _createIconLabel(self) -> QLabel:
        '''创建图标标签'''

        iconLabel = QLabel(self)
        iconLabel.setPixmap(
            self.parentWindow.windowIcon().pixmap(
                self.ICON_WIDTH,
                self.ICON_HEIGHT
            )
        )

        return iconLabel

    def _createControlLayout(self) -> QHBoxLayout:
        '''创建窗口控制按钮布局'''

        controlLayout = QHBoxLayout()
        controlLayout.setSpacing(self.CONTROL_SPACING)

        buttonMinimize = self._createControlButton("-", self.minimizeFunc)
        buttonMaximize = self._createControlButton("口", self.maximizeFunc)
        buttonClose = self._createControlButton("X", self.closeFunc)

        controlLayout.addWidget(buttonMinimize)
        controlLayout.addWidget(buttonMaximize)
        controlLayout.addWidget(buttonClose)

        return controlLayout

    def _createControlButton(self, text: str, clickedFunc: Callable) -> QPushButton:
        """创建窗口控制按钮

        :param text:        按钮文本
        :param clickedFunc: 点击回调函数
        :return:            按钮对象
        """

        button = QPushButton(text)
        button.setFixedSize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button.setStyleSheet(self.BUTTON_STYLE)
        button.clicked.connect(clickedFunc)

        return button