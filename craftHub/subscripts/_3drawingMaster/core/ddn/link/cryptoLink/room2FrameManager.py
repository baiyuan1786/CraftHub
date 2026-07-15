##########################################################################################################
#   Description: 第二房间虚线框管理器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Optional

from ezdxf.math import Vec2

from ....common.graph import CADColor, CustomBlock
from ....common.graph import 灰色边框虚线


class Room2FrameManager:
    '''第二房间虚线框管理器'''

    FRAME_EXTEND_LEFT = 40
    FRAME_EXTEND_RIGHT = 36
    FRAME_EXTEND_TOP = 13
    FRAME_EXTEND_BOTTOM = 16
    FRAME_EXTEND_LEFT_MIN = 5

    TEXT_HEIGHT = 6
    TEXT_WIDTH_FACTOR = 4
    TITLE_OFFSET_Y = 2

    def __init__(self, room2Name: Optional[str]) -> None:
        """初始化第二房间虚线框管理器

        :param room2Name: 第二房间名称
        """

        self.room2Name = "" if room2Name is None else str(room2Name)
        self.leftBottom: Optional[Vec2] = None
        self.rightTop: Optional[Vec2] = None
        self.devCount = 0 # 设备数

    def recordPanel(
            self,
            insertPoint: Vec2,
            width: float,
            height: float
    ):
        '''记录第二房间设备边界'''

        leftBottom = insertPoint
        rightTop = insertPoint + Vec2(width, height)

        if self.leftBottom is None:
            self.leftBottom = leftBottom
            self.rightTop = rightTop
            return

        assert self.rightTop is not None

        self.leftBottom = Vec2(
            min(self.leftBottom.x, leftBottom.x),
            min(self.leftBottom.y, leftBottom.y)
        )

        self.rightTop = Vec2(
            max(self.rightTop.x, rightTop.x),
            max(self.rightTop.y, rightTop.y)
        )
        self.devCount += 1

    def drawInto(self, block: CustomBlock):
        '''绘制第二房间虚线框'''

        if self.leftBottom is None or self.rightTop is None:
            return
        
        # 第二房间边界
        extendLeft = self.FRAME_EXTEND_LEFT_MIN # self.FRAME_EXTEND_LEFT 左侧先不扩展
        if self.devCount > 1:
            extendLeft = self.FRAME_EXTEND_LEFT_MIN

        leftBottom = Vec2(
            self.leftBottom.x - extendLeft,
            self.leftBottom.y - self.FRAME_EXTEND_BOTTOM
        )

        rightTop = Vec2(
            self.rightTop.x + self.FRAME_EXTEND_RIGHT,
            self.rightTop.y + self.FRAME_EXTEND_TOP
        )

        width = rightTop.x - leftBottom.x
        height = rightTop.y - leftBottom.y

        block.addRectangle(
            width=width,
            height=height,
            line=灰色边框虚线(),
            insertPoint=leftBottom
        )

        block.addMtext(
            textContent=self.room2Name,
            textFontHeight=self.TEXT_HEIGHT,
            textWidth=max(width * 0.5, len(self.room2Name) * self.TEXT_WIDTH_FACTOR),
            textColor=CADColor.toIndex("ByBlock"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(
                leftBottom.x + width / 2,
                rightTop.y - self.TITLE_OFFSET_Y
            ),
            style="gedi",
            attachment=2
        )