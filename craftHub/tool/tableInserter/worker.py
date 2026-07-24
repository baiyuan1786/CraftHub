##########################################################################################################
#   Description: 表格插入器工作线程
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import traceback

import pythoncom

from PyQt6.QtCore import QThread, pyqtSignal

from .main import TableInserterMain


class TableInserterWorker(QThread):
    '''表格插入器工作线程'''

    succeeded = pyqtSignal(
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
        """初始化表格插入器工作线程

        :param tableInserterMain: 表格插入器业务主类
        """

        super().__init__()

        self.tableInserterMain = (
            tableInserterMain
        )

    def run(self) -> None:
        '''在线程中执行完整表格插入流程'''

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
            pythoncom.CoUninitialize()