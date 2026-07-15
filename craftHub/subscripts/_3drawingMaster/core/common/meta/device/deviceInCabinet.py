##########################################################################################################
#   Description: 机柜中设备面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph.shape import TextBox
from ...graph.line import 本期新增设备, 现有设备, 普通红色线02
from ...graph.color import CADColor

from ..unit import U2CM

from ezdxf.document import Drawing
from ezdxf.math import Vec2
from typing import Optional, Literal

DeviceType = Literal[
    "normal",
    "new",
    "remove",
    "replace",
    "replaced",
    "dropped"
]

class DeviceInCabinet(TextBox):
    '''屏柜面板图中的设备'''

    INSIDE_START_POINT = Vec2(5.9, 5.8179)
    WIDTH = 48.2

    NEW_LINE_TYPES = {"new", "replaced"}
    RED_TEXT_TYPES = {"remove", "replace"}
    NOTE_TYPES = {"remove", "replace", "replaced"}

    TYPE_TEXT_DICT = {
        "remove": "拆除",
        "replace": "替换"
    }

    def __init__(self,
                 doc: Drawing,
                 name: str,
                 heightU: int,
                 altitudeU: int,
                 devType: DeviceType = "normal",
                 replacedDeviceName: Optional[str] = None) -> None:
        """设备初始化

        :param doc: 绘图文件
        :param name: 设备名称
        :param heightU: 设备高度，按U计算
        :param altitudeU: 设备海拔，按U计算
        :param devType: 设备类型
        :param replacedDeviceName: 替代设备名称
        """

        self.name = name
        self.heightU = heightU
        self.devType = devType
        self.replacedDeviceName = replacedDeviceName
        self.altitudeU = altitudeU

        if self.startU < 0 or self.endU > 47:
            raise ValueError(f"设备位置脱离了屏柜: {self}")

        self._checkTextLineNum()

        super().__init__(
            doc=doc,
            boxHeight=U2CM(self.heightU),
            boxWidth=self.WIDTH,
            boxLine=self._boxLine(),
            textContent=self.name,
            textColor=self._textColor(),
            textFontHeight=self._textFontHeight(),
            textLineSpacingDistance=1,
            textStyle="天联"
        )

    def _checkTextLineNum(self):
        '''检查文字行数是否超过设备U数'''

        textLineNum = len(self.name.split("\n"))

        if textLineNum > self.heightU:
            raise ValueError(f"文本行数大于U数, 请调整: {repr(self.name)}")

    def _textFontHeight(self):
        '''文字大小'''

        fontHeight = 2.8955
        maxNameLineLen = max(len(v) for v in self.name.split("\n"))

        if self.heightU < 2 and maxNameLineLen > 15:
            fontHeight *= 0.7

        return fontHeight

    def _boxLine(self):
        '''文本框线型'''

        if self.devType in self.NEW_LINE_TYPES:
            return 本期新增设备()

        return 现有设备()

    def _textColor(self):
        '''文本颜色'''

        if self.devType in self.RED_TEXT_TYPES:
            return CADColor.toIndex("红色")

        return CADColor.toIndex("白色")

    def _noteText(self) -> Optional[str]:
        '''设备状态说明文字'''

        if self.devType == "replaced":
            return f"替换设备 \n'{CADColor.colored(self.replacedDeviceName)}'"

        return self.TYPE_TEXT_DICT.get(self.devType)

    @property
    def startU(self):
        '''设备开始U数'''
        return self.altitudeU

    @property
    def endU(self):
        '''设备结束U数'''
        return self.altitudeU + self.heightU

    def isCrashed(self, otherDevice):
        '''是否与另一设备位置冲突'''
        if not isinstance(otherDevice, DeviceInCabinet):
            return NotImplemented
        
        return not (
            otherDevice.startU >= self.endU
            or otherDevice.endU <= self.startU
        )

    def __str__(self):
        return f"'{self.name}', [{self.startU}, {self.endU}]"

    def _addTypeNote(self):
        '''绘制设备类型说明'''

        noteText = self._noteText()

        if noteText is None:
            return

        startPoint = Vec2(54.1, 0)
        endPoint = startPoint + Vec2(0, U2CM(self.heightU))

        startPoint2 = startPoint + Vec2(8.2, 0)
        endPoint2 = endPoint + Vec2(8.2, 0)

        midPoint = (startPoint2 + endPoint2) / 2
        midPointUp = midPoint + Vec2(0, 1.1)
        midPointDown = midPoint - Vec2(0, 1.1)
        midPointRight = midPoint + Vec2(2, 0)

        points = [
            startPoint,
            startPoint + Vec2(8.2, 0),
            midPointDown,
            midPointRight,
            midPointUp,
            endPoint2,
            endPoint
        ]

        self.addPolyLine(points, 普通红色线02())

        self.addMtext(
            textContent=noteText,
            textColor=CADColor.toIndex("byblock"),
            textFontHeight=3,
            textWidth=35,
            attachment=4,
            textLineSpacingDistance=1,
            insertPoint=midPointRight + Vec2(1, 0),
            style="gedi"
        )

    def insertInto(self, layout):
        """创建文本框块，将此块插入到屏柜空间中"""

        self._addTypeNote()

        super().insertInto(
            layout=layout,
            insertPoint=self.INSIDE_START_POINT + Vec2(0, U2CM(self.altitudeU))
        )