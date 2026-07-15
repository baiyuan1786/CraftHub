##########################################################################################################
#   Description: 表格导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...common.reader import DataUnit
from .cableLay import CableLayTable
from .network import NetworkLinkTable
from craftHub.tool import GLog

from pathlib import Path
from typing import List, Optional

import pandas as pd
import os

class IDNTableExporter:
    '''表格导出器, 一次导出所有表格到一个excel文件中'''
    def __init__(self, 
                 dataUnitFullList: List[DataUnit],
                 dataUnitList: List[DataUnit],
                 config: dict):
        """初始化总表管理器

        :param config: 配置字典
        """        
  
        self.cableLayTable = CableLayTable(
            dataUnitFullList = dataUnitFullList,
            dataUnitList = dataUnitList,
            referrenceExcelPath = config["cableLay"],
            referrenceSheetName = config["cableLaySheet"],
            referrenceExcelPath2 = config["netJump"],
            referrenceSheetName2 = config["netJumpSheet"]
        )

        self.networkTable = NetworkLinkTable(
            dataUnitFullList,
            dataUnitList
        )
        
        self.config = config
        
    def export(self):
        '''导出所有表格在同一个文件中'''
        destPath: Path = self.config["dest"] / f"{self.config["project"]}-相关表格_{GLog.date()}.xlsx"

        with pd.ExcelWriter(destPath, engine="xlsxwriter") as writer:
            self.cableLayTable.export(writer, self.config["project"])
            self.networkTable.export(writer, self.config["project"])
            
        GLog.logInfo(f"{GLog.GREEN}线缆敷设表已保存至 \'{destPath}\'{GLog.END}")
        os.startfile(destPath)
        
