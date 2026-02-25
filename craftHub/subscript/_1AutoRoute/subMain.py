##########################################################################################################
#   Description: 工具子脚本函数
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .subPage import AutoRoutePage
from .subPath import PATH_INFO, PATH_DESC

from ..subscript import Subscript

class AutoRoute(Subscript):
    '''自动化路由计算器'''
    def __init__(self):
        super().__init__(name = "AutoRoute",
                         pageCls = AutoRoutePage,
                         infoPath = PATH_INFO,
                         descPath = PATH_DESC)