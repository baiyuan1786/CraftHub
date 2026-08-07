##########################################################################################################
#   Description: 屏柜面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..device.deviceInCabinet import DeviceInCabinet

from ...graph import NewBlock
from ...graph import 本期占用机柜, 本期新增机柜Panel, 现有设备, 普通黄色线, 灰色边框虚线, 普通白色粗实线
from ...graph import CADColor

from ..unit import U, U2CM

from typing import List
from ezdxf.document import Drawing
from ezdxf.math import Vec2

class CabinetPanel(NewBlock):
    '''屏柜面板图'''

    INSIDE_PANEL_WIDTH = 48.2       # 内屏柜尺寸
    PANEL_HEIGHT_U = 47             # 屏柜高度U
    EDGE_WHITE_LINE_LEN = 10.4041   # 边界白色线尺寸
    EDGE_YELLOW_LINE_LEN = 3        # 边界黄色线尺寸
    
    def __init__(self,
                 doc: Drawing,
                 pNum: str,
                 name: str, 
                 height: int = 220,
                 width: int = 60,
                 isNew: bool = False,
                 withGroudLine = False
                 ) -> None:
        """屏柜初始化

        :param doc:     绘图文件
        :param pNum:    P号, 例如1P
        :param name:    屏柜名, 例如路由器1屏
        :param height:  高, cm
        :param width:   宽, cm
        :param isNew:   面板图只有利旧和新增的区别
        :param withGroudLine: 绘制屏柜接地线
        """        
        
        super().__init__(doc = doc)
        
        self.pNum = pNum
        self.name = name
        self.height = height
        self.width = width
        self.isNew = isNew

        # 设备列表
        self.deviceList: List[DeviceInCabinet] = []
        
        # 下面绘制模板图形
        # 外圈矩形 / 外圈矩形坐标为零点坐标
        self.addRectangle(width = width, height = height, line = 本期新增机柜Panel() if self.isNew else 现有设备(), insertPoint = Vec2(0, 0))

        # 内圈矩形 / 内圈线型固定白色
        self.addRectangle(width = self.INSIDE_PANEL_WIDTH, height = U * self.PANEL_HEIGHT_U, line = 现有设备(), insertPoint = DeviceInCabinet.INSIDE_START_POINT)
        
        # 绘制双边线
        for i in range(self.PANEL_HEIGHT_U * 3 + 1):
            if i % 3 == 0:
                self.addLine(
                    startPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(0, i * U / 3),
                    endPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(-1 * self.EDGE_WHITE_LINE_LEN, i * U / 3),
                    line = 现有设备()
                )
                self.addLine(
                    startPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(0, i * U / 3) + Vec2(self.INSIDE_PANEL_WIDTH, 0),
                    endPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(self.EDGE_WHITE_LINE_LEN, i * U / 3) + Vec2(self.INSIDE_PANEL_WIDTH, 0),
                    line = 现有设备()
                )
                continue
            
            self.addLine(
                startPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(0, i * U / 3),
                endPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(-1 * self.EDGE_YELLOW_LINE_LEN, i * U / 3),
                line = 普通黄色线()
            )
            
            self.addLine(
                startPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(0, i * U / 3) + Vec2(self.INSIDE_PANEL_WIDTH, 0),
                endPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(self.EDGE_YELLOW_LINE_LEN, i * U / 3) + Vec2(self.INSIDE_PANEL_WIDTH, 0),
                line = 普通黄色线()
            )
    
        # 绘制U数文字
        for i in range(1, self.PANEL_HEIGHT_U + 1):
            if i % 5 == 0 or i == 1 or i == self.PANEL_HEIGHT_U:
                # 左侧
                self.addMtext(
                    textContent = f"{self.PANEL_HEIGHT_U + 1 - i}U",
                    textColor = CADColor.toIndex("白色"),
                    textFontHeight = 1.5486,
                    textWidth = 4.5,
                    attachment = 4,
                    textLineSpacingDistance = 4.24,
                    insertPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(-1 * self.EDGE_WHITE_LINE_LEN, 0) + Vec2(0, U / 2) + Vec2(0, U * (i - 1))
                )
                # 右侧
                self.addMtext(
                    textContent = f"{i}U",
                    textColor = CADColor.toIndex("白色"),
                    textFontHeight = 1.5486,
                    textWidth = 4.5,
                    attachment = 6,
                    textLineSpacingDistance = 4.24,
                    insertPoint = DeviceInCabinet.INSIDE_START_POINT + Vec2(self.INSIDE_PANEL_WIDTH, 0) +
                    Vec2(self.EDGE_WHITE_LINE_LEN, 0) + Vec2(0, U / 2) + Vec2(0, U * (i - 1))
                )
               
        # 绘制顶部文字
        self.addMtext(
            textContent = f"{self.pNum} {self.name}(本期新增)" if self.isNew else f"{self.pNum} {self.name}(本期利旧)",
            textColor = CADColor.toIndex("红色") if self.isNew else CADColor.toIndex("白色"),
            textFontHeight = 3.7641,
            textWidth = self.width * 2,
            attachment = 2,
            textLineSpacingDistance = 1,
            insertPoint = Vec2(self.width / 2, self.height + 7),
            style = "天联"
        )
        
        # 绘制底部文字
        self.addMtext(
            textContent = f"H{self.height * 10}*W{self.width * 10}mm (19英寸)",
            textColor = CADColor.toIndex("红色") if self.isNew else CADColor.toIndex("白色"),
            textFontHeight = 3.7641,
            textWidth = self.width * 2,
            attachment = 8,
            textLineSpacingDistance = 1,
            insertPoint = Vec2(self.width / 2, 0 - 7),
            style = "天联"
        )
        
        # 添加接地线绘制
        if withGroudLine:
            self._addGL()
        
    def _addGL(self):
        """添加设备接地线"""
        
        # 一根竖线三根横线组成
        y = DeviceInCabinet.INSIDE_START_POINT.y
        basePoint = Vec2(0, y)
        self.addLine(startPoint = basePoint, endPoint = basePoint - Vec2(11.6, 0), line = 普通白色粗实线())
        basePoint -= Vec2(11.6, 0)
        self.addLine(startPoint = basePoint, endPoint = basePoint - Vec2(0, 6), line = 普通白色粗实线())
        basePoint -= Vec2(0, 6)
        self.addLine(startPoint = basePoint - Vec2(2.7, 0), endPoint = basePoint + Vec2(2.7, 0), line = 普通白色粗实线())
        basePoint -= Vec2(0, 1)
        self.addLine(startPoint = basePoint - Vec2(2.1, 0), endPoint = basePoint + Vec2(2.1, 0), line = 普通白色粗实线())
        basePoint -= Vec2(0, 1)
        self.addLine(startPoint = basePoint - Vec2(1.3, 0), endPoint = basePoint + Vec2(1.3, 0), line = 普通白色粗实线())

    def addDevice(self,
                  device: DeviceInCabinet):
        """添加设备到屏柜中, 并立即完成绘图

        :param device: 新设备
        :param altitude: 放置位置
        """
        if device.devType == "dropped":
            return
        
        # 插入并完成冲突检测
        for d in self.deviceList:
            if d.isCrashed(device):
                raise ValueError(f"新设备 \'{device}\' 与已有设备 \'{d}\' 位置冲突")
        
        self.deviceList.append(device)
        
        # 插入本块
        device.insertInto(self.block)