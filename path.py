##########################################################################################################
#   Description: 重构路径管理器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
import os
import sys
import win32com.client

from pathlib import Path

# 工具根路径
PATH_ROOT = Path(__file__).parent.resolve()
PATH_SUBSCRIPT = PATH_ROOT / "craftHub" / "subscript"

# 全局路径规划
PATH_RESOURCE = PATH_ROOT / "doc"
PATH_README = PATH_RESOURCE / "readme"
PATH_LOG_ROOT = PATH_RESOURCE / "log" / "hub"
PATH_SERIAL_LOG_ROOT = PATH_RESOURCE / "log" / "serial"

# 依赖路径
PATH_DEPENDENCE = PATH_ROOT / "dependence"
PATH_DEPENDENCEZIP = PATH_ROOT / "dependence.zip"
PATH_IPERF_FULL = PATH_DEPENDENCE / "iperf" / "iperf3.exe"
PATH_ADB = PATH_DEPENDENCE / "adb" / "adb.exe"
PATH_EDGE_DRIVER = PATH_DEPENDENCE / "edgedriver_win64" / "msedgedriver.exe"
PATH_PADDLEOCR = PATH_DEPENDENCE / "paddleocr"
PATH_CNOCR = PATH_DEPENDENCE / "cnocr"

PATH_DESKTOP = Path(win32com.client.Dispatch("WScript.Shell").SpecialFolders("Desktop")) # 桌面路径，windows下有效
