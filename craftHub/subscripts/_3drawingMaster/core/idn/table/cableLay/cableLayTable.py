##########################################################################################################
#   Description: 线缆敷设表导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .link import EmptyLink, Title, FiberJumpLink
from .cableLayTableOne import cableLayTableOne
from ....common.reader import DataUnit

from craftHub.tool import GLog

from pathlib import Path
from pandas import DataFrame
from typing import List, Optional

import pandas as pd
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet

class CableLayTable:
    '''线缆敷设表'''
    
    referrenceTitleList: List = [
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
    
    def __init__(self,
                 dataUnitFullList: List[DataUnit],
                 dataUnitList: List[DataUnit],
                 referrenceExcelPath: Optional[Path],
                 referrenceSheetName: Optional[str],
                 referrenceExcelPath2: Optional[Path] = None,
                 referrenceSheetName2: Optional[str] = None,):
        """线缆敷设表初始化

        :param dataUnitFullList: 全部的数据单元
        :param dataUnitList: 有效的数据单元
        :param referrenceExcelPath: 参考表格路径
        :parma referrenceSheetName: 参考Sheet名称
        """
        self.dataUnitFullList = dataUnitFullList
        self.dataUnitList = dataUnitList
        self.cableLayExcel = referrenceExcelPath
        self.cableLaySheet = referrenceSheetName

        # 初始化各站点(仅接入层建好的)
        self.cableLayOneList = [cableLayTableOne(data) for data in dataUnitList if data.get("build")]

        # 获取总跳纤链路
        self.fiberJumpLinkList: List[FiberJumpLink] = []
        for data in dataUnitFullList:
            # 跳过地调和备调链路
            if "备调" in data.get("substationName") or "地调" in data.get("substationName"):
                continue
            
            self.fiberJumpLinkList += cableLayTableOne.toFiberJumpLinkList(data, dataUnitFullList)

        # 跳纤链路去重
        fiberJumpLinkListFiltered = []
        for link in self.fiberJumpLinkList:
            if all([link != exitedLink for exitedLink in fiberJumpLinkListFiltered]):
                fiberJumpLinkListFiltered.append(link)
        self.fiberJumpLinkList = fiberJumpLinkListFiltered
        
        # 排序
        self.fiberJumpLinkList.sort(key = lambda a: a.substationName)
            
        # 插入跳纤链路
        for cableLayOne in self.cableLayOneList:
            cableLayOne.insertFiberJumpLinkList(self.fiberJumpLinkList)
            
        # 读取参考表格数据
        self._readExcel(referrenceExcelPath, referrenceSheetName)
        self._readExcel(referrenceExcelPath2, referrenceSheetName2) # 读取第二个参考表格
            
    def _readExcel(self, 
                   referrenceExcelPath: Optional[Path], 
                   referrenceSheetName: Optional[str]):
        """读取参照表格

        :param referrenceExcelPath: 参照表格文件路径
        :param referrenceSheetName: 参照Sheet路径
        """        

        if referrenceExcelPath is None or referrenceSheetName is None:
            # 无需处理
            GLog.logInfo("无参考表格")
            return
        
        GLog.logInfo(f"参考表格: {referrenceExcelPath}:{referrenceSheetName}")
        if not referrenceExcelPath.exists():
            raise FileNotFoundError(f"参考表格未找到: \'{referrenceExcelPath}\'")

        allDF = pd.read_excel(io = referrenceExcelPath, sheet_name = referrenceSheetName)

        notFoundTitleList: List[str] = [title for title in self.referrenceTitleList if title not in allDF.columns]
        if notFoundTitleList:
            raise ValueError(f"参考表格缺少列: \'{notFoundTitleList}\'")
        
        # 逐个站读取信息
        # 接入层站点读取信息
        for cableLayOne in self.cableLayOneList:
            substationName = cableLayOne.substationName
            subDF = allDF[allDF["站名"] == substationName]
            if subDF.empty:
                GLog.logInfo(f"{GLog.YELLOW}没有找到站名为 \'{substationName}\' 的参考信息{GLog.END}")
                continue
            
            GLog.logInfo(f"{GLog.GREEN}找到站名为 \'{substationName}\' 的参考信息{GLog.END}")
            cableLayOne.readExcel(subDF = subDF)
            
        # 跳纤链路表读取信息
        for fiberJumpLink in self.fiberJumpLinkList:
            substationName = fiberJumpLink.substationName
            subDF = allDF[allDF["站名"] == substationName]
            if subDF.empty:
                continue
            
            fiberJumpLink.readExcel(subDF = subDF)

    def _toCableLayDataFrame(self):
        '''导出线缆敷设表的dataFrame'''
        dfList = [pd.concat([c.toDF(), EmptyLink().toDF(), EmptyLink().toDF()]) for c in self.cableLayOneList] 
        
        return pd.concat(dfList)

    def _toFiberJumpLinkDataFrame(self):
        '''导出跳纤链路表DataFrame'''

        dfList = [f.toDF() for f in self.fiberJumpLinkList]
        return pd.concat(dfList)
    
    def export(self, 
               writer: pd.ExcelWriter, 
               project: str):
        '''导出表格'''

        sheetName1 = f"线缆敷设表(单台设备)"
        sheetName2 = f"线缆敷设表(跳纤链路)"
        colunmLenList: List[float] = [16.5, 4.5, 17, 23.25, 19.5, 26.75, 10.25, 7, 7, 24.5, 11.3, 9, 9, 9, 9, 9, 34.25] # 标准列宽
            
        cableLayDF = self._toCableLayDataFrame()
        cableLayDF.to_excel(writer, sheet_name=sheetName1, index=False)
        fiberJumpLinkDF = self._toFiberJumpLinkDataFrame()
        fiberJumpLinkDF.to_excel(writer, sheet_name=sheetName2, index=False)

        workbook = writer.book
        worksheet1: Worksheet = writer.sheets[sheetName1]
        worksheet2: Worksheet = writer.sheets[sheetName2]
        
        # 常规格式
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
        
        # 获取格式
        formatbase = makeFormat()
        formatR = makeFormat(bg_color="#FF0000")
        formatG = makeFormat(bg_color="#00FF00")
        formatY = makeFormat(bg_color="#FBFF00")
        formatGr = makeFormat(bg_color="#EEEEE7")
    
        formatbaseBold = makeFormat(bold=True)
        formatRBold = makeFormat(bg_color="#FF0000", bold=True)
        formatGBold = makeFormat(bg_color="#00FF00", bold=True)
        formatYBold = makeFormat(bg_color="#FBFF00", bold=True)
        formatGrBold = makeFormat(bg_color="#EEEEE7", bold=True)

        worksheet1.set_zoom(70) # 比例
        worksheet2.set_zoom(70) # 比例
        
        # 逐列格式
        for index, colunmLen in enumerate(colunmLenList):
            if index >= 15:
                fmat = formatG
            elif index >= 13:
                fmat = formatR
            elif index >= 11:
                fmat = formatY
            else:
                fmat = formatbase
                
            worksheet1.set_column(index, index, colunmLen, fmat)
            worksheet2.set_column(index, index, colunmLen, fmat)
            
        # 逐行格式 / 线缆敷设表
        for rowNum, (_, row) in enumerate(cableLayDF.iterrows()):
            # 站首列，加粗处理
            if row.iloc[1] == "序号":

                excelRow = rowNum + 1  # +1 跳过Excel表头
                for colIdx, value in enumerate(row):

                    if colIdx >= 15:
                        fmt = formatGBold
                    elif colIdx >= 13:
                        fmt = formatRBold
                    elif colIdx >= 11:
                        fmt = formatYBold
                    else:
                        fmt = formatbaseBold

                    worksheet1.write(
                        excelRow,
                        colIdx,
                        value,
                        fmt
                    )
                    
        # 逐行格式 / 跳纤链路表
        lastRowSubstationName = None
        lastBaseFormat = formatbase
        for rowNum, (_, row) in enumerate(fiberJumpLinkDF.iterrows()):

            rowSubstationName = row["站名"]

            # 基础格式
            if rowSubstationName == lastRowSubstationName:
                baseFmt = lastBaseFormat
            else:
                baseFmt = formatbase if formatbase != lastBaseFormat else formatGr

            excelRow = rowNum + 1
            for colIdx, value in enumerate(row):

                # 高列格式
                if colIdx >= 15:
                    fmt = formatGBold
                elif colIdx >= 13:
                    fmt = formatRBold
                elif colIdx >= 11:
                    fmt = formatYBold
                else:
                    fmt = baseFmt

                worksheet2.write(
                    excelRow,
                    colIdx,
                    value,
                    fmt
                )
            lastRowSubstationName = rowSubstationName
            lastBaseFormat = baseFmt



        
        