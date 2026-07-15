##########################################################################################################
#   Description: 线程绘图进程
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..core import DrawingMasterCore
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

class PlotWorker(QThread):
    finishedSignal = pyqtSignal()
    errorSignal = pyqtSignal(str)

    def __init__(self, core: DrawingMasterCore):
        super().__init__()
        self.core = core

    def run(self):
        try:
            self.core.plot()
            self.finishedSignal.emit()
        except Exception as e:
            self.errorSignal.emit(str(e))