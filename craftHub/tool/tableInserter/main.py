##########################################################################################################
#   Description: 表格插入器业务主函数
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import gc
import time

from pathlib import Path
from typing import List, Literal, Optional

import ezdxf
import psutil
import win32com.client

from craftHub.tool import GLog

from .cadLocator import CadLocator
from .data import Data
from .inserter import Inserter
from .reader import Reader
from .sizeAdjuster import SizeAdjuster


Attachment = Literal[2, 4, 6, 8]

InsertMode = Literal[
    "fixedPoint",
    "singleSign",
    "doubleSign"
]

InsertType = Literal[
    "OLE_EMBED",
    "xlPicture",
    "xlBitmap"
]

SizeMode = Literal[
    "fixedWidth",
    "fixedHeight",
    "maxSize"
]


class TableInserterMain:
    '''表格插入器业务主类'''

    INSERT_MODE_FIXED_POINT = "fixedPoint"
    INSERT_MODE_SINGLE_SIGN = "singleSign"
    INSERT_MODE_DOUBLE_SIGN = "doubleSign"

    SIZE_MODE_FIXED_WIDTH = SizeAdjuster.MODE_FIXED_WIDTH
    SIZE_MODE_FIXED_HEIGHT = SizeAdjuster.MODE_FIXED_HEIGHT
    SIZE_MODE_MAX_SIZE = SizeAdjuster.MODE_MAX_SIZE

    INSERT_TYPE_OLE_EMBED = Inserter.INSERT_TYPE_OLE_EMBED
    INSERT_TYPE_XL_PICTURE = Inserter.INSERT_TYPE_XL_PICTURE
    INSERT_TYPE_XL_BITMAP = Inserter.INSERT_TYPE_XL_BITMAP

    ATTACHMENT_TOP = 8
    ATTACHMENT_LEFT = 4
    ATTACHMENT_BOTTOM = 2
    ATTACHMENT_RIGHT = 6

    VALID_INSERT_MODE_SET = {
        INSERT_MODE_FIXED_POINT,
        INSERT_MODE_SINGLE_SIGN,
        INSERT_MODE_DOUBLE_SIGN
    }

    VALID_SIZE_MODE_SET = {
        SIZE_MODE_FIXED_WIDTH,
        SIZE_MODE_FIXED_HEIGHT,
        SIZE_MODE_MAX_SIZE
    }

    VALID_INSERT_TYPE_SET = {
        INSERT_TYPE_OLE_EMBED,
        INSERT_TYPE_XL_PICTURE,
        INSERT_TYPE_XL_BITMAP
    }

    VALID_ATTACHMENT_SET = {
        ATTACHMENT_TOP,
        ATTACHMENT_LEFT,
        ATTACHMENT_BOTTOM,
        ATTACHMENT_RIGHT
    }

    CAD_OPEN_RETRY_COUNT = 5
    CAD_OPEN_RETRY_INTERVAL_SECONDS = 1.0
    CAD_READY_WAIT_SECONDS = 2.0

    EXCEL_PROCESS_EXIT_WAIT_SECONDS = 2.0
    EXCEL_PROCESS_TERMINATE_TIMEOUT_SECONDS = 3.0

    TAG_PLACEHOLDER = "{tag}"

    def __init__(
            self,
            cadPath: Path,
            excelPath: Path,
            sheetName: str,
            insertMode: InsertMode,
            attachment1: Attachment = ATTACHMENT_TOP,
            sign2: Optional[str] = None,
            attachment2: Attachment = ATTACHMENT_TOP,
            insertType: InsertType = INSERT_TYPE_XL_PICTURE,
            tableAttachment: Attachment = ATTACHMENT_TOP,
            sizeMode: SizeMode = SIZE_MODE_FIXED_WIDTH,
            fixedWidth: Optional[float] = None,
            fixedHeight: Optional[float] = None,
            maxWidth: Optional[float] = None,
            maxHeight: Optional[float] = None,
            searchBlockReference: bool = True
    ) -> None:
        """初始化表格插入器业务主类

        :param cadPath: 待插入表格的DXF文件路径
        :param excelPath: Excel文件路径
        :param sheetName: Excel Sheet名称
        :param insertMode:
            fixedPoint：使用Excel中的固定插入点；
            singleSign：使用Data.tag作为单标记定位；
            doubleSign：使用Data.tag和sign2双标记定位
        :param attachment1:
            第一标记方向；
            8：上，4：左，2：下，6：右
        :param sign2: 双标记模式使用的第二标记
        :param attachment2:
            第二标记最终取点方向；
            8：上，4：左，2：下，6：右
        :param insertType:
            OLE_EMBED、xlPicture、xlBitmap
        :param tableAttachment:
            表格插入基点；
            8：上中，4：左中，2：下中，6：右中
        :param sizeMode:
            fixedWidth：固定宽度；
            fixedHeight：固定高度；
            maxSize：限制最大宽度和最大高度
        :param fixedWidth: 固定宽度
        :param fixedHeight: 固定高度
        :param maxWidth: 最大宽度
        :param maxHeight: 最大高度
        :param searchBlockReference: 搜索块参照
        """

        self.cadPath = Path(cadPath)
        self.excelPath = Path(excelPath)
        self.sheetName = sheetName.strip()

        self.insertMode = insertMode
        self.attachment1 = attachment1

        self.sign2 = (
            sign2.strip()
            if sign2 is not None
            else None
        )

        self.attachment2 = attachment2

        self.insertType = insertType
        self.tableAttachment = tableAttachment

        self.sizeMode = sizeMode

        self.fixedWidth = fixedWidth
        self.fixedHeight = fixedHeight

        self.maxWidth = maxWidth
        self.maxHeight = maxHeight
        self.searchBlockReference = bool(
            searchBlockReference
        )
    def run(self) -> List[Data]:
        '''执行完整表格插入流程'''

        return self.insert()

    def insert(self) -> List[Data]:
        '''执行完整表格初始化、定位和插入'''

        self._validateParameters()

        GLog.logInfo(
            f"{GLog.BLUE}"
            f"开始执行CAD表格插入"
            f"{GLog.END}"
        )

        GLog.logInfo(
            f"CAD文件: {self.cadPath}"
        )

        GLog.logInfo(
            f"Excel文件: {self.excelPath}"
        )

        GLog.logInfo(
            f"Sheet名称: {self.sheetName}"
        )

        GLog.logInfo(
            f"插入模式: {self.insertMode}"
        )

        GLog.logInfo(
            f"尺寸模式: {self.sizeMode}"
        )

        dataList = self._readDataList()

        self._validateDataList(
            dataList=dataList
        )

        self._locateDataList(
            dataList=dataList
        )

        self._insertDataList(
            dataList=dataList
        )

        locatedCount = sum(
            data.insertPoint is not None
            for data in dataList
        )

        insertedCount = sum(
            getattr(
                data,
                "cadObject",
                None
            ) is not None
            for data in dataList
        )

        GLog.logInfo(
            f"{GLog.GREEN}"
            f"CAD表格插入完成: "
            f"总数={len(dataList)}, "
            f"定位成功={locatedCount}, "
            f"插入成功={insertedCount}, "
            f"跳过={len(dataList) - insertedCount}"
            f"{GLog.END}"
        )

        GLog.logInfo(
            f"{GLog.YELLOW}"
            f"CAD文件未自动保存，也未自动关闭；"
            f"请检查结果后在AutoCAD中手动保存"
            f"{GLog.END}"
        )

        return dataList

    def _validateParameters(self) -> None:
        '''检查表格插入参数'''

        if not self.cadPath.exists():
            raise FileNotFoundError(
                f"CAD文件不存在: {self.cadPath}"
            )

        if not self.cadPath.is_file():
            raise ValueError(
                f"CAD路径不是文件: {self.cadPath}"
            )

        if self.cadPath.suffix.lower() != ".dxf":
            raise ValueError(
                f"当前表格插入器只支持DXF文件: "
                f"{self.cadPath}"
            )

        if not self.excelPath.exists():
            raise FileNotFoundError(
                f"Excel文件不存在: {self.excelPath}"
            )

        if not self.excelPath.is_file():
            raise ValueError(
                f"Excel路径不是文件: "
                f"{self.excelPath}"
            )

        if not self.sheetName:
            raise ValueError(
                "Sheet名称不能为空"
            )

        if (
                self.insertMode
                not in self.VALID_INSERT_MODE_SET
        ):
            raise ValueError(
                f"未知插入模式: "
                f"{self.insertMode}"
            )

        if (
                self.sizeMode
                not in self.VALID_SIZE_MODE_SET
        ):
            raise ValueError(
                f"未知尺寸模式: "
                f"{self.sizeMode}"
            )

        if (
                self.insertType
                not in self.VALID_INSERT_TYPE_SET
        ):
            raise ValueError(
                f"未知OLE插入类型: "
                f"{self.insertType}"
            )

        self._validateAttachment(
            attachment=self.attachment1,
            parameterName="attachment1"
        )

        self._validateAttachment(
            attachment=self.attachment2,
            parameterName="attachment2"
        )

        self._validateAttachment(
            attachment=self.tableAttachment,
            parameterName="tableAttachment"
        )

        if (
                self.insertMode
                == self.INSERT_MODE_DOUBLE_SIGN
        ):
            if not self.sign2:
                raise ValueError(
                    "双标记模式必须设置第二标记sign2"
                )

        if (
                self.sizeMode
                == self.SIZE_MODE_FIXED_WIDTH
        ):
            self.fixedWidth = self._validatePositiveNumber(
                value=self.fixedWidth,
                parameterName="fixedWidth"
            )

        elif (
                self.sizeMode
                == self.SIZE_MODE_FIXED_HEIGHT
        ):
            self.fixedHeight = self._validatePositiveNumber(
                value=self.fixedHeight,
                parameterName="fixedHeight"
            )

        elif (
                self.sizeMode
                == self.SIZE_MODE_MAX_SIZE
        ):
            self.maxWidth = self._validatePositiveNumber(
                value=self.maxWidth,
                parameterName="maxWidth"
            )

            self.maxHeight = self._validatePositiveNumber(
                value=self.maxHeight,
                parameterName="maxHeight"
            )

    def _validateDataList(
            self,
            dataList: List[Data]
    ) -> None:
        '''检查Reader生成的数据列表'''

        if not dataList:
            raise ValueError(
                "Excel中未读取到任何待插入表格"
            )

        if (
                self.insertMode
                != self.INSERT_MODE_FIXED_POINT
        ):
            return

        missingPointTagList = [
            data.tag
            for data in dataList
            if data.fixedInsertPoint is None
        ]

        if missingPointTagList:
            raise ValueError(
                "固定点插入模式下，以下TAG未配置固定插入点: "
                + "、".join(
                    missingPointTagList
                )
            )

    def _readDataList(self) -> List[Data]:
        '''读取Excel并生成Data列表'''

        reader = Reader(
            excelPath=self.excelPath,
            sheetName=self.sheetName
        )

        dataList = reader.toDataList()

        GLog.logInfo(
            f"{GLog.GREEN}"
            f"Excel数据读取完成，共读取"
            f"{len(dataList)}个子表格"
            f"{GLog.END}"
        )

        for data in dataList:
            GLog.logInfo(
                f"读取子表格: "
                f"TAG={data.tag}, "
                f"Range={data.rangeAddress()}, "
                f"FixedPoint={data.fixedInsertPoint}"
            )

        return dataList

    def _locateDataList(
            self,
            dataList: List[Data]
    ) -> None:
        '''读取DXF并定位所有Data的插入位置'''

        try:
            locateDoc = ezdxf.readfile( # type: ignore
                str(self.cadPath)
            )

        except Exception as e:
            raise RuntimeError(
                f"使用ezdxf读取DXF失败: "
                f"{self.cadPath} | {e}"
            ) from e

        cadLocator = CadLocator(
            doc=locateDoc,
            searchBlockReference=self.searchBlockReference
        )

        for data in dataList:
            sign1, sign2 = self._getLocateSign(
                data=data
            )

            insertPoint = cadLocator.locate(
                data=data,
                sign1=sign1,
                attachment1=self.attachment1, # type: ignore
                sign2=sign2,
                attachment2=self.attachment2 # type: ignore
            )

            if insertPoint is None:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"未能定位子表格，后续将跳过插入: "
                    f"TAG={data.tag}, "
                    f"sign1={sign1!r}, "
                    f"sign2={sign2!r}"
                    f"{GLog.END}"
                )

                continue

            GLog.logInfo(
                f"{GLog.GREEN}"
                f"子表格定位成功: "
                f"TAG={data.tag}, "
                f"InsertPoint={insertPoint}"
                f"{GLog.END}"
            )

    def _getLocateSign(
            self,
            data: Data
    ) -> tuple[Optional[str], Optional[str]]:
        '''根据插入模式获取定位标记'''

        if (
                self.insertMode
                == self.INSERT_MODE_FIXED_POINT
        ):
            return None, None

        if (
                self.insertMode
                == self.INSERT_MODE_SINGLE_SIGN
        ):
            return data.tag, None

        if (
                self.insertMode
                == self.INSERT_MODE_DOUBLE_SIGN
        ):
            return (
                data.tag,
                self._resolveSign(
                    sign=self.sign2,
                    data=data
                )
            )

        raise ValueError(
            f"未知插入模式: "
            f"{self.insertMode}"
        )

    def _resolveSign(
            self,
            sign: Optional[str],
            data: Data
    ) -> Optional[str]:
        '''解析当前Data对应的第二定位标记'''

        if sign is None:
            return None

        return sign.replace(
            self.TAG_PLACEHOLDER,
            data.tag
        )

    def _insertDataList(
            self,
            dataList: List[Data]
    ) -> None:
        '''打开Excel和AutoCAD并插入所有Data'''

        excelPIDSetBefore = (
            self._getExcelPIDSet()
        )

        excel = None
        workbook = None
        worksheet = None

        acad = None
        cadDoc = None

        insertCompleted = False

        try:
            excel = win32com.client.DispatchEx(
                "Excel.Application"
            )

            excel.Visible = False
            excel.DisplayAlerts = False

            workbook = excel.Workbooks.Open(
                str(self.excelPath)
            )

            worksheet = workbook.Worksheets(
                self.sheetName
            )

            workbook.Activate()
            worksheet.Activate()

            acad = win32com.client.Dispatch(
                "AutoCAD.Application"
            )

            acad.Visible = True

            cadDoc = acad.Documents.Open(
                str(self.cadPath)
            )

            self._activateCadDocument(
                cadDoc=cadDoc
            )

            time.sleep(
                self.CAD_READY_WAIT_SECONDS
            )

            sizeAdjuster = (
                self._createSizeAdjuster()
            )

            inserter = Inserter(
                cadDoc=cadDoc,
                worksheet=worksheet,
                sizeAdjuster=sizeAdjuster
            )

            for index, data in enumerate(
                    dataList,
                    start=1
            ):
                GLog.logInfo(
                    f"{GLog.BLUE}"
                    f"正在插入表格 "
                    f"{index}/{len(dataList)}: "
                    f"TAG={data.tag}"
                    f"{GLog.END}"
                )

                inserter.insert(
                    data=data,
                    insertType=self.insertType, # type: ignore
                    attachment=self.tableAttachment # type: ignore
                )

            insertCompleted = True

        finally:
            try:
                if excel is not None:
                    excel.CutCopyMode = False

            except Exception:
                pass

            self._clearClipboard()

            try:
                if workbook is not None:
                    workbook.Close(
                        SaveChanges=False
                    )

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"关闭Excel工作簿失败: "
                    f"{e}"
                    f"{GLog.END}"
                )

            try:
                if excel is not None:
                    excel.Quit()

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"退出Excel失败: "
                    f"{e}"
                    f"{GLog.END}"
                )

            # 只释放Excel COM对象。
            # 不调用cadDoc.Save()、cadDoc.Close()或acad.Quit()。
            try:
                del worksheet
            except Exception:
                pass

            try:
                del workbook
            except Exception:
                pass

            try:
                del excel
            except Exception:
                pass

            gc.collect()

            time.sleep(
                self.EXCEL_PROCESS_EXIT_WAIT_SECONDS
            )

            gc.collect()

            excelPIDSetAfter = (
                self._getExcelPIDSet()
            )

            excelPIDSetNew = (
                excelPIDSetAfter
                - excelPIDSetBefore
            )

            if excelPIDSetNew:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"检测到新增残留Excel进程: "
                    f"{excelPIDSetNew}"
                    f"{GLog.END}"
                )

                self._killExcelPIDSet(
                    pidSet=excelPIDSetNew
                )

            # 释放本线程中的AutoCAD COM代理，
            # 但不向AutoCAD发送保存、关闭或退出命令。
            try:
                del cadDoc
            except Exception:
                pass

            try:
                del acad
            except Exception:
                pass

            if not insertCompleted:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"表格插入流程中途发生异常；"
                    f"CAD文件仍保持打开，"
                    f"已完成内容尚未保存"
                    f"{GLog.END}"
                )

    def _createSizeAdjuster(
            self
    ) -> SizeAdjuster:
        '''根据当前参数创建OLE尺寸调整器'''

        return SizeAdjuster(
            mode=self.sizeMode, # type: ignore
            attachment=self.tableAttachment, # type: ignore
            width=self.fixedWidth,
            height=self.fixedHeight,
            maxWidth=self.maxWidth,
            maxHeight=self.maxHeight
        )

    def _activateCadDocument(
            self,
            cadDoc
    ) -> None:
        '''激活AutoCAD文档，失败时重试'''

        lastError: Optional[Exception] = None

        for retryIndex in range(
                self.CAD_OPEN_RETRY_COUNT
        ):
            try:
                cadDoc.Activate()
                return

            except Exception as e:
                lastError = e

                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"激活CAD文件失败，准备重试: "
                    f"{retryIndex + 1}/"
                    f"{self.CAD_OPEN_RETRY_COUNT}"
                    f"{GLog.END}"
                )

                time.sleep(
                    self.CAD_OPEN_RETRY_INTERVAL_SECONDS
                )

        raise RuntimeError(
            f"无法激活AutoCAD文档: "
            f"{lastError}"
        )

    def _validateAttachment(
            self,
            attachment: int,
            parameterName: str
    ) -> None:
        '''检查方向参数是否合法'''

        if attachment not in self.VALID_ATTACHMENT_SET:
            raise ValueError(
                f"{parameterName}方向不合法: "
                f"{attachment}; "
                f"仅支持8、4、2、6"
            )

    @staticmethod
    def _validatePositiveNumber(
            value: Optional[float],
            parameterName: str
    ) -> float:
        '''检查参数是否为大于0的数字'''

        if value is None:
            raise ValueError(
                f"{parameterName}不能为空"
            )

        try:
            numberValue = float(value)

        except (TypeError, ValueError) as e:
            raise ValueError(
                f"{parameterName}必须是数字: "
                f"{value}"
            ) from e

        if numberValue <= 0:
            raise ValueError(
                f"{parameterName}必须大于0"
            )

        return numberValue

    @staticmethod
    def _getExcelPIDSet() -> set[int]:
        '''获取当前全部Excel进程PID'''

        pidSet: set[int] = set()

        for process in psutil.process_iter(
                ["pid", "name"]
        ):
            try:
                processName = (
                    process.info["name"]
                )

                if (
                        processName
                        and processName.lower()
                        == "excel.exe"
                ):
                    pidSet.add(
                        int(
                            process.info["pid"]
                        )
                    )

            except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess
            ):
                continue

            except Exception:
                continue

        return pidSet

    @classmethod
    def _killExcelPIDSet(
            cls,
            pidSet: set[int]
    ) -> None:
        '''结束指定Excel进程'''

        for pid in pidSet:
            try:
                if not psutil.pid_exists(pid):
                    continue

                process = psutil.Process(pid)

                if (
                        process.name().lower()
                        != "excel.exe"
                ):
                    continue

                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"结束新增残留Excel进程: "
                    f"PID={pid}"
                    f"{GLog.END}"
                )

                process.terminate()

                try:
                    process.wait(
                        timeout=(
                            cls.EXCEL_PROCESS_TERMINATE_TIMEOUT_SECONDS
                        )
                    )

                except psutil.TimeoutExpired:
                    process.kill()

                    process.wait(
                        timeout=(
                            cls.EXCEL_PROCESS_TERMINATE_TIMEOUT_SECONDS
                        )
                    )

            except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess
            ):
                continue

            except Exception as e:
                GLog.logInfo(
                    f"{GLog.YELLOW}"
                    f"结束Excel进程失败: "
                    f"PID={pid}, "
                    f"错误={e}"
                    f"{GLog.END}"
                )

    @staticmethod
    def _clearClipboard() -> None:
        '''清空Windows剪贴板'''

        try:
            import win32clipboard

            win32clipboard.OpenClipboard()

            try:
                win32clipboard.EmptyClipboard()

            finally:
                win32clipboard.CloseClipboard()

        except Exception:
            pass