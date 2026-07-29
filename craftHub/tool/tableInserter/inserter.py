##########################################################################################################
#   Description: Excel表格CAD插入器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import threading
import time
import ctypes
import pywintypes
import win32clipboard

from typing import Any, Literal, Optional, Tuple

import win32com.client
from ezdxf.math import Vec2

from craftHub.tool import GLog

from .data import Data
from .sizeAdjuster import SizeAdjuster


InsertType = Literal[
    "OLE_EMBED",
    "xlPicture",
    "xlBitmap"
]

Attachment = Literal[
    2,
    4,
    6,
    8
]

# 调试开关：强制模拟剪贴板内容不匹配
DEBUG_FORCE_CLIPBOARD_MISMATCH = False

class Inserter:
    '''Excel表格CAD插入器'''

    INSERT_TYPE_OLE_EMBED = "OLE_EMBED"
    INSERT_TYPE_XL_PICTURE = "xlPicture"
    INSERT_TYPE_XL_BITMAP = "xlBitmap"

    ATTACHMENT_TOP = 2
    ATTACHMENT_LEFT = 4
    ATTACHMENT_RIGHT = 6
    ATTACHMENT_BOTTOM = 8

    VALID_INSERT_TYPE_SET = {
        INSERT_TYPE_OLE_EMBED,
        INSERT_TYPE_XL_PICTURE,
        INSERT_TYPE_XL_BITMAP
    }

    VALID_ATTACHMENT_SET = {
        ATTACHMENT_TOP,
        ATTACHMENT_LEFT,
        ATTACHMENT_RIGHT,
        ATTACHMENT_BOTTOM
    }

    XL_SCREEN = 1
    XL_PICTURE = -4147
    XL_BITMAP = 2

    COM_POINT_VARIANT_TYPE = 8197

    DEFAULT_RETRY_COUNT = 5
    DEFAULT_MAX_WAIT_SECONDS = 10.0
    DEFAULT_RETRY_INTERVAL_SECONDS = 2.0
    OBJECT_CHECK_INTERVAL_SECONDS = 0.2
    CLIPBOARD_READY_WAIT_SECONDS = 0.5
    AUTO_CONFIRM_DELAY_SECONDS = 2.0
    
    # Windows标准剪贴板格式
    CLIPBOARD_FORMAT_BITMAP = 2
    CLIPBOARD_FORMAT_METAFILE_PICTURE = 3
    CLIPBOARD_FORMAT_DIB = 8
    CLIPBOARD_FORMAT_ENHANCED_METAFILE = 14
    CLIPBOARD_FORMAT_DIB_V5 = 17

    VECTOR_CLIPBOARD_FORMAT_SET = {
        CLIPBOARD_FORMAT_METAFILE_PICTURE,
        CLIPBOARD_FORMAT_ENHANCED_METAFILE
    }

    BITMAP_CLIPBOARD_FORMAT_SET = {
        CLIPBOARD_FORMAT_BITMAP,
        CLIPBOARD_FORMAT_DIB,
        CLIPBOARD_FORMAT_DIB_V5
    }

    CLIPBOARD_CHECK_TIMEOUT_SECONDS = 3.0
    CLIPBOARD_CHECK_INTERVAL_SECONDS = 0.05

    CLIPBOARD_OPEN_RETRY_COUNT = 20
    CLIPBOARD_OPEN_RETRY_INTERVAL_SECONDS = 0.05

    def __init__(
            self,
            cadDoc: Any,
            worksheet: Any,
            sizeAdjuster: Optional[SizeAdjuster] = None
    ) -> None:
        """初始化Excel表格CAD插入器

        :param cadDoc: AutoCAD COM文档对象
        :param worksheet: Excel COM工作表对象
        :param sizeAdjuster: 表格尺寸调整器
        """

        if cadDoc is None:
            raise ValueError("AutoCAD文档对象不能为空")

        if worksheet is None:
            raise ValueError("Excel工作表对象不能为空")

        self.cadDoc = cadDoc
        self.worksheet = worksheet

        # 即使暂时不设置尺寸，也保证每次插入都会调用adjust接口
        self.sizeAdjuster = (
            sizeAdjuster
            if sizeAdjuster is not None
            else SizeAdjuster()
        )

    def insert(
            self,
            data: Data,
            insertType: InsertType = INSERT_TYPE_XL_PICTURE,
            attachment: Attachment = ATTACHMENT_BOTTOM
    ) -> Optional[Any]:
        """插入一个Data指定的Excel表格区域

        :param data: 待插入表格数据
        :param insertType:
            OLE_EMBED：嵌入式OLE对象
            xlPicture：Excel矢量图片
            xlBitmap：Excel位图
        :param attachment:
            data.insertPoint对应表格的哪个基准点；
            2：上中点
            4：左中点
            6：右中点
            8：下中点
        :return: 插入成功返回CAD对象，失败或无插入点返回None
        """

        self._validateInsertType(insertType)
        self._validateAttachment(attachment)

        if data.insertPoint is None:
            GLog.logInfo(
                f"{GLog.YELLOW}"
                f"表格未确定插入位置，跳过插入: "
                f"TAG={data.tag}, "
                f"Range={data.rangeAddress()}"
                f"{GLog.END}"
            )

            data.cadObject = None
            return None

        self._validateWorksheet(data)

        excelRange = None

        try:
            excelRange = self.worksheet.Range(
                data.rangeAddress()
            )

            self._copyExcelRange(
                excelRange=excelRange,
                insertType=insertType
            )

            time.sleep(
                self.CLIPBOARD_READY_WAIT_SECONDS
            )

            self.cadDoc.Activate()

            cadObject = self._pasteClipWithRetry(
                insertPoint=data.insertPoint,
                insertType=insertType
            )

            data.cadObject = cadObject

            # 每次插入后都调用尺寸调整器。
            # 当前SizeAdjuster为空实现，后续增加尺寸配置即可。
            self.sizeAdjuster.adjust(
                cadObject=cadObject,
                data=data
            )

            # 必须在尺寸调整完成后执行锚点坐标变换
            self._alignObjectToInsertPoint(
                cadObject=cadObject,
                targetPoint=data.insertPoint,
                attachment=attachment
            )

            GLog.logInfo(
                f"{GLog.GREEN}"
                f"表格插入完成: "
                f"TAG={data.tag}, "
                f"Range={data.rangeAddress()}, "
                f"InsertPoint={data.insertPoint}, "
                f"Attachment={attachment}, "
                f"InsertType={insertType}"
                f"{GLog.END}"
            )

            return cadObject

        finally:
            self._clearExcelCopyMode()

            try:
                del excelRange
            except Exception:
                pass

    def _validateWorksheet(
            self,
            data: Data
    ) -> None:
        '''检查Data对应的Sheet与当前工作表是否一致'''

        try:
            currentSheetName = str(
                self.worksheet.Name
            )

        except Exception:
            return

        if currentSheetName != data.sheetName:
            raise ValueError(
                f"Data对应的Sheet与当前工作表不一致: "
                f"Data.sheetName={data.sheetName}, "
                f"Worksheet.Name={currentSheetName}"
            )

    def _copyExcelRange(
            self,
            excelRange: Any,
            insertType: InsertType
    ) -> None:
        '''按照指定格式复制Excel区域，并检查剪贴板结果'''

        workbook = self.worksheet.Parent

        workbook.Activate()
        self.worksheet.Activate()

        # OLE嵌入使用普通Range.Copy。
        # 当前CopyPicture兼容性问题不影响该模式。
        if insertType == self.INSERT_TYPE_OLE_EMBED:
            excelRange.Copy()
            return

        # 矢量图和位图检查剪切板类型
        if insertType == self.INSERT_TYPE_XL_PICTURE:
            pictureFormat = self.XL_PICTURE
            expectedFormatSet = (
                self.VECTOR_CLIPBOARD_FORMAT_SET
            )

        elif insertType == self.INSERT_TYPE_XL_BITMAP:
            pictureFormat = self.XL_BITMAP
            expectedFormatSet = (
                self.BITMAP_CLIPBOARD_FORMAT_SET
            )

        else:
            raise ValueError(
                f"不支持的表格插入格式: "
                f"{insertType}"
            )

        # 必须先清空剪贴板。
        # 否则上一次遗留的图片可能导致本次检查误判成功。
        self._clearClipboard()

        sequenceNumberBefore = (
            self._getClipboardSequenceNumber()
        )

        try:
            excelRange.CopyPicture(
                Appearance=self.XL_SCREEN,
                Format=pictureFormat
            )

        except pywintypes.com_error as e:
            raise RuntimeError(
                f"Excel执行CopyPicture失败: "
                f"insertType={insertType}, "
                f"pictureFormat={pictureFormat}"
            ) from e

        if DEBUG_FORCE_CLIPBOARD_MISMATCH:
            GLog.logInfo(
                f"{GLog.YELLOW}"
                f"调试模式：强制模拟CopyPicture剪贴板格式不匹配"
                f"{GLog.END}"
            )

            copySucceeded = False

        else:
            copySucceeded = (
                self._waitForClipboardFormat(
                    sequenceNumberBefore=sequenceNumberBefore,
                    expectedFormatSet=expectedFormatSet
                )
            )

        if copySucceeded:
            GLog.logInfo(
                f"{GLog.GREEN}"
                f"Excel表格复制成功，"
                f"剪贴板中已检测到目标格式: "
                f"insertType={insertType}"
                f"{GLog.END}"
            )

            return

        clipboardFormatList = (
            self._getClipboardFormatList()
        )

        raise RuntimeError(
            f"Excel表格复制失败："
            f"CopyPicture执行后，"
            f"剪贴板中未检测到对应图片格式；"
            f"insertType={insertType}, "
            f"期望格式={sorted(expectedFormatSet)}, "
            f"实际格式={clipboardFormatList}",
            f"可能是Excel版本不支持该方法，请尝试使用其他OLE类型插入"
        )

    def _waitForClipboardFormat(
            self,
            sequenceNumberBefore: int,
            expectedFormatSet: set[int]
    ) -> bool:
        '''等待剪贴板更新并出现目标格式'''

        deadline = (
            time.monotonic()
            + self.CLIPBOARD_CHECK_TIMEOUT_SECONDS
        )

        while time.monotonic() <= deadline:
            sequenceNumberCurrent = (
                self._getClipboardSequenceNumber()
            )

            sequenceChanged = (
                sequenceNumberCurrent
                != sequenceNumberBefore
            )

            expectedFormatAvailable = any(
                self._isClipboardFormatAvailable(
                    clipboardFormat=clipboardFormat
                )
                for clipboardFormat
                in expectedFormatSet
            )

            if (
                    sequenceChanged
                    and expectedFormatAvailable
            ):
                return True

            time.sleep(
                self.CLIPBOARD_CHECK_INTERVAL_SECONDS
            )

        return False

    @staticmethod
    def _getClipboardSequenceNumber() -> int:
        '''获取Windows剪贴板内容变化序号'''

        return int(
            ctypes.windll.user32
            .GetClipboardSequenceNumber()
        )

    @staticmethod
    def _isClipboardFormatAvailable(
            clipboardFormat: int
    ) -> bool:
        '''检查剪贴板是否存在指定格式'''

        return bool(
            ctypes.windll.user32
            .IsClipboardFormatAvailable(
                int(clipboardFormat)
            )
        )

    @classmethod
    def _clearClipboard(cls) -> None:
        '''清空Windows剪贴板'''

        lastError: Optional[Exception] = None

        for _ in range(
                cls.CLIPBOARD_OPEN_RETRY_COUNT
        ):
            clipboardOpened = False

            try:
                win32clipboard.OpenClipboard()
                clipboardOpened = True

                win32clipboard.EmptyClipboard()

                return

            except Exception as e:
                lastError = e

                time.sleep(
                    cls.CLIPBOARD_OPEN_RETRY_INTERVAL_SECONDS
                )

            finally:
                if clipboardOpened:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass

        raise RuntimeError(
            f"无法清空Windows剪贴板: "
            f"{lastError}"
        )

    @classmethod
    def _getClipboardFormatList(
            cls
    ) -> list[int]:
        '''获取剪贴板中的全部格式编号'''

        formatList: list[int] = []
        lastError: Optional[Exception] = None

        for _ in range(
                cls.CLIPBOARD_OPEN_RETRY_COUNT
        ):
            clipboardOpened = False

            try:
                win32clipboard.OpenClipboard()
                clipboardOpened = True

                currentFormat = 0

                while True:
                    currentFormat = (
                        win32clipboard.EnumClipboardFormats(
                            currentFormat
                        )
                    )

                    if currentFormat == 0:
                        break

                    formatList.append(
                        int(currentFormat)
                    )

                return formatList

            except Exception as e:
                lastError = e

                time.sleep(
                    cls.CLIPBOARD_OPEN_RETRY_INTERVAL_SECONDS
                )

            finally:
                if clipboardOpened:
                    try:
                        win32clipboard.CloseClipboard()
                    except Exception:
                        pass

        GLog.logInfo(
            f"{GLog.YELLOW}"
            f"读取剪贴板格式失败: "
            f"{lastError}"
            f"{GLog.END}"
        )

        return formatList

    def _pasteClipWithRetry(
            self,
            insertPoint: Vec2,
            insertType: InsertType,
            retryCount: int = DEFAULT_RETRY_COUNT,
            maxWaitSeconds: float = DEFAULT_MAX_WAIT_SECONDS
    ) -> Any:
        '''使用PASTECLIP粘贴Excel表格并返回新增CAD对象'''

        lastError: Optional[Exception] = None

        for retryIndex in range(retryCount):
            try:
                modelSpace = self.cadDoc.ModelSpace
                beforeCount = modelSpace.Count

                self._sendPasteClipCommand(
                    insertPoint=insertPoint,
                    insertType=insertType
                )

                cadObject = self._waitForNewObject(
                    beforeCount=beforeCount,
                    maxWaitSeconds=maxWaitSeconds
                )

                if cadObject is not None:
                    return cadObject

                lastError = RuntimeError(
                    f"第{retryIndex + 1}次粘贴后未检测到新增对象"
                )

            except Exception as e:
                lastError = e

            GLog.logInfo(
                f"{GLog.YELLOW}"
                f"PASTECLIP粘贴失败，准备重试: "
                f"{retryIndex + 1}/{retryCount}, "
                f"错误={lastError}"
                f"{GLog.END}"
            )

            time.sleep(
                self.DEFAULT_RETRY_INTERVAL_SECONDS
            )

        raise RuntimeError(
            f"PASTECLIP粘贴失败，"
            f"已重试{retryCount}次: {lastError}"
        )

    def _sendPasteClipCommand(
            self,
            insertPoint: Vec2,
            insertType: InsertType
    ) -> None:
        '''向AutoCAD发送PASTECLIP命令'''

        x = float(insertPoint.x)
        y = float(insertPoint.y)

        if insertType == self.INSERT_TYPE_OLE_EMBED:
            self._pressEnterLater(
                delay=self.AUTO_CONFIRM_DELAY_SECONDS
            )

            self.cadDoc.SendCommand(
                f"_.PASTECLIP {x},{y}\n"
            )

            return

        if insertType == self.INSERT_TYPE_XL_PICTURE:
            self._pressEnterLater(
                delay=self.AUTO_CONFIRM_DELAY_SECONDS
            )

            self.cadDoc.SendCommand(
                f"_.PASTECLIP\n{x},{y}\n"
            )

            return

        self.cadDoc.SendCommand(
            f"_.PASTECLIP\n{x},{y}\n"
        )

    def _waitForNewObject(
            self,
            beforeCount: int,
            maxWaitSeconds: float
    ) -> Optional[Any]:
        '''等待AutoCAD模型空间产生新增对象'''

        startTime = time.time()

        while (
                time.time() - startTime
                <= maxWaitSeconds
        ):
            modelSpace = self.cadDoc.ModelSpace

            if modelSpace.Count > beforeCount:
                return self._getNewPasteObject(
                    beforeCount=beforeCount
                )

            time.sleep(
                self.OBJECT_CHECK_INTERVAL_SECONDS
            )

        return None

    def _getNewPasteObject(
            self,
            beforeCount: int
    ) -> Optional[Any]:
        '''从模型空间新增对象中查找可测量的粘贴对象'''

        modelSpace = self.cadDoc.ModelSpace
        fallbackObject = None

        for objectIndex in range(
                beforeCount,
                modelSpace.Count
        ):
            cadObject = modelSpace.Item(
                objectIndex
            )

            if fallbackObject is None:
                fallbackObject = cadObject

            try:
                objectName = cadObject.ObjectName

                GLog.logInfo(
                    f"检测到新增CAD对象: {objectName}"
                )

            except Exception:
                pass

            try:
                cadObject.GetBoundingBox()
                return cadObject

            except Exception:
                continue

        return fallbackObject

    def _alignObjectToInsertPoint(
            self,
            cadObject: Any,
            targetPoint: Vec2,
            attachment: Attachment
    ) -> None:
        '''将对象指定边缘中点移动到目标插入点'''

        minPoint, maxPoint = self._getObjectBoundingBox(
            cadObject=cadObject
        )

        currentAttachmentPoint = (
            self._calculateAttachmentPoint(
                minPoint=minPoint,
                maxPoint=maxPoint,
                attachment=attachment
            )
        )

        xOffset = (
            float(targetPoint.x)
            - currentAttachmentPoint.x
        )

        yOffset = (
            float(targetPoint.y)
            - currentAttachmentPoint.y
        )

        self._moveObject(
            cadObject=cadObject,
            xOffset=xOffset,
            yOffset=yOffset
        )

    def _getObjectBoundingBox(
            self,
            cadObject: Any
    ) -> Tuple[Vec2, Vec2]:
        '''读取CAD对象外接框'''

        try:
            minPointRaw, maxPointRaw = (
                cadObject.GetBoundingBox()
            )

        except Exception as e:
            raise RuntimeError(
                "无法读取新增CAD表格对象的外接框"
            ) from e

        minPoint = Vec2(
            float(minPointRaw[0]),
            float(minPointRaw[1])
        )

        maxPoint = Vec2(
            float(maxPointRaw[0]),
            float(maxPointRaw[1])
        )

        return minPoint, maxPoint

    def _calculateAttachmentPoint(
            self,
            minPoint: Vec2,
            maxPoint: Vec2,
            attachment: Attachment
    ) -> Vec2:
        '''计算外接框指定方向的边缘中点'''

        centerX = (
            minPoint.x + maxPoint.x
        ) / 2

        centerY = (
            minPoint.y + maxPoint.y
        ) / 2

        if attachment == self.ATTACHMENT_TOP:
            return Vec2(
                centerX,
                maxPoint.y
            )

        if attachment == self.ATTACHMENT_LEFT:
            return Vec2(
                minPoint.x,
                centerY
            )

        if attachment == self.ATTACHMENT_RIGHT:
            return Vec2(
                maxPoint.x,
                centerY
            )

        if attachment == self.ATTACHMENT_BOTTOM:
            return Vec2(
                centerX,
                minPoint.y
            )

        raise ValueError(
            f"不支持的表格基准点方向: {attachment}"
        )

    def _moveObject(
            self,
            cadObject: Any,
            xOffset: float,
            yOffset: float
    ) -> None:
        '''按照偏移量移动CAD对象'''

        fromPoint = win32com.client.VARIANT(
            self.COM_POINT_VARIANT_TYPE,
            (
                0.0,
                0.0,
                0.0
            )
        )

        toPoint = win32com.client.VARIANT(
            self.COM_POINT_VARIANT_TYPE,
            (
                float(xOffset),
                float(yOffset),
                0.0
            )
        )

        cadObject.Move(
            fromPoint,
            toPoint
        )

    def _clearExcelCopyMode(self) -> None:
        '''清除Excel复制状态'''

        try:
            self.worksheet.Application.CutCopyMode = False
        except Exception:
            pass

    @staticmethod
    def _pressEnterLater(
            delay: float
    ) -> None:
        '''延迟按回车确认AutoCAD粘贴弹窗'''

        def worker() -> None:
            time.sleep(delay)

            try:
                import pyautogui
                pyautogui.press("enter")

            except Exception:
                pass

        thread = threading.Thread(
            target=worker,
            daemon=True
        )

        thread.start()

    def _validateInsertType(
            self,
            insertType: str
    ) -> None:
        '''检查插入类型是否合法'''

        if insertType not in self.VALID_INSERT_TYPE_SET:
            raise ValueError(
                f"表格插入类型不合法: {insertType}; "
                f"仅支持"
                f"{self.INSERT_TYPE_OLE_EMBED}、"
                f"{self.INSERT_TYPE_XL_PICTURE}、"
                f"{self.INSERT_TYPE_XL_BITMAP}"
            )

    def _validateAttachment(
            self,
            attachment: int
    ) -> None:
        '''检查表格基准点是否合法'''

        if attachment not in self.VALID_ATTACHMENT_SET:
            raise ValueError(
                f"表格基准点方向不合法: {attachment}; "
                f"仅支持2、4、6、8"
            )