##########################################################################################################
#   Description: CAD表格插入数据定义
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from dataclasses import dataclass
from typing import Any, Optional

from ezdxf.math import Vec2


@dataclass
class Data:
    '''待插入Excel子表格数据'''

    sheetName: str
    tag: str

    # Excel中的起止行列均使用1基索引
    startRow: int
    endRow: int
    startCol: int
    endCol: int

    # Excel中配置的固定插入点
    fixedInsertPoint: Optional[Vec2] = None

    # CAD定位器最终计算得到的实际插入点
    insertPoint: Optional[Vec2] = None
    
    # Inserter插入后生成的AutoCAD COM对象
    cadObject: Optional[Any] = None

    def __post_init__(self) -> None:
        '''校验子表格数据'''

        if not self.sheetName:
            raise ValueError("sheetName不能为空")

        if not self.tag:
            raise ValueError("tag不能为空")

        if self.startRow <= 0 or self.endRow <= 0:
            raise ValueError(
                f"Excel行号必须大于0: "
                f"startRow={self.startRow}, endRow={self.endRow}"
            )

        if self.startCol <= 0 or self.endCol <= 0:
            raise ValueError(
                f"Excel列号必须大于0: "
                f"startCol={self.startCol}, endCol={self.endCol}"
            )

        if self.startRow > self.endRow:
            raise ValueError(
                f"开始行不能位于结束行之后: "
                f"startRow={self.startRow}, endRow={self.endRow}"
            )

        if self.startCol > self.endCol:
            raise ValueError(
                f"开始列不能位于结束列之后: "
                f"startCol={self.startCol}, endCol={self.endCol}"
            )

    @staticmethod
    def colIndexToName(colIndex: int) -> str:
        '''将1基Excel列号转换为Excel列名'''

        if colIndex <= 0:
            raise ValueError(f"Excel列号必须大于0: {colIndex}")

        colName = ""
        currentIndex = colIndex

        while currentIndex > 0:
            currentIndex, remainder = divmod(currentIndex - 1, 26)
            colName = chr(ord("A") + remainder) + colName

        return colName

    def rangeAddress(self, includeSheetName: bool = False) -> str:
        '''返回子表格对应的Excel Range地址'''

        startColName = self.colIndexToName(self.startCol)
        endColName = self.colIndexToName(self.endCol)

        rangeAddress = (
            f"{startColName}{self.startRow}:"
            f"{endColName}{self.endRow}"
        )

        if not includeSheetName:
            return rangeAddress

        escapedSheetName = self.sheetName.replace("'", "''")
        return f"'{escapedSheetName}'!{rangeAddress}"

    def hasFixedInsertPoint(self) -> bool:
        '''判断是否配置了固定插入点'''

        return self.fixedInsertPoint is not None

    def hasInsertPoint(self) -> bool:
        '''判断是否已经确定实际CAD插入点'''

        return self.insertPoint is not None