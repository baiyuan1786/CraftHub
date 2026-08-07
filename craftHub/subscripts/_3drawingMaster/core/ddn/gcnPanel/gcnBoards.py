##########################################################################################################
#   Description: GCN网板卡解析
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from dataclasses import dataclass
from typing import Any, List, Literal, Optional
import re

from ...common.reader import DataUnit


@dataclass
class GCNETHBoardData:
    '''GCN以太网板卡数据'''

    slotNum: int
    insertType: Literal["新增", "占用", "普通"]


class GCNETHboards:
    '''GCN以太网板卡数据解析器'''

    DATA_KEY_ETH_SLOT_LIST = "GCNETHslotList"

    TAG_OCCUPIED = "o"
    TAG_NEW = "n"
    TAG_VALUE_LIST = [
        None,
        TAG_OCCUPIED,
        TAG_NEW
    ]

    INSERT_TYPE_NEW = "新增"
    INSERT_TYPE_OCCUPIED = "占用"
    INSERT_TYPE_NORMAL = "普通"

    SLOT_PATTERN = re.compile(r"^(\d+)(?:<([^<>]+)>)?$")

    def __init__(
            self,
            data: DataUnit,
            validSlotList: Optional[List[int]] = None
    ) -> None:
        """初始化GCN以太网板卡数据解析器

        :param data:          数据单元
        :param validSlotList: 允许插入以太网板卡的槽位列表
        """

        self.data = data
        self.validSlotList = validSlotList
        self.validSlotSet = set(validSlotList) if validSlotList is not None else None

        self.boardDataList: List[GCNETHBoardData] = []

        self._build()

    def toBoardDataList(self) -> List[GCNETHBoardData]:
        '''获取板卡数据列表'''

        return self.boardDataList

    def _build(self):
        '''构建板卡数据列表'''

        usedSlotSet = set()
        slotList = self._getListData(self.DATA_KEY_ETH_SLOT_LIST)

        for rawSlot in slotList:
            slotNum, tag = self._parseSlot(rawSlot)
            insertType = self._tagToInsertType(tag, rawSlot)

            self._appendBoardData(
                slotNum=slotNum,
                insertType=insertType,
                usedSlotSet=usedSlotSet
            )

    def _getListData(self, key: str) -> List[Any]:
        '''读取列表字段'''

        value = self.data.get(key)

        if value is None:
            return []

        if not isinstance(value, list):
            raise TypeError(
                f"{key}字段类型错误，应为list，当前类型为{type(value)}"
            )

        return value

    def _parseSlot(self, rawSlot: Any) -> tuple[int, Optional[str]]:
        '''解析槽位参数'''

        if isinstance(rawSlot, bool):
            raise TypeError(f"GCN以太网板卡槽位不能是bool类型: {rawSlot}")

        if isinstance(rawSlot, int):
            slotNum = rawSlot
            tag = None

        elif isinstance(rawSlot, str):
            match = self.SLOT_PATTERN.fullmatch(rawSlot.strip())

            if match is None:
                raise ValueError(
                    f"GCN以太网板卡槽位格式错误: {rawSlot}, "
                    "正确格式示例: 1、2<o> 或 3<n>"
                )

            slotNum = int(match.group(1))
            tag = match.group(2)

            if tag is not None:
                tag = tag.strip().lower()

        else:
            raise TypeError(
                f"GCN以太网板卡槽位类型错误: {rawSlot}, "
                f"当前类型为{type(rawSlot)}"
            )

        self._checkSlotNum(slotNum)

        return slotNum, tag

    def _tagToInsertType(
            self,
            tag: Optional[str],
            rawSlot: Any
    ) -> Literal["新增", "占用", "普通"]:
        '''根据槽位标记获取板卡插入类型'''

        if tag is None:
            return self.INSERT_TYPE_NORMAL

        if tag == self.TAG_OCCUPIED:
            return self.INSERT_TYPE_OCCUPIED

        if tag == self.TAG_NEW:
            return self.INSERT_TYPE_NEW

        raise ValueError(
            f"GCN以太网板卡槽位标记不符合标准: {rawSlot}, "
            f"只允许使用 <{self.TAG_OCCUPIED}>、<{self.TAG_NEW}> 或不填写标记"
        )

    def _checkSlotNum(self, slotNum: int):
        '''检查槽位号是否合法'''

        if slotNum <= 0:
            raise ValueError(f"GCN以太网板卡槽位必须大于0: {slotNum}")

        if self.validSlotSet is None:
            return

        if slotNum not in self.validSlotSet:
            raise ValueError(
                f"第 '{slotNum}' 号位置不可插入以太网板卡，"
                f"允许的槽位为: {sorted(self.validSlotSet)}"
            )

    def _appendBoardData(
            self,
            slotNum: int,
            insertType: Literal["新增", "占用", "普通"],
            usedSlotSet: set
    ):
        '''添加板卡数据，并检查重复'''

        if slotNum in usedSlotSet:
            raise ValueError(f"GCN以太网板卡槽位重复: {slotNum}")

        usedSlotSet.add(slotNum)

        self.boardDataList.append(
            GCNETHBoardData(
                slotNum=slotNum,
                insertType=insertType
            )
        )