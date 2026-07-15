##########################################################################################################
#   Description: 工具主页面
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import random
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QTabWidget, QTextEdit

from page import Page
from ui.home.Ui_home import Ui_Form

from ..subscript.subscriptMng import SubscriptsMng

class HomePage(Page, Ui_Form):
    '''CraftHub主页'''

    COLUMN_NO = 0
    COLUMN_NAME = 1
    COLUMN_VERSION = 2
    COLUMN_DESCRIPTION = 3
    COLUMN_AUTHOR = 4
    COLUMN_OPEN = 5

    ROW_NO_START = 1

    WELCOME_TEXT_LIST = [
        "天青色等烟雨，而我在等你",
        "怀念是月光，照亮来时的路",
        "宠辱不惊，肝木自宁",
        "酒盈尊，云满屋，不见人间荣辱",
        "四时风月一闲身。无用人，诗酒乐天真",
        "不拟人间更求事，些些疏懒亦何妨",
        "枯藤老树昏鸦，小桥流水人家",
        "闲看庭前花开花落，漫随天外云卷云舒",
        "醒来明月，醉后清风",
        "行到水穷处，坐看云起时",
        "人有悲欢离合，月有阴晴圆缺",
        "鹰击长空，鱼翔浅底",
        "真正重要的东西，永远都是非常简单",
        "你的意志指引黎明, 你的高洁灼人双眼",
        "执拗的花朵，不会因为风暴褪去颜色",
        "自由的火，鼓动着黎明的歌",
        "人生是旷野，而非轨道",
        "一旦选择相信 ，一切皆有可能",
        "你累的时候，世界也愿意陪你歇一歇",
        "星星那么多，总有一颗在为你亮着",
    ]

    def __init__(self, tab: QTabWidget):
        """初始化主页面

        :param tab: 主选卡项容器
        """
        Page.__init__(self, title="Home")
        Ui_Form.__init__(self)

        self.setupUi(self)
        self._randomWelcome()
        self._buildScriptList(tab)

    def _randomWelcome(self):
        '''随机欢迎语句'''

        self.label_welcome.setText(random.choice(self.WELCOME_TEXT_LIST))

    def _buildScriptList(self, tab: QTabWidget):
        '''构建脚本列表'''

        scriptList = SubscriptsMng.gets(True)

        for index, script in enumerate(scriptList):
            self._addScriptRow(index, script, tab)

    def _addScriptRow(self, index: int, script, tab: QTabWidget):
        '''添加脚本行'''

        labelNo = QLabel(str(index + self.ROW_NO_START))
        labelNo.setFont(QFont("Arial", 10, QFont.Weight.Bold, italic=True))

        labelName = QLabel(script.name)
        labelVersion = QLabel(script.version)

        textDescription = QTextEdit()
        textDescription.setPlainText(script.description)
        textDescription.setReadOnly(True)

        labelAuthor = QLabel(script.author)

        buttonOpen = QPushButton("打开")
        buttonOpen.clicked.connect(partial(script.buildPage, tab=tab))

        self.gridLayout_scripts.addWidget(
            labelNo,
            index,
            self.COLUMN_NO,
            Qt.AlignmentFlag.AlignCenter
        )
        self.gridLayout_scripts.addWidget(
            labelName,
            index,
            self.COLUMN_NAME,
            Qt.AlignmentFlag.AlignCenter
        )
        self.gridLayout_scripts.addWidget(
            labelVersion,
            index,
            self.COLUMN_VERSION,
            Qt.AlignmentFlag.AlignCenter
        )
        self.gridLayout_scripts.addWidget(
            textDescription,
            index,
            self.COLUMN_DESCRIPTION,
            Qt.AlignmentFlag.AlignCenter
        )
        self.gridLayout_scripts.addWidget(
            labelAuthor,
            index,
            self.COLUMN_AUTHOR,
            Qt.AlignmentFlag.AlignCenter
        )
        self.gridLayout_scripts.addWidget(
            buttonOpen,
            index,
            self.COLUMN_OPEN,
            Qt.AlignmentFlag.AlignCenter
        )