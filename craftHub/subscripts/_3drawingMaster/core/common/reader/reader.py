##########################################################################################################
#   Description: 表格信息读取器
#                将表格格式信息读取为绘图信息
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog

import pandas as pd
from enum import Enum
from pathlib import Path
from pandas import DataFrame, Timestamp
from typing import Dict, Any, List, Optional, Literal, Tuple, Type

class ExcelValueType(Enum):
    '''Excel数据类型推断'''
    
    INT = 1         # int类型数据
    STR = 2         # string类型数据
    BOOL = 3        # bool类型数据
    LIST_STR = 4    # 字符串列表类型数据
    LIST_INT = 5    # 整数列表类型数据
    LIST_MIXED = 6  # 混合列表
    UNKNOWEN = 7    # 未知类型
    NONE = 8        # 空类型
    MIXED = 9       # 整形和字符串混合类型
    
    @classmethod
    def detectType(cls, valueList: List[str]):
        """侦测一列数据的类型

        :param valueList: 数据列
        """      
        try:
                
            # 未知类型
            if any([isinstance(value, Timestamp) for value in valueList]):
                return cls.UNKNOWEN
                
            # Bool类型
            if all([cls.isBool(value) for value in valueList]):
                return cls.BOOL
            
            # Int类型
            if all([cls.isInt(value) for value in valueList]):
                return cls.INT
            
            # Str类型
            if all([cls.isStr(value) for value in valueList]):
                return cls.STR
            
            # 混合类型
            if all([cls.isMixed(value) for value in valueList]):
                return cls.MIXED
            
            # 列表整形
            if all([cls.isListInt(value) for value in valueList]):
                return cls.LIST_INT
            
            # 列表字符串
            if all([cls.isListStr(value) for value in valueList]):
                return cls.LIST_STR

        except Exception as e:
            GLog.logInfo(f"解析类型出错 | {str(e)}")
            return cls.UNKNOWEN
        
        return cls.NONE

    @classmethod
    def isListInt(cls, value: Any):
        '''是否是列表Int类型数据
        仅判断单个数据'''
        
        #print(f"输入值为{value}, 类型为{type(value)}")
        
        # 空值也判定为是
        if cls._isEmptyValue(value):
            #print("空值，判定为是")
            return True

        if isinstance(value, int):
            value = str(value)
            
        assert isinstance(value, str)
        
        valueList = [splitValue for splitValue in value.split(";") if bool(splitValue.strip())]

        if ";" in value and all([cls.isInt(splitValue) for splitValue in valueList]):
            #print("多个int，判定为是")
            return True
        elif cls.isInt(value):
            #print("单个int，判定为是")
            return True     # 单个值为Int也视作是列表
        else:
            #print("判定为不是")
            return False
        
    @classmethod
    def isListStr(cls, value: Any):
        '''是否是列表Str类型数据
        仅判断单个数据
        条件放宽
        '''
        
        # 所有值判定为是字符串列表！
        return True
        
        # 空值也判定为是
        if cls._isEmptyValue(value):
            return True

        if isinstance(value, int):
            value = str(value)

        if ";" in value and any([not cls.isInt(splitValue) for splitValue in value.split(";")]):
            return True
        elif not cls.isInt(value):
            return True     # 单个值为Int也视作是列表
        else:
            return False
    
    @classmethod
    def isStr(cls, value: Any):
        '''是否是Str类型数据'''
        
        # 空值也判定为是
        if cls._isEmptyValue(value):
            return True
        
        try:
            if ";" in value:
                return False
            if cls.isInt(value):
                return False
            
        except Exception:
            return False
        else:
            return True
    
    @classmethod
    def isInt(cls, value: Any):
        '''是否是int类型数据'''
        
        # 空值也判定为是
        if cls._isEmptyValue(value):
            return True
        
        try:
            valueInt = int(value)
        except Exception:
            return False
        else:
            return True
        
    @classmethod
    def isBool(cls, value: Any):
        '''是否是Bool类型数据'''
        
        # 空值也判定为是
        if cls._isEmptyValue(value):
            return True
        
        try:
            valueInt = int(value)
        except Exception:
            return False
        else:
            return valueInt == 0 or valueInt == 1
        
    @classmethod
    def isMixed(cls, value: Any):
        '''是否是整形和字符串的混合类型数据, 不能是列表或其他类型'''
        
        if cls._isEmptyValue(value):
            return True

        try:
            assert isinstance(value, str) or isinstance(value, int)
            
            if ";" in str(value):
                return False

        except Exception:
            return False

        return True

    @staticmethod
    def _isEmptyValue(value: Any):
        '''Value是空值'''
        return value is None or pd.isna(value) or value == "None"

class Reader:
    '''表格信息读取器
    表格到程序的中转接口，表格读取器会自动判断并转换数据类型，无需手动处理'''
    def __init__(self,
                 excelPath: Path,
                 sheetName: str,
                 ) -> None:
        self.excelPath = excelPath
        self.sheetName = sheetName
    
        # 加载绘图数据
        df = pd.read_excel(self.excelPath, sheet_name = self.sheetName, dtype = object)
        self.df = df
        # 表格的字典形式
        self.dfDict = {}
        self.typeDict: Dict[str, ExcelValueType] = {}

        # 按列解析
        GLog.logInfo(f"{GLog.BLUE}开始表格类型解析{GLog.END}")
        for col in df.columns:
            #df[col] = self.parseColumn(df, col) # 赋值之后类型改变了 / 需要替换一个数据结构存储
            try:
                self.dfDict[col] = self.parseColumn(df, col)
            except Exception as e:
                GLog.logInfo(f"{GLog.RED}列解析出错 | {col} | {str(e)}{GLog.END}")
                raise e
            
    def assertColType(self, col: str, wishType: ExcelValueType):
        '''断言某个列是某个类型'''
        if col not in self.typeDict:
            raise ValueError(f"表格中缺少列 \'{col}\'")
        
        # 全空，返回
        if not any(self.dfDict[col]):
            return 
        
        assert self.typeDict[col] == wishType, f"列 \'{col}\' 的期望类型是 {wishType.name} 但实际类型是 {self.typeDict[col].name}"

    def parseColumn(self, df: DataFrame, col: str)->list:
        '''解析一列'''

        valueList = df[col].tolist() # 获取列值
        
        # 处理分号问题
        for index, value in enumerate(valueList):
            if isinstance(value, str) and "；" in value:
                valueList[index] = value.replace("；", ";")
        
        # 表格类型解析
        columnType = ExcelValueType.detectType(valueList = valueList)
        
        GLog.logInfo(f"表格类型解析 | \'{col}\'的解析类型为{columnType.name}")
        self.typeDict[col] = columnType # 记录类型

        # 自动类型检查转换
        if columnType == ExcelValueType.INT:
            parsedList = [int(value) if not ExcelValueType._isEmptyValue(value) else None
                          for value in valueList]

        elif columnType == ExcelValueType.STR:
            parsedList = [str(value).strip() if not ExcelValueType._isEmptyValue(value) else None 
                          for value in valueList]
          
        elif columnType == ExcelValueType.BOOL:
            parsedList = [bool(value) if not ExcelValueType._isEmptyValue(value) else False 
                          for value in valueList]
            
        elif columnType == ExcelValueType.MIXED:
            parsedList = []
            for value in valueList:
                if ExcelValueType._isEmptyValue(value):
                    parsedList.append(None)
                elif ExcelValueType.isInt(value):
                    parsedList.append(int(value))
                else:
                    parsedList.append(str(value).strip())
            
        elif columnType == ExcelValueType.LIST_INT:
            parsedList = []
            for value in valueList:
                if ExcelValueType._isEmptyValue(value):
                    parsedList.append([])
                elif ExcelValueType.isInt(value):
                    parsedList.append([int(value)])
                else:
                    subValueList = [splitValue.strip() for splitValue in value.split(";")]
                    subValueList = [splitValue for splitValue in subValueList if bool(splitValue)]

                    parsedList.append([int(splitValue) if not ExcelValueType._isEmptyValue(splitValue) else None
                                       for splitValue in subValueList])
    
        elif columnType == ExcelValueType.LIST_STR:
            parsedList = []
            for value in valueList:
                
                if isinstance(value, int):
                    value = str(value)
                
                if ExcelValueType._isEmptyValue(value):
                    parsedList.append([])
                else:
                    subValueList = [splitValue.strip() for splitValue in value.split(";")]
                    subValueList = [splitValue for splitValue in subValueList if bool(splitValue)]

                    parsedList.append([str(splitValue).strip() if not ExcelValueType._isEmptyValue(splitValue) else None
                                       for splitValue in subValueList])
                    
        elif columnType == ExcelValueType.UNKNOWEN:
            parsedList = valueList # 不做处理

        else:
            raise TypeError(f"类型解析错误 | 未知类型 \'{columnType}\'")
    
        return parsedList
    
    def __len__(self):
        return len(self.df)


