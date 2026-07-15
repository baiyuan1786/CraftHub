##########################################################################################################
#   Description: 统一表格插入器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..reader import DataUnit

import time
import gc
import psutil
import pandas as pd
import win32com.client

from pathlib import Path
from pandas import DataFrame
from typing import List, Optional
from ezdxf.math import Vec2

from craftHub.tool import GLog
from typing import Literal

class TableInserter:
    '''统一表格插入器'''

    def __init__(self,
                 DXFpath: Path,
                 insertExcel: Path,
                 insertSheet: str,
                 dataList: List[DataUnit],
                 startCol: str,
                 endCol: str,
                 oleInsertPointOffset: Vec2,
                 oleWidth: float
                 ) -> None:
        """统一表格插入器

        :param DXFpath: DXF文件路径
        :param insertExcel: 待插入表格
        :param insertSheet: 待插入表格Sheet
        :param dataList: 数据列表
        :param startCol: 开始列
        :param endCol: 结束列
        :param oleInsertPointOffset: OLE插入点偏移，最终位置的上中点距离初始左下角点的位置
        :param oleWidth: OLE目标宽度，注意无需设置高度
        """

        if not DXFpath.exists():
            raise FileNotFoundError(f"还没有保存文件: {DXFpath}")

        if not insertExcel or not insertExcel.exists():
            raise FileNotFoundError(f"待插入表格不存在, 无法插入: {insertExcel}")

        self.DXFpath = DXFpath
        self.insertExcel = insertExcel
        self.insertSheet = insertSheet
        self.dataList: List[DataUnit] = dataList
        self.startCol = startCol
        self.endCol = endCol
        self.oleInsertPointOffset = oleInsertPointOffset
        self.oleWidth = oleWidth

    @staticmethod
    def _waitAcadIdle(acad, sleepTime: float = 3.0):
        '''等待ACAD空闲'''
        time.sleep(sleepTime)

    @staticmethod
    def zoomToPoint(acad, x: float, y: float, viewSize: float = 500):
        """移动AutoCAD视角到指定点附近"""

        acad.ZoomCenter(
            win32com.client.VARIANT(8197, (x, y, 0.0)),
            viewSize
        )

    @staticmethod
    def _getStationExcelRange(df: DataFrame,
                              substationName: str,
                              startCol: str,
                              endCol: str) -> Optional[str]:
        """根据站名计算本站点对应的Excel Range"""

        if "站名" not in df.columns:
            raise ValueError("待插入表格中不存在'站名'列")

        matchIndexList = df.index[df["站名"] == substationName].tolist()

        if len(matchIndexList) == 0:
            return None

        topIndex = min(matchIndexList)
        bottomIndex = max(matchIndexList)

        # pandas index 0 对应 Excel 第2行，因为第1行是表头
        topExcelRow = int(topIndex) + 2
        bottomExcelRow = int(bottomIndex) + 2

        return f"{startCol}{topExcelRow}:{endCol}{bottomExcelRow}"

    @staticmethod
    def _getExcelPIDSet() -> set[int]:
        """获取当前所有 Excel 进程 PID"""
        pidSet = set()

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = proc.info["name"]
                if name and name.lower() == "excel.exe":
                    pidSet.add(proc.info["pid"])
            except:
                continue

        return pidSet

    @staticmethod
    def _killPIDSet(pidSet: set[int]):
        """强制结束指定 PID 集合"""
        for pid in pidSet:
            try:
                if not psutil.pid_exists(pid):
                    continue

                proc = psutil.Process(pid)

                if proc.name().lower() != "excel.exe":
                    continue

                GLog.logInfo(f"{GLog.YELLOW}强制结束新增 Excel 进程 PID: {pid}{GLog.END}")

                proc.terminate()

                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    proc.kill()

            except Exception as e:
                GLog.logInfo(f"{GLog.YELLOW}结束 Excel 进程失败 PID={pid}: {e}{GLog.END}")

    @staticmethod
    def _getNewPasteObject(cadDoc, beforeCount: int):
        """获取本次粘贴新增对象"""
        model = cadDoc.ModelSpace

        for i in range(beforeCount, model.Count):
            obj = model.Item(i)
            try:
                GLog.logInfo(f"新增对象: {obj.ObjectName}")
                return obj
            except:
                continue

        return None

    @staticmethod
    def _getOLESize(oleObj, substationName: str):
        """获取OLE对象宽高"""
        try:
            if oleObj is None:
                raise ValueError(f"未找到新增OLE对象: {substationName}")

            minPt, maxPt = oleObj.GetBoundingBox()

            minX, minY, _ = minPt
            maxX, maxY, _ = maxPt

            width = maxX - minX
            height = maxY - minY

            GLog.logInfo(
                f"{GLog.GREEN}OLE尺寸: {substationName} | "
                f"width={width:.4f}, height={height:.4f}{GLog.END}"
            )

            return width, height

        except Exception as e:
            GLog.logInfo(f"{GLog.YELLOW}读取OLE尺寸失败: {substationName} | {e}{GLog.END}")
            return None, None
        
    @staticmethod
    def _pressEnterLater(delay: float = 5.0):
        """延迟按一次回车，用于确认AutoCAD OLE弹窗"""

        import time
        import threading
        import pyautogui

        def worker():
            time.sleep(delay)
            pyautogui.press("enter")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    @staticmethod
    def scaleOLE(oleObj, scaleFactor: float):
        """等比例缩放OLE"""

        minPt, maxPt = oleObj.GetBoundingBox()
        minX, minY, _ = minPt

        basePoint = (minX, minY, 0)

        oleObj.ScaleEntity(
            win32com.client.VARIANT(8197, basePoint),
            scaleFactor
        )

    @staticmethod
    def moveOLE(oleObj, xOffset: float, yOffset: float):
        """移动OLE对象"""

        oleObj.Move(
            win32com.client.VARIANT(8197, (0.0, 0.0, 0.0)),
            win32com.client.VARIANT(8197, (xOffset, yOffset, 0.0))
        )

    def pasteClipWithRetry(self,
                        cadDoc,
                        x: float,
                        y: float,
                        insertType: Literal["OLE_EMBED", "xlPicture", "default"],
                        retryCount: int = 5,
                        maxWaitSeconds: float = 10):
        """带重试的AutoCAD剪贴板粘贴

        :param cadDoc: AutoCAD文档对象
        :param x: 插入点X
        :param y: 插入点Y
        :param insertType: 插入类型
        :param retryCount: 最大重试次数
        :param waitSeconds: 每次粘贴后的等待时间
        """

        lastError = None
        for i in range(retryCount):
            try:
                waitSeconds = 0
                beforeCount = cadDoc.ModelSpace.Count

                if insertType == "OLE_EMBED":
                    self._pressEnterLater(2)
                    cadDoc.SendCommand(f"_.PASTECLIP {x},{y} \n")

                elif insertType == "xlPicture":
                    self._pressEnterLater(2)
                    cadDoc.SendCommand(f"_.PASTECLIP\n{x},{y}\n")

                else:
                    cadDoc.SendCommand(f"_.PASTECLIP\n{x},{y}\n")

                while cadDoc.ModelSpace.Count <= beforeCount:
                    time.sleep(0.2)
                    waitSeconds += 0.2
                    if waitSeconds > maxWaitSeconds:
                        lastError = RuntimeError(
                            f"第{i + 1}次粘贴后未检测到新增对象"
                        )
                        break
                else:
                    return

            except Exception as e:
                lastError = e
                GLog.logInfo(f"{GLog.YELLOW}{str(lastError)}, sleep 2 seconds{GLog.END}")
                time.sleep(2)
    
        raise RuntimeError(f"PASTECLIP粘贴失败，已重试{retryCount}次: {lastError}")

    def insertOLE(self, insertType: Literal["OLE_EMBED", "xlBitmap", "xlPicture"] = "xlPicture", MaxHeight: Optional[int] = None):
        """插入所有站点的表格OLE对象到DXF之中

        :param insertType: 插入类型
        """        
        
        assert insertType in ["OLE_EMBED", "xlBitmap", "xlPicture"], f"使用的插入类型不合法: {insertType}"
        excelPIDSetBefore = self._getExcelPIDSet()

        excel = None
        wb = None
        ws = None
        acad = None
        cadDoc = None

        try:
            insertDF = pd.read_excel(
                self.insertExcel,
                sheet_name=self.insertSheet,
                header=0
            )

            if "站名" not in insertDF.columns:
                raise ValueError("待插入表格中不存在'站名'列")

            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False

            wb = excel.Workbooks.Open(str(self.insertExcel))
            ws = wb.Worksheets(self.insertSheet)
            wb.Activate()
            ws.Activate()

            acad = win32com.client.Dispatch("AutoCAD.Application")
            acad.Visible = True

            cadDoc = acad.Documents.Open(str(self.DXFpath))
            
            for failCount in range(5):
                try:
                    cadDoc.Activate()
                    break
                except Exception as e:
                    GLog.logInfo(f"{GLog.YELLOW}打开CAD文件失败, 重试 {failCount} / 5{GLog.END}")
                    continue

            self._waitAcadIdle(acad)

            for data in self.dataList:
                substationName = data.get("substationName")

                rangeAddr = self._getStationExcelRange(
                    df=insertDF,
                    substationName=substationName,  # type: ignore
                    startCol=self.startCol,
                    endCol=self.endCol
                )

                if rangeAddr is None:
                    GLog.logInfo(f"{GLog.YELLOW}未找到站点表格数据: {substationName}{GLog.END}")
                    continue

                GLog.logInfo(f"{GLog.BLUE}插入表格OLE: {substationName} | {rangeAddr}{GLog.END}")

                insertPoint = data.drawOrderToOffset()
                x = float(insertPoint.x)
                y = float(insertPoint.y)

                rng = None

                try:
                    wb.Activate()
                    ws.Activate()

                    rng = ws.Range(rangeAddr)
                    
                    if insertType == "OLE_EMBED":
                        rng.Copy()
                    elif insertType == "xlPicture":
                        XL_SCREEN = 1
                        XL_PICTURE = -4147

                        rng.CopyPicture(
                            Appearance=XL_SCREEN,
                            Format=XL_PICTURE
                        )
                    else:
                        rng.CopyPicture(
                            Appearance=1, # xlScreen 
                            Format=2 # xlBitmap 
                        )

                    time.sleep(0.5)

                    cadDoc.Activate()

                    beforeCount = cadDoc.ModelSpace.Count
                    
                    viewPoint = insertPoint + self.oleInsertPointOffset

                    self.zoomToPoint(
                        acad=acad,
                        x=float(viewPoint.x),
                        y=float(viewPoint.y),
                        viewSize=500
                    )

                    # 先插入到站点布局原点，再根据左上角偏移修正
                    self.pasteClipWithRetry(
                        cadDoc=cadDoc,
                        x=x,
                        y=y,
                        insertType=insertType, # type: ignore
                        retryCount=5,
                    )

                    oleObj = self._getNewPasteObject(cadDoc, beforeCount)
                    oleRawWidth, oleRawHeight = self._getOLESize(oleObj, substationName)

                    if oleObj is None or oleRawWidth is None or oleRawHeight is None:
                        continue
                    
                    # 计算缩放因子：先按目标宽度缩放
                    scaleFactor = self.oleWidth / oleRawWidth

                    oleNewWidth = oleRawWidth * scaleFactor
                    oleNewHeight = oleRawHeight * scaleFactor

                    # 最大高度限制
                    if MaxHeight is not None and oleNewHeight >= MaxHeight:
                        heightScaleFactor = MaxHeight / oleNewHeight

                        oleNewWidth = oleNewWidth * heightScaleFactor
                        oleNewHeight = oleNewHeight * heightScaleFactor

                        scaleFactor = scaleFactor * heightScaleFactor

                    self.scaleOLE(
                        oleObj=oleObj,
                        scaleFactor=scaleFactor
                    )

                    # oleInsertPointOffset 是目标左上角偏移；
                    # PASTECLIP 初始参考点更接近左下角，所以 y 方向需要减去缩放后的高度
                    self.moveOLE(
                        oleObj=oleObj,
                        xOffset=float(self.oleInsertPointOffset.x - oleNewWidth / 2),
                        yOffset=float(self.oleInsertPointOffset.y - oleNewHeight)
                    )

                finally:
                    try:
                        del rng
                    except:
                        pass

            self._waitAcadIdle(acad)

            #if self.DXFpath.suffix == ".dxf":
            #    savePath = Path(str(self.DXFpath).replace(".dxf", ".dwg"))
            #    cadDoc.SaveAs(savePath)
            #    GLog.logInfo(f"{GLog.GREEN}文件已保存到新路径: {savePath}{GLog.END}")
            #else:
            cadDoc.Save()
            GLog.logInfo(f"{GLog.GREEN}文件已保存到原路径{GLog.END}")
            cadDoc.Close(False)

        finally:
            try:
                if excel is not None:
                    excel.CutCopyMode = False
            except:
                pass

            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
            except:
                pass

            time.sleep(1)

            try:
                if excel is not None:
                    excel.Quit()
            except Exception as e:
                GLog.logInfo(f"{GLog.YELLOW}退出Excel失败: {e}{GLog.END}")

            try:
                del ws
                del wb
                del excel
                del cadDoc
                del acad
            except:
                pass

            gc.collect()
            time.sleep(2)
            gc.collect()

            excelPIDSetAfter = self._getExcelPIDSet()
            excelPIDSetNew = excelPIDSetAfter - excelPIDSetBefore

            if len(excelPIDSetNew) > 0:
                GLog.logInfo(f"{GLog.YELLOW}检测到新增残留 Excel 进程: {excelPIDSetNew}{GLog.END}")
                self._killPIDSet(excelPIDSetNew)
