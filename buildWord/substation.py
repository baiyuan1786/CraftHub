##########################################################################################################
#   Description: 变电站类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from typing import List, Dict, Optional, Literal
from pathlib import Path

import pandas as pd

class Substation:
    '''从Excel表格提取的变电站信息'''
    def __init__(self, 
                 name: str,
                 materialExcelPath: Optional[str] = None
                 ):
        """数据管理使用的变电站类

        :param name: 名称
        :param materialExcelPath: 材料表路径
        """
        
        # 初始化属性
        self.name = name


        # 处理表格
        self.df = pd.read_excel(materialExcelPath, sheet_name = "Sheet1")
        self.substaionNameSeries = self.df["站点"]
        self._loadInfo()
        
        
    def _loadInfo(self):
        '''从DataFrame加载变电站信息'''

        # 获取站点列号
        if self.name not in self.substaionNameSeries:
            raise ValueError(f"在变电站列表中找不到站点: {self.name}")

        substationIndex = self.substaionNameSeries[self.substaionNameSeries == self.name].index[0]
        print(f"找到变电站 {self.name}，索引为 {substationIndex}")

        # 从找到的索引行提取信息(一行信息)
        substationInfo = self.df.iloc[substationIndex] 
        
        
        
        
if __name__ == "__main__":
    # 测试变电站类
    substation = Substation(name="500kV卧龙变", materialExcelPath = r"E:\gzq\两网工勘工程\收资表\云浮\云浮材料表.xlsx")
    
