##########################################################################################################
#   Description: 纵向加密IDF连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from .....common.graph import CADColor, NewBlock
from .....common.graph import 现有设备, 本期新增网线

class CDIDFConnectionPanel(NewBlock):
    '''纵向加密IDF连接面板图'''

    WIDTH = 42
    HEIGHT = 21

    PORT_BOX_WIDTH = 14
    PORT_BOX_HEIGHT = 8.5

    PORT_BOX_BOTTOM_Y = 0
    PORT_BOX_TOP_Y = HEIGHT - PORT_BOX_HEIGHT

    PORT_TEXT_HEIGHT = 3
    DEVICE_TEXT_HEIGHT = 3

    PORT_TEXT_WIDTH_RATE = 0.9
    DEVICE_TEXT_WIDTH_RATE = 0.9

    CUT_BUSINESS_LINE_LENGTH = 18
    CUT_BUSINESS_TEXT_HEIGHT = 3
    CUT_BUSINESS_TEXT_WIDTH = 90
    CUT_BUSINESS_TEXT_OFFSET_Y = 2
    CUT_BUSINESS_TEXT_OFFSET_X = 13
    CUT_BUSINESS_TEXT = "业务割接时断开与旧A网路由器的链路"

    ALIGN_TOLERANCE = 0.5

    @classmethod
    def insertPointFromFrontPoints(
            cls,
            insertX: float,
            rtLinkPoint: Vec2,
            nrtLinkPoint: Vec2
    ) -> Vec2:
        '''根据实时/非实时接入点反算IDF插入点'''

        rtInsertY = rtLinkPoint.y - cls._rtPointFrontLocalStatic().y
        nrtInsertY = nrtLinkPoint.y - cls._nrtPointFrontLocalStatic().y

        if abs(rtInsertY - nrtInsertY) > cls.ALIGN_TOLERANCE:
            raise ValueError(
                "无法保证IDF两个接入点同时水平连接: "
                f"rtInsertY={rtInsertY}, nrtInsertY={nrtInsertY}, "
                f"rtLinkPoint={rtLinkPoint}, nrtLinkPoint={nrtLinkPoint}"
            )

        return Vec2(insertX, (rtInsertY + nrtInsertY) / 2)

    @classmethod
    def _rtPointFrontLocalStatic(cls) -> Vec2:
        '''获取实时纵向加密端口前点局部坐标'''

        return Vec2(0, cls.PORT_BOX_TOP_Y + cls.PORT_BOX_HEIGHT / 2)

    @classmethod
    def _nrtPointFrontLocalStatic(cls) -> Vec2:
        '''获取非实时纵向加密端口前点局部坐标'''

        return Vec2(0, cls.PORT_BOX_BOTTOM_Y + cls.PORT_BOX_HEIGHT / 2)


    def __init__(
            self,
            doc: Drawing,
            devNum: str,
            devName: str,
            portR: str,
            portNR: str,
            insertPoint: Vec2,
            isCutBusiness: bool = False
    ) -> None:
        """纵向加密IDF连接面板图初始化

        :param doc: CAD文档
        :param devNum: 设备号，例如40P10
        :param devName: 设备名，例如IDF配线单元
        :param portR: 实时纵向加密使用端口
        :param portNR: 非实时纵向加密使用端口
        :param insertPoint: 插入点
        :param isCutBusiness: 是否绘制业务断开标记
        """

        super().__init__(doc)

        self.insertPoint = insertPoint

        self.devNum = devNum
        self.devName = devName
        self.portR = portR
        self.portNR = portNR
        self.isCutBusiness = isCutBusiness

        self._drawOuterFrame()
        self._drawPortBox()
        self._drawPortText()
        self._drawDeviceText()

        if self.isCutBusiness:
            self._drawCutBusiness()

    def _drawOuterFrame(self):
        '''绘制外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawPortBox(self):
        '''绘制端口框'''

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, self.PORT_BOX_TOP_Y)
        )

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, self.PORT_BOX_BOTTOM_Y)
        )

    def _drawPortText(self):
        '''绘制端口文字'''

        self.addMtext(
            textContent=CADColor.colored(self.portR),
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_BOX_WIDTH * self.PORT_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.PORT_BOX_WIDTH / 2, self._rtCenterY()),
            style="gedi",
            attachment=5
        )

        self.addMtext(
            textContent=CADColor.colored(self.portNR),
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_BOX_WIDTH * self.PORT_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.PORT_BOX_WIDTH / 2, self._nrtCenterY()),
            style="gedi",
            attachment=5
        )

    def _drawDeviceText(self):
        '''绘制设备文字'''

        deviceText = f"{CADColor.colored(self.devNum)} {self.devName}"

        self.addMtext(
            textContent=deviceText,
            textFontHeight=self.DEVICE_TEXT_HEIGHT,
            textWidth=(self.WIDTH - self.PORT_BOX_WIDTH) * self.DEVICE_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2((self.PORT_BOX_WIDTH + self.WIDTH) / 2, self.HEIGHT / 2),
            style="gedi",
            attachment=5
        )

    def _drawCutBusiness(self):
        '''绘制业务断开标记'''
        if self.portR:
            self._drawCutBusinessTop()
        if self.portNR:
            self._drawCutBusinessBottom()

    def _drawCutBusinessTop(self):
        '''绘制上方业务断开标记'''

        startPoint = self._rtPortTopCenterLocal()
        endPoint = startPoint + Vec2(0, self.CUT_BUSINESS_LINE_LENGTH)

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=本期新增网线(),
            fork=True
        )

        self.addMtext(
            textContent=self.CUT_BUSINESS_TEXT,
            textFontHeight=self.CUT_BUSINESS_TEXT_HEIGHT,
            textWidth=self.CUT_BUSINESS_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=endPoint + Vec2(self.CUT_BUSINESS_TEXT_OFFSET_X, self.CUT_BUSINESS_TEXT_OFFSET_Y),
            style="gedi",
            attachment=8
        )

    def _drawCutBusinessBottom(self):
        '''绘制下方业务断开标记'''

        startPoint = self._nrtPortBottomCenterLocal()
        endPoint = startPoint + Vec2(0, -self.CUT_BUSINESS_LINE_LENGTH)

        self.addLine(
            startPoint=startPoint,
            endPoint=endPoint,
            line=本期新增网线(),
            fork=True
        )

        self.addMtext(
            textContent=self.CUT_BUSINESS_TEXT,
            textFontHeight=self.CUT_BUSINESS_TEXT_HEIGHT,
            textWidth=self.CUT_BUSINESS_TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=endPoint + Vec2(self.CUT_BUSINESS_TEXT_OFFSET_X, -1 * self.CUT_BUSINESS_TEXT_OFFSET_Y),
            style="gedi",
            attachment=2
        )

    def _rtPortTopCenterLocal(self) -> Vec2:
        '''获取实时纵向加密端口框上中点局部坐标'''

        return Vec2(
            self.PORT_BOX_WIDTH / 2,
            self.PORT_BOX_TOP_Y + self.PORT_BOX_HEIGHT
        )

    def _nrtPortBottomCenterLocal(self) -> Vec2:
        '''获取非实时纵向加密端口框下中点局部坐标'''

        return Vec2(
            self.PORT_BOX_WIDTH / 2,
            self.PORT_BOX_BOTTOM_Y
        )


    def _rtCenterY(self) -> float:
        '''获取实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_TOP_Y + self.PORT_BOX_HEIGHT / 2

    def _nrtCenterY(self) -> float:
        '''获取非实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_BOTTOM_Y + self.PORT_BOX_HEIGHT / 2

    def _rtPointFrontLocal(self) -> Vec2:
        '''获取实时纵向加密端口前点局部坐标'''

        return Vec2(0, self._rtCenterY())

    def _rtPointAfterLocal(self) -> Vec2:
        '''获取实时纵向加密端口后点局部坐标'''

        return Vec2(self.PORT_BOX_WIDTH, self._rtCenterY())

    def _nrtPointFrontLocal(self) -> Vec2:
        '''获取非实时纵向加密端口前点局部坐标'''

        return Vec2(0, self._nrtCenterY())

    def _nrtPointAfterLocal(self) -> Vec2:
        '''获取非实时纵向加密端口后点局部坐标'''

        return Vec2(self.PORT_BOX_WIDTH, self._nrtCenterY())

    def RTPointFront(self) -> Vec2:
        '''返回实时纵向加密端口前点绝对坐标'''


        return self.insertPoint + self._rtPointFrontLocal()

    def RTPointAfter(self) -> Vec2:
        '''返回实时纵向加密端口后点绝对坐标'''

        return self.insertPoint + self._rtPointAfterLocal()

    def NRTPointFront(self) -> Vec2:
        '''返回非实时纵向加密端口前点绝对坐标'''

        return self.insertPoint + self._nrtPointFrontLocal()

    def NRTPointAfter(self) -> Vec2:
        '''返回非实时纵向加密端口后点绝对坐标'''

        return self.insertPoint + self._nrtPointAfterLocal()

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''插入纵向加密IDF连接面板图'''

        return super().insertInto(layout, self.insertPoint)