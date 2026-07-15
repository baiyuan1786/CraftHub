##########################################################################################################
#   Description: ddn定向式绘图网络连接图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Callable, Dict, List

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from ...common.graph import NewBlock
from ...common.meta import ConnectionIntroduction
from ..reader import DataUnitDDN

from .cryptoLink import CryptoLink
from .ddnDevice import DDN设备连接面板图
from .gcnLink.gcnLink import GCNLink
from .gcnLink.gcnLinkData import GCNLinkData
from .powerLink import DDNPowerLink


class ConnectionMap(NewBlock):
    '''ddn定向式绘图网络连接图'''

    TITLE_INSERT_POINT = Vec2(141, 181)
    DEVICE_PANEL_INSERT_POINT = Vec2(0, 0)

    POWER_LINK_WIDTH = 50.05
    POWER_LINK_OFFSET_Y = 20

    CRYPTO_LINK_INSERT_POINT = Vec2(110, 0)
    CRYPTO_SIMPLIFIED = False

    GCN_LINK_INSERT_POINT = Vec2(130, 90)
    GCN_LINK_POINT_NUM = 2

    DATA_KEY_DDN_INSTALL_PNUM = "DDNInstallPnum"

    GCN_LINK_BOARD_1 = "电口1"
    GCN_LINK_BOARD_2 = "电口2"
    GCN_LINK_BOARD_3 = "电口3"
    GCN_LINK_BOARD_4 = "电口4"

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN
    ) -> None:
        """连接图初始化

        :param doc: CAD文档
        :param data: ddn数据单元
        """

        super().__init__(doc)

        self.doc = doc
        self.data = data

        self.deviceConPanel = self._buildDevicePanel()
        self._build()

    def _build(self):
        '''构建连接图'''

        self._buildTitle()
        self._buildPowerLink()
        self._buildCryptoLink()
        self._buildGCNLink()

    def _buildDevicePanel(self) -> DDN设备连接面板图:
        '''构建设备连接面板图'''

        deviceConPanel = DDN设备连接面板图(
            doc=self.doc,
            installPnum=self.data.get(self.DATA_KEY_DDN_INSTALL_PNUM)
        )

        deviceConPanel.insertInto(
            self.block,
            self.DEVICE_PANEL_INSERT_POINT
        )

        return deviceConPanel

    def _buildTitle(self):
        '''构建连接图标题'''

        connectionIntro = ConnectionIntroduction(self.doc)
        connectionIntro.insertInto(self.block, self.TITLE_INSERT_POINT)

    def _buildPowerLink(self):
        '''构建电源连接图'''

        powerLink = DDNPowerLink(
            doc=self.doc,
            data=self.data,
            powerPoint1=self.deviceConPanel.power1Point(),
            powerPoint2=self.deviceConPanel.power2Point(),
            insertPoint=self._powerLinkInsertPoint()
        )

        powerLink.insertInto(self.block)

    def _buildCryptoLink(self):
        '''构建纵向加密连接图'''

        cryptoLink = CryptoLink(
            doc=self.doc,
            data=self.data,

            # CryptoLink内部会根据RT/NRT接入点修正Y坐标，这里主要控制X坐标
            insertPoint=self.CRYPTO_LINK_INSERT_POINT,

            rtLinkPoint=self.deviceConPanel.board3Point(),
            nrtLinkPoint=self.deviceConPanel.board4Point(),

            simplified=self.CRYPTO_SIMPLIFIED
        )

        cryptoLink.insertInto(self.block)

    def _buildGCNLink(self):
        '''构建GCN网连接图'''

        linkPointList = self._getGCNLinkPointList()
        self._checkGCNLinkPointList(linkPointList)

        gcnLink = GCNLink(
            doc=self.doc,
            data=self.data,
            insertPoint=self.GCN_LINK_INSERT_POINT,
            linkPoint1=linkPointList[0],
            linkPoint2=linkPointList[1],
        )

        gcnLink.insertInto(self.block)

    def _powerLinkInsertPoint(self) -> Vec2:
        '''获取电源连接图插入点'''

        return Vec2(
            (self.deviceConPanel.width - self.POWER_LINK_WIDTH) / 2,
            self.deviceConPanel.height + self.POWER_LINK_OFFSET_Y
        )

    def _getGCNLinkPointList(self) -> List[Vec2]:
        '''获取GCN网接入点列表'''

        linkData = GCNLinkData(self.data)

        return [
            self._getGCNLinkPoint(linkBoard)
            for linkBoard in linkData.getLinkBoardList()
        ]

    def _getGCNLinkPoint(self, linkBoard: str) -> Vec2:
        '''根据GCN网连接电口获取接入点'''

        linkBoardPointFuncDict = self._getGCNLinkBoardPointFuncDict()

        if linkBoard not in linkBoardPointFuncDict:
            raise ValueError(
                "GCN网连接电口只能是 电口1、电口2、电口3、电口4，"
                f"当前值为{linkBoard}"
            )

        return linkBoardPointFuncDict[linkBoard]()

    def _getGCNLinkBoardPointFuncDict(self) -> Dict[str, Callable[[], Vec2]]:
        '''获取GCN网连接电口与接入点函数映射'''

        return {
            self.GCN_LINK_BOARD_1: self.deviceConPanel.board1Point,
            self.GCN_LINK_BOARD_2: self.deviceConPanel.board2Point,
            self.GCN_LINK_BOARD_3: self.deviceConPanel.board3Point,
            self.GCN_LINK_BOARD_4: self.deviceConPanel.board4Point,
        }

    def _checkGCNLinkPointList(self, linkPointList: List[Vec2]):
        '''检查GCN网接入点列表'''

        if len(linkPointList) != self.GCN_LINK_POINT_NUM:
            raise ValueError(
                f"GCN网连接点数量必须为{self.GCN_LINK_POINT_NUM}，"
                f"当前数量为{len(linkPointList)}"
            )