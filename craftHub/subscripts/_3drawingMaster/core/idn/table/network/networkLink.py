##########################################################################################################
#   Description: 组网链路表表格导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ....common.reader import DataUnit
from ..idnSearcher import IDNSearcher

from craftHub.tool import GLog
import pandas as pd
import numpy as np
from pandas import DataFrame
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from typing import List

class NetworkLinkTable:
    '''组网链路表'''
    def __init__(self,
                 dataUnitFullList: List[DataUnit],
                 dataUnitList: List[DataUnit]):
        """组网链路表初始化

        :param dataUnitFullList: 全部的数据单元
        :param dataUnitList: 有效的数据单元
        """        
        self.dataUnitFullList = dataUnitFullList
        self.dataUnitList = dataUnitList

    def toSingle(self, data: DataUnit):
        '''由单个DataUnit导出组网链路图'''

        assert isinstance(data.get("odfLinkTerminateStrList"), list)
        substaionNetLinkDF = DataFrame({
            "站名": [],
            "序号": [],
            "业务起点所属层级": [],
            "业务起点站点名称": [],
            "业务终点所属层级": [],
            "业务终点站点名称": [],
            "承载网络": [],
            "链路带宽": [],
            "链路类型": [],
            "备注": []
        })
        
        searcher = IDNSearcher(dataUnitFullList = self.dataUnitFullList)
        
        # ODF光纤直连链路
        for index, ODFterminateSta in enumerate(data.get("odfLinkTerminateStrList"), 1):
            terminateLayer = searcher.searchLayer(ODFterminateSta)
            if terminateLayer is None:
                GLog.logInfo(f"{GLog.YELLOW}{data.get('substationName')} | 光纤直连链路终点的层级未找到: {ODFterminateSta}{GLog.END}")
                continue
            
            newFrame = DataFrame({
                "站名": data.get("substationName"),
                "序号": index,
                "业务起点所属层级": data.get("layer"),
                "业务起点站点名称": data.get("substationName"),
                "业务终点所属层级": terminateLayer,
                "业务终点站点名称": ODFterminateSta,
                "承载网络": "云浮地区光缆网",
                "链路带宽": "10G",  # 接入层之间的带宽都是10G
                "链路类型": "光纤直连",
                "备注": f"{data.get('layer')}与{terminateLayer}互联链路"
                }, index=[0])
            
            # 拼接
            substaionNetLinkDF = pd.concat([substaionNetLinkDF, newFrame])
            
        # GCN网链路
        if data.get("GCNTargetStation") is not None:
            GCNTargetStation = data.get("GCNTargetStation")
            terminateLayer = searcher.searchLayer(GCNTargetStation)
            if terminateLayer is None:
                raise ValueError(f"{data.get('substationName')} | GCN网链路终点的层级未找到: {GCNTargetStation}")
            
            newFrame = DataFrame({
                "站名": data.get("substationName"),
                "序号": index + 1,
                "业务起点所属层级": data.get("layer"),
                "业务起点站点名称": data.get("substationName"),
                "业务终点所属层级": terminateLayer,
                "业务终点站点名称": GCNTargetStation,
                "承载网络": "传输新网B（广东粤北区ASON域）",
                "链路带宽": "GE",
                "链路类型": "MSTP GE",
                "备注": f"{data.get('layer')}与{terminateLayer}互联链路"
                }, index=[0])
            
            substaionNetLinkDF = pd.concat([substaionNetLinkDF, newFrame])
            
        return substaionNetLinkDF

    def toDF(self):
        '''转换为一个DataFrame'''
       # 空的表
        emptyDF = DataFrame({
            "站名": np.nan,
            "序号": np.nan,
            "业务起点所属层级": np.nan,
            "业务起点站点名称": np.nan,
            "业务终点所属层级": np.nan,
            "业务终点站点名称": np.nan,
            "承载网络": np.nan,
            "链路带宽": np.nan,
            "链路类型": np.nan,
            "备注": np.nan
        }, index=[0])
        
        frameList: List[DataFrame] = []

        # 绘图列表
        for data in self.dataUnitList:
            if not data.get("build"):
                continue
            
            try:
                newFrame = self.toSingle(data)
                frameList += [emptyDF] * 3
                frameList.append(newFrame)
            except Exception as e:
                GLog.logInfo(f"{GLog.RED}导出组网链路表错误 | {str(e)} {GLog.END}")
                
        return pd.concat(frameList)

    def export(self,
            writer: pd.ExcelWriter,
            project: str):
        '''导出组网链路表'''

        colunmLenList: List[float] = [8.38, 8.38, 8.38, 10.75, 8.38, 10, 12.5, 8.5, 8.38, 20.38]
        sheetName = f"组网链路需求表"

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

        formatbase = makeFormat()
        formatbaseTitle = makeFormat(bold=True, bg_color="#B4C6E7")

        for index, colunmLen in enumerate(colunmLenList):
            worksheet.set_column(index, index, colunmLen, formatbase)

        def isEmptyRow(row) -> bool:
            return row.isna().all() or row.astype(str).str.strip().eq("").all()

        def writeTitle(row: int, stationName: str):
            '''row是Excel中的0基行号，占用row和row+1两行'''

            # A列为站名列，写入当前站名
            #worksheet.merge_range(row, 0, row + 1, 0, stationName, formatbaseTitle)
            
            worksheet.write(row, 0, stationName, formatbaseTitle)
            worksheet.write(row + 1, 0, stationName, formatbaseTitle)

            worksheet.merge_range(row, 1, row + 1, 1, "序号", formatbaseTitle)

            worksheet.merge_range(row, 2, row, 3, "业务起点", formatbaseTitle)
            worksheet.write(row + 1, 2, "所属层级", formatbaseTitle)
            worksheet.write(row + 1, 3, "站点名称", formatbaseTitle)

            worksheet.merge_range(row, 4, row, 5, "业务终点", formatbaseTitle)
            worksheet.write(row + 1, 4, "所属层级", formatbaseTitle)
            worksheet.write(row + 1, 5, "站点名称", formatbaseTitle)

            worksheet.merge_range(row, 6, row + 1, 6, "承载网络", formatbaseTitle)
            worksheet.merge_range(row, 7, row + 1, 7, "链路带宽", formatbaseTitle)
            worksheet.merge_range(row, 8, row + 1, 8, "链路类型", formatbaseTitle)
            worksheet.merge_range(row, 9, row + 1, 9, "备注", formatbaseTitle)

        # 检测：当前行非空，且上面两行为空
        for rowIdx in range(2, len(saveFrame)):
            currentRow = saveFrame.iloc[rowIdx]
            preRow1 = saveFrame.iloc[rowIdx - 1]
            preRow2 = saveFrame.iloc[rowIdx - 2]

            if (
                not isEmptyRow(currentRow)
                and isEmptyRow(preRow1)
                and isEmptyRow(preRow2)
            ):
                titleRow = rowIdx - 1
                stationName = str(currentRow["站名"])
                writeTitle(titleRow, stationName)
