##########################################################################################################
#   Description: CAD块参照批量打印PDF页面
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import time
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)

try:
    import win32com.client
except ImportError:
    win32com = None

from pypdf import PdfReader, PdfWriter


from page import Page
from path import PATH_HUB_ROOT

from .lspBuilder import CadBlockPrinterLspBuilder
from .pdfVerticalCropper import PdfVerticalCropper


class CadBlockPrinter(Page):
    '''CAD块参照批量打印PDF页面'''

    PAGE_TITLE = "CAD块参照批量打印PDF"

    CAD_FILE_FILTER = "CAD Files (*.dwg *.dxf)"
    CAD_SUFFIX_LIST = [".dwg", ".dxf"]

    PATH_DATA = PATH_HUB_ROOT / "tool" / "cadBlockPrinter" / "data.yaml"

    DEFAULT_BLOCK_PREFIX = CadBlockPrinterLspBuilder.DEFAULT_BLOCK_PREFIX

    TEMP_LSP_FILE_NAME = "_cadBlockPrinter_temp.lsp"
    DONE_FLAG_FILE_NAME = CadBlockPrinterLspBuilder.DONE_FLAG_FILE_NAME
    MERGED_FILE_SUFFIX = "merged.pdf"

    WAIT_INTERVAL_SECOND = 0.5
    DEFAULT_TIMEOUT_SECOND = 3600

    def __init__(self):
        '''页面初始化'''

        super().__init__(title=self.PAGE_TITLE, dataPath=self.PATH_DATA)

        self.initUI()
        self.load()

    def initUI(self):
        '''初始化页面UI'''

        self.cadPathEdit = QLineEdit()
        self.cadPathEdit.setObjectName("cadPathEdit")

        self.blockPrefixEdit = QLineEdit()
        self.blockPrefixEdit.setObjectName("blockPrefixEdit")
        self.blockPrefixEdit.setText(self.DEFAULT_BLOCK_PREFIX)
        self.blockPrefixEdit.setPlaceholderText("例如 GEDI_TQ")

        self.attrNameEdit = QLineEdit()
        self.attrNameEdit.setObjectName("attrNameEdit")
        self.attrNameEdit.setPlaceholderText("可选，例如 DRAWINGNUMBER；为空则按默认顺序输出")

        self.outputDirEdit = QLineEdit()
        self.outputDirEdit.setObjectName("outputDirEdit")

        self.resultTextEdit = QPlainTextEdit()
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.resultTextEdit.setReadOnly(True)

        self.selectCadBtn = QPushButton("选择CAD文件")
        self.selectOutputDirBtn = QPushButton("选择导出文件夹")
        self.runBtn = QPushButton("开始打印")
        self.clearBtn = QPushButton("清空日志")

        self.selectCadBtn.clicked.connect(self.selectCadFile)
        self.selectOutputDirBtn.clicked.connect(self.selectOutputDir)
        self.runBtn.clicked.connect(self.runPrinter)
        self.clearBtn.clicked.connect(self.resultTextEdit.clear)

        cadLayout = QHBoxLayout()
        cadLayout.addWidget(self.cadPathEdit)
        cadLayout.addWidget(self.selectCadBtn)

        outputLayout = QHBoxLayout()
        outputLayout.addWidget(self.outputDirEdit)
        outputLayout.addWidget(self.selectOutputDirBtn)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel("CAD文件路径:"), 0, 0)
        gridLayout.addLayout(cadLayout, 0, 1)

        gridLayout.addWidget(QLabel("块名前缀:"), 1, 0)
        gridLayout.addWidget(self.blockPrefixEdit, 1, 1)

        gridLayout.addWidget(QLabel("排序属性名称:"), 2, 0)
        gridLayout.addWidget(self.attrNameEdit, 2, 1)

        gridLayout.addWidget(QLabel("PDF导出文件夹:"), 3, 0)
        gridLayout.addLayout(outputLayout, 3, 1)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.runBtn)
        btnLayout.addWidget(self.clearBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addLayout(btnLayout)
        mainLayout.addWidget(QLabel("执行日志:"))
        mainLayout.addWidget(self.resultTextEdit)

        self.setLayout(mainLayout)

    def selectCadFile(self):
        '''选择CAD文件'''

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "选择CAD文件",
            "",
            self.CAD_FILE_FILTER,
        )

        if filePath:
            self.cadPathEdit.setText(filePath)

    def selectOutputDir(self):
        '''选择导出文件夹'''

        outputDir = QFileDialog.getExistingDirectory(
            self,
            "选择PDF导出文件夹",
            "",
        )

        if outputDir:
            self.outputDirEdit.setText(outputDir)

    def runPrinter(self):
        '''执行CAD块参照批量打印'''

        try:
            cadPath = self.readPara(
                self.cadPathEdit,
                isPath=True,
                checkPath=True,
                notFoundStr="CAD文件不存在",
            )
            blockPrefix = self.readPara(self.blockPrefixEdit)
            attrName = self.readPara(self.attrNameEdit)
            outputDir = self.readPara(
                self.outputDirEdit,
                isPath=True,
                checkPath=False,
            )

            if cadPath is None:
                raise ValueError("请选择CAD文件")

            if outputDir is None:
                raise ValueError("请选择PDF导出文件夹")

            if blockPrefix is None:
                blockPrefix = self.DEFAULT_BLOCK_PREFIX

            cadPath = Path(cadPath)
            outputDir = Path(outputDir)
            blockPrefix = str(blockPrefix).strip()

            if not blockPrefix:
                raise ValueError("块名前缀不能为空")

            self._checkCadFile(cadPath)
            outputDir.mkdir(parents=True, exist_ok=True)

            if not self._confirmOutputDirIsEmpty(outputDir):
                return

            self._removeRuntimeFiles(outputDir)

            self.save()
            self.resultTextEdit.clear()

            self._appendLog(f"CAD文件: {cadPath}")
            self._appendLog(f"导出目录: {outputDir}")
            self._appendLog(f"块名前缀: {blockPrefix}")

            if attrName:
                self._appendLog(f"排序属性: {attrName}")
            else:
                self._appendLog("排序属性: 未输入，将按默认顺序输出")

            pdfPathList = self.plotCadBlocksToPdf(
                cadPath=cadPath,
                outputDir=outputDir,
                blockPrefix=blockPrefix,
                attrName=attrName, # type: ignore
            )

            mergedPdfPath = outputDir / f"{cadPath.stem}{self.MERGED_FILE_SUFFIX}"
            croppedPdfPath = outputDir / f"{cadPath.stem}cropped.pdf"

            self.mergePdfFiles(
                pdfPathList=pdfPathList,
                mergedPdfPath=mergedPdfPath,
            )
            
            self._appendLog("开始裁剪PDF, 请等待")
            PdfVerticalCropper.cropPdf(mergedPdfPath, croppedPdfPath)

            self._appendLog("")
            self._appendLog(f"全部PDF导出完成，共 {len(pdfPathList)} 个")
            self._appendLog(f"合并PDF: {croppedPdfPath}")

            QMessageBox.information(
                self,
                "打印完成",
                f"PDF导出完成\n\n合并文件:\n{croppedPdfPath}",
            )

        except Exception as error:
            QMessageBox.critical(self, "打印失败", str(error))
            self._appendLog(f"错误: {error}")

    def plotCadBlocksToPdf(
            self,
            cadPath: Path,
            outputDir: Path,
            blockPrefix: str,
            attrName: Optional[str],
    ) -> List[Path]:
        '''调用AutoCAD打印块参照PDF'''

        self._checkWin32ComAvailable()

        tempLspPath = outputDir / self.TEMP_LSP_FILE_NAME
        doneFlagPath = outputDir / self.DONE_FLAG_FILE_NAME

        lspBuilder = CadBlockPrinterLspBuilder(
            blockPrefix=blockPrefix,
        )

        lspBuilder.writeLspFile(
            lspPath=tempLspPath,
            outputDir=outputDir,
            fileStem=cadPath.stem,
            attrName=attrName,
        )

        self._appendLog("正在启动AutoCAD...")
        acadApp = win32com.client.Dispatch("AutoCAD.Application")  # type: ignore
        acadApp.Visible = True

        self._appendLog("正在打开CAD文件...")
        cadDoc = acadApp.Documents.Open(str(cadPath))

        self._appendLog("正在加载并执行临时LSP...")
        lspPathText = lspBuilder.toLspPath(tempLspPath)
        cadDoc.SendCommand(f'(progn (load "{lspPathText}") (c:{CadBlockPrinterLspBuilder.LSP_COMMAND_NAME}))\n')

        self._appendLog("正在等待AutoCAD打印完成...")
        self._waitForDoneFlag(doneFlagPath)

        self._appendLog("正在扫描导出目录PDF...")
        pdfPathList = self._collectPdfPathList(
            outputDir=outputDir,
            cadPath=cadPath,
        )

        return pdfPathList

    def mergePdfFiles(self, pdfPathList: List[Path], mergedPdfPath: Path):
        '''合并PDF文件'''

        writer = PdfWriter()

        for pdfPath in pdfPathList:
            if not pdfPath.exists():
                raise FileNotFoundError(f"PDF文件不存在，无法合并: {pdfPath}")

            self._appendLog(f"合并PDF: {pdfPath.name}")

            reader = PdfReader(str(pdfPath))

            for page in reader.pages:
                writer.add_page(page)

        with mergedPdfPath.open("wb") as file:
            writer.write(file)

        try:
            writer.close()
        except Exception:
            pass

    def _confirmOutputDirIsEmpty(self, outputDir: Path) -> bool:
        '''确认输出目录是否为空'''

        fileList = [
            path for path in outputDir.iterdir()
            if path.name not in [self.TEMP_LSP_FILE_NAME, self.DONE_FLAG_FILE_NAME]
        ]

        if not fileList:
            return True

        result = QMessageBox.warning(
            self,
            "导出目录非空",
            "当前导出文件夹不是空文件夹。\n\n"
            "本工具会在打印完成后扫描该文件夹内的所有PDF并合并。\n"
            "如果目录中存在旧PDF，可能会被错误合并。\n\n"
            "建议使用空文件夹。\n\n"
            "是否仍然继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        return result == QMessageBox.StandardButton.Yes

    def _removeRuntimeFiles(self, outputDir: Path):
        '''删除运行时文件'''

        runtimeFileNameList = [
            self.TEMP_LSP_FILE_NAME,
            self.DONE_FLAG_FILE_NAME,
        ]

        for fileName in runtimeFileNameList:
            filePath = outputDir / fileName

            if not filePath.exists():
                continue

            try:
                filePath.unlink()
            except Exception:
                pass

    def _waitForDoneFlag(self, doneFlagPath: Path):
        '''等待AutoCAD完成标记'''

        startTime = time.time()

        while time.time() - startTime < self.DEFAULT_TIMEOUT_SECOND:
            QApplication.processEvents()

            if doneFlagPath.exists():
                time.sleep(self.WAIT_INTERVAL_SECOND)
                return

            time.sleep(self.WAIT_INTERVAL_SECOND)

        raise TimeoutError("等待AutoCAD打印PDF超时")

    def _collectPdfPathList(self, outputDir: Path, cadPath: Path) -> List[Path]:
        '''扫描导出目录中的PDF文件'''

        mergedPdfPath = outputDir / f"{cadPath.stem}{self.MERGED_FILE_SUFFIX}"

        pdfPathList = [
            pdfPath for pdfPath in outputDir.glob("*.pdf")
            if pdfPath.resolve() != mergedPdfPath.resolve()
        ]

        pdfPathList.sort(key=lambda path: path.name.lower())

        if not pdfPathList:
            raise RuntimeError("导出目录中没有找到PDF文件")

        for pdfPath in pdfPathList:
            self._appendLog(f"发现PDF: {pdfPath.name}")

        return pdfPathList

    def _checkCadFile(self, cadPath: Path):
        '''检查CAD文件格式'''

        if cadPath.suffix.lower() not in self.CAD_SUFFIX_LIST:
            raise ValueError(f"仅支持dwg和dxf文件: {cadPath}")

    def _checkWin32ComAvailable(self):
        '''检查win32com是否可用'''

        if win32com is None:
            raise RuntimeError("未安装pywin32，无法调用AutoCAD")

    def _appendLog(self, text: str):
        '''追加日志'''

        self.resultTextEdit.appendPlainText(text)
        QApplication.processEvents()