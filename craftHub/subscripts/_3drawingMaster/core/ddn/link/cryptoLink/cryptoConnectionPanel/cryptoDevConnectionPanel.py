##########################################################################################################
#   Description: 纵向加密设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal, Optional

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from .....common.graph import CADColor, NewBlock
from .....common.graph import 现有设备


class CDConnectionPanel(NewBlock):
    '''纵向加密设备连接面板图'''

    PORT_BOX_WIDTH = 16
    PORT_BOX_HEIGHT = 8.5

    PORT_TEXT_HEIGHT = 3
    PORT_TEXT_WIDTH_RATE = 0.9
    
    DEVICE_BODY_WIDTH = 40

    WIDTH = DEVICE_BODY_WIDTH + PORT_BOX_WIDTH
    HEIGHT = 18

    TEXT_FONT_HEIGHT = 3.3
    TEXT_WIDTH = WIDTH * 0.99
    TEXT_LINE_SPACING_DISTANCE = 1

    TEXT_LINE_1_Y = 14
    TEXT_LINE_2_Y = 9
    TEXT_LINE_3_Y = 4

    FRONT_POINT_RT_Y = 3
    FRONT_POINT_NRT_Y = HEIGHT - 3

    CRYPO_TYPE_RT = "rt"
    CRYPO_TYPE_NRT = "nrt"

    RT_TYPE_TEXT = "(A平面-实时)"
    NRT_TYPE_TEXT = "(A平面-非实时)"

    CRYPTO_TYPE_RT = "rt"
    CRYPTO_TYPE_NRT = "nrt"

    ALIGN_TOLERANCE = 0.5

    def __init__(
            self,
            doc: Drawing,
            devPnum: str,
            devPname: str,
            crypoType: str,
            insertPoint: Vec2,
            portName: Optional[str] = None
    ) -> None:
        """纵向加密设备连接面板图初始化

        :param doc: CAD文档
        :param devPnum: 设备屏位号
        :param devPname: 设备屏位名
        :param crypoType: 纵向加密类型，rt 或 nrt
        :param insertPoint: 插入点
        :param portName: 端口号
        """

        super().__init__(doc, blockName=None)

        self.insertPoint = insertPoint

        self.devPnum = devPnum
        self.devPname = devPname
        self.crypoType = crypoType
        self.portName = portName

        self._drawOuterFrame()
        self._drawPortBox()
        self._drawPortText()

        self._checkCrypoType()
        self._drawText()

    @classmethod
    def insertPointFromFrontPoint(
            cls,
            frontPoint: Vec2,
            crypoType: str
    ) -> Vec2:
        '''根据前连接点反算插入点'''

        return frontPoint - cls._frontPointLocalStatic(crypoType)

    @classmethod
    def _frontPointLocalStatic(
            cls,
            crypoType: str
    ) -> Vec2:
        '''获取前连接点局部坐标'''

        if crypoType == cls.CRYPTO_TYPE_RT:
            return Vec2(0, cls.PORT_BOX_HEIGHT / 2)

        if crypoType == cls.CRYPTO_TYPE_NRT:
            return Vec2(0, cls.HEIGHT - cls.PORT_BOX_HEIGHT / 2)

        raise ValueError(f"未知纵向加密类型: {crypoType}")

    def _drawPortBox(self):
        '''绘制端口号框'''

        self.addRectangle(
            width=self.PORT_BOX_WIDTH,
            height=self.PORT_BOX_HEIGHT,
            line=现有设备(),
            insertPoint=self._portBoxInsertPointLocal()
        )

    def _drawPortText(self):
        '''绘制端口号文字'''

        if self.portName is None:
            return

        self.addMtext(
            textContent=CADColor.colored(self.portName),
            textFontHeight=self.PORT_TEXT_HEIGHT,
            textWidth=self.PORT_BOX_WIDTH * self.PORT_TEXT_WIDTH_RATE,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=self._portBoxCenterLocal(),
            style="gedi",
            attachment=5
        )

    def _portBoxInsertPointLocal(self) -> Vec2:
        '''获取端口号框插入点局部坐标'''

        if self.crypoType == self.CRYPTO_TYPE_RT:
            return Vec2(0, 0)

        if self.crypoType == self.CRYPTO_TYPE_NRT:
            return Vec2(0, self.HEIGHT - self.PORT_BOX_HEIGHT)

        raise ValueError(f"未知纵向加密类型: {self.crypoType}")

    def _portBoxCenterLocal(self) -> Vec2:
        '''获取端口号框中心局部坐标'''

        portBoxInsertPoint = self._portBoxInsertPointLocal()

        return portBoxInsertPoint + Vec2(
            self.PORT_BOX_WIDTH / 2,
            self.PORT_BOX_HEIGHT / 2
        )


    def _checkCrypoType(self):
        '''检查加密设备类型'''

        if self.crypoType not in [self.CRYPO_TYPE_RT, self.CRYPO_TYPE_NRT]:
            raise ValueError(f"crypoType必须是'rt'或'nrt'，当前值为{self.crypoType}")

    def _drawOuterFrame(self):
        '''绘制外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawText(self):
        '''绘制文字'''

        text = f"至{CADColor.colored(self.devPnum)} {CADColor.colored(self.devPname)}\n"
        text += "纵向加密认证装置\n"
        text += self._getCrypoTypeText()
        
        self.addMtext(
            textContent=text,
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(
                self.PORT_BOX_WIDTH + self.DEVICE_BODY_WIDTH / 2,
                self.HEIGHT / 2
            ),
            style="gedi",
            attachment=5
        )

    def _getCrypoTypeText(self) -> str:
        '''获取加密设备类型文字'''

        if self.crypoType == self.CRYPO_TYPE_RT:
            return self.RT_TYPE_TEXT

        return self.NRT_TYPE_TEXT

    def frontPoint(self) -> Vec2:
        '''返回前连接点绝对坐标'''

        return self.insertPoint + self._frontPointLocal()

    def _frontPointLocal(self) -> Vec2:
        '''获取前连接点局部坐标'''

        portBoxInsertPoint = self._portBoxInsertPointLocal()

        return portBoxInsertPoint + Vec2(
            0,
            self.PORT_BOX_HEIGHT / 2
        )

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''插入纵向加密设备连接面板图'''

        return super().insertInto(layout, self.insertPoint)