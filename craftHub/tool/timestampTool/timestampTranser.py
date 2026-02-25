##########################################################################################################
#   Description: 时间戳转换模块
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from craftHub.tool import tryDo
from page import Page
from ui.timestampTool.Ui_timestamp import Ui_TimestampTranser

from datetime import datetime

class TimestampTranser(Page, Ui_TimestampTranser):
    '''时间戳转换器'''
    def __init__(self):
        Page.__init__(self, title = "TimestampTranser")
        Ui_TimestampTranser.__init__(self)
        self.setupUi(self)
        
    @tryDo(title = "转换时间戳")
    def _trans(self):
        """将左侧文本框的时间戳转换为右侧的UTC-8标准时间
        """        
        
        rawTimestampList = self.plainTextEdit_src.toPlainText().splitlines()
        transTimestampList = [datetime.fromtimestamp(int(timestamp)) for timestamp in rawTimestampList]
        
        self.plainTextEdit_dst.clear()
        for transTimestamp in transTimestampList:
            self.plainTextEdit_dst.insertPlainText(str(transTimestamp) + "\n")