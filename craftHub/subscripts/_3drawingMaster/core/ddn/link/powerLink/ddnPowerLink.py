##########################################################################################################
#   Description: ddn电源连接图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import NewBlock, 本期新增电源线, 现有设备
from ...reader import DataUnitDDN

from .pduBase import PDUConnectionPanel
from .powerCabinet import PowerCabinetConnectionPanel2
from .pdu32A1536W import PDU_32A1536W
from .pdu63A3000W import PDU_63A3000W


PowerCabinetTkA = Literal["10A", "16A", "20A", "32A", "63A"]


class DDNPowerLink(NewBlock):
    '''ddn电源连接图'''

    POWER_CABINET_LEFT_OFFSET_X = -30.24
    POWER_CABINET_RIGHT_OFFSET_X = 30.24
    POWER_CABINET_OFFSET_Y = 13.5

    POWER_CABINET_LEFT_ORIENT = "left"
    POWER_CABINET_RIGHT_ORIENT = "right"

    INSERT_POINT = Vec2(0, 0)

    DATA_KEY_POWER_CABINET_PNUM1 = "powerCabinetPnum1"
    DATA_KEY_POWER_CABINET_PNAME1 = "powerCabinetPname1"
    DATA_KEY_POWER_CABINET_TKNUM1 = "powerCabinetTknum1"
    DATA_KEY_POWER_CABINET_TKA1 = "powerCabinetTkA1"

    DATA_KEY_POWER_CABINET_PNUM2 = "powerCabinetPnum2"
    DATA_KEY_POWER_CABINET_PNAME2 = "powerCabinetPname2"
    DATA_KEY_POWER_CABINET_TKNUM2 = "powerCabinetTknum2"
    DATA_KEY_POWER_CABINET_TKA2 = "powerCabinetTkA2"

    DATA_KEY_DDN_INSTALL_PNUM = "DDNInstallPnum"
    DATA_KEY_DDN_INSTALL_PNUM_COMPAT = "DDNinstallPnum"

    DATA_KEY_DDN_IS_USE_PDU = "DDNisUsePDU"
    DATA_KEY_DDN_IS_NEW_PDU = "DDNisNewPDU"

    DATA_KEY_ROOM_NAME = "roomName"

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN,
            insertPoint: Vec2,
            powerPoint1: Vec2,
            powerPoint2: Vec2
    ) -> None:
        """ddn电源连接图初始化，使用绝对坐标，PDU左下角点为本块基点

        :param doc: CAD文档
        :param data: ddn数据单元
        :param insertPoint: 插入点，使用绝对坐标，PDU左下角点为本块基点
        :param powerPoint1: 电源模块1点
        :param powerPoint2: 电源模块2点
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.data = data

        self.insertPoint = insertPoint
        self.powerPoint1 = powerPoint1
        self.powerPoint2 = powerPoint2

        self._loadData()
        self._buildPanel()
        self._drawPowerLink()

    def _loadData(self):
        '''读取电源连接图数据'''

        self.powerCabinetPNum1 = self.data.get(self.DATA_KEY_POWER_CABINET_PNUM1)
        self.powerCabinetPName1 = self.data.get(self.DATA_KEY_POWER_CABINET_PNAME1)
        self.powerCabinetTkNum1 = self.data.get(self.DATA_KEY_POWER_CABINET_TKNUM1)
        self.powerCabinetTkA1 = self.data.get(self.DATA_KEY_POWER_CABINET_TKA1)

        self.powerCabinetPNum2 = self.data.get(self.DATA_KEY_POWER_CABINET_PNUM2)
        self.powerCabinetPName2 = self.data.get(self.DATA_KEY_POWER_CABINET_PNAME2)
        self.powerCabinetTkNum2 = self.data.get(self.DATA_KEY_POWER_CABINET_TKNUM2)
        self.powerCabinetTkA2 = self.data.get(self.DATA_KEY_POWER_CABINET_TKA2)

        self.pduInstallPnum = self._getDDNInstallPnum()
        self.isUsePDU = self.data.get(self.DATA_KEY_DDN_IS_USE_PDU)
        self.isNewPDU = self.data.get(self.DATA_KEY_DDN_IS_NEW_PDU)

        self.roomName = self.data.get(self.DATA_KEY_ROOM_NAME)

    def _buildPanel(self):
        '''构建电源连接图面板'''

        self.pduConnectionPanel = self._createPduConnectionPanel()

        self.powerCabinetConnectionPanel1 = PowerCabinetConnectionPanel2(
            doc=self.doc,
            pNum=self.powerCabinetPNum1,
            pName=self.powerCabinetPName1,
            tkNum=self.powerCabinetTkNum1,
            tkA=self.powerCabinetTkA1,
            roomName=self.roomName,
            orient=self.POWER_CABINET_LEFT_ORIENT
        )

        self.powerCabinetConnectionPanel2 = PowerCabinetConnectionPanel2(
            doc=self.doc,
            pNum=self.powerCabinetPNum2,
            pName=self.powerCabinetPName2,
            tkNum=self.powerCabinetTkNum2,
            tkA=self.powerCabinetTkA2,
            roomName=self.roomName,
            orient=self.POWER_CABINET_RIGHT_ORIENT
        )

    def _getDDNInstallPnum(self) -> str:
        '''获取ddn安装屏编号'''

        ddnInstallPnum = self.data.get(self.DATA_KEY_DDN_INSTALL_PNUM)

        if ddnInstallPnum is None:
            ddnInstallPnum = self.data.get(self.DATA_KEY_DDN_INSTALL_PNUM_COMPAT)

        if ddnInstallPnum is None:
            raise ValueError("未找到ddn安装屏编号，无法绘制电源连接图")

        return str(ddnInstallPnum)

    def _createPduConnectionPanel(self) -> Optional[PDUConnectionPanel]:
        '''创建PDU连接面板'''

        if not self.isUsePDU:
            return None

        if self.powerCabinetTkA1 in ["40A", "32A"]:
            # 使用32APDU试试
            return PDU_32A1536W(
                doc=self.doc,
                installPnum=self.pduInstallPnum,
                isNew=self.isNewPDU
            )
        elif self.powerCabinetTkA1 in ["63A"]:
            return PDU_63A3000W(
                doc=self.doc,
                installPnum=self.pduInstallPnum,
                isNew=self.isNewPDU
            ) 
        else:
            raise ValueError(f"电源端子暂无匹配的PDU模型: {self.powerCabinetTkA1}")

    def _drawPowerLink(self):
        '''绘制电源连接图'''

        ipPDU = self.insertPoint
        ipPowerCabinet1 = self._getPowerCabinetInsertPoint1(ipPDU)
        ipPowerCabinet2 = self._getPowerCabinetInsertPoint2(ipPDU)

        self.powerCabinetConnectionPanel1.insertInto(self.block, ipPowerCabinet1)
        self.powerCabinetConnectionPanel2.insertInto(self.block, ipPowerCabinet2)

        powerCabinetPoint1 = Vec2(self.powerPoint1.x, ipPowerCabinet1.y)
        powerCabinetPoint2 = Vec2(self.powerPoint2.x, ipPowerCabinet2.y)

        if self.pduConnectionPanel is None:
            self._drawLineWithoutPdu(
                powerCabinetPoint1=powerCabinetPoint1,
                powerCabinetPoint2=powerCabinetPoint2
            )
            return

        self._drawLineWithPdu(
            powerCabinetPoint1=powerCabinetPoint1,
            powerCabinetPoint2=powerCabinetPoint2
        )

    def _getPowerCabinetInsertPoint1(self, ipPDU: Vec2) -> Vec2:
        '''获取电源屏1插入点'''

        return (
            ipPDU
            + Vec2(0, PDUConnectionPanel.height)
            + Vec2(self.POWER_CABINET_LEFT_OFFSET_X, self.POWER_CABINET_OFFSET_Y)
        )

    def _getPowerCabinetInsertPoint2(self, ipPDU: Vec2) -> Vec2:
        '''获取电源屏2插入点'''

        return (
            ipPDU
            + Vec2(PDUConnectionPanel.width, PDUConnectionPanel.height)
            + Vec2(
                self.POWER_CABINET_RIGHT_OFFSET_X - PowerCabinetConnectionPanel2.width1,
                self.POWER_CABINET_OFFSET_Y
            )
        )

    def _drawLineWithoutPdu(
            self,
            powerCabinetPoint1: Vec2,
            powerCabinetPoint2: Vec2
    ):
        '''绘制无PDU电源连接线'''

        self.addLine(self.powerPoint1, powerCabinetPoint1, 本期新增电源线())
        self.addLine(self.powerPoint2, powerCabinetPoint2, 本期新增电源线())

    def _drawLineWithPdu(
            self,
            powerCabinetPoint1: Vec2,
            powerCabinetPoint2: Vec2
    ):
        '''绘制带PDU电源连接线'''

        if self.pduConnectionPanel is None:
            return

        # 确认插入点坐标
        pduInPoint1 = self.pduConnectionPanel.inPoint(self.insertPoint, "left")
        pduInPoint2 = self.pduConnectionPanel.inPoint(self.insertPoint, "right")
        pduOutPoint1 = self.pduConnectionPanel.outPoint(self.insertPoint, "left")
        pduOutPoint2 = self.pduConnectionPanel.outPoint(self.insertPoint, "right")

        self.addLine(self.powerPoint1, pduOutPoint1, 本期新增电源线(), polyLine = True, polyLineOrient = "y")
        self.addLine(self.powerPoint2, pduOutPoint2, 本期新增电源线(), polyLine = True, polyLineOrient = "y")

        self.pduConnectionPanel.insertInto(self.block, self.insertPoint)

        pduToPowerCabinetLineType = 本期新增电源线() if self.isNewPDU else 现有设备()

        # 更新屏柜插入点
        powerCabinetPoint1 = Vec2(pduInPoint1.x, powerCabinetPoint1.y)
        powerCabinetPoint2 = Vec2(pduInPoint2.x, powerCabinetPoint2.y)

        # 确认插入点坐标
        self.addLine(pduInPoint1, powerCabinetPoint1, pduToPowerCabinetLineType)
        self.addLine(pduInPoint2, powerCabinetPoint2, pduToPowerCabinetLineType)

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''连接图插入到零点即可'''

        return super().insertInto(layout, self.INSERT_POINT)