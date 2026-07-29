##########################################################################################################
#   Description: Excel与WPS表格进程管理器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import threading
from typing import Dict, Set
import psutil
from craftHub.tool import GLog


class ExcelProcessManager:
    '''Excel与WPS表格进程管理器'''

    PROCESS_NAME_EXCEL = "excel.exe"
    PROCESS_NAME_WPS_TABLE = "et.exe"

    PROCESS_NAME_SET = {
        PROCESS_NAME_EXCEL,
        PROCESS_NAME_WPS_TABLE
    }

    PROCESS_TERMINATE_WAIT_SECONDS = 2.0

    # PID对应进程创建时间。
    # 同时记录创建时间，可以避免操作系统重复使用PID时产生误判。
    _recordedProcessMap: Dict[int, float] = {}

    _hasRecorded = False
    _processLock = threading.RLock()

    @classmethod
    def record(cls) -> Set[int]:
        '''记录当前存在的Excel和WPS表格进程

        再次调用该方法时，会完全刷新此前保存的进程记录。

        :return: 当前记录的进程PID集合
        '''

        with cls._processLock:
            cls._recordedProcessMap = (
                cls._getCurrentProcessMap()
            )

            cls._hasRecorded = True

            recordedPIDSet = set(
                cls._recordedProcessMap.keys()
            )

        GLog.logInfo(
            f"已记录Excel与WPS表格进程: "
            f"{sorted(recordedPIDSet)}"
        )

        return recordedPIDSet

    @classmethod
    def kill(cls) -> Set[int]:
        '''结束最近一次record后新增的Excel和WPS表格进程

        :return: 已请求结束的新增进程PID集合
        '''

        with cls._processLock:
            if not cls._hasRecorded:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"尚未记录Excel进程，"
                    f"无法判断哪些进程属于新增进程"
                    f"{GLog.END}"
                )

                return set()

            currentProcessMap = (
                cls._getCurrentProcessMap()
            )

            newProcessMap = {
                processPID: createTime
                for processPID, createTime
                in currentProcessMap.items()
                if (
                    cls._recordedProcessMap.get(
                        processPID
                    ) != createTime
                )
            }

        if not newProcessMap:
            GLog.logInfo(
                "未检测到新增Excel或WPS表格进程"
            )

            return set()

        newPIDSet = set(
            newProcessMap.keys()
        )

        GLog.logInfo(
            f"{GLog.YELLOW}"
            f"检测到新增Excel与WPS表格进程，"
            f"准备结束: "
            f"{sorted(newPIDSet)}"
            f"{GLog.END}"
        )

        cls._killProcessMap(
            processMap=newProcessMap
        )

        return newPIDSet

    @classmethod
    def _getCurrentProcessMap(
            cls
    ) -> Dict[int, float]:
        '''获取当前Excel和WPS表格进程'''

        processMap: Dict[int, float] = {}

        for process in psutil.process_iter(
                attrs=[
                    "pid",
                    "name",
                    "create_time"
                ]
        ):
            try:
                processName = str(
                    process.info.get("name")
                    or ""
                ).lower()

                if (
                        processName
                        not in cls.PROCESS_NAME_SET
                ):
                    continue

                processPID = int(
                    process.info["pid"]
                )

                createTime = float(
                    process.info["create_time"]
                )

                processMap[
                    processPID
                ] = createTime

            except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                    TypeError,
                    ValueError
            ):
                continue

        return processMap

    @classmethod
    def _killProcessMap(
            cls,
            processMap: Dict[int, float]
    ) -> None:
        '''结束指定的Excel和WPS表格进程'''

        terminatedProcessList = []

        for processPID, expectedCreateTime in (
                processMap.items()
        ):
            try:
                process = psutil.Process(
                    processPID
                )

                processName = (
                    process.name().lower()
                )

                actualCreateTime = float(
                    process.create_time()
                )

                # 防止扫描完成后PID被其他程序重新使用。
                if (
                        processName
                        not in cls.PROCESS_NAME_SET
                ):
                    continue

                if (
                        actualCreateTime
                        != expectedCreateTime
                ):
                    continue

                process.terminate()

                terminatedProcessList.append(
                    process
                )

                GLog.logInfo(
                    f"正在结束表格进程: "
                    f"PID={processPID}, "
                    f"Name={processName}"
                )

            except psutil.NoSuchProcess:
                continue

            except psutil.AccessDenied as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"没有权限结束表格进程: "
                    f"PID={processPID}, "
                    f"错误={e}"
                    f"{GLog.END}"
                )

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"结束表格进程失败: "
                    f"PID={processPID}, "
                    f"错误={e}"
                    f"{GLog.END}"
                )

        if not terminatedProcessList:
            return

        _, aliveProcessList = (
            psutil.wait_procs(
                terminatedProcessList,
                timeout=(
                    cls.PROCESS_TERMINATE_WAIT_SECONDS
                )
            )
        )

        # terminate后仍未退出，再强制结束。
        for process in aliveProcessList:
            try:
                processPID = process.pid

                process.kill()

                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"强制结束残留表格进程: "
                    f"PID={processPID}"
                    f"{GLog.END}"
                )

            except psutil.NoSuchProcess:
                continue

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"强制结束表格进程失败: "
                    f"PID={process.pid}, "
                    f"错误={e}"
                    f"{GLog.END}"
                )