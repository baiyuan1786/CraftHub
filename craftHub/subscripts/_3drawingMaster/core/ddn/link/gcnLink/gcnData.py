##########################################################################################################
#   Description: GCN网连接数据接口
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Optional


@dataclass
class EdgedIDFData:
    '''成端IDF数据'''

    devNum: str
    devName: str
    altitudeU: Any = None
    isNew: bool = False

    tag: Optional[str] = field(init=False, default=None)

    def __post_init__(self):
        '''初始化后清洗数据'''

        self.devNum = self._cleanValue(self.devNum)
        self.devName = self._cleanValue(self.devName)

        self._checkData()

    def _checkData(self):
        '''检查成端IDF数据'''

        if self.devNum == "":
            raise ValueError("成端IDF设备编号不能为空")

        if self.devName == "":
            raise ValueError("成端IDF设备名称不能为空")

        if self.isNew and self.altitudeU is None:
            raise ValueError("本期新增成端IDF安装高度不能为空")

    def shouldDraw(self) -> bool:
        '''判断是否应该绘制'''

        return True

    def isRoom2(self) -> bool:
        '''成端IDF默认不属于第二房间'''

        return False

    def isJump(self) -> bool:
        '''成端IDF默认不跳过绘制'''

        return False

    @staticmethod
    def _cleanValue(value) -> str:
        '''清洗数据值'''

        if value is None:
            return ""

        return str(value).strip()
    
@dataclass
class GCNLinkItemData:
    '''GCN网单条出局链路数据'''

    targetStation: str
    linkBoard: str

    VALID_LINK_BOARD_SET: ClassVar[set[str]] = {
        "电口1",
        "电口2",
        "电口3",
        "电口4"
    }

    def __post_init__(self):
        '''初始化后清洗数据'''

        self.targetStation = self._cleanValue(self.targetStation)
        self.linkBoard = self._cleanValue(self.linkBoard)

        self._checkData()

    def _checkData(self):
        '''检查GCN网单条出局链路数据'''

        if self.targetStation == "":
            raise ValueError("GCN网目标站不能为空")

        if self.linkBoard not in self.VALID_LINK_BOARD_SET:
            raise ValueError(
                "GCN网连接板卡只能是 电口1、电口2、电口3、电口4，"
                f"当前值为{self.linkBoard}"
            )

    def linkBoardText(self) -> str:
        '''获取连接板卡显示文字'''

        return self.linkBoard.replace("电口", "") + "路"

    @staticmethod
    def _cleanValue(value) -> str:
        '''清洗数据值'''

        if value is None:
            return ""

        return str(value).strip()


@dataclass
class GCNDeviceData:
    '''GCN网传输设备数据'''

    pNum: str
    pName: str
    boardName: str
    areaName: str
    idfUnitList: List[str]
    targetStationList: List[str]
    linkBoardList: List[str]
    slotNumList: List[int]

    TARGET_STATION_NUM: ClassVar[int] = 2

    SLOT_NUM_MIN: ClassVar[int] = 1
    SLOT_NUM_MAX: ClassVar[int] = 12
    SLOT_NUM_COUNT: ClassVar[int] = 2
    DEFAULT_SLOT_NUM_LIST: ClassVar[List[int]] = [1, 3]

    linkItemDataList: List[GCNLinkItemData] = field(init=False)

    def __post_init__(self):
        '''初始化后清洗数据'''

        self.pNum = self._cleanValue(self.pNum)
        self.pName = self._cleanValue(self.pName)
        self.boardName = self._cleanValue(self.boardName)
        self.areaName = self._cleanValue(self.areaName)

        self.idfUnitList = self._cleanList(self.idfUnitList)
        self.targetStationList = self._cleanList(self.targetStationList)
        self.linkBoardList = self._cleanList(self.linkBoardList)
        self.slotNumList = self._cleanSlotNumList(self.slotNumList)

        self._checkData()
        self.linkItemDataList = self._buildLinkItemDataList()

    def _checkData(self):
        '''检查GCN网传输设备数据'''

        if self.pNum == "":
            raise ValueError("GCN网传输设备屏号不能为空")

        if self.pName == "":
            raise ValueError("GCN网传输设备屏名不能为空")

        if self.boardName == "":
            raise ValueError("GCN网板卡名称不能为空")

        if self.areaName == "":
            raise ValueError("GCN网所属域不能为空")

        if len(self.targetStationList) != self.TARGET_STATION_NUM:
            raise ValueError(
                f"GCN网目标站数量必须为{self.TARGET_STATION_NUM}，"
                f"当前数量为{len(self.targetStationList)}"
            )

        if len(self.slotNumList) != self.SLOT_NUM_COUNT:
            raise ValueError(
                f"GCN网槽位数量必须为{self.SLOT_NUM_COUNT}，"
                f"当前槽位列表为{self.slotNumList}"
            )

        for slotNum in self.slotNumList:
            if slotNum < self.SLOT_NUM_MIN or slotNum > self.SLOT_NUM_MAX:
                raise ValueError(
                    f"GCN网槽位号必须在{self.SLOT_NUM_MIN}-{self.SLOT_NUM_MAX}之间，"
                    f"当前值为{slotNum}"
                )

        if len(self.linkBoardList) != len(self.targetStationList):
            raise ValueError(
                "GCN网连接板卡数量必须与目标站数量一致，"
                f"目标站数量为{len(self.targetStationList)}，"
                f"连接板卡数量为{len(self.linkBoardList)}"
            )

        if len(set(self.linkBoardList)) != len(self.linkBoardList):
            raise ValueError(
                "GCN网连接电口不能重复，"
                f"当前连接电口列表为{self.linkBoardList}"
            )

    def _buildLinkItemDataList(self) -> List[GCNLinkItemData]:
        '''构建GCN网出局链路数据列表'''

        return [
            GCNLinkItemData(
                targetStation=targetStation,
                linkBoard=linkBoard
            )
            for targetStation, linkBoard in zip(
                self.targetStationList,
                self.linkBoardList
            )
        ]

    def iterIDFUnit(self):
        '''遍历IDF跳接单元'''

        return iter(self.idfUnitList)

    def iterLinkItem(self):
        '''遍历GCN网出局链路'''

        return iter(self.linkItemDataList)

    def hasIDFUnit(self) -> bool:
        '''判断是否存在IDF跳接单元'''

        return len(self.idfUnitList) > 0

    def titleText(self) -> str:
        '''获取设备标题文字'''

        return f"{self.pNum} {self.pName}/传输设备"

    def boardText(self) -> str:
        '''获取板卡文字'''

        return f"({self.boardName}以太网板卡)"

    @staticmethod
    def _cleanValue(value) -> str:
        '''清洗数据值'''

        if value is None:
            return ""

        return str(value).strip()

    @classmethod
    def _cleanList(cls, valueList) -> List[str]:
        '''清洗列表数据'''

        if valueList is None:
            return []

        if not isinstance(valueList, list):
            raise TypeError(f"期望列表类型，当前类型为{type(valueList)}")

        return [
            cls._cleanValue(value)
            for value in valueList
            if cls._cleanValue(value) != ""
        ]
        
    @classmethod
    def _cleanSlotNumList(cls, valueList) -> List[int]:
        '''清洗槽位号列表'''

        if valueList is None:
            return cls.DEFAULT_SLOT_NUM_LIST.copy()

        if isinstance(valueList, str):
            valueList = valueList.split(";")

        if not isinstance(valueList, list):
            raise TypeError(f"GCNSlotList期望列表类型，当前类型为{type(valueList)}")

        slotNumList: List[int] = []

        for value in valueList:
            cleanValue = cls._cleanValue(value)

            if cleanValue == "":
                continue

            if not cleanValue.isdigit():
                raise ValueError(f"GCNSlotList槽位号必须是数字，当前值为{cleanValue}")

            slotNumList.append(int(cleanValue))

        if len(slotNumList) == 0:
            return cls.DEFAULT_SLOT_NUM_LIST.copy()

        return slotNumList