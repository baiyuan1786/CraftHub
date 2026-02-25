##########################################################################################################
#   Description: 传输段读取模块
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from craftHub.tool import gLog
from ...substation import Substation

import os, time
import pandas as pd
from tqdm import tqdm_gui
from pathlib import Path
from itertools import permutations
from typing import Tuple, List, Dict, Any, Optional

class TransmissionSegmentReader:
    '''传输段读取器'''
    def __init__(self, srcPath: Path):
        """传输段读取器初始化

        :param srcPath: 传输段表格路径
        """       
        self.srcPath = srcPath
        try:
            tsDF = pd.read_excel(srcPath, sheet_name = 0)
        except Exception as e:
            raise Exception(f"Load Excel failed: {str(e)}")
        
        # 检查列
        for col in ["A端站点", "Z端站点"]:
            if col not in tsDF.columns:
                raise ValueError(f"Find no \'{col}\' column in excel")

            
        # 变电站列表
        self.substationsDict: Dict[str, Substation] = {}    # 变电站字典
        
        # 注意同一条链路只有单方向的一条记录
        # 从表格获取站点和名字信息
        for index, row in tsDF.iterrows():

            staAname: str = row["A端站点"]
            staZname: str = row["Z端站点"]

            if(pd.isna(staAname)):
                staAname = f"unknowen{index}_a"
                gLog.logInfo(f"Warning: detect NAN in dataFrame row {index}, rename to \'{staAname}'")
            if(pd.isna(staZname)):
                staZname = f"unknowen{index}_z"
                gLog.logInfo(f"Warning: detect NAN in dataFrame row {index}, rename to \'{staZname}'")
            
            for staname1, staname2 in permutations([staAname, staZname], 2):
                if staname1 not in self.substationsDict.keys():
                    newSta = Substation(name = staname1) 
                    self.substationsDict[staname1] = newSta
                else:
                    newSta = self.substationsDict[staname1]
                newSta.addNb(name = staname2)
            
        self.substations = list(self.substationsDict.values())
            
        # ID赋值
        for index, sta in enumerate(self.substationsDict.values()):
            sta.ID = index
            
        gLog.logInfo("Load TransmissionSegment success")
    
    def toExcel(self, saveFolder: Path, isOpen = False):
        '''导出excel表格'''
        if not saveFolder.is_dir():
            raise ValueError(f"savePath is not a folder: {saveFolder}")
        
        idList = [sta.ID for sta in self.substations]
        nameList = [sta.name for sta in self.substations]

        nbNamesList = [[nbLink.name for nbLink in sta.nbLinks] for sta in self.substations]
        asonsList = [[nbLink.ason for nbLink in sta.nbLinks] for sta in self.substations]
        weightsList = [[nbLink.weight for nbLink in sta.nbLinks] for sta in self.substations]
        fiberPointsList = [[nbLink.fiberPoints for nbLink in sta.nbLinks] for sta in self.substations]
        
        mydf = pd.DataFrame({
                "ID": idList,
                "Name": nameList,
                "Neighbors" : nbNamesList,
                "Asons" : asonsList,
                "Weights" : weightsList,
                "FiberPoints" : fiberPointsList
            })

        savePath = saveFolder / f"adj_{gLog.date()}.xlsx"

        # 保存并打开文件
        with pd.ExcelWriter(savePath, engine = "xlsxwriter") as writer:
            mydf.to_excel(writer, sheet_name = "Sheet1", index = False)

            # 控制列宽
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            for i, col in enumerate(mydf.columns):
                maxLen = max(mydf[col].astype(str).apply(len).max(), len(col))
                worksheet.set_column(i, i, maxLen * 1.3)
                
        gLog.logInfo(f"Save excel to {savePath}")
        if isOpen:
            os.startfile(savePath)
            
            
        
        