##########################################################################################################
#   Description: 地区ddn线缆敷设表导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import List, Optional

import pandas as pd
from pandas import DataFrame
from xlsxwriter.worksheet import Worksheet

from craftHub.tool import GLog

from ....common.reader import DataUnit
from .cableLayTableOne import cableLayTableOne
from .link import EmptyLink


class CableLayTable:
    '''地区ddn线缆敷设表'''

    REFERRNCE_TITLE_LIST: List[str] = [
        "站名",
        "序号",
        "线缆类型",
        "规格",
        "起点",
        "终点",
        "单条长度/m",
        "数量/条",
        "合计/米",
        "备注",
        "走线",
        "跨越机柜",
        "跨越行",
        "跨层",
        "同层跨房间"
    ]

    SHEET_NAME_TEMPLATE = "线缆敷设表(单台设备)"

    COLUMN_LEN_LIST: List[float] = [
        16.5,
        4.5,
        17,
        23.25,
        19.5,
        26.75,
        10.25,
        7,
        7,
        24.5,
        11.3,
        9,
        9,
        9,
        9,
        9,
        34.25
    ]

    ZOOM_SCALE = 70

    FORMAT_INDEX_GREEN_START = 15
    FORMAT_INDEX_RED_START = 13
    FORMAT_INDEX_YELLOW_START = 11

    EMPTY_ROW_NUM = 2

    def __init__(
            self,
            dataUnitFullList: List[DataUnit],
            dataUnitList: List[DataUnit],
            referrenceExcelPath: Optional[Path],
            referrenceSheetName: Optional[str],
            referrenceExcelPath2: Optional[Path] = None,
            referrenceSheetName2: Optional[str] = None
    ) -> None:
        """线缆敷设表初始化

        :param dataUnitFullList:      全部的数据单元
        :param dataUnitList:          有效的数据单元
        :param referrenceExcelPath:   参考表格路径
        :param referrenceSheetName:   参考Sheet名称
        :param referrenceExcelPath2:  第二个参考表格路径
        :param referrenceSheetName2:  第二个参考Sheet名称
        """

        self.dataUnitFullList = dataUnitFullList
        self.dataUnitList = dataUnitList
        self.cableLayExcel = referrenceExcelPath
        self.cableLaySheet = referrenceSheetName

        self.cableLayOneList = [
            cableLayTableOne(data)
            for data in dataUnitList
            if data.get("build")
        ]

        self._readExcel(referrenceExcelPath, referrenceSheetName)
        self._readExcel(referrenceExcelPath2, referrenceSheetName2)

    def _readExcel(
            self,
            referrenceExcelPath: Optional[Path],
            referrenceSheetName: Optional[str]
    ):
        """读取参照表格

        :param referrenceExcelPath: 参照表格文件路径
        :param referrenceSheetName: 参照Sheet名称
        """

        if referrenceExcelPath is None or referrenceSheetName is None:
            GLog.logInfo("无参考表格")
            return

        GLog.logInfo(f"参考表格: {referrenceExcelPath}:{referrenceSheetName}")

        if not referrenceExcelPath.exists():
            raise FileNotFoundError(f"参考表格未找到: '{referrenceExcelPath}'")

        allDF = pd.read_excel(
            io=referrenceExcelPath,
            sheet_name=referrenceSheetName
        )

        notFoundTitleList: List[str] = [
            title
            for title in self.REFERRNCE_TITLE_LIST
            if title not in allDF.columns
        ]

        if notFoundTitleList:
            raise ValueError(f"参考表格缺少列: '{notFoundTitleList}'")

        for cableLayOne in self.cableLayOneList:
            substationName = cableLayOne.substationName
            subDF = allDF[allDF["站名"] == substationName]

            if subDF.empty:
                GLog.logInfo(
                    f"{GLog.YELLOW}没有找到站名为 '{substationName}' 的参考信息{GLog.END}"
                )
                continue

            GLog.logInfo(
                f"{GLog.GREEN}找到站名为 '{substationName}' 的参考信息{GLog.END}"
            )
            cableLayOne.readExcel(subDF=subDF)

    def _toCableLayDataFrame(self) -> DataFrame:
        '''导出线缆敷设表DataFrame'''

        dfList: List[DataFrame] = []

        for cableLayOne in self.cableLayOneList:
            dfList.append(cableLayOne.toDF())

            for _ in range(self.EMPTY_ROW_NUM):
                dfList.append(EmptyLink().toDF())

        if not dfList:
            return EmptyLink().toDF()

        return pd.concat(dfList)

    def export(
            self,
            writer: pd.ExcelWriter,
            project: str
    ):
        '''导出线缆敷设表'''

        sheetName = self.SHEET_NAME_TEMPLATE
        cableLayDF = self._toCableLayDataFrame()

        cableLayDF.to_excel(
            writer,
            sheet_name=sheetName,
            index=False
        )

        workbook = writer.book
        worksheet: Worksheet = writer.sheets[sheetName]

        worksheet.set_zoom(self.ZOOM_SCALE)

        formatDict = {
            "text_wrap": True,
            "align": "center",
            "valign": "vcenter",
            "font_name": "Microsoft YaHei",
            "font_size": 10,
        }

        def makeFormat(**kwargs):
            fmtDict = formatDict.copy()
            fmtDict.update(kwargs)
            return workbook.add_format(fmtDict)  # type: ignore

        formatBase = makeFormat()
        formatR = makeFormat(bg_color="#FF0000")
        formatG = makeFormat(bg_color="#00FF00")
        formatY = makeFormat(bg_color="#FBFF00")

        formatBaseBold = makeFormat(bold=True)
        formatRBold = makeFormat(bg_color="#FF0000", bold=True)
        formatGBold = makeFormat(bg_color="#00FF00", bold=True)
        formatYBold = makeFormat(bg_color="#FBFF00", bold=True)

        for index, columnLen in enumerate(self.COLUMN_LEN_LIST):
            worksheet.set_column(
                index,
                index,
                columnLen,
                self._getColumnFormat(
                    index=index,
                    formatBase=formatBase,
                    formatR=formatR,
                    formatG=formatG,
                    formatY=formatY
                )
            )

        for rowNum, (_, row) in enumerate(cableLayDF.iterrows()):
            if row.iloc[1] != "序号":
                continue

            excelRow = rowNum + 1

            for colIdx, value in enumerate(row):
                worksheet.write(
                    excelRow,
                    colIdx,
                    value,
                    self._getColumnFormat(
                        index=colIdx,
                        formatBase=formatBaseBold,
                        formatR=formatRBold,
                        formatG=formatGBold,
                        formatY=formatYBold
                    )
                )

    def _getColumnFormat(
            self,
            index: int,
            formatBase,
            formatR,
            formatG,
            formatY
    ):
        '''获取列格式'''

        if index >= self.FORMAT_INDEX_GREEN_START:
            return formatG

        if index >= self.FORMAT_INDEX_RED_START:
            return formatR

        if index >= self.FORMAT_INDEX_YELLOW_START:
            return formatY

        return formatBase