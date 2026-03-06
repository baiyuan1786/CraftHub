##########################################################################################################
#   Description: 工具子脚本函数
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .page.subPage import SurveyMasterPage
from .subPath import PATH_INFO, PATH_DESC

from ..subscript import Subscript

class SurveyMaster(Subscript):
    '''工勘图片切割工具'''
    def __init__(self):
        super().__init__(name = "SurveyMaster",
                         pageCls = SurveyMasterPage,
                         infoPath = PATH_INFO,
                         descPath = PATH_DESC)