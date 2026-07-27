##########################################################################################################
#   Description: 屏柜绘图器，主绘图器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from typing import Dict, List

from ezdxf.document import Drawing

from craftHub.tool import GLog

from ..reader import ReaderCabinet, DataUnitCabinet
from .substation import Cabinet_subplt


class Cabinet_mainplt:
    '''屏柜主绘图器'''

    def __init__(
            self,
            doc: Drawing,
            config: Dict
    ) -> None:
        """初始化屏柜主绘图器

        :param doc: CAD文档
        :param config: 配置字典
        """

        self.doc = doc
        self.config = config

        self.excelPath = config["src"]
        self.sheetName = config["srcSheet"]

        self.dataUnitList: List[DataUnitCabinet] = []
        self.dataUnitFullList: List[DataUnitCabinet] = []
        self.drawerList: List[Cabinet_subplt] = []

        self._loadData()

    def _loadData(self):
        '''读取数据'''

        errorList = []

        try:
            reader = ReaderCabinet(
                excelPath=self.excelPath,
                sheetName=self.sheetName
            )
        except Exception as e:
            raise ValueError(f"读取器 | 加载错误: {e}")

        for index, data in enumerate(reader):
            try:
                self.dataUnitFullList.append(data)
                data.typeCheck()
                self.dataUnitList.append(data)
            except Exception as e:
                errorList.append(
                    f"解析表格 | 解析第{int(index) + 2}行 "
                    f"{data.get('substationName')}时出错: {str(e)}"
                )

        for err in errorList:
            GLog.logInfo(f"{GLog.RED}{err}{GLog.END}")

        self.dataUnitList.sort(key=lambda data: data.get("drawOrder"))
        self.dataUnitFullList.sort(key=lambda data: data.get("drawOrder"))

        GLog.logInfo(
            f"{GLog.GREEN}屏柜绘图器 | 共解析成功 {len(self.dataUnitList)} 条数据{GLog.END}"
        )

    def plot(self):
        '''执行批量绘图'''

        success = 0
        errorList = []
        self.drawerList = []

        if not self.dataUnitList:
            GLog.logInfo("没有数据可绘制")
            return

        for index, data in enumerate(self.dataUnitList, start=1):
            if not data.get("build"):
                continue

            try:
                GLog.logInfo(
                    f"{GLog.BLUE}屏柜绘图器 | 绘制第 "
                    f"'{index}/{len(self.dataUnitList)}' 个屏柜: "
                    f"{data.get('substationName')}{GLog.END}"
                )

                drawer = Cabinet_subplt(
                    doc=self.doc,
                    data=data
                )

                self.drawerList.append(drawer)
                drawer.plot()
                drawer.insertInto(
                    self.doc.modelspace(),
                    data.drawOrderToOffset()
                )

                success += 1

            except Exception as e:
                errorList.append(f"{data.get('substationName')} | {str(e)}")

        if errorList:
            GLog.logInfo(
                f"{GLog.RED}屏柜绘图器 | 共产生了{len(errorList)}个错误{GLog.END}"
            )
            for err in errorList:
                GLog.logInfo(f"{GLog.RED}屏柜绘图器 | {err}{GLog.END}")
        else:
            GLog.logInfo(f"{GLog.GREEN}屏柜绘图器 | 没有发生错误{GLog.END}")

        GLog.logInfo(
            f"{GLog.BLUE}屏柜绘图器 | 绘制完成, 共完成 {success} 个屏柜绘制{GLog.END}"
        )