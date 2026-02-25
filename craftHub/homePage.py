##########################################################################################################
#   Description: 工具主页面
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from ui.home.Ui_home import Ui_Form
from page import Page

from .subscript import gSubscriptMng

import random
from typing import List
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QLabel, QTextEdit, QPushButton, QLabel, QTabWidget, QGridLayout)

class HomePage(Page, Ui_Form):
    '''CraftHub 主页创建函数'''
    def __init__(self, tab: QTabWidget): 
        """初始化主页面

        :param tab: 主选卡项容器
        """        
        Page.__init__(self, title = "Home")
        Ui_Form.__init__(self)
        self.setupUi(self)
        self._randomWelcome()

        # 插入脚本    
        for index, script in enumerate(gSubscriptMng.gets()):
            
            # 创建序号标签 (NO)
            label_no = QLabel(str(index + 1))
            label_no.setFont(QFont("Arial", 10, QFont.Weight.Bold, italic=True))
            
            # 创建脚本名称标签
            label_name = QLabel(script.name)
            
            # 创建版本标签
            label_version = QLabel(script.version)
            
            # 创建描述文本框
            text_description = QTextEdit()
            text_description.setPlainText(script.description)
            text_description.setReadOnly(True)
            
            # 创建作者标签
            label_author = QLabel(script.author)
            
            # 创建打开按钮
            button_open = QPushButton("打开")
            from functools import partial
            button_open.clicked.connect(partial(script.buildPage, tab=tab))
            
            # 添加所有控件到网格布局
            self.gridLayout_scripts.addWidget(label_no, index, 0, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(label_name, index, 1, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(label_version, index, 2, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(text_description, index, 3, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(label_author, index, 4, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_open, index, 5, Qt.AlignmentFlag.AlignCenter)
            
    def _randomWelcome(self):
        '''随机欢迎语句'''
        
        welcomeList: List[str] = [
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
            "鹰击长空，鱼翔浅底"
        ]
        
        welcomeList += [
            "真正重要的东西，永远都是非常简单",
            "你的意志指引黎明, 你的高洁灼人双眼",
            "执拗的花朵，不会因为风暴褪去颜色",
            "自由的火，鼓动着黎明的歌",
            "有些鸟儿是关不住的, 它的每一根羽毛都闪耀着自由的光辉",
            "人生是旷野，而非轨道",
            "宁为自由之草，不做金笼之鸟",
            "不能听命于自己者，就要受命于他人",
            "一旦选择相信 ，一切皆有可能"
        ]
        
        welcomeList += [
            "你累的时候，世界也愿意陪你歇一歇",
            "星星那么多，总有一颗在为你亮着",
            "你不是孤岛，只是暂时退潮",
            "努力是为了以后能好好偷懒"
        ]
        
        self.label_welcome.setText(random.choice(welcomeList))