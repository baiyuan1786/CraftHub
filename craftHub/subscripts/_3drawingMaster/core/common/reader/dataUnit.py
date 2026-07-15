##########################################################################################################
#   Description: 数据单元
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from craftHub.tool import GLog

from typing import Dict, Any, List, Optional, Literal, Tuple, Type
from ezdxf.math import Vec2

class DataUnit:
    '''数据单元
    仅容纳一行的数据'''
    DRAWING_OFFSET_X = 0
    DRAWING_OFFSET_Y_STEP = 400
    DRAWING_GRID_MAX_ROW = 10
    DRAWING_GRID_COLUMN_STEP = 2100
    
    LAYOUT_GRID = "grid"
    LAYOUT_LIST = "list"
    LAYOUT_FORMATS = (LAYOUT_GRID, LAYOUT_LIST)

    layoutFormat = LAYOUT_LIST
    
    @classmethod
    def setLayoutFormat(cls, layoutFormat: Literal["grid", "list"] = "list"):
        if layoutFormat not in cls.LAYOUT_FORMATS:
            raise ValueError(f"无效的布局参数: {layoutFormat}")
        
        cls.layoutFormat = layoutFormat
    
    def __init__(self, rowIndex: int, dfDict: Dict) -> None:
        """初始化绘图容器

        :param rowIndex: 行索引
        :param dfDict: 表格的字典形式
        """

        self.columns = list(dfDict.keys())
        
        for name, valueList in dfDict.items():
            setattr(self, name, valueList[rowIndex])    

    def statics(self) -> None:
        """打印当前实例的所有成员的值"""
        for col in self.columns:
            GLog.logInfo(f"{col}: {self.get(col)}, type: {type(self.get(col))}")

    def get(self, col: str)->Any:
        '''获取数据单元的某个值'''
        if hasattr(self, col):
            return getattr(self, col)

        else:
            raise ValueError(f"数据单元读取错误 | 表格中不包含列 \'{col}\'")
        
    def set(self, col: str, value):
        '''设置数据单元的某个值'''
        if hasattr(self, col):
            setattr(self, col, value)
        else:
            raise ValueError(f"数据单元读取错误 | 表格中不包含列 \'{col}\'")
        
    def append(self, col: str, value: Any):
        '''为某个列表添加某个值'''
        targetValue = self.get(col)
        if not isinstance(targetValue, list):
            raise TypeError(f"数据单元读取错误 | 成员\'{col}\'不是列表类型")
        
        targetValue.append(value)
        
    def assertType(self, valueName: str, targetType: Type, allowAuto:bool = False, allowNone:bool = False):
        """宣言某个变量是某个理想类型

        :param valueName: 变量名称
        :param targetType: 理想类型
        """
        value = self.get(valueName)
        actualType = type(value).__name__ if value is not None else "None"
        
        if value is None and allowNone:
            return
        
        if not allowAuto:
            assert isinstance(value, targetType), \
                f"{valueName}必须是{targetType.__name__}类型，实际值为{repr(value)}，实际类型为{actualType}"
        else:
            assert isinstance(value, targetType) or value == "auto", \
                f"{valueName}必须是{targetType.__name__}类型或者auto，实际值为{repr(value)}，实际类型为{actualType}"
                
            
    def assertValue(self, valueName: str, targetValue: Any):
        """宣言某个变量具有某个值，或处于某个范围

        :param valueName: 变量名称
        :param targetValue: 目标值
        """        
        value = self.get(valueName)
        if isinstance(targetValue, list):
            assert value in targetValue, f"{valueName}必须是[{", ".join(targetValue)}]之一, 但实际值为{repr(value)}"
        else:
            assert value == targetValue, f"{valueName}必须是{targetValue}, 但实际值为{repr(value)}"
            
    def assertLen(self, valueName: str, targetLen: int):
        """
        断言某个变量是指定长度的列表

        :param valueName: 变量名称
        :param targetLen: 目标长度
        """
        value = self.get(valueName)
        actualType = type(value).__name__ if value is not None else "None"

        assert isinstance(value, list), \
            f"{valueName}必须是list类型，实际值为{repr(value)}，实际类型为{actualType}"

        assert len(value) == targetLen, \
            f"{valueName}长度必须为{targetLen}，实际长度为{len(value)}，实际值为{repr(value)}"
            
     
    def drawOrderToOffset(self):
        '''绘图顺序转换全局布局偏置'''

        layoutFormat = DataUnit.layoutFormat
        drawOrder = self.get("drawOrder")

        assert isinstance(drawOrder, int), f"drawOrder 不是int类型, 其类型为 {type(drawOrder)}"
        assert drawOrder >= 1, f"drawOrder 必须大于等于1, 当前值为 {drawOrder}"
        assert layoutFormat in ["grid", "list"], f"layoutFormat 必须为 grid 或 list, 当前值为 {layoutFormat}"

        if layoutFormat == "list":
            return Vec2(
                self.DRAWING_OFFSET_X,
                -(drawOrder - 1) * self.DRAWING_OFFSET_Y_STEP
            )

        rowIndex = (drawOrder - 1) % self.DRAWING_GRID_MAX_ROW
        colIndex = (drawOrder - 1) // self.DRAWING_GRID_MAX_ROW

        return Vec2(
            self.DRAWING_OFFSET_X + colIndex * self.DRAWING_GRID_COLUMN_STEP,
            -rowIndex * self.DRAWING_OFFSET_Y_STEP
        )