##########################################################################################################
#   Description: 图形块类
#                实现块的工厂化创建
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..line import 本期新增机柜, 本期占用机柜, 本期新增设备, 现有设备
from ..line import 本期新增电源线, 本期新增跳纤, 本期新增网线
from ..line import 现有互联六类电缆, 现有互联光缆, 逻辑连线示意, 普通黄色线, 普通红色线
from ..line import Line
from ..color import CADColor

from craftHub.tool import GLog

from ezdxf.math import Vec2
from ezdxf.document import Drawing
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace

from pathlib import Path
from typing import  Optional, Any, Literal, List

class CustomBlock:
    '''自定义块布局块'''
    blockCount = 0
        
    def __init__(
            self,
            doc: Drawing,
            blockName: Optional[str] = None,
            allowExisted: bool = False,
            allowCreate: bool = True
    ) -> None:
        """创建自定义块

        :param doc: 文档
        :param blockName: 块名，设置为None表示自动命名
        :param allowExisted: 是否允许调用已存在块
        :param allowCreate: 是否允许创建新块
        """

        self.doc = doc
        self.isNewBlock = False

        if blockName is None:
            if not allowCreate:
                raise ValueError("不允许创建新块时，blockName 不能为 None")

            blockName = f"Block_{CustomBlock.blockCount}"

            while blockName in doc.blocks:
                CustomBlock.blockCount += 1
                blockName = f"Block_{CustomBlock.blockCount}"

        try:
            if blockName not in doc.blocks:
                if not allowCreate:
                    raise FileNotFoundError(f"块不存在，不允许创建新块: '{blockName}'")

                self.block = doc.blocks.new(name=blockName)
                self.isNewBlock = True
                GLog.logInfo(f"'{blockName}' | 创建了新块")

            elif allowExisted:
                self.block = doc.blocks.get(blockName)
                self.isNewBlock = False
                GLog.logInfo(f"'{blockName}' | 调用了已有块")

            else:
                raise FileExistsError(f"块已存在，不允许调用该块: '{blockName}'")

        except Exception as error:
            raise Exception(f"创建或获取块失败: {str(error)}")
        
    @classmethod
    def setBlockCount(cls, blockCount: int):
        '''设置块计数器'''
        assert isinstance(blockCount, int)
        cls.blockCount = blockCount
 
    def addRectangle(self,
                    width: float,
                    height: float,
                    line: Line,
                    insertPoint: Vec2 = Vec2(0, 0),
                    isFill: bool = False
                    ):
        """向块中添加矩形

        :param insertPoint: 起始点, 选作左下角点
        :param width: 宽度
        :param height: 高度
        :param line: 绘图线格式
        :param isFill: 是否增加ANSI31红色斜线填充
        """

        points = [
            insertPoint,                        # 左下
            insertPoint + Vec2(width, 0),       # 右下
            insertPoint + Vec2(width, height),  # 右上
            insertPoint + Vec2(0, height)       # 左上
        ]

        if isFill:
            hatch = self.block.add_hatch()

            hatch.set_pattern_fill(
                name="ANSI31",
                scale=1.0,
                angle=0,
                color=CADColor.toIndex("红色")
            )

            hatch.paths.add_polyline_path(
                [
                    (point.x, point.y)
                    for point in points
                ],
                is_closed=True
            )

        # 创建矩形边框
        self.block.add_lwpolyline(
            points=points,
            close=True,
            dxfattribs=line.attributes
        )
        
    def addMtext(self,
                 textContent: str,
                 textFontHeight: float,
                 textWidth: float,
                 textColor: int = CADColor.toIndex("白色"),
                 textLineSpacingDistance: float = 1,
                 insertPoint: Vec2 = Vec2(0, 0),
                 style: str = "Standard",
                 attachment: int = 5,
                 rotation: int = 0):
        """插入多行文本框

        :param textContent: 文本内容
        :param textFontHeight: 文本字号
        :param textWidth: 文本框宽度
        :param textColor: 文本颜色
        :param textLineSpacingDistance: 文本框行间距比例因子
        :param insertPoint: 插入点, 一般选择中心位置插入, 需计算中心位置
        :param style: 字体样式
        :param attachment: 对齐方式, 1左上 2 上中 3 右上, 4 左中, 5 正中, 6 右中, 7 左下, 8 下中, 9 右下 
        :param rotation: 逆时针旋转角度
        """        
        
        return self.block.add_mtext(
            text = textContent,
            dxfattribs={
                'insert': insertPoint,                                  # 插入点
                'char_height': textFontHeight,                          # 字符高度
                'width': textWidth,                                     # 文本框宽度
                'attachment_point': attachment,                         # 中心对齐
                'color': textColor,                                     # 颜色
                'layer': "文本",                                        # 图层
                'style': style,                                        # 样式
                'line_spacing_factor': textLineSpacingDistance,         # 行间距设置（根据ezdxf版本）

                # 其他可能的属性
                'line_spacing_style': 1,  # 1 = 精确间距
                "rotation": rotation,
            }
        )
        
    def addLine(self,
                startPoint: Vec2,
                endPoint: Vec2,
                line: Line,
                text: Optional[str] = None,
                note: Optional[str] = None,
                num: int = 1,
                offsetOrient: Literal["x", "y"] = "x",
                fork: bool = False,
                arrow: bool = False,
                line2: Optional[Line] = None,
                line2StartOffset: Optional[Vec2] = None,
                polyLine: bool = False,
                polyLineOrient: Literal["x", "y"] = "x",
                polyLineMiddleOffset: Optional[Vec2] = None,
                polyLineFirstLineLen: Optional[float] = None):
        """画一条直线或折线

        :param startPoint: 起点
        :param endPoint: 终点
        :param line: 线类型
        :param text: 线上的文本说明, defaults to None
        :param note: 线注释, defaults to None
        :param num: 并列线条数, defaults to 1
        :param offsetOrient: 并列线条数偏移, defaults to "x"
        :param fork: 绘制线时带有红色×
        :param arrow: 线末端将带有箭头
        :param line2: 第二条线的线型, 仅当num指定为2时有用
        :param line2StartOffset: 第二条线起点偏置，仅影响起点
        :param polyLine: 是否绘制折线, defaults to False
        :param polyLineOrient: 多段线偏移方向, 影响折线往哪个方向拐
        :param polyLineMiddleOffset: 多段线中点偏移
        :param polyLineFirstLineLen: 多段线第一段线长度
        """

        offsetDict = {
            "x": Vec2(1, 0),
            "y": Vec2(0, 1)
        }

        centerPoint = (startPoint + endPoint) / 2
        offsetVector = offsetDict[offsetOrient]

        def drawPolyline(polyLineOrient: Literal["x", "y"] = "x",
                        polyLineMiddleOffset: Optional[Vec2] = None):
            """绘制折线"""

            if not polyLine:
                return False

            if polyLineMiddleOffset is None:
                polyLineMiddleOffset = Vec2(0, 0)

            if polyLineOrient == "x":
                if polyLineFirstLineLen is not None:
                    middleX = startPoint.x + polyLineFirstLineLen
                else:
                    middleX = (startPoint.x + endPoint.x) / 2

                pointList = [
                    startPoint,
                    Vec2(middleX, startPoint.y) + polyLineMiddleOffset,
                    Vec2(middleX, endPoint.y) + polyLineMiddleOffset,
                    endPoint
                ]
            else:
                if polyLineFirstLineLen is not None:
                    middleY = startPoint.y + polyLineFirstLineLen
                else:
                    middleY = (startPoint.y + endPoint.y) / 2

                pointList = [
                    startPoint,
                    Vec2(startPoint.x, middleY) + polyLineMiddleOffset,
                    Vec2(endPoint.x, middleY) + polyLineMiddleOffset,
                    endPoint
                ]

            drawPolylineByPoints(pointList)
            return True

        def drawPolylineByPoints(pointList: List[Vec2]):
            """根据点列表绘制一条或多条并列折线"""

            # 遍历多条线
            for lineIndex in range(num):
                currentLine = line

                if lineIndex == 1 and line2 is not None:
                    currentLine = line2

                currentOffset = offsetVector * lineIndex

                if lineIndex == 1 and line2StartOffset is not None:
                    firstPointOffset = currentOffset + line2StartOffset
                else:
                    firstPointOffset = currentOffset

                # 整体偏移
                currentPointList = [
                    point + currentOffset
                    for point in pointList
                ]
                
                # 拐点偏移
                middleOffset = Vec2(-1, 0)  if polyLineOrient == "x" else Vec2(0, 1)
                for pointIndex, point in enumerate(currentPointList):
                    if pointIndex == 0 or pointIndex == len(currentPointList) - 1:
                        continue
                    currentPointList[pointIndex] += middleOffset * lineIndex

                # 起始点偏移
                currentPointList[0] = pointList[0] + firstPointOffset

                self.block.add_lwpolyline(
                    points=currentPointList,
                    dxfattribs=currentLine.attributes
                )
                
            # 插入文本
            if text is not None:
                self.addMtext(
                    textContent=text,
                    textFontHeight=2.16,
                    textWidth=len(text) * 4,
                    style="GEDITXT",
                    insertPoint= (pointList[-1] + pointList[-2]) / 2 + Vec2(0, 1),
                    attachment = 8
                )

            # 多段线标记
            if num > 1:
                markPoint = pointList[2] + (pointList[3] - pointList[2]) / 4 + offsetVector * ((num - 1) / 2)

                if offsetOrient == "x":
                    self.block.add_ellipse(
                        center=markPoint,
                        major_axis=Vec2(2.5936, 0),
                        ratio=0.2708
                    )
                else:
                    self.block.add_ellipse(
                        center=markPoint,
                        major_axis=Vec2(0, 2.5936),
                        ratio=0.2708
                    )

                self.addNote(point=markPoint, text=f"{num}条")


        def drawBaseLine():
            """绘制基础线"""
            self.block.add_lwpolyline(
                points=[
                    startPoint,
                    endPoint
                ],
                dxfattribs=line.attributes
            )

        def getParallelLine(lineIndex: int) -> Line:
            """获取并列线线型"""

            if lineIndex == 1 and line2 is not None:
                return line2

            return line

        def getParallelLineStartOffset(lineIndex: int) -> Vec2:
            """获取并列线起点偏移"""

            if lineIndex == 1 and line2StartOffset is not None:
                return line2StartOffset

            return Vec2(0, 0)

        def drawParallelLines():
            """绘制并列线，并添加线条数量标记"""

            if num <= 1:
                return

            middleOffset = Vec2(2, 0) if offsetOrient == "y"  else Vec2(0, 2)
            for lineIndex in range(1, num):
                self.addLine(
                    startPoint=startPoint + offsetVector * lineIndex + getParallelLineStartOffset(lineIndex),
                    endPoint=endPoint + offsetVector * lineIndex,
                    line=getParallelLine(lineIndex),
                    polyLineMiddleOffset = middleOffset * lineIndex,
                    polyLine = polyLine
                    
                )

            markPoint = startPoint + (endPoint - startPoint) / 4 + offsetVector * ((num - 1) / 2)

            if offsetOrient == "x":
                self.block.add_ellipse(
                    center=markPoint,
                    major_axis=Vec2(2.5936, 0),
                    ratio=0.2708
                )
            else:
                self.block.add_ellipse(
                    center=markPoint,
                    major_axis=Vec2(0, 2.5936),
                    ratio=0.2708
                )

            self.addNote(point=markPoint, text=f"{num}条")

        def drawCenterNote():
            """绘制线中间的注释"""
            if note is None:
                return

            self.addNote(
                point=centerPoint,
                text=note
            )

        def drawLineText(text: Optional[str]):
            """绘制线上的文本说明"""
            if text is None:
                return

            insertPoint = centerPoint + Vec2(0, 2) * num

            self.addMtext(
                textContent=text,
                textFontHeight=2.16,
                textWidth=len(text) * 4,
                style="GEDITXT",
                insertPoint=insertPoint
            )

        def drawFork():
            """在线中心绘制红色叉号"""
            if not fork:
                return

            self.addLine(
                startPoint=centerPoint + Vec2(-1.5, 1.5),
                endPoint=centerPoint - Vec2(-1.5, 1.5),
                line=普通红色线()
            )

            self.addLine(
                startPoint=centerPoint + Vec2(1.5, 1.5),
                endPoint=centerPoint - Vec2(1.5, 1.5),
                line=普通红色线()
            )

        def drawArrow():
            """在线末端绘制箭头"""
            if not arrow:
                return

            angle = (endPoint - startPoint).angle
            arrowLine1 = Vec2(-3.6, 1.59).rotate(angle)
            arrowLine2 = Vec2(-3.6, -1.59).rotate(angle)

            self.addLine(
                startPoint=endPoint,
                endPoint=endPoint + arrowLine1,
                line=line
            )

            self.addLine(
                startPoint=endPoint,
                endPoint=endPoint + arrowLine2,
                line=line
            )

        if drawPolyline(polyLineOrient, polyLineMiddleOffset):
            return

        drawBaseLine()
        drawParallelLines()
        drawCenterNote()
        drawLineText(text=text)
        drawFork()
        drawArrow()
            
    
    def addPolyLine(self, points: List[Vec2], line: Line):
        '''添加多段线'''
        self.block.add_lwpolyline(
            points = points,
            dxfattribs = line.attributes
        )

    def addNote(self,
                point: Vec2,
                text: str):
        """增加注释, 注释由两条线和一个文字构成

        :param point: 注释点
        :param text: 说明文字
        """
        
        point1 = Vec2(2, -4.5) + point # 往下画
        point2 = (Vec2(6, 0) * len(text) / 2 ) + point1
        
        points = [
            point,
            point1,
            point2                   
        ]

        self.block.add_lwpolyline(
            points = points,
            dxfattribs = 现有设备().attributes
        )
        
        self.addMtext(textContent = text,
                      textFontHeight = 2.16,
                      textWidth = len(text) * 3,
                      style = "GEDITXT",
                      insertPoint = (point1 + point2) / 2 + Vec2(0, 2)
                      )        

    def insertInto(self,
               layout: BlockLayout | Modelspace | Any,
               insertPoint: Optional[Vec2] = None):
        """将当前布局添加到上层布局，注意必须输入布局

        :param layout: 插入的布局对象，建议使用块来管理多图形结构
        :param insertPoint: 插入点, 如果不指定则使用self.boxBasePoinit
        """        

        if insertPoint is None:
            insertPoint = Vec2(0, 0)

        if isinstance(layout, CustomBlock):
            return layout.block.add_blockref(self.block.name, insertPoint)
        
        return layout.add_blockref(self.block.name, insertPoint)

