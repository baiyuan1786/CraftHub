##########################################################################################################
#   Description: IDN集成式网络数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...common.reader.reader import Reader
from .dataUnit import DataUnitIDN

from pathlib import Path


class ReaderIDN(Reader):
    def __init__(self, excelPath: Path, sheetName: str) -> None:
        super().__init__(excelPath, sheetName)
        
    def __iter__(self):
        return iter([DataUnitIDN(index, self.dfDict) for index in range(len(self)) ])
   