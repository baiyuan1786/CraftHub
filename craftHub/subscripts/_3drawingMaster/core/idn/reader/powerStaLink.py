##########################################################################################################
#   Description: 供电所idn接入链路读取器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
import pandas as pd
from pathlib import Path
from typing import List, Optional, Dict, Any
from ...common.reader import DataUnit
from craftHub.tool import GLog

class PowerStaLink:
    '''供电所idn接入链路'''
    def __init__(self,
                 powerName: str,
                 accessStation: str,
                 accessPanel: str,
                 accessODF: str,
                 jumper: Optional[str],
                 remark: str,
                 ) -> None:
        """初始化供电所接入链路

        :param powerName:       供电所名称
        :param accessStation:   接入站
        :param accessPanel:     接入屏
        :param accessODF:       接入ODF
        :param jumper:          跳纤信息
        :param remark:          备注信息
        """        
        
        self.powerName = self.cleanValue(powerName)
        self.accessStation = self.cleanValue(accessStation)
        self.accessPanel = self.cleanValue(accessPanel)
        self.accessODF = self.cleanValue(accessODF)
        self.jumper = self.cleanOptionalValue(jumper)
        self.remark = self.cleanValue(remark)
        
    @staticmethod
    def cleanValue(value: Any) -> str:
        """清洗单元格数据， 将None和nan转换为空字符串

        :param value: 原始数据
        :return:      清洗后的字符串
        """        
        
        if value is None:
            return ""
        
        valueStr = str(value).strip()
        if valueStr.lower() == "nan":
            return ""
        
        return valueStr
    
    @staticmethod
    def cleanOptionalValue(value: Any) -> Optional[str]:
        """清洗可选单元格数据， 空值转换为None

        :param value: 原始数据
        :return:      清洗后的字符串或None
        """        
        
        valueStr = PowerStaLink.cleanValue(value)
        
        if valueStr == "":
            return None
        
        return valueStr
    
    def get(self, key: str) -> Optional[str]:
        """根据字段名称获取数据

        :param key: 字段名称
        :return:    字段值
        """        
        
        dataDict = {
            "powerName": self.powerName,
            "accessStation": self.accessStation,
            "accessPanel": self.accessPanel,
            "accessODF": self.accessODF,
            "jumper": self.jumper,
            "remark": self.remark,
            
            "供电所名称": self.powerName,
            "接入站": self.accessStation,
            "接入屏": self.accessPanel,
            "接入ODF": self.accessODF,
            "跳纤": self.jumper,
            "备注": self.remark,
        }
        
        if key not in dataDict:
            raise KeyError(f"PowerStaLink | 不存在字段: {key}")
        
        return dataDict[key]

    def isDeprecated(self) -> bool:
        """判断该供电所节点是否已废弃

        :return: 是否已废弃
        """        
        
        return "已废弃" in self.remark
    
    def toDict(self) -> Dict[str, Optional[str]]:
        """转换为字典

        :return: 字典数据
        """        
        
        return {
            "供电所名称": self.powerName,
            "接入站": self.accessStation,
            "接入屏": self.accessPanel,
            "接入ODF": self.accessODF,
            "跳纤": self.jumper,
            "备注": self.remark,
        }
    
    def inheritODFP(self, data: DataUnit):
        '''从data继承ODF屏数据'''
        referPfullName = data.get("odfLinkODFPfullNameList")[0]     # 完整名称
        referP = referPfullName.split("P")[0]                       # P号

        if self.accessODF.startswith(referP):
            self.accessPanel = referPfullName

        else:
            raise ValueError(f"供电所接入ODF屏继承失败: {self}, {referPfullName}")
    
    def __repr__(self) -> str:
        return f"PowerStaLink({self.powerName}, {self.accessStation}, {self.accessPanel}, {self.accessODF}, {self.jumper}, {self.remark})"
    
    def __eq__(self, value: object) -> bool:
        
        if not isinstance(value, DataUnit):
            return NotImplemented

        return self.accessStation in value.get("substationName")
    
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)
    
    def __str__(self) -> str:
        return f"{self.powerName}->{self.accessStation}->{self.accessPanel}->{self.accessODF}->{self.jumper}"

class PowerStaLinksReader:
    '''供电所idn接入链路集合'''
    
    REQUIRED_COLUMNS = [
        "供电所名称",
        "接入站",
        "接入屏",
        "接入ODF",
        "跳纤",
        "备注",
    ]
    
    def __init__(self,
                 excelPath: Path,
                 sheetName: str,
                 ) -> None:
        """初始化供电所接入链路集合

        :param excelPath:   Excel表格路径
        :param sheetName:   工作簿名称
        """        
        
        self.excelPath = Path(excelPath)
        self.sheetName = sheetName
        self.powerLinkList: List[PowerStaLink] = []
        self.powerLinkFullList: List[PowerStaLink] = []
        errorList = []
        
        # 检查表格路径
        if not self.excelPath.exists():
            raise FileNotFoundError(f"PowerLinks | 表格不存在: {self.excelPath}")
        
        # 读取表格
        try:
            dataFrame = pd.read_excel(self.excelPath,
                                      sheet_name = self.sheetName,
                                      dtype = str,
                                      keep_default_na = False)
        except Exception as e:
            raise ValueError(f"PowerLinks | 读取表格失败: {e}")
        
        # 清洗表头
        dataFrame.columns = [str(column).strip() for column in dataFrame.columns]
        
        # 检查字段
        self.checkColumns(dataFrame)
        
        # 解析数据
        for index, row in dataFrame.iterrows():
            try:
                powerName = self.cleanValue(row["供电所名称"])
                accessODF = self.cleanValue(row["接入ODF"])
                
                # 跳过空行
                if powerName == "" or accessODF == "":
                    continue
                
                powerLink = PowerStaLink(powerName = row["供电所名称"],
                                      accessStation = row["接入站"],
                                      accessPanel = row["接入屏"],
                                      accessODF = row["接入ODF"],
                                      jumper = row["跳纤"],
                                      remark = row["备注"])
                
                self.powerLinkFullList.append(powerLink)
                
                # 默认有效数据排除已废弃节点
                if powerLink.isDeprecated():
                    GLog.logInfo(f"{powerLink.powerName} 已废弃，跳过")
                    continue

                self.powerLinkList.append(powerLink)
                
            except Exception as e:
                errorList.append(f"PowerLinks | 解析第{int(index) + 2}行时出错: {str(e)}") # type: ignore
                continue
        
        # 输出错误信息
        for err in errorList:
            GLog.logInfo(err)
    
    @staticmethod
    def cleanValue(value: Any) -> str:
        """清洗单元格数据， 将None和nan转换为空字符串

        :param value: 原始数据
        :return:      清洗后的字符串
        """        
        
        return PowerStaLink.cleanValue(value)
    
    def checkColumns(self, dataFrame: pd.DataFrame) -> None:
        """检查表格字段是否完整

        :param dataFrame: 表格数据
        """        
        
        missingColumnList = []
        
        for column in self.REQUIRED_COLUMNS:
            if column not in dataFrame.columns:
                missingColumnList.append(column)
        
        if len(missingColumnList) > 0:
            raise ValueError(f"PowerLinks | sheet【{self.sheetName}】缺少字段: {missingColumnList}, 当前字段: {list(dataFrame.columns)}")
    
    def getPowerLink(self,
                     powerName: str,
                     fuzzy: bool = False,
                     includeDeprecated: bool = False,
                     ) -> Optional[PowerStaLink]:
        """根据供电所名称查找链路

        :param powerName:           供电所名称
        :param fuzzy:               是否模糊匹配
        :param includeDeprecated:   是否包含已废弃节点
        :return:                    PowerLink对象， 如果未找到则返回None
        """        
        
        powerName = self.cleanValue(powerName)
        
        if includeDeprecated:
            powerLinkList = self.powerLinkFullList
        else:
            powerLinkList = self.powerLinkList
        
        for powerLink in powerLinkList:
            if fuzzy:
                if powerName in powerLink.powerName or powerLink.powerName in powerName:
                    return powerLink
            else:
                if powerName == powerLink.powerName:
                    return powerLink
        
        return None
    
    def toDataFrame(self,
                    includeDeprecated: bool = False,
                    ) -> pd.DataFrame:
        """转换为DataFrame

        :param includeDeprecated: 是否包含已废弃节点
        :return:                  DataFrame数据
        """        
        
        if includeDeprecated:
            powerLinkList = self.powerLinkFullList
        else:
            powerLinkList = self.powerLinkList
        
        return pd.DataFrame([powerLink.toDict() for powerLink in powerLinkList])
    
    def __len__(self) -> int:
        return len(self.powerLinkList)
    
    def __iter__(self):
        return iter(self.powerLinkList)