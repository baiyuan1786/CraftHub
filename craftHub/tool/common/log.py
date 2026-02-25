##########################################################################################################
#   Description: log工具
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

import os
import sys
import subprocess
import threading
import queue
from datetime import datetime
from path import PATH_LOG_ROOT
from typing import Literal

IS_LOG_INIT = False

class Log:
    '''全局自定义log'''
    
    # 颜色参数
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    def __init__(self):
        global IS_LOG_INIT
        if IS_LOG_INIT:
            raise Exception("Log can only init once")
        else:
            IS_LOG_INIT = True

        self.logPath = PATH_LOG_ROOT / f"HUB_{self.date()}.log"
        with self.logPath.open('w+', encoding = 'utf-8') as file:
            file.write(f"===================PY CRAFT HUB EXPORT LOG {self.date()}================\n\n")

    def open(self):
        '''打开log文件'''
        try:
            os.startfile(self.logPath)
        except Exception as e:
            raise Exception(f"open log fail: {str(e)}")

    def date(self, timeFormat : Literal["underLine", 'suffix', 'log'] = "underLine"):
        '''获取时间后缀'''
        curDateTime = datetime.now()
        timeFormatDicr = {
            "underLine": curDateTime.strftime("%Y_%m_%d_%H_%M_%S"),
            "suffix": curDateTime.strftime("%Y%m%d%H%M%S"),
            "log": curDateTime.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            return timeFormatDicr[timeFormat]
        except Exception:
            raise ValueError(f"undefined format \'{timeFormat}\'")

    def logInfo(self, *args, **kwargs):
        '''输出log信息'''
        datatimelog = "[{0}]".format(self.date(timeFormat = "log"))

        print(datatimelog, end = "")
        print(*args, **kwargs)

        try:
            with self.logPath.open("a", encoding = "utf-8") as file:
                outPutStr = " ".join(map(str, args))
                file.write(datatimelog + outPutStr + "\n")
        except Exception as e:
            raise Exception(f"写入log失败: {str(e)}")

    def logInfoWithNoTime(self, *args, **kwargs):
        '''不带时间的输出log信息'''

        print(*args, **kwargs)

        with self.logPath.open("a", encoding = "utf-8") as file:
            outPutStr = " ".join(map(str, args))
            file.write(outPutStr + "\n")
            
    def enter(self):
        '''输出一个单独的回车'''
        self.logInfoWithNoTime("")

    def logInfoSubRun(self, executable, *args):
        '''提供一个python源码或者exe, 将以子线程形式运行这个代码, 代码运行时, 其输出也会同时被输出到log中'''
        def enqueue_output(out, queue):

            for line in iter(out.readline, ''):
                queue.put(line)
            out.close()

        self.logInfo(f"[logInfoSubRun]执行子脚本 {executable} {list(args)}")
        if not os.path.exists(executable):
            raise FileNotFoundError(f"{executable} 不存在，该脚本不支持以此方式运行")

        # 确定是否为合法程序
        if executable.endswith('.py'):
            command = [sys.executable, '-u', executable] + list(args)
        elif executable.endswith('.exe'):
            command = [executable] + list(args)
        else:
            raise TypeError(f"[logInfoSubRun]使用了不支持格式的子脚本: {executable}")

        # 创建子进程
        proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, text = True, bufsize = 1, cwd = os.path.dirname(executable))
        q = queue.Queue()

        # 启动线程来捕获输出
        t = threading.Thread(target = enqueue_output, args = (proc.stdout, q))
        t.daemon = True
        t.start()

        # 读取输出
        while True:
            try:
                line = q.get(timeout = .1)    # 调整超时时间
                line = line.rstrip()
                self.logInfo(line)
            except queue.Empty:
                if proc.poll() is not None:
                    break

        # 确保线程结束
        t.join()

gLog = Log()