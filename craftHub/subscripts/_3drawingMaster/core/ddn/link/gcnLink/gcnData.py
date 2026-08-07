##########################################################################################################
#   Description: GCN网连接数据接口
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from dataclasses import dataclass, field
from typing import Any, ClassVar, Dict, List, Optional

from ....common.reader import ParseUnit

@dataclass
class GCNETHSlotData:
    '''保底通信网以太网板卡槽位数据'''

    slotNum: int
    tag: Optional[str] = None

    TAG_OCCUPIED: ClassVar[str] = "o"
    TAG_NEW: ClassVar[str] = "n"

    @classmethod
    def fromRaw(cls, rawValue: Any) -> "GCNETHSlotData":
        '''从原始字符串构建以太网槽位数据'''

        parseUnit = ParseUnit(str(rawValue))

        if not parseUnit.value.isdigit():
            raise ValueError(f"GCNETHslotList槽位号必须是数字，当前值为{parseUnit.value}")

        return cls(
            slotNum=int(parseUnit.value),
            tag=parseUnit.tag
        )

    def isOccupied(self) -> bool:
        '''判断是否为占用板卡'''

        return self.tag == self.TAG_OCCUPIED

    def isNew(self) -> bool:
        '''判断是否为新增板卡'''

        return self.tag == self.TAG_NEW

    def isIrrelevant(self) -> bool:
        '''判断是否为无关板卡'''

        return self.tag is None

    def isUsedByProject(self) -> bool:
        '''判断是否为本项目使用板卡'''

        return self.isOccupied() or self.isNew()

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
    '''保底通信网传输设备数据'''

    pNum: str
    pName: str
    boardName: str
    areaName: str

    existedEdgedIDF: Optional[str]

    targetStationList: List[str]
    linkBoardList: List[str]
    slotNumList: List[int]

    isExpansion: bool
    ethSlotRawList: List[Any]
    newETHslotEdgedIDF: Optional[str]

    TARGET_STATION_NUM: ClassVar[int] = 2

    SLOT_NUM_MIN: ClassVar[int] = 1
    SLOT_NUM_MAX: ClassVar[int] = 12
    SLOT_NUM_COUNT: ClassVar[int] = 2
    DEFAULT_SLOT_NUM_LIST: ClassVar[List[int]] = [1, 3]

    ethSlotDataList: List[GCNETHSlotData] = field(init=False)
    ethSlotDataDict: Dict[int, GCNETHSlotData] = field(init=False)
    linkItemDataList: List[GCNLinkItemData] = field(init=False)

    def __post_init__(self):
        '''初始化后清洗数据'''

        self.pNum = self._cleanValue(self.pNum)
        self.pName = self._cleanValue(self.pName)
        self.boardName = self._cleanValue(self.boardName)
        self.areaName = self._cleanValue(self.areaName)

        self.existedEdgedIDF = self._cleanValue(self.existedEdgedIDF)
        self.newETHslotEdgedIDF = self._cleanValue(self.newETHslotEdgedIDF)

        self.targetStationList = self._cleanList(self.targetStationList)
        self.linkBoardList = self._cleanList(self.linkBoardList)
        self.slotNumList = self._cleanSlotNumList(self.slotNumList)

        self.isExpansion = self._cleanBool(self.isExpansion)
        self.ethSlotDataList = self._cleanETHSlotDataList(self.ethSlotRawList)
        self.ethSlotDataDict = {
            ethSlotData.slotNum: ethSlotData
            for ethSlotData in self.ethSlotDataList
        }

        self._checkData()
        self.linkItemDataList = self._buildLinkItemDataList()

    def _checkData(self):
        '''检查数据合法性'''

        if self.pNum == "":
            raise ValueError("保底通信网设备屏号不能为空")

        if self.pName == "":
            raise ValueError("保底通信网设备屏名不能为空")

        if self.boardName == "":
            raise ValueError("保底通信网板卡名称不能为空")

        if self.areaName == "":
            raise ValueError("保底通信网所属域不能为空")

        if len(self.targetStationList) != self.TARGET_STATION_NUM:
            raise ValueError(
                f"保底通信网目标站数量必须为{self.TARGET_STATION_NUM}，"
                f"当前为{self.targetStationList}"
            )

        if len(self.linkBoardList) != len(self.targetStationList):
            raise ValueError(
                "保底通信网连接电口数量必须与目标站数量一致，"
                f"目标站数量为{len(self.targetStationList)}，"
                f"连接电口数量为{len(self.linkBoardList)}"
            )

        if len(set(self.linkBoardList)) != len(self.linkBoardList):
            raise ValueError(f"保底通信网连接电口不能重复，当前为{self.linkBoardList}")

        if len(self.slotNumList) != self.SLOT_NUM_COUNT:
            raise ValueError(
                f"GCNSlotList必须配置{self.SLOT_NUM_COUNT}个槽位，"
                f"当前为{self.slotNumList}"
            )

        for slotNum in self.slotNumList:
            if slotNum < self.SLOT_NUM_MIN or slotNum > self.SLOT_NUM_MAX:
                raise ValueError(
                    f"GCNSlotList槽位号必须在{self.SLOT_NUM_MIN}-{self.SLOT_NUM_MAX}之间，"
                    f"当前值为{slotNum}"
                )

        self._checkExpansionData()

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


    def iterLinkItem(self):
        '''遍历GCN网出局链路'''

        return iter(self.linkItemDataList)

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
    
    @classmethod
    def _cleanBool(cls, value: Any) -> bool:
        '''清洗布尔值'''

        if isinstance(value, bool):
            return value

        if value is None:
            return False

        cleanValue = str(value).strip().lower()

        if cleanValue in ["true", "1", "是", "y", "yes"]:
            return True

        if cleanValue in ["false", "0", "否", "n", "no", ""]:
            return False

        raise ValueError(f"GCNisExpansion期望为bool值，当前值为{value}")

    @classmethod
    def _cleanETHSlotDataList(cls, rawList: Any) -> List[GCNETHSlotData]:
        '''清洗以太网槽位数据列表'''

        if rawList is None:
            return []

        if isinstance(rawList, str):
            rawList = rawList.split(";")

        if not isinstance(rawList, list):
            raise TypeError(f"GCNETHslotList期望为list类型，当前类型为{type(rawList)}")

        ethSlotDataList: List[GCNETHSlotData] = []

        for rawValue in rawList:
            cleanValue = cls._cleanValue(rawValue)

            if cleanValue == "":
                continue

            ethSlotDataList.append(GCNETHSlotData.fromRaw(cleanValue))

        return ethSlotDataList
    
    def _checkExpansionData(self):
        '''检查扩容数据'''

        if not self.isExpansion:
            return

        if len(self.ethSlotDataList) == 0:
            raise ValueError("GCNisExpansion为True时，GCNETHslotList不能为空")

        if len(self.ethSlotDataDict) != len(self.ethSlotDataList):
            raise ValueError(f"GCNETHslotList存在重复槽位，当前为{self.ethSlotDataList}")

        for slotNum in self.slotNumList:
            if slotNum not in self.ethSlotDataDict:
                raise ValueError(
                    f"GCNSlotList中的槽位{slotNum}未在GCNETHslotList中出现，"
                    f"GCNETHslotList={self.ethSlotDataList}"
                )

            ethSlotData = self.ethSlotDataDict[slotNum]

            if not ethSlotData.isUsedByProject():
                raise ValueError(
                    f"GCNSlotList中的槽位{slotNum}在GCNETHslotList中未标记<o>或<n>，"
                    "参与本项目连接的槽位必须明确标记"
                )

        # 注意：
        # <o> 占用板卡允许 GCNexistedEdgedIDF 为空。
        # 为空时表示不经过旧成端IDF，直接连接到保底网传输设备对应槽位。
        
    def getETHSlotDataBySlotNum(self, slotNum: int) -> GCNETHSlotData:
        '''根据槽位号获取以太网槽位数据'''

        if slotNum not in self.ethSlotDataDict:
            raise ValueError(f"未找到{slotNum}槽对应的以太网板卡数据")

        return self.ethSlotDataDict[slotNum]

    def hasExistedEdgedIDF(self) -> bool:
        '''判断是否存在旧成端IDF'''

        return self.existedEdgedIDF != ""

    def hasNewETHslotEdgedIDF(self) -> bool:
        '''判断是否存在新增板卡成端IDF'''

        return self.newETHslotEdgedIDF != ""

    def iterIDFUnit(self):
        '''兼容旧接口：遍历已有GCN设备成端IDF'''

        if not self.hasExistedEdgedIDF():
            return iter([])

        return iter([self.existedEdgedIDF])

    def hasIDFUnit(self) -> bool:
        '''兼容旧接口：判断是否存在已有GCN设备成端IDF'''

        return self.hasExistedEdgedIDF()
        