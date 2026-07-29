##########################################################################################################
#   Description: 表格插入器工作线程
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import traceback

import pythoncom

from PyQt6.QtCore import (
    QThread,
    pyqtSignal,
    pyqtSlot
)

from .main import TableInserterMain


class TableInserterWorker(QThread):
    '''表格插入器工作线程'''

    insertStarted = pyqtSignal()

    succeeded = pyqtSignal(
        int,
        int,
        int
    )

    stopped = pyqtSignal(
        int,
        int,
        int
    )

    failed = pyqtSignal(
        str,
        str
    )

    def __init__(
            self,
            tableInserterMain: TableInserterMain
    ) -> None:
        super().__init__()

        self.tableInserterMain = (
            tableInserterMain
        )

        self.tableInserterMain.setInsertStartedCallback(
            self._emitInsertStarted
        )

    def run(self) -> None:
        '''执行表格插入任务'''

        pythoncom.CoInitialize()

        try:
            dataList = (
                self.tableInserterMain.run()
            )

            totalCount = len(dataList)

            locatedCount = sum(
                data.insertPoint is not None
                for data in dataList
            )

            insertedCount = sum(
                getattr(
                    data,
                    "cadObject",
                    None
                ) is not None
                for data in dataList
            )

            if (
                    self.tableInserterMain
                    .wasStopped
            ):
                self.stopped.emit(
                    totalCount,
                    locatedCount,
                    insertedCount
                )

            else:
                self.succeeded.emit(
                    totalCount,
                    locatedCount,
                    insertedCount
                )

        except Exception as e:
            self.failed.emit(
                str(e),
                traceback.format_exc()
            )

        finally:
            self.tableInserterMain.setInsertStartedCallback(
                None
            )

            pythoncom.CoUninitialize()

    @pyqtSlot()
    def requestStop(self) -> None:
        '''请求停止后续表格插入'''

        self.tableInserterMain.requestStop()

    def _emitInsertStarted(self) -> None:
        '''通知GUI已经进入逐个表格插入阶段'''

        self.insertStarted.emit()