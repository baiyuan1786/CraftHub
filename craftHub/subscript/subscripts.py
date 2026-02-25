##########################################################################################################
#   Description: 子脚本群管理，子脚本管理器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from craftHub.tool import gLog
from .subscript import Subscript
from ._1AutoRoute import AutoRoute
from ._2ImageSplit import SplitImage

from typing import List

MNG_IS_INIT = False
class SubscriptsMng:
    '''子脚本管理器， 
    维护所有子脚本信息, 子脚本管理器实例仅允许存在一个'''
    def __init__(self):
        global MNG_IS_INIT
        if MNG_IS_INIT:
            raise Exception("[SubscriptsMng]can only init once")
        
        self.subscriptList: List[Subscript] = []

        try:
            self.subscriptList.append(AutoRoute())
        except Exception as e:
            gLog.logInfo(f"Load \'AutoRoute\' failed: {str(e)}")
        
        try:
            self.subscriptList.append(SplitImage())
        except Exception as e:
            gLog.logInfo(f"Load \'SplitImage\' failed: {str(e)}")
        
        MNG_IS_INIT = True
         
    def gets(self):
        '''获取子脚本列表'''
        return self.subscriptList
    
# 全局子脚本管理器
gSubscriptMng = SubscriptsMng()