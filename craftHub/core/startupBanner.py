##########################################################################################################
#   Description: CraftHub启动Banner打印器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from datetime import datetime
from typing import List
from .version import CraftHubVersion

from ..tool import GLog
class StartupBanner:
    '''CraftHub启动Banner打印器'''

    LOGO = \
r"""
   ____            __ _   _   _       _     
  / ___|_ __ __ _ / _| |_| | | |_   _| |__  
 | |   | '__/ _` | |_| __| |_| | | | | '_ \ 
 | |___| | | (_| |  _| |_|  _  | |_| | |_) |
  \____|_|  \__,_|_|  \__|_| |_|\__,_|_.__/ 

                    CraftHub
"""

    SEPARATOR = "=" * 70

    @classmethod
    def printBanner(cls):
        '''打印启动Banner'''

        startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        GLog.logInfoWithNoTime(cls.SEPARATOR)
        GLog.logInfoWithNoTime(cls.LOGO)
        GLog.logInfoWithNoTime(cls.SEPARATOR)
        GLog.logInfoWithNoTime(f"Version : {CraftHubVersion.APP_VERSION}")
        GLog.logInfoWithNoTime(f"Author  : {CraftHubVersion.APP_AUTHOR}")
        GLog.logInfoWithNoTime(f"Start   : {startTime}")
        GLog.logInfoWithNoTime(cls.SEPARATOR)
        GLog.logInfoWithNoTime()