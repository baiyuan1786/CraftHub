##########################################################################################################
#   Description: 纵向加密设备连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any, Literal

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from .....common.graph import CADColor, NewBlock
from .....common.graph import 现有设备


class CDConnectionPanel(NewBlock):
    '''纵向加密设备连接面板图'''

    WIDTH = 40
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

    def __init__(
            self,
            doc: Drawing,
            devPnum: str,
            devPname: str,
            crypoType: Literal["rt", "nrt"],
            insertPoint: Vec2
    ) -> None:
        """纵向加密设备连接面板图初始化

        :param doc: CAD文档
        :param devPnum: 设备屏位编号，例如40P
        :param devPname: 设备屏位名称，例如ddn设备屏
        :param crypoType: 加密设备类型，rt表示实时，nrt表示非实时
        :param insertPoint: 插入点，仍然表示设备框左下角点
        """

        super().__init__(doc)

        self.devPnum = devPnum
        self.devPname = devPname
        self.crypoType = crypoType
        self.insertPoint = insertPoint

        self._checkCrypoType()
        self._drawOuterFrame()
        self._drawText()

    @classmethod
    def insertPointFromFrontPoint(
            cls,
            frontPoint: Vec2,
            crypoType: Literal["rt", "nrt"]
    ) -> Vec2:
        '''根据前连接点反算设备框左下角插入点'''

        if crypoType == cls.CRYPO_TYPE_RT:
            return frontPoint - Vec2(0, cls.FRONT_POINT_RT_Y)

        if crypoType == cls.CRYPO_TYPE_NRT:
            return frontPoint - Vec2(0, cls.FRONT_POINT_NRT_Y)

        raise ValueError(f"crypoType必须是'rt'或'nrt'，当前值为{crypoType}")

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

        self._drawLine1()
        self._drawLine2()
        self._drawLine3()

    def _drawLine1(self):
        '''绘制第一行文字'''

        text = f"至{CADColor.colored(self.devPnum)} {CADColor.colored(self.devPname)}"

        self.addMtext(
            textContent=text,
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.TEXT_LINE_1_Y),
            style="gedi",
            attachment=5
        )

    def _drawLine2(self):
        '''绘制第二行文字'''

        self.addMtext(
            textContent="纵向加密认证装置",
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.TEXT_LINE_2_Y),
            style="gedi",
            attachment=5
        )

    def _drawLine3(self):
        '''绘制第三行文字'''

        self.addMtext(
            textContent=self._getCrypoTypeText(),
            textFontHeight=self.TEXT_FONT_HEIGHT,
            textWidth=self.TEXT_WIDTH,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=self.TEXT_LINE_SPACING_DISTANCE,
            insertPoint=Vec2(self.WIDTH / 2, self.TEXT_LINE_3_Y),
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

        if self.crypoType == self.CRYPO_TYPE_RT:
            return self.insertPoint + Vec2(0, self.FRONT_POINT_RT_Y)

        return self.insertPoint + Vec2(0, self.FRONT_POINT_NRT_Y)

    def insertInto(self, layout: BlockLayout | Modelspace | Any):
        '''插入纵向加密设备连接面板图'''

        return super().insertInto(layout, self.insertPoint)