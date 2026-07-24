##########################################################################################################
#   Description: CAD表格插入数据读取器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import re

from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

import pandas as pd
from pandas import DataFrame
from ezdxf.math import Vec2

from .data import Data


class Reader:
    '''CAD表格插入数据读取器'''

    HEADER_ROW_INDEX = 0
    FIRST_DATA_ROW_INDEX = 1

    HEADER_TAG = "TAG"
    HEADER_INSERT_POINT = "插入点"

    START_COL_MARK = "<s>"
    END_COL_MARK = "<e>"

    # 这是匹配一个什么字符串
    POINT_PATTERN = re.compile(
        r"^\s*(?:Vec|Vec2)\s*\(\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
        r"\s*,\s*"
        r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
        r"\s*\)\s*$"
    )

    def __init__(
            self,
            excelPath: Path,
            sheetName: str
    ) -> None:
        '''初始化读取器

        :param excelPath: Excel文件路径
        :param sheetName: 待读取的Sheet名称
        '''

        self.excelPath = Path(excelPath)
        self.sheetName = sheetName

        if not self.excelPath.exists():
            raise FileNotFoundError(
                f"Excel文件不存在: {self.excelPath}"
            )

        if not self.excelPath.is_file():
            raise ValueError(
                f"Excel路径不是文件: {self.excelPath}"
            )

        if not self.sheetName:
            raise ValueError("sheetName不能为空")

    def read(self) -> List[Data]:
        '''读取Sheet并返回Data列表'''

        tableDF = self._readSheet()

        if tableDF.empty:
            raise ValueError(
                f"Sheet为空，无法读取待插入表格数据: "
                f"{self.sheetName}"
            )

        headerList = self._readHeaderList(tableDF)

        # 找到必须表头TAG
        tagColIndex = self._findRequiredHeaderCol(
            headerList=headerList,
            headerName=self.HEADER_TAG
        )

        # 找到必须表头插入点
        insertPointColIndex = self._findRequiredHeaderCol(
            headerList=headerList,
            headerName=self.HEADER_INSERT_POINT
        )

        # 定位开始列和结束列
        startColIndex, endColIndex = self._findInsertColRange(
            headerList=headerList
        )

        # 解析数据列表
        dataList = self._buildDataList(
            tableDF=tableDF,
            tagColIndex=tagColIndex,
            insertPointColIndex=insertPointColIndex,
            startColIndex=startColIndex,
            endColIndex=endColIndex
        )

        if len(dataList) == 0:
            raise ValueError(
                f"Sheet中没有读取到任何有效TAG数据: "
                f"{self.sheetName}"
            )

        return dataList

    def toDataList(self) -> List[Data]:
        '''读取Sheet并导出Data列表'''

        return self.read()

    def _readSheet(self) -> DataFrame:
        '''读取完整Sheet，第一行保留为普通数据行'''

        try:
            return pd.read_excel(
                self.excelPath,
                sheet_name=self.sheetName,
                header=None,
                dtype=object,
                keep_default_na=False
            )

        except ValueError as e:
            raise ValueError(
                f"无法读取Sheet '{self.sheetName}': {e}"
            ) from e

        except Exception as e:
            raise RuntimeError(
                f"读取Excel失败: {self.excelPath} | "
                f"Sheet={self.sheetName} | {e}"
            ) from e

    def _readHeaderList(
            self,
            tableDF: DataFrame
    ) -> List[str]:
        '''读取并规范化第一行表头, 获取表头列表'''

        if len(tableDF.index) <= self.HEADER_ROW_INDEX:
            raise ValueError(
                f"Sheet中不存在表头行: {self.sheetName}"
            )

        headerList: List[str] = []

        for colIndex in range(len(tableDF.columns)):
            rawValue = tableDF.iat[
                self.HEADER_ROW_INDEX,
                colIndex
            ]

            if self._isEmpty(rawValue):
                headerList.append("")
                continue

            headerList.append(str(rawValue).strip())

        return headerList

    def _findRequiredHeaderCol(
            self,
            headerList: Sequence[str],
            headerName: str
    ) -> int:
        '''查找必须且唯一存在的表头列'''

        matchIndexList = [
            colIndex
            for colIndex, currentHeader in enumerate(headerList)
            if currentHeader == headerName
        ]

        if len(matchIndexList) == 0:
            raise ValueError(
                f"Sheet第一行中不存在必须表头: {headerName}"
            )

        if len(matchIndexList) > 1:
            excelColList = [
                Data.colIndexToName(colIndex + 1)
                for colIndex in matchIndexList
            ]

            raise ValueError(
                f"Sheet第一行中存在多个'{headerName}'表头: "
                f"{', '.join(excelColList)}"
            )

        return matchIndexList[0]

    def _findInsertColRange(
            self,
            headerList: Sequence[str]
    ) -> Tuple[int, int]:
        '''根据<s>和<e>确定待插入列闭区间'''

        startMarkColList = self._findMarkColList(
            headerList=headerList,
            mark=self.START_COL_MARK
        )

        endMarkColList = self._findMarkColList(
            headerList=headerList,
            mark=self.END_COL_MARK
        )

        if len(startMarkColList) == 0:
            raise ValueError(
                f"Sheet第一行中不存在开始列标记: "
                f"{self.START_COL_MARK}"
            )

        if len(startMarkColList) > 1:
            raise ValueError(
                f"Sheet第一行中存在多个开始列标记"
                f"'{self.START_COL_MARK}': "
                f"{self._formatColIndexList(startMarkColList)}"
            )

        if len(endMarkColList) == 0:
            raise ValueError(
                f"Sheet第一行中不存在结束列标记: "
                f"{self.END_COL_MARK}"
            )

        if len(endMarkColList) > 1:
            raise ValueError(
                f"Sheet第一行中存在多个结束列标记"
                f"'{self.END_COL_MARK}': "
                f"{self._formatColIndexList(endMarkColList)}"
            )

        startColIndex = startMarkColList[0]
        endColIndex = endMarkColList[0]

        if startColIndex > endColIndex:
            startColName = Data.colIndexToName(
                startColIndex + 1
            )

            endColName = Data.colIndexToName(
                endColIndex + 1
            )

            raise ValueError(
                f"开始列标记不能位于结束列标记之后: "
                f"开始列={startColName}, 结束列={endColName}"
            )

        return startColIndex, endColIndex

    def _findMarkColList(
            self,
            headerList: Sequence[str],
            mark: str
    ) -> List[int]:
        '''查找指定标记出现的列'''

        markColList: List[int] = []

        for colIndex, headerValue in enumerate(headerList):
            markCount = headerValue.count(mark)

            for _ in range(markCount):
                markColList.append(colIndex)

        return markColList

    def _buildDataList(
            self,
            tableDF: DataFrame,
            tagColIndex: int,
            insertPointColIndex: int,
            startColIndex: int,
            endColIndex: int
    ) -> List[Data]:
        '''根据相同且连续的TAG生成Data列表'''

        dataList: List[Data] = []

        currentTag: Optional[str] = None
        currentStartRowIndex: Optional[int] = None

        for rowIndex in range(
                self.FIRST_DATA_ROW_INDEX,
                len(tableDF.index)
        ):
            tag = self._normalizeTag(
                tableDF.iat[rowIndex, tagColIndex]
            )

            # 空TAG会结束当前分组
            if tag is None:
                if (
                        currentTag is not None
                        and currentStartRowIndex is not None
                ):
                    dataList.append(
                        self._buildData(
                            tableDF=tableDF,
                            tag=currentTag,
                            startRowIndex=currentStartRowIndex,
                            endRowIndex=rowIndex - 1,
                            insertPointColIndex=insertPointColIndex,
                            startColIndex=startColIndex,
                            endColIndex=endColIndex
                        )
                    )

                    currentTag = None
                    currentStartRowIndex = None

                continue

            # 开始一个新分组
            if currentTag is None:
                currentTag = tag
                currentStartRowIndex = rowIndex
                continue

            # TAG保持不变，继续当前分组
            if tag == currentTag:
                continue

            # TAG发生变化，结束旧分组并开始新分组
            dataList.append(
                self._buildData(
                    tableDF=tableDF,
                    tag=currentTag,
                    startRowIndex=currentStartRowIndex,  # type: ignore
                    endRowIndex=rowIndex - 1,
                    insertPointColIndex=insertPointColIndex,
                    startColIndex=startColIndex,
                    endColIndex=endColIndex
                )
            )

            currentTag = tag
            currentStartRowIndex = rowIndex

        # Sheet结尾仍存在未完成分组
        if (
                currentTag is not None
                and currentStartRowIndex is not None
        ):
            dataList.append(
                self._buildData(
                    tableDF=tableDF,
                    tag=currentTag,
                    startRowIndex=currentStartRowIndex,
                    endRowIndex=len(tableDF.index) - 1,
                    insertPointColIndex=insertPointColIndex,
                    startColIndex=startColIndex,
                    endColIndex=endColIndex
                )
            )

        return dataList

    def _buildData(
            self,
            tableDF: DataFrame,
            tag: str,
            startRowIndex: int,
            endRowIndex: int,
            insertPointColIndex: int,
            startColIndex: int,
            endColIndex: int
    ) -> Data:
        '''生成一个连续TAG分组对应的Data'''

        fixedInsertPoint = self._readFixedInsertPoint(
            tableDF=tableDF,
            tag=tag,
            startRowIndex=startRowIndex,
            endRowIndex=endRowIndex,
            insertPointColIndex=insertPointColIndex
        )

        return Data(
            sheetName=self.sheetName,
            tag=tag,

            # pandas使用0基索引，Excel使用1基索引
            startRow=startRowIndex + 1,
            endRow=endRowIndex + 1,
            startCol=startColIndex + 1,
            endCol=endColIndex + 1,

            fixedInsertPoint=fixedInsertPoint
        )

    def _readFixedInsertPoint(
            self,
            tableDF: DataFrame,
            tag: str,
            startRowIndex: int,
            endRowIndex: int,
            insertPointColIndex: int
    ) -> Optional[Vec2]:
        '''读取一个TAG分组中的固定插入点'''

        pointItemList: List[Tuple[int, Any]] = []

        for rowIndex in range(
                startRowIndex,
                endRowIndex + 1
        ):
            rawValue = tableDF.iat[
                rowIndex,
                insertPointColIndex
            ]

            if self._isEmpty(rawValue):
                continue

            pointItemList.append(
                (rowIndex, rawValue)
            )

        if len(pointItemList) == 0:
            return None

        if len(pointItemList) > 1:
            cellAddressList = [
                self._cellAddress(
                    rowIndex=rowIndex,
                    colIndex=insertPointColIndex
                )
                for rowIndex, _ in pointItemList
            ]

            raise ValueError(
                f"TAG '{tag}' 的插入点列中存在多个非空值: "
                f"{', '.join(cellAddressList)}"
            )

        rowIndex, rawValue = pointItemList[0]

        return self._parseInsertPoint(
            rawValue=rawValue,
            cellAddress=self._cellAddress(
                rowIndex=rowIndex,
                colIndex=insertPointColIndex
            )
        )

    def _parseInsertPoint(
            self,
            rawValue: Any,
            cellAddress: str
    ) -> Vec2:
        '''将插入点对象或字符串转换为Vec2'''

        # 支持Vec、Vec2及其他带x、y属性的对象
        if (
                hasattr(rawValue, "x")
                and hasattr(rawValue, "y")
        ):
            try:
                return Vec2(
                    float(rawValue.x),
                    float(rawValue.y)
                )

            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"插入点对象坐标无法转换为数字: "
                    f"{cellAddress}={rawValue}"
                ) from e

        # 额外支持二元tuple和list
        if (
                isinstance(rawValue, (tuple, list))
                and len(rawValue) == 2
        ):
            try:
                return Vec2(
                    float(rawValue[0]),
                    float(rawValue[1])
                )

            except (TypeError, ValueError) as e:
                raise ValueError(
                    f"插入点序列坐标无法转换为数字: "
                    f"{cellAddress}={rawValue}"
                ) from e

        # Excel中通常保存的是字符串
        if isinstance(rawValue, str):
            normalizedValue = (
                rawValue
                .replace("，", ",")
                .strip()
            )

            matchResult = self.POINT_PATTERN.fullmatch(
                normalizedValue
            )

            if matchResult is not None:
                return Vec2(
                    float(matchResult.group(1)),
                    float(matchResult.group(2))
                )

        raise ValueError(
            f"插入点格式不正确: "
            f"{cellAddress}={rawValue!r}; "
            f"支持格式示例: "
            f"Vec(100, 200) 或 Vec2(100, 200)"
        )

    def _normalizeTag(
            self,
            rawValue: Any
    ) -> Optional[str]:
        '''规范化TAG值，空值返回None'''

        if self._isEmpty(rawValue):
            return None

        if isinstance(rawValue, bool):
            return str(rawValue)

        if isinstance(rawValue, int):
            return str(rawValue)

        if isinstance(rawValue, float):
            if rawValue.is_integer():
                return str(int(rawValue))

            return str(rawValue)

        normalizedTag = str(rawValue).strip()

        if not normalizedTag:
            return None

        return normalizedTag

    @staticmethod
    def _isEmpty(rawValue: Any) -> bool:
        '''判断Excel单元格值是否为空'''

        if rawValue is None:
            return True

        if isinstance(rawValue, str):
            return len(rawValue.strip()) == 0

        try:
            return bool(pd.isna(rawValue))

        except (TypeError, ValueError):
            return False

    @staticmethod
    def _cellAddress(
            rowIndex: int,
            colIndex: int
    ) -> str:
        '''将0基行列索引转换为Excel单元格地址'''

        colName = Data.colIndexToName(colIndex + 1)
        return f"{colName}{rowIndex + 1}"

    @staticmethod
    def _formatColIndexList(
            colIndexList: Sequence[int]
    ) -> str:
        '''格式化0基列索引列表'''

        return ", ".join(
            Data.colIndexToName(colIndex + 1)
            for colIndex in colIndexList
        )