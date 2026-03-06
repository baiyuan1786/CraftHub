##########################################################################################################
#   Description: 输出页面，通过此页面显示信息
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from ui.surveyMaster.Ui_output import Ui_Form
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout

class OutputWidget(QWidget, Ui_Form):
    '''输出组件'''
    def __init__(self):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)
