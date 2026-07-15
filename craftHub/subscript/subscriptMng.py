##########################################################################################################
#   Description: 子脚本群管理，子脚本管理器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import importlib
import inspect
import pkgutil
import webbrowser
from functools import partial
from typing import List, Optional, Type

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QRadioButton, QButtonGroup, QTabWidget

from page import Page
from ui.manager.Ui_manager import Ui_Form

from craftHub import subscripts as subscriptPackageRoot
from craftHub.tool import GLog

from .subscript import Subscript


class SubscriptsMng(Page, Ui_Form):
    '''子脚本管理器，维护所有子脚本信息'''

    PAGE_TITLE = "Manager"

    ENABLE_FILTER_ON = True
    ENABLE_FILTER_OFF = False

    FIRST_ROW_INDEX = 1
    SHOW_INDEX_OFFSET = 1

    COLUMN_NO = 0
    COLUMN_NAME = 1
    COLUMN_AUTHOR = 2
    COLUMN_ENABLE_TRUE = 3
    COLUMN_ENABLE_FALSE = 4
    COLUMN_INFO = 5
    COLUMN_DESC = 6
    COLUMN_README = 7
    COLUMN_LINK = 8
    COLUMN_ROOT = 9

    ENABLE_TRUE_TEXT = "T"
    ENABLE_FALSE_TEXT = "F"

    BUTTON_EDIT_TEXT = "edit"
    BUTTON_OPEN_TEXT = "OPEN"
    BUTTON_EMPTY_TEXT = "-"

    FONT_NAME = "Arial"
    FONT_SIZE = 10

    subscriptClassListCache: Optional[List[Type[Subscript]]] = None

    @classmethod
    def gets(cls, filter: bool = False, reload: bool = False) -> List[Subscript]:
        """获取子脚本列表

        :param filter: 启用enable过滤器
        :param reload: 是否重新扫描子脚本类
        :return: 子脚本列表
        """

        subscriptList: List[Subscript] = []
        subscriptClassList = cls.getSubscriptClassList(reload=reload)

        for subscriptClass in subscriptClassList:
            try:
                subscriptList.append(subscriptClass()) # type: ignore
            except Exception as error:
                GLog.logInfo(f"Load '{subscriptClass.__name__}' failed: {str(error)}")

        if filter:
            return [subscript for subscript in subscriptList if subscript.enable]

        return subscriptList

    @classmethod
    def getSubscriptClassList(cls, reload: bool = False) -> List[Type[Subscript]]:
        """获取子脚本类列表

        :param reload: 是否重新扫描
        :return: 子脚本类列表
        """

        if cls.subscriptClassListCache is not None and not reload:
            return cls.subscriptClassListCache

        subscriptClassList = cls._scanSubscriptClassList()
        cls.subscriptClassListCache = subscriptClassList

        return subscriptClassList

    @classmethod
    def _scanSubscriptClassList(cls) -> List[Type[Subscript]]:
        '''扫描所有子脚本类'''

        subscriptClassList: List[Type[Subscript]] = []

        for moduleInfo in pkgutil.iter_modules(subscriptPackageRoot.__path__):
            if not moduleInfo.ispkg:
                continue

            moduleName = f"{subscriptPackageRoot.__name__}.{moduleInfo.name}"

            try:
                module = importlib.import_module(moduleName)
                subscriptClassList.extend(cls._findSubscriptClassList(module))
            except Exception as error:
                GLog.logInfo(f"Scan subscript module '{moduleName}' failed: {str(error)}")

        return subscriptClassList

    @classmethod
    def _findSubscriptClassList(cls, module) -> List[Type[Subscript]]:
        '''从模块中查找Subscript派生类'''

        subscriptClassList: List[Type[Subscript]] = []

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj is Subscript:
                continue

            if not issubclass(obj, Subscript):
                continue

            subscriptClassList.append(obj)

        return subscriptClassList

    def __init__(self):
        '''初始化子脚本管理器页面'''

        super().__init__(title=self.PAGE_TITLE)

        Ui_Form.__init__(self)
        self.setupUi(self)

        self.buttonGroupList: List[QButtonGroup] = []

        self._loadUI()

    def _loadUI(self):
        '''加载UI'''

        for index, script in enumerate(self.gets()):
            self._addScriptRow(index, script)

    def _addScriptRow(self, index: int, script: Subscript):
        """添加子脚本信息行

        :param index: 子脚本序号
        :param script: 子脚本对象
        """

        rowIndex = index + self.FIRST_ROW_INDEX

        labelNo = QLabel(str(index + self.SHOW_INDEX_OFFSET), self)
        labelNo.setFont(QFont(self.FONT_NAME, self.FONT_SIZE, QFont.Weight.Bold, italic=True))

        labelName = QLabel(script.name, self)
        labelAuthor = QLabel(str(script.author or self.BUTTON_EMPTY_TEXT), self)

        radioButtonTrue = QRadioButton(self.ENABLE_TRUE_TEXT, self)
        radioButtonFalse = QRadioButton(self.ENABLE_FALSE_TEXT, self)

        buttonGroup = self._createEnableButtonGroup(
            script=script,
            radioButtonTrue=radioButtonTrue,
            radioButtonFalse=radioButtonFalse
        )

        self.buttonGroupList.append(buttonGroup)

        buttonInfo = QPushButton(self.BUTTON_EDIT_TEXT, self)
        buttonDesc = QPushButton(self.BUTTON_EDIT_TEXT, self)
        buttonReadme = QPushButton(str(script.readme or self.BUTTON_EMPTY_TEXT), self)
        buttonLink = QPushButton(str(script.link or self.BUTTON_EMPTY_TEXT), self)
        buttonRoot = QPushButton(self.BUTTON_OPEN_TEXT, self)

        buttonInfo.clicked.connect(partial(script.openInfo))
        buttonDesc.clicked.connect(partial(script.openDesc))
        buttonReadme.clicked.connect(partial(script.openReadme))
        buttonRoot.clicked.connect(partial(script.openRoot))

        if script.link:
            buttonLink.clicked.connect(partial(self._openLink, script.link))
        else:
            buttonLink.setEnabled(False)

        self._addWidgetToGrid(labelNo, rowIndex, self.COLUMN_NO)
        self._addWidgetToGrid(labelName, rowIndex, self.COLUMN_NAME)
        self._addWidgetToGrid(labelAuthor, rowIndex, self.COLUMN_AUTHOR)
        self._addWidgetToGrid(radioButtonTrue, rowIndex, self.COLUMN_ENABLE_TRUE)
        self._addWidgetToGrid(radioButtonFalse, rowIndex, self.COLUMN_ENABLE_FALSE)
        self._addWidgetToGrid(buttonInfo, rowIndex, self.COLUMN_INFO)
        self._addWidgetToGrid(buttonDesc, rowIndex, self.COLUMN_DESC)
        self._addWidgetToGrid(buttonReadme, rowIndex, self.COLUMN_README)
        self._addWidgetToGrid(buttonLink, rowIndex, self.COLUMN_LINK)
        self._addWidgetToGrid(buttonRoot, rowIndex, self.COLUMN_ROOT)

    def _createEnableButtonGroup(
            self,
            script: Subscript,
            radioButtonTrue: QRadioButton,
            radioButtonFalse: QRadioButton
    ) -> QButtonGroup:
        """创建启用状态按钮组

        :param script: 子脚本对象
        :param radioButtonTrue: 启用按钮
        :param radioButtonFalse: 禁用按钮
        :return: 按钮组
        """

        buttonGroup = QButtonGroup(self)
        buttonGroup.addButton(radioButtonTrue)
        buttonGroup.addButton(radioButtonFalse)

        if script.enable:
            radioButtonTrue.setChecked(True)
        else:
            radioButtonFalse.setChecked(True)

        buttonGroup.buttonClicked.connect(partial(script.setEnabled))

        return buttonGroup

    def _addWidgetToGrid(self, widget, rowIndex: int, columnIndex: int):
        """添加控件到表格布局

        :param widget: 控件
        :param rowIndex: 行号
        :param columnIndex: 列号
        """

        self.gridLayout_scripts.addWidget(
            widget,
            rowIndex,
            columnIndex,
            Qt.AlignmentFlag.AlignCenter
        )

    @staticmethod
    def _openLink(link: str):
        """打开链接

        :param link: 链接
        """

        webbrowser.open(link)