##########################################################################################################
#   Description: idn电源连接图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import NewBlock, 本期新增电源线, 现有设备
from .pdu import PDUConnectionPanel
from .powerCabinet import PowerCabinetConnectionPanel

PowerCabinetTkA = Literal["10A", "16A", "20A", "32A", "63A"]

class IDNPowerLink(NewBlock):
    '''idn电源连接图'''

    POWER_CABINET_LEFT_OFFSET_X = -30.24
    POWER_CABINET_RIGHT_OFFSET_X = 30.24
    POWER_CABINET_OFFSET_Y = 13.5

    INSERT_POINT = Vec2(0, 0)

    def __init__(
            self,
            doc: Drawing,
            powerCabinetPNum1: str,
            powerCabinetPName1: str,
            powerCabinetTkNum1: str,
            powerCabinetTkA1: PowerCabinetTkA,
            powerCabinetPNum2: str,
            powerCabinetPName2: str,
            powerCabinetTkNum2: str,
            powerCabinetTkA2: PowerCabinetTkA,
            pduInstallPnum: str,
            isUsePDU: bool,
            isNewPDU: bool,
            insertPoint: Vec2,
            powerPoint1: Vec2,
            powerPoint2: Vec2
    ) -> None:
        """idn电源连接图初始化，使用绝对坐标，PDU左下角点为本块基点

        :param doc: 文档
        :param powerCabinetPNum1: 电源屏1编号
        :param powerCabinetPName1: 电源屏1名字
        :param powerCabinetTkNum1: 电源屏1空开编号
        :param powerCabinetTkA1: 电源屏1空开电流
        :param powerCabinetPNum2: 电源屏2编号
        :param powerCabinetPName2: 电源屏2名字
        :param powerCabinetTkNum2: 电源屏2空开编号
        :param powerCabinetTkA2: 电源屏2空开电流
        :param pduInstallPnum: PDU安装屏编号
        :param isUsePDU: 是否使用PDU
        :param isNewPDU: 是否为新增PDU
        :param insertPoint: 插入点，使用绝对坐标，PDU左下角点为本块基点
        :param powerPoint1: 电源模块1点
        :param powerPoint2: 电源模块2点
        """
        super().__init__(doc=doc)

        self.pduConnectionPanel = self._createPduConnectionPanel(
            doc=doc,
            pduInstallPnum=pduInstallPnum,
            isNewPDU=isNewPDU,
            isUsePDU=isUsePDU
        )

        self.powerCabinetConnectionPanel1 = PowerCabinetConnectionPanel(
            doc=doc,
            pNum=powerCabinetPNum1,
            pName=powerCabinetPName1,
            tkNum=powerCabinetTkNum1,
            tkA=powerCabinetTkA1
        )
        self.powerCabinetConnectionPanel2 = PowerCabinetConnectionPanel(
            doc=doc,
            pNum=powerCabinetPNum2,
            pName=powerCabinetPName2,
            tkNum=powerCabinetTkNum2,
            tkA=powerCabinetTkA2
        )

        self._drawPowerLink(
            insertPoint=insertPoint,
            powerPoint1=powerPoint1,
            powerPoint2=powerPoint2,
            isNewPDU=isNewPDU
        )

    def _createPduConnectionPanel(
            self,
            doc: Drawing,
            pduInstallPnum: str,
            isNewPDU: bool,
            isUsePDU: bool
    ) -> PDUConnectionPanel | None:
        """创建PDU连接面板

        :param doc: 文档
        :param pduInstallPnum: PDU安装屏编号
        :param isNewPDU: 是否为新增PDU
        :param isUsePDU: 是否使用PDU
        :return: PDU连接面板
        """

        if not isUsePDU:
            return None

        return PDUConnectionPanel(
            doc=doc,
            installPnum=pduInstallPnum,
            isNew=isNewPDU
        )

    def _drawPowerLink(
            self,
            insertPoint: Vec2,
            powerPoint1: Vec2,
            powerPoint2: Vec2,
            isNewPDU: bool
    ):
        """绘制电源连接图

        :param insertPoint: 插入点
        :param powerPoint1: 电源模块1点
        :param powerPoint2: 电源模块2点
        :param isNewPDU: 是否为新增PDU
        """

        ipPDU = insertPoint
        ipPowerCabinet1 = self._getPowerCabinetInsertPoint1(ipPDU)
        ipPowerCabinet2 = self._getPowerCabinetInsertPoint2(ipPDU)

        self.powerCabinetConnectionPanel1.insertInto(self.block, ipPowerCabinet1)
        self.powerCabinetConnectionPanel2.insertInto(self.block, ipPowerCabinet2)

        powerCabinetPoint1 = Vec2(powerPoint1.x, ipPowerCabinet1.y)
        powerCabinetPoint2 = Vec2(powerPoint2.x, ipPowerCabinet2.y)

        if self.pduConnectionPanel is None:
            self._drawLineWithoutPdu(
                powerPoint1=powerPoint1,
                powerPoint2=powerPoint2,
                powerCabinetPoint1=powerCabinetPoint1,
                powerCabinetPoint2=powerCabinetPoint2
            )
            return

        self._drawLineWithPdu(
            insertPoint=insertPoint,
            powerPoint1=powerPoint1,
            powerPoint2=powerPoint2,
            powerCabinetPoint1=powerCabinetPoint1,
            powerCabinetPoint2=powerCabinetPoint2,
            isNewPDU=isNewPDU
        )

    def _getPowerCabinetInsertPoint1(self, ipPDU: Vec2) -> Vec2:
        """获取电源屏1插入点

        :param ipPDU: PDU插入点
        :return: 电源屏1插入点
        """

        return (
            ipPDU
            + Vec2(0, PDUConnectionPanel.height)
            + Vec2(self.POWER_CABINET_LEFT_OFFSET_X, self.POWER_CABINET_OFFSET_Y)
        )

    def _getPowerCabinetInsertPoint2(self, ipPDU: Vec2) -> Vec2:
        """获取电源屏2插入点

        :param ipPDU: PDU插入点
        :return: 电源屏2插入点
        """

        return (
            ipPDU
            + Vec2(PDUConnectionPanel.width, PDUConnectionPanel.height)
            + Vec2(
                self.POWER_CABINET_RIGHT_OFFSET_X - PowerCabinetConnectionPanel.width1,
                self.POWER_CABINET_OFFSET_Y
            )
        )

    def _drawLineWithoutPdu(
            self,
            powerPoint1: Vec2,
            powerPoint2: Vec2,
            powerCabinetPoint1: Vec2,
            powerCabinetPoint2: Vec2
    ):
        """绘制无PDU电源连接线

        :param powerPoint1: 电源模块1点
        :param powerPoint2: 电源模块2点
        :param powerCabinetPoint1: 电源屏1连接点
        :param powerCabinetPoint2: 电源屏2连接点
        """

        self.addLine(powerPoint1, powerCabinetPoint1, 本期新增电源线())
        self.addLine(powerPoint2, powerCabinetPoint2, 本期新增电源线())

    def _drawLineWithPdu(
            self,
            insertPoint: Vec2,
            powerPoint1: Vec2,
            powerPoint2: Vec2,
            powerCabinetPoint1: Vec2,
            powerCabinetPoint2: Vec2,
            isNewPDU: bool
    ):
        """绘制带PDU电源连接线

        :param insertPoint: PDU插入点
        :param powerPoint1: 电源模块1点
        :param powerPoint2: 电源模块2点
        :param powerCabinetPoint1: 电源屏1连接点
        :param powerCabinetPoint2: 电源屏2连接点
        :param isNewPDU: 是否为新增PDU
        """

        pduInPoint1 = self.pduConnectionPanel.inPoint(powerPoint1, insertPoint) #type: ignore
        pduInPoint2 = self.pduConnectionPanel.inPoint(powerPoint2, insertPoint)#type: ignore
        pduOutPoint1 = self.pduConnectionPanel.outPoint(powerPoint1, insertPoint)#type: ignore
        pduOutPoint2 = self.pduConnectionPanel.outPoint(powerPoint2, insertPoint)#type: ignore

        self.addLine(powerPoint1, pduOutPoint1, 本期新增电源线())
        self.addLine(powerPoint2, pduOutPoint2, 本期新增电源线())

        self.pduConnectionPanel.insertInto(self.block, insertPoint)#type: ignore

        pduToPowerCabinetLineType = 本期新增电源线() if isNewPDU else 现有设备()

        self.addLine(pduInPoint1, powerCabinetPoint1, pduToPowerCabinetLineType)
        self.addLine(pduInPoint2, powerCabinetPoint2, pduToPowerCabinetLineType)

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''连接图插入到零点即可'''

        return super().insertInto(layout, self.INSERT_POINT)