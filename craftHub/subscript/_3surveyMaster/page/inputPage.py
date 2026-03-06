##########################################################################################################
#   Description: 输入页面，通过此页面进行信息录入
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from ui.surveyMaster.Ui_input import Ui_Form
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame, QVBoxLayout

class InputWidget(QWidget, Ui_Form):
    '''输入组件'''
    def __init__(self):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)

