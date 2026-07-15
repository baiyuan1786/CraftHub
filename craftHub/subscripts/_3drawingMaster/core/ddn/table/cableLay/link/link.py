##########################################################################################################
#   Description: 单条线缆连接
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import math
from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
from pandas import DataFrame, Series


class LinkBase(ABC):
    '''连接基类'''

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def toDF(self) -> DataFrame:
        '''转换为DataFrame'''

        pass


class Link(LinkBase):
    '''单条线缆连接'''

    BASE_LEN = 3

    ARMORED_JUMPER_LINE_TYPE = "铠装跳纤"
    ARMORED_JUMPER_LEN_TUPLE = (
        1, 3, 5, 8, 10, 15, 20, 25,
        30, 35, 40, 45, 50, 60, 80, 100
    )

    COLUMN_STATION_NAME = "站名"
    COLUMN_ORDER = "序号"
    COLUMN_LINE_TYPE = "线缆类型"
    COLUMN_SPECIFICATION = "规格"
    COLUMN_START_POS = "起点"
    COLUMN_END_POS = "终点"
    COLUMN_ONE_LINE_LEN = "单条长度/m"
    COLUMN_NUM = "数量/条"
    COLUMN_WHOLE_LINE_LEN = "合计/米"
    COLUMN_NOTE = "备注"
    COLUMN_WALK_LINE = "走线"
    COLUMN_CROSSING_CABINET = "跨越机柜"
    COLUMN_CROSSING_ROW = "跨越行"
    COLUMN_CROSSING_FLOOR = "跨层"
    COLUMN_CROSSING_ROOM = "同层跨房间"
    COLUMN_REFERENCED = "参照"
    COLUMN_FULL_LINE_TYPE = "完整线缆类型"

    UNKNOWN_KEYWORD = "未知"
    NEED_FILL_KEYWORD = "请填"
    NEED_FILL_TEXT = "请填写"

    CABLE_FLOOR_WALK_LINE = "电缆层走线"

    CROSSING_FLOOR_LEN = 70
    CROSSING_ROOM_LEN = 50
    CROSSING_CABINET_LEN = 0.8
    CROSSING_ROW_LEN = 1.6
    CABLE_FLOOR_EXTRA_LEN = 6

    # 保留旧变量名，避免其他模块直接引用时失效
    baseLen = BASE_LEN
    armoredJumperLineType = ARMORED_JUMPER_LINE_TYPE
    armoredJumperLenTuple = ARMORED_JUMPER_LEN_TUPLE

    def __init__(
            self,
            order: int,
            lineType: str,
            specification: str,
            startPos: str,
            endPos: str,
            num: int,
            note: str = "",
            crossingCabinet: int = 0,
            crossingRow: int = 0,
            crossingFloor: bool = False,
            crossingRoom: bool = False
    ) -> None:
        """单条线缆连接初始化

        :param order:           序号
        :param lineType:        线缆类型
        :param specification:   规格
        :param startPos:        起点
        :param endPos:          终点
        :param num:             数量
        :param note:            备注
        :param crossingCabinet: 跨机柜数量
        :param crossingRow:     跨行数量
        :param crossingFloor:   是否跨层
        :param crossingRoom:    是否同层跨房间
        """

        self.order = order
        self.lineType = lineType
        self.specification = specification
        self.startPos = startPos
        self.endPos = endPos
        self.num = num
        self.note = note

        self.crossingCabinet = crossingCabinet
        self.crossingRow = crossingRow
        self.crossingFloor = crossingFloor
        self.crossingRoom = crossingRoom

        self.isReferrenced = False

    def convergeArmoredJumperLen(self, rawLen: float) -> int:
        '''铠装跳纤长度收敛'''

        for standardLen in self.ARMORED_JUMPER_LEN_TUPLE:
            if rawLen <= standardLen:
                return standardLen

        raise ValueError(f"铠装跳纤长度超过上限: '{rawLen}' m")

    def oneLineLen(
            self,
            walkLine: str,
            startPos: Optional[str] = None,
            endPos: Optional[str] = None
    ):
        '''计算单条线缆长度/m'''

        for pos in [startPos, endPos]:
            if pos is not None and (
                    self.UNKNOWN_KEYWORD in pos
                    or self.NEED_FILL_KEYWORD in pos
            ):
                return self.UNKNOWN_KEYWORD

        if self.crossingFloor:
            wholeLen = self.CROSSING_FLOOR_LEN

        elif self.crossingRoom:
            wholeLen = self.CROSSING_ROOM_LEN

        else:
            wholeLen = self.BASE_LEN
            wholeLen += self.crossingCabinet * self.CROSSING_CABINET_LEN
            wholeLen += self.crossingRow * self.CROSSING_ROW_LEN

            if (
                    walkLine == self.CABLE_FLOOR_WALK_LINE
                    and (self.crossingCabinet > 0 or self.crossingRow > 0)
            ):
                wholeLen += self.CABLE_FLOOR_EXTRA_LEN

        if self.lineType.strip() == self.ARMORED_JUMPER_LINE_TYPE:
            return self.convergeArmoredJumperLen(wholeLen)

        return math.ceil(wholeLen)

    def wholeLineLen(
            self,
            walkLine: str,
            startPos: Optional[str] = None,
            endPos: Optional[str] = None
    ):
        '''计算全部线缆长度/m'''

        oneLen = self.oneLineLen(walkLine, startPos, endPos)

        if isinstance(oneLen, float) or isinstance(oneLen, int):
            return oneLen * self.num

        return self.UNKNOWN_KEYWORD

    def toDF(
            self,
            substationName: str,
            walkLine: str
    ) -> DataFrame:
        '''转换为DataFrame'''

        return DataFrame({
            self.COLUMN_STATION_NAME: substationName,
            self.COLUMN_ORDER: self.order,
            self.COLUMN_LINE_TYPE: self.lineType,
            self.COLUMN_SPECIFICATION: self.specification,
            self.COLUMN_START_POS: self.startPos,
            self.COLUMN_END_POS: self.endPos,
            self.COLUMN_ONE_LINE_LEN: self.oneLineLen(walkLine, self.startPos, self.endPos),
            self.COLUMN_NUM: self.num,
            self.COLUMN_WHOLE_LINE_LEN: self.wholeLineLen(walkLine, self.startPos, self.endPos),
            self.COLUMN_NOTE: self.note,
            self.COLUMN_WALK_LINE: walkLine,
            self.COLUMN_CROSSING_CABINET: int(self.crossingCabinet),
            self.COLUMN_CROSSING_ROW: int(self.crossingRow),
            self.COLUMN_CROSSING_FLOOR: int(self.crossingFloor),
            self.COLUMN_CROSSING_ROOM: int(self.crossingRoom),
            self.COLUMN_REFERENCED: int(self.isReferrenced),
            self.COLUMN_FULL_LINE_TYPE: f"{self.lineType} + {self.specification}",
        }, index=[0])

    def isRowMatched(self, row: Series):
        '''判断连接是否和一行匹配'''

        if pd.isna(row[self.COLUMN_NOTE]):
            row[self.COLUMN_NOTE] = ""

        if not (
                self.order == row[self.COLUMN_ORDER]
                and self.lineType == row[self.COLUMN_LINE_TYPE]
                and self.specification == row[self.COLUMN_SPECIFICATION]
                and self.note == row[self.COLUMN_NOTE]
        ):
            return False

        if (
                self.startPos == row[self.COLUMN_START_POS]
                and self.endPos == row[self.COLUMN_END_POS]
        ):
            return True

        if (
                self.NEED_FILL_TEXT in self.startPos
                or self.NEED_FILL_TEXT in self.endPos
        ):
            return True

        return False

    def readRowArgs(self, row: Series):
        '''读取参照行参数'''

        if not self.isRowMatched(row):
            return

        self.crossingCabinet = (
            row[self.COLUMN_CROSSING_CABINET]
            if not pd.isna(row[self.COLUMN_CROSSING_CABINET])
            else 0
        )

        self.crossingRow = (
            row[self.COLUMN_CROSSING_ROW]
            if not pd.isna(row[self.COLUMN_CROSSING_ROW])
            else 0
        )

        self.crossingFloor = (
            row[self.COLUMN_CROSSING_FLOOR]
            if not pd.isna(row[self.COLUMN_CROSSING_FLOOR])
            else 0
        )

        self.crossingRoom = (
            row[self.COLUMN_CROSSING_ROOM]
            if not pd.isna(row[self.COLUMN_CROSSING_ROOM])
            else 0
        )

        if self.NEED_FILL_TEXT in self.startPos:
            self.startPos = (
                row[self.COLUMN_START_POS]
                if not pd.isna(row[self.COLUMN_START_POS])
                else "请填写起点"
            )

        if self.NEED_FILL_TEXT in self.endPos:
            self.endPos = (
                row[self.COLUMN_END_POS]
                if not pd.isna(row[self.COLUMN_END_POS])
                else "请填写终点"
            )

        self.isReferrenced = True