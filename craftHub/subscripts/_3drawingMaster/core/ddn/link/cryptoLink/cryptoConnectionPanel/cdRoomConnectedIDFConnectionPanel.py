##########################################################################################################
#   Description: 纵向加密机房互联IDF连接面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Literal, Optional

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from .cryptoIDFconnectionPanel import CDIDFConnectionPanel

class CDroomConnectedIDFConnectionPanel(CDIDFConnectionPanel):
    '''纵向加密机房互联IDF连接面板图'''

    DEVICE_NAME = "机房互联IDF配线单元"

    @classmethod
    def insertPointFromFrontPoints(
            cls,
            insertX: float,
            rtLinkPoint: Vec2,
            nrtLinkPoint: Vec2,
            direction: Literal["left", "right"] = "left"
    ) -> Vec2:
        '''根据实时/非实时接入点反算机房互联IDF插入点'''

        cls._checkDirection(direction)

        if direction == cls.DIRECTION_LEFT:
            return CDIDFConnectionPanel.insertPointFromFrontPoints(
                insertX=insertX,
                rtLinkPoint=rtLinkPoint,
                nrtLinkPoint=nrtLinkPoint,
                direction=direction
            )

        rtInsertY = rtLinkPoint.y - cls.HEIGHT / 2
        nrtInsertY = nrtLinkPoint.y - cls.HEIGHT / 2

        if abs(rtInsertY - nrtInsertY) > cls.ALIGN_TOLERANCE:
            raise ValueError(
                "无法保证右侧机房互联IDF两个接入点同时水平连接: "
                f"rtInsertY={rtInsertY}, nrtInsertY={nrtInsertY}, "
                f"rtLinkPoint={rtLinkPoint}, nrtLinkPoint={nrtLinkPoint}"
            )

        return Vec2(insertX, (rtInsertY + nrtInsertY) / 2)

    def __init__(
            self,
            doc: Drawing,
            devNum: str,
            portR: Optional[str],
            portNR: Optional[str],
            insertPoint: Vec2,
            isCutBusiness: bool = False,
            direction: Literal["left", "right"] = "left"
    ) -> None:
        """纵向加密机房互联IDF连接面板图初始化

        :param doc: CAD文档
        :param devNum: 设备号
        :param portR: 实时纵向加密使用端口
        :param portNR: 非实时纵向加密使用端口
        :param insertPoint: 插入点
        :param isCutBusiness: 是否绘制业务断开标记
        :param direction: 端口朝向，left为左侧端口，right为右侧端口
        """

        super().__init__(
            doc=doc,
            devNum=devNum,
            devName=self.DEVICE_NAME,
            portR=portR,
            portNR=portNR,
            insertPoint=insertPoint,
            isCutBusiness=isCutBusiness,
            direction=direction
        )

    def _leftMiddleLocal(self) -> Vec2:
        '''获取方框左中点局部坐标'''

        return Vec2(0, self.HEIGHT / 2)

    def _rightMiddleLocal(self) -> Vec2:
        '''获取方框右中点局部坐标'''

        return Vec2(self.WIDTH, self.HEIGHT / 2)

    def RTPointFront(self) -> Vec2:
        '''返回实时纵向加密端口前点绝对坐标'''

        if self.direction == self.DIRECTION_RIGHT:
            return self.insertPoint + self._leftMiddleLocal()

        return super().RTPointFront()

    def NRTPointFront(self) -> Vec2:
        '''返回非实时纵向加密端口前点绝对坐标'''

        if self.direction == self.DIRECTION_RIGHT:
            return self.insertPoint + self._leftMiddleLocal()

        return super().NRTPointFront()

    def RTPointAfter(self) -> Vec2:
        '''返回实时纵向加密端口后点绝对坐标'''

        if self.direction == self.DIRECTION_LEFT:
            return self.insertPoint + self._rightMiddleLocal()

        return super().RTPointAfter()

    def NRTPointAfter(self) -> Vec2:
        '''返回非实时纵向加密端口后点绝对坐标'''

        if self.direction == self.DIRECTION_LEFT:
            return self.insertPoint + self._rightMiddleLocal()

        return super().NRTPointAfter()