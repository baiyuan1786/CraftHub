##########################################################################################################
#   Description: 工具子脚本函数
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .page.subPage import ImageSplitPage
from .subPath import PATH_INFO, PATH_DESC

from ..subscript import Subscript

class SplitImage(Subscript):
    '''工勘图片切割工具'''
    def __init__(self):
        super().__init__(name = "SplitImage",
                         pageCls = ImageSplitPage,
                         infoPath = PATH_INFO,
                         descPath = PATH_DESC)