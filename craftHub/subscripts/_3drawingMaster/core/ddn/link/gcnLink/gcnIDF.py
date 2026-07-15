##########################################################################################################
#   Description: GCN网IDF连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Any

from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from ....common.graph import CADColor, NewBlock, 现有设备


class GCNIDFConnectionPanel(NewBlock):
    '''GCN网IDF连接面板图'''

    WIDTH = 21.3
    HEIGHT = 11

    TEXT_HEIGHT = 3.2
    TEXT_WIDTH_FACTOR = 0.9
    TEXT_STYLE = "gedi"

    DEVICE_NAME = "IDF配线单元"

    DEV_NUM_TEXT_OFFSET_Y = 3.2
    DEV_NAME_TEXT_OFFSET_Y = 7.2

    @classmethod
    def insertPointFromFrontPoint(
            cls,
            insertX: float,
            frontPoint: Vec2
    ) -> Vec2:
        '''根据前连接点反算插入点'''

        return Vec2(insertX, frontPoint.y - cls.HEIGHT / 2)

    def __init__(
            self,
            doc: Drawing,
            devNum: str,
            insertPoint: Vec2,
            devName: str = DEVICE_NAME
    ) -> None:
        """初始化GCN网IDF连接面板图

        :param doc: 文档
        :param devNum: 设备号
        :param insertPoint: 插入点
        :param devName: 设备名称
        """

        super().__init__(doc=doc)

        self.doc = doc
        self.devNum = str(devNum)
        self.devName = str(devName)
        self.insertPoint = insertPoint

        self._build()

    def _build(self):
        '''构建面板图'''

        self._drawOutline()
        self._drawTexts()

    def _drawOutline(self):
        '''绘制外框'''

        self.addRectangle(
            width=self.WIDTH,
            height=self.HEIGHT,
            line=现有设备(),
            insertPoint=Vec2(0, 0)
        )

    def _drawTexts(self):
        '''绘制文字'''

        self.addMtext(
            textContent=CADColor.colored(self.devNum, "红色"),
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=self.WIDTH * self.TEXT_WIDTH_FACTOR,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.WIDTH / 2, self.HEIGHT - self.DEV_NUM_TEXT_OFFSET_Y),
            style=self.TEXT_STYLE,
            attachment=2
        )

        self.addMtext(
            textContent=self.devName,
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=self.WIDTH * self.TEXT_WIDTH_FACTOR,
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(self.WIDTH / 2, self.HEIGHT - self.DEV_NAME_TEXT_OFFSET_Y),
            style=self.TEXT_STYLE,
            attachment=2
        )

    def frontPoint(self) -> Vec2:
        '''返回前连接点，取左侧中点绝对坐标'''

        return self.insertPoint + Vec2(0, self.HEIGHT / 2)

    def afterPoint(self) -> Vec2:
        '''返回后连接点，取右侧中点绝对坐标'''

        return self.insertPoint + Vec2(self.WIDTH, self.HEIGHT / 2)

    def insertInto(
            self,
            layout: BlockLayout | Modelspace | Any
    ):
        '''插入到布局中'''

        return super().insertInto(layout, self.insertPoint)