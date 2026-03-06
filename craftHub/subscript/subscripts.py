##########################################################################################################
#   Description: 子脚本群管理，子脚本管理器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from page import Page
from craftHub.tool import gLog
from .subscript import Subscript
from ui.manager.Ui_manager import Ui_Form

from ._1AutoRoute import AutoRoute
from ._2ImageSplit import SplitImage
from ._3surveyMaster import SurveyMaster

from functools import partial
from typing import List
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QLabel, QTextEdit, QPushButton, QLabel, QTabWidget, QGridLayout, QRadioButton, QButtonGroup)

class SubscriptsMng(Page, Ui_Form):
    '''子脚本管理器， 
    维护所有子脚本信息'''
    
    @classmethod
    def gets(cls, filter: bool = False):
        """获取子脚本列表

        :param filter: 启用enable过滤器, defaults to False
        :return: 子脚本列表
        """        

        subscriptList: List[Subscript] = []

        # 加载脚本1
        try:
            subscriptList.append(AutoRoute())
        except Exception as e:
            gLog.logInfo(f"Load \'AutoRoute\' failed: {str(e)}")

        # 加载脚本2
        try:
            subscriptList.append(SplitImage())
        except Exception as e:
            gLog.logInfo(f"Load \'SplitImage\' failed: {str(e)}")
            
        # 加载脚本3
        try:
            subscriptList.append(SurveyMaster())
        except Exception as e:
            gLog.logInfo(f"Load \'SurveyMaster\' failed: {str(e)}")

        if filter:
            return [s for s in subscriptList if s.enable]
        else:
            return subscriptList
    
    def __init__(self):
        super().__init__(title = "Manager")
        Ui_Form.__init__(self)
        self.setupUi(self)          # 加载UI
        self._loadUI()
        
    def _loadUI(self):
        '''加载UI'''
        
        # 插入各个脚本信息
        for index, script in enumerate(self.gets()):

            label_no = QLabel(str(index + 1), self)
            label_no.setFont(QFont("Arial", 10, QFont.Weight.Bold, italic=True))
            label_name = QLabel(script.name, self)
            label_author = QLabel(script.author, self)
            
            radioButtonT = QRadioButton("T", self)
            radioButtonF = QRadioButton("F", self)
            
            # 启用脚本按钮组
            buttonGroupTF = QButtonGroup(self)
            buttonGroupTF.addButton(radioButtonT, 0)
            buttonGroupTF.addButton(radioButtonF, 1)
            
            if script.enable:
                radioButtonT.setChecked(True)
            else:
                radioButtonF.setChecked(True)

            button_info = QPushButton("edit", self)             # info按钮
            button_desc = QPushButton("edit", self)             # 描述按钮
            button_readme = QPushButton(script.readme, self)    # readme按钮
            button_link = QPushButton(script.link, self)        # 连接按钮
            button_root = QPushButton("OPEN", self)             # 根路径按钮
            
            # 绑定信号
            button_info.clicked.connect(partial(script.openInfo))
            button_desc.clicked.connect(partial(script.openDesc))
            button_readme.clicked.connect(partial(script.openReadme))
            button_root.clicked.connect(partial(script.openRoot))
            
            buttonGroupTF.buttonClicked.connect(partial(script.setEnabled))
            
            index += 1
            # 添加所有控件到网格布局
            self.gridLayout_scripts.addWidget(label_no, index, 0, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(label_name, index, 1, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(label_author, index, 2, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(radioButtonT, index, 3, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(radioButtonF, index, 4, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_info, index, 5, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_desc, index, 6, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_readme, index, 7, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_link, index, 8, Qt.AlignmentFlag.AlignCenter)
            self.gridLayout_scripts.addWidget(button_root, index, 9, Qt.AlignmentFlag.AlignCenter)