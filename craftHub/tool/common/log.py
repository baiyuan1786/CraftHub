##########################################################################################################
#   Description: log工具
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional

from path import PATH_LOG_ROOT


class GLog:
    '''全局自定义log'''

    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"

    LOG_FILE_PREFIX = "HUB"
    LOG_FILE_SUFFIX = ".log"
    LOG_ENCODING = "utf-8"

    TIME_FORMAT_UNDER_LINE = "underLine"
    TIME_FORMAT_SUFFIX = "suffix"
    TIME_FORMAT_LOG = "log"

    SUBPROCESS_READ_TIMEOUT = 0.1

    PYTHON_FILE_SUFFIX = ".py"
    EXE_FILE_SUFFIX = ".exe"

    LOG_HEADER_TEMPLATE = "===================PY CRAFT HUB EXPORT LOG {date}================\n\n"

    isInitialized = False
    logPath: Optional[Path] = None

    def __new__(cls, *args, **kwargs):
        '''禁止实例化Log类'''

        raise TypeError("Log不允许实例化，请直接使用Log.logInfo(...)或GLog.logInfo(...)")

    @classmethod
    def init(cls):
        '''初始化Log工具'''

        if cls.isInitialized:
            return

        PATH_LOG_ROOT.mkdir(parents=True, exist_ok=True)

        cls.logPath = PATH_LOG_ROOT / f"{cls.LOG_FILE_PREFIX}_{cls.date()}{cls.LOG_FILE_SUFFIX}"

        with cls.logPath.open("w+", encoding=cls.LOG_ENCODING) as file:
            file.write(cls.LOG_HEADER_TEMPLATE.format(date=cls.date()))

        cls.isInitialized = True

    @classmethod
    def open(cls):
        '''打开log文件'''

        cls._ensureInitialized()

        try:
            os.startfile(cls.logPath)  # type: ignore[arg-type]
        except Exception as error:
            raise Exception(f"open log fail: {str(error)}")

    @classmethod
    def date(
            cls,
            timeFormat: Literal["underLine", "suffix", "log"] = "underLine"
    ) -> str:
        '''获取时间后缀'''

        curDateTime = datetime.now()

        timeFormatDict = {
            cls.TIME_FORMAT_UNDER_LINE: curDateTime.strftime("%Y_%m_%d_%H_%M_%S"),
            cls.TIME_FORMAT_SUFFIX: curDateTime.strftime("%Y%m%d%H%M%S"),
            cls.TIME_FORMAT_LOG: curDateTime.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if timeFormat not in timeFormatDict:
            raise ValueError(f"undefined format '{timeFormat}'")

        return timeFormatDict[timeFormat]

    @classmethod
    def logInfo(cls, *args, **kwargs):
        '''输出log信息'''

        cls._ensureInitialized()

        dateTimeLog = f"[{cls.date(timeFormat=cls.TIME_FORMAT_LOG)}]"

        print(dateTimeLog, end="")
        print(*args, **kwargs)

        try:
            with cls.logPath.open("a", encoding=cls.LOG_ENCODING) as file:  # type: ignore[union-attr]
                outputStr = " ".join(map(str, args))
                file.write(dateTimeLog + outputStr + "\n")
        except Exception as error:
            raise Exception(f"写入log失败: {str(error)}")

    @classmethod
    def logInfoWithNoTime(cls, *args, **kwargs):
        '''不带时间的输出log信息'''

        cls._ensureInitialized()

        print(*args, **kwargs)

        try:
            with cls.logPath.open("a", encoding=cls.LOG_ENCODING) as file:  # type: ignore[union-attr]
                outputStr = " ".join(map(str, args))
                file.write(outputStr + "\n")
        except Exception as error:
            raise Exception(f"写入log失败: {str(error)}")

    @classmethod
    def enter(cls):
        '''输出一个单独的回车'''

        cls.logInfoWithNoTime("")

    @classmethod
    def logInfoSubRun(cls, executable: str | Path, *args: str):
        '''以子进程方式运行脚本，并将子进程输出同步写入log'''

        cls._ensureInitialized()

        executablePath = Path(executable)

        cls.logInfo(f"[logInfoSubRun]执行子脚本 {executablePath} {list(args)}")

        if not executablePath.exists():
            raise FileNotFoundError(f"{executablePath} 不存在，该脚本不支持以此方式运行")

        command = cls._buildSubRunCommand(executablePath, *args)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(executablePath.parent)
        )

        if process.stdout is None:
            raise RuntimeError("[logInfoSubRun]无法获取子进程输出流")

        outputQueue: queue.Queue[str] = queue.Queue()

        outputThread = threading.Thread(
            target=cls._enqueueOutput,
            args=(process.stdout, outputQueue)
        )
        outputThread.daemon = True
        outputThread.start()

        cls._readSubRunOutput(process, outputQueue)

        outputThread.join()

    @classmethod
    def _ensureInitialized(cls):
        '''确保Log已经初始化'''

        if not cls.isInitialized:
            cls.init()

    @classmethod
    def _buildSubRunCommand(cls, executablePath: Path, *args: str) -> list[str]:
        '''构建子进程运行命令'''

        executableStr = str(executablePath)

        if executableStr.endswith(cls.PYTHON_FILE_SUFFIX):
            return [sys.executable, "-u", executableStr] + list(args)

        if executableStr.endswith(cls.EXE_FILE_SUFFIX):
            return [executableStr] + list(args)

        raise TypeError(f"[logInfoSubRun]使用了不支持格式的子脚本: {executableStr}")

    @staticmethod
    def _enqueueOutput(outputStream, outputQueue: queue.Queue[str]):
        '''将子进程输出写入队列'''

        for line in iter(outputStream.readline, ""):
            outputQueue.put(line)

        outputStream.close()

    @classmethod
    def _readSubRunOutput(
            cls,
            process: subprocess.Popen,
            outputQueue: queue.Queue[str]
    ):
        '''读取子进程输出队列'''

        while True:
            try:
                line = outputQueue.get(timeout=cls.SUBPROCESS_READ_TIMEOUT)
                cls.logInfo(line.rstrip())
            except queue.Empty:
                if process.poll() is not None:
                    break
