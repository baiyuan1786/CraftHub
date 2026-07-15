##########################################################################################################
#   Description: 地区ddn组网链路表导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import List

import numpy as np
import pandas as pd
from pandas import DataFrame
from xlsxwriter.worksheet import Worksheet

from craftHub.tool import GLog

from ....common.reader import DataUnit
from ..ddnSearcher import DDNSearcher

class NetworkLinkTable:
    '''地区ddn组网链路表'''

    COLUMN_NAME_LIST = [
        "站名",
        "序号",
        "业务起点所属层级",
        "业务起点站点名称",
        "业务终点所属层级",
        "业务终点站点名称",
        "承载网络",
        "链路带宽",
        "链路类型",
        "备注"
    ]

    COLUMN_LEN_LIST = [8.38, 8.38, 8.38, 10.75, 8.38, 10, 12.5, 8.5, 8.38, 20.38]

    SHEET_NAME_TEMPLATE = "组网链路需求表"

    LINK_BANDWIDTH = "100M"
    LINK_TYPE = "MSTP FE"
    CARRIER_NETWORK_TEMPLATE = "传输新网B({})"
    REMARK_TEMPLATE = "{}与{}互联链路"

    TITLE_ROW_OFFSET = 1
    EMPTY_ROW_NUM = 3

    def __init__(
            self,
            dataUnitFullList: List[DataUnit],
            dataUnitList: List[DataUnit]
    ) -> None:
        """组网链路表初始化

        :param dataUnitFullList: 全部的数据单元
        :param dataUnitList:     有效的数据单元
        """

        self.dataUnitFullList = dataUnitFullList
        self.dataUnitList = dataUnitList
        self.searcher = DDNSearcher(dataUnitFullList=self.dataUnitFullList)

    def toSingle(self, data: DataUnit) -> DataFrame:
        '''由单个DataUnit导出组网链路表'''

        self._checkSingleData(data)

        rowDataList = []

        for index, targetStation in enumerate(data.get("GCNTargetStationList"), 1):
            terminateLayer = self.searcher.searchLayer(targetStation)

            if terminateLayer is None:
                raise ValueError(
                    f"{data.get('substationName')} | GCN网链路终点的层级未找到: {targetStation}"
                )

            rowDataList.append({
                "站名": data.get("substationName"),
                "序号": index,
                "业务起点所属层级": data.get("layer"),
                "业务起点站点名称": data.get("substationName"),
                "业务终点所属层级": terminateLayer,
                "业务终点站点名称": targetStation,
                "承载网络": self.CARRIER_NETWORK_TEMPLATE.format(data.get("GCNareaName")),
                "链路带宽": self.LINK_BANDWIDTH,
                "链路类型": self.LINK_TYPE,
                "备注": self.REMARK_TEMPLATE.format(data.get("layer"), terminateLayer)
            })

        return DataFrame(rowDataList, columns=self.COLUMN_NAME_LIST)

    def toDF(self) -> DataFrame:
        '''转换为一个DataFrame'''

        frameList: List[DataFrame] = []

        for data in self.dataUnitList:
            if not data.get("build"):
                continue

            try:
                newFrame = self.toSingle(data)
                frameList += [self._emptyTableFrame()] * self.EMPTY_ROW_NUM
                frameList.append(newFrame)

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.RED}导出ddn组网链路表错误 | "
                    f"{data.get('substationName')} | {str(e)}{GLog.END}"
                )

        if len(frameList) == 0:
            return self._emptyTableFrame(rowNum=0)

        return pd.concat(frameList)

    def export(
            self,
            writer: pd.ExcelWriter,
            project: str
    ):
        '''导出组网链路表'''

        sheetName = self.SHEET_NAME_TEMPLATE
        saveFrame = self.toDF()

        saveFrame.to_excel(
            writer,
            sheet_name=sheetName,
            index=False,
            header=True
        )

        workbook = writer.book
        worksheet: Worksheet = writer.sheets[sheetName]
        worksheet.set_zoom(100)

        formatDict = {
            "text_wrap": True,
            "align": "center",
            "valign": "vcenter",
            "font_name": "宋体",
            "font_size": 10,
            "border": True
        }

        def makeFormat(**kwargs):
            fmtDict = formatDict.copy()
            fmtDict.update(kwargs)
            return workbook.add_format(fmtDict)  # type: ignore

        formatBase = makeFormat()
        formatBaseTitle = makeFormat(bold=True, bg_color="#B4C6E7")

        for index, columnLen in enumerate(self.COLUMN_LEN_LIST):
            worksheet.set_column(index, index, columnLen, formatBase)

        for rowIdx in range(2, len(saveFrame)):
            currentRow = saveFrame.iloc[rowIdx]
            preRow1 = saveFrame.iloc[rowIdx - 1]
            preRow2 = saveFrame.iloc[rowIdx - 2]

            if (
                    not self._isEmptyRow(currentRow)
                    and self._isEmptyRow(preRow1)
                    and self._isEmptyRow(preRow2)
            ):
                titleRow = rowIdx - self.TITLE_ROW_OFFSET
                stationName = str(currentRow["站名"])

                self._writeTitle(
                    worksheet=worksheet,
                    row=titleRow,
                    stationName=stationName,
                    formatBaseTitle=formatBaseTitle
                )

    def _checkSingleData(self, data: DataUnit):
        '''检查单站组网链路数据'''

        assert isinstance(data.get("GCNTargetStationList"), list)
        assert isinstance(data.get("GCNareaName"), str)

    def _emptyTableFrame(self, rowNum: int = 1) -> DataFrame:
        '''构建空表格DataFrame'''

        return DataFrame(
            {
                columnName: np.nan
                for columnName in self.COLUMN_NAME_LIST
            },
            index=list(range(rowNum))
        )

    def _isEmptyRow(self, row) -> bool:
        '''判断是否为空行'''

        return row.isna().all() or row.astype(str).str.strip().eq("").all()

    def _writeTitle(
            self,
            worksheet: Worksheet,
            row: int,
            stationName: str,
            formatBaseTitle
    ):
        '''写入站点表头，row是Excel中的0基行号，占用row和row+1两行'''

        worksheet.write(row, 0, stationName, formatBaseTitle)
        worksheet.write(row + 1, 0, stationName, formatBaseTitle)

        worksheet.merge_range(row, 1, row + 1, 1, "序号", formatBaseTitle)

        worksheet.merge_range(row, 2, row, 3, "业务起点", formatBaseTitle)
        worksheet.write(row + 1, 2, "所属层级", formatBaseTitle)
        worksheet.write(row + 1, 3, "站点名称", formatBaseTitle)

        worksheet.merge_range(row, 4, row, 5, "业务终点", formatBaseTitle)
        worksheet.write(row + 1, 4, "所属层级", formatBaseTitle)
        worksheet.write(row + 1, 5, "站点名称", formatBaseTitle)

        worksheet.merge_range(row, 6, row + 1, 6, "承载网络", formatBaseTitle)
        worksheet.merge_range(row, 7, row + 1, 7, "链路带宽", formatBaseTitle)
        worksheet.merge_range(row, 8, row + 1, 8, "链路类型", formatBaseTitle)
        worksheet.merge_range(row, 9, row + 1, 9, "备注", formatBaseTitle)