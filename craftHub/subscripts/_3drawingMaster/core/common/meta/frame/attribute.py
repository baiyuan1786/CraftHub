##########################################################################################################
#   Description: 增强属性
#   Authors:     BaiYuan <V:gzq395642104>
#########################################################################################################
from ezdxf.document import Drawing
from ezdxf.entities.insert import Insert
from ezdxf.layouts.blocklayout import BlockLayout
from ezdxf.layouts.layout import Modelspace
from ezdxf.math import Vec2

from craftHub.tool import GLog

class Attribute:
    '''增强属性, 增强属性是Insert类的属性'''

    DEFAULT_OFFSET = Vec2(0, 0)

    def __init__(
            self,
            tag: str,
            text: str,
            height: float,
            width: float,
            halign: int = 0,
            style: str = "gedi",
            offset: Vec2 | None = None
    ) -> None:
        """增强属性初始化

        :param tag: 增强属性tag
        :param text: 增强属性文本
        :param height: 高度因子
        :param width: 宽度因子
        :param halign: 水平对齐参数, 0 左对齐, 1 居中, 2 右对齐, 3 两端对齐, 4 中央对齐, 5 适合模式
        :param style: 文字样式
        :param offset: 属性插入偏移，用于修正部分增强属性的异常偏移
        """

        self.tag = tag
        self.text = text
        self.height = height
        self.width = width
        self.halign = halign
        self.style = style
        self.offset = self.DEFAULT_OFFSET if offset is None else offset

    def _attDefLocate(self, insert: Insert) -> Vec2 | None:
        """获取ATTDEF的预设位置

        :param insert: 某个插入对象
        :return: ATTDEF预设位置
        """

        blockLayout = insert.block()
        if blockLayout is None:
            return None

        for attdef in blockLayout.attdefs():
            if attdef.dxf.tag != self.tag:
                continue

            if not attdef.dxf.hasattr("insert"):
                continue

            return Vec2(attdef.dxf.insert)

        return None

    def _insertLocate(self, insert: Insert) -> Vec2:
        """获取块参照插入位置

        :param insert: 某个插入对象
        :return: 块参照插入位置
        """

        return Vec2(insert.dxf.insert)

    def add_attrib_autoLocate(self, insert: Insert):
        '''自动寻址插入增强属性'''

        attDefPoint = self._attDefLocate(insert=insert)
        if attDefPoint is None:
            # raise ValueError(f"模板中没有属性 '{self.tag}'")
            GLog.logInfo(f"模板中没有属性 '{self.tag}' 跳过插入")
            return

        insertBasePoint = self._insertLocate(insert=insert)
        attribInsertPoint = attDefPoint + insertBasePoint + self.offset

        insert.add_attrib(
            tag=self.tag,
            text=self.text,
            insert=attribInsertPoint,
            dxfattribs={
                "height": self.height,
                "width": self.width,
                "style": self.style,
                "halign": self.halign,
            }
        ).set_placement(attribInsertPoint)