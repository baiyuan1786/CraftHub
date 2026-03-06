##########################################################################################################
#   Description: 工勘大师主要页面
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from page import Page
from ui.surveyMaster.Ui_main import Ui_Form

from .slider import SwitchSlider
from .inputPage import InputWidget
from .outputPage import OutputWidget

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout
from PyQt6.QtCore import QPoint, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QMouseEvent

class SurveyMasterPage(Page, Ui_Form):
    '''工勘大师页面'''
    def __init__(self, title: str = "SurveyMaster"):
        Page.__init__(self, title = title)
        Ui_Form.__init__(self)
        self.setupUi(self)
        
        # 滑块
        self.slider = SwitchSlider()
        self.slider.stateChanged.connect(self.onModeSwitched)
        
        # 创建两个页面
        self.inputWidget = InputWidget()
        self.outputWidget = OutputWidget()
    
        # 页面容器
        self.stackedWidget = QWidget()
        self.stackedLayout = QVBoxLayout()
        self.stackedWidget.setLayout(self.stackedLayout)
        
        # 布局
        self.mainLayout.addWidget(self.slider)
        self.mainLayout.addWidget(self.stackedWidget)

        # 初始显示录入页面
        self.stackedLayout.addWidget(self.inputWidget)
        self.currentWidget = self.inputWidget

    # 切换模式
    def onModeSwitched(self, isLeft):
        """处理模式切换信号"""
        # 移除当前页面
        self.stackedLayout.removeWidget(self.currentWidget)
        self.currentWidget.hide()
        
        # 添加新页面
        if isLeft:
            self.currentWidget = self.inputWidget
        else:
            self.currentWidget = self.outputWidget
        
        self.stackedLayout.addWidget(self.currentWidget)
        self.currentWidget.show()
        
    
