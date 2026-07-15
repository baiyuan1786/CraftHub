##########################################################################################################
#   Description: 纵向加密接入交换机连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from .....common.graph import CADColor, NewBlock
from .....common.graph import 现有设备


class AccessSwitchConnectionPanel(NewBlock):
    '''纵向加密接入交换机连接面板图'''

    DEVICE_NAME = "接入交换机"

    WIDTH = 42

    TITLE_HEIGHT = 8

    # 接口区与 CDIDFConnectionPanel 完全对齐
    INTERFACE_HEIGHT = 21

    HEIGHT = TITLE_HEIGHT + INTERFACE_HEIGHT

    PORT_BOX_WIDTH = 14
    PORT_BOX_HEIGHT = 8.5

    PORT_BOX_BOTTOM_Y = 0
    PORT_BOX_TOP_Y = INTERFACE_HEIGHT - PORT_BOX_HEIGHT

    PORT_TEXT_HEIGHT = 3
    DEVICE_TEXT_HEIGHT = 3

    PORT_TEXT_WIDTH_RATE = 0.9
    DEVICE_TEXT_WIDTH_RATE = 0.9

    ALIGN_TOLERANCE = 0.5

    DEFAULT_FRONT_PORT_1 = "端口1"
    DEFAULT_FRONT_PORT_2 = "端口2"
    DEFAULT_AFTER_PORT_1 = "端口3"
    DEFAULT_AFTER_PORT_2 = "端口4"

    @classmethod
    def insertPointFromFrontPoints(
            cls,
            insertX: float,
            rtLinkPoint: Vec2,
            nrtLinkPoint: Vec2
    ) -> Vec2:
        '''根据实时/非实时接入点反算接入交换机插入点'''

        rtInsertY = rtLinkPoint.y - cls._rtPointFrontLocalStatic().y
        nrtInsertY = nrtLinkPoint.y - cls._nrtPointFrontLocalStatic().y

        if abs(rtInsertY - nrtInsertY) > cls.ALIGN_TOLERANCE:
            raise ValueError(
                "无法保证接入交换机两个接入点同时水平连接: "
                f"rtInsertY={rtInsertY}, nrtInsertY={nrtInsertY}, "
                f"rtLinkPoint={rtLinkPoint}, nrtLinkPoint={nrtLinkPoint}"
            )

        return Vec2(insertX, (rtInsertY + nrtInsertY) / 2)

    @classmethod
    def _rtPointFrontLocalStatic(cls) -> Vec2:
        '''获取实时纵向加密前端口前点局部坐标'''

        return Vec2(0, cls.PORT_BOX_TOP_Y + cls.PORT_BOX_HEIGHT / 2)

    @classmethod
    def _nrtPointFrontLocalStatic(cls) -> Vec2:
        '''获取非实时纵向加密前端口前点局部坐标'''

        return Vec2(0, cls.PORT_BOX_BOTTOM_Y + cls.PORT_BOX_HEIGHT / 2)

    def __init__(
            self,
            doc: Drawing,
            devNum: str,
            devName: str = DEVICE_NAME,
            frontPort1: str = DEFAULT_FRONT_PORT_1,
            frontPort2: str = DEFAULT_FRONT_PORT_2,
            afterPort1: str = DEFAULT_AFTER_PORT_1,
            afterPort2: str = DEFAULT_AFTER_PORT_2,
            insertPoint: Vec2 = Vec2(0, 0)
    ) -> None:
        """纵向加密接入交换机连接面板图初始化

        :param doc:        CAD文档
        :param devNum:     设备号
        :param devName:    设备名
        :param frontPort1: 实时前端口
        :param frontPort2: 非实时前端口
        :param afterPort1: 实时后端口
        :param afterPort2: 非实时后端口
        :param insertPoint: 插入点
        """

        super().__init__(doc)

        self.insertPoint = insertPoint

        self.devNum = devNum
        self.devName = devName
        self.frontPort1 = frontPort1
        self.frontPort2 = frontPort2
        self.afterPort1 = afterPort1
        self.afterPort2 = afterPort2

        self._drawOuterFrame()
        self._drawTitleFrame()
        self._drawPortBox()
        self._drawPortText()
        self._drawDeviceText()

    def _drawOuterFrame(self):
        '''绘制外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawTitleFrame(self):
        '''绘制标题框'''

        self.addLine(
            startPoint=Vec2(0, self.INTERFACE_HEIGHT),
            endPoint=Vec2(self.WIDTH, self.INTERFACE_HEIGHT),
            line=现有设备()
        )

    def _drawPortBox(self):
        '''绘制端口框'''

        # 左侧前端口，位置与 IDF 完全一致
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

        # 右侧后端口，Y 坐标与左侧前端口完全一致
        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(self.WIDTH - self.PORT_BOX_WIDTH, self.PORT_BOX_TOP_Y)
        )

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(self.WIDTH - self.PORT_BOX_WIDTH, self.PORT_BOX_BOTTOM_Y)
        )

    def _drawPortText(self):
        '''绘制端口文字'''

        self._drawPortMtext(
            textContent=self.frontPort1,
            insertPoint=Vec2(self.PORT_BOX_WIDTH / 2, self._rtCenterY())
        )

        self._drawPortMtext(
            textContent=self.frontPort2,
            insertPoint=Vec2(self.PORT_BOX_WIDTH / 2, self._nrtCenterY())
        )

        self._drawPortMtext(
            textContent=self.afterPort1,
            insertPoint=Vec2(self.WIDTH - self.PORT_BOX_WIDTH / 2, self._rtCenterY())
        )

        self._drawPortMtext(
            textContent=self.afterPort2,
            insertPoint=Vec2(self.WIDTH - self.PORT_BOX_WIDTH / 2, self._nrtCenterY())
        )

    def _drawPortMtext(
            self,
            textContent: str,
            insertPoint: Vec2
    ):
        '''绘制端口文字'''

        self.addMtext(
            textContent=CADColor.colored(textContent),
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_BOX_WIDTH * self.PORT_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=insertPoint,
            style="gedi",
            attachment=5
        )

    def _drawDeviceText(self):
        '''绘制设备文字'''

        deviceText = f"{CADColor.colored(self.devNum)} {self.devName}"

        self.addMtext(
            textContent=deviceText,
            textFontHeight=self.DEVICE_TEXT_HEIGHT,
            textWidth=self.WIDTH * self.DEVICE_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.WIDTH / 2, self.INTERFACE_HEIGHT + self.TITLE_HEIGHT / 2),
            style="gedi",
            attachment=5
        )

    def _rtCenterY(self) -> float:
        '''获取实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_TOP_Y + self.PORT_BOX_HEIGHT / 2

    def _nrtCenterY(self) -> float:
        '''获取非实时纵向加密端口中心Y坐标'''

        return self.PORT_BOX_BOTTOM_Y + self.PORT_BOX_HEIGHT / 2

    def _rtPointFrontLocal(self) -> Vec2:
        '''获取实时纵向加密前端口前点局部坐标'''

        return Vec2(0, self._rtCenterY())

    def _rtPointAfterLocal(self) -> Vec2:
        '''获取实时纵向加密后端口后点局部坐标'''

        return Vec2(self.WIDTH, self._rtCenterY())

    def _nrtPointFrontLocal(self) -> Vec2:
        '''获取非实时纵向加密前端口前点局部坐标'''

        return Vec2(0, self._nrtCenterY())

    def _nrtPointAfterLocal(self) -> Vec2:
        '''获取非实时纵向加密后端口后点局部坐标'''

        return Vec2(self.WIDTH, self._nrtCenterY())

    def RTPointFront(self) -> Vec2:
        '''返回实时纵向加密前端口前点绝对坐标'''

        return self.insertPoint + self._rtPointFrontLocal()

    def RTPointAfter(self) -> Vec2:
        '''返回实时纵向加密后端口后点绝对坐标'''

        return self.insertPoint + self._rtPointAfterLocal()

    def NRTPointFront(self) -> Vec2:
        '''返回非实时纵向加密前端口前点绝对坐标'''

        return self.insertPoint + self._nrtPointFrontLocal()

    def NRTPointAfter(self) -> Vec2:
        '''返回非实时纵向加密后端口后点绝对坐标'''

        return self.insertPoint + self._nrtPointAfterLocal()

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''插入纵向加密接入交换机连接面板图'''

        return super().insertInto(layout, self.insertPoint)