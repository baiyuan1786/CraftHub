##########################################################################################################
#   Description: Python代码行数统计页面
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from pathlib import Path
from typing import List, Tuple

from PyQt6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)

from page import Page
from path import PATH_HUB_ROOT


class PythonLineCounterPage(Page):
    '''Python代码行数统计页面'''

    PAGE_TITLE = "PythonCounter"
    PATH_DATA = PATH_HUB_ROOT / "tool" / "pythonLineCounter" / "data.yaml"

    PYTHON_FILE_PATTERN = "*.py"
    DEFAULT_EXCLUDE_TEXT = "__"

    EXCLUDE_SEPARATOR_LIST = [";", "；", ",", "，", "\n"]

    def __init__(self):
        '''初始化Python代码行数统计页面'''

        super().__init__(
            title=self.PAGE_TITLE,
            dataPath=self.PATH_DATA
        )

        self.initUI()
        self.load()

    def initUI(self):
        '''初始化界面'''

        mainLayout = QVBoxLayout(self)
        formLayout = QGridLayout()

        self.targetDirEdit = QLineEdit()
        self.targetDirEdit.setObjectName("targetDirEdit")
        self.targetDirEdit.setPlaceholderText("请选择需要统计的目标文件夹")

        self.excludeTextEdit = QLineEdit()
        self.excludeTextEdit.setObjectName("excludeTextEdit")
        self.excludeTextEdit.setText(self.DEFAULT_EXCLUDE_TEXT)
        self.excludeTextEdit.setPlaceholderText("包含这些字符串的文件不统计，多个字符串可用分号分隔，例如: __;test")

        self.resultTextEdit = QPlainTextEdit()
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.resultTextEdit.setReadOnly(True)

        self.selectDirBtn = QPushButton("选择文件夹")
        self.runBtn = QPushButton("开始统计")
        self.clearBtn = QPushButton("清空结果")

        formLayout.addWidget(QLabel("目标文件夹:"), 0, 0)
        formLayout.addWidget(self.targetDirEdit, 0, 1)
        formLayout.addWidget(self.selectDirBtn, 0, 2)

        formLayout.addWidget(QLabel("排除字符串:"), 1, 0)
        formLayout.addWidget(self.excludeTextEdit, 1, 1, 1, 2)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(self.resultTextEdit)
        mainLayout.addWidget(self.runBtn)
        mainLayout.addWidget(self.clearBtn)

        self.selectDirBtn.clicked.connect(self.selectTargetDir)
        self.runBtn.clicked.connect(self.runCounter)
        self.clearBtn.clicked.connect(self.resultTextEdit.clear)

    def selectTargetDir(self):
        '''选择目标文件夹'''

        dirPathText = QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹",
            self.targetDirEdit.text().strip()
        )

        if not dirPathText:
            return

        self.targetDirEdit.setText(dirPathText)

    def runCounter(self):
        '''执行Python代码行数统计'''

        targetDir = Path(self.targetDirEdit.text().strip())

        if not targetDir.exists() or not targetDir.is_dir():
            self._appendResultLine("错误: 目标文件夹不存在或不是有效文件夹")
            return

        self.save()
        self.resultTextEdit.clear()

        excludeStringList = self._collectExcludeStringList()
        fileLineCountList, skippedFileList = self._countPythonFiles(
            targetDir=targetDir,
            excludeStringList=excludeStringList
        )

        totalLineCount = sum(lineCount for _, lineCount in fileLineCountList)

        self._appendResultLine("=" * 80)
        self._appendResultLine("Python代码行数统计结果")
        self._appendResultLine("=" * 80)
        self._appendResultLine(f"目标文件夹: {targetDir}")
        self._appendResultLine(f"统计文件类型: {self.PYTHON_FILE_PATTERN}")
        self._appendResultLine(f"排除字符串: {', '.join(excludeStringList) if excludeStringList else '无'}")
        self._appendResultLine(f"参与统计文件数: {len(fileLineCountList)}")
        self._appendResultLine(f"跳过文件数: {len(skippedFileList)}")
        self._appendResultLine(f"总行数: {totalLineCount}")
        self._appendResultLine("")

        self._appendResultLine("=" * 80)
        self._appendResultLine("参与统计文件明细")
        self._appendResultLine("=" * 80)

        for filePath, lineCount in fileLineCountList:
            relativePath = self._toRelativePathText(filePath, targetDir)
            self._appendResultLine(f"{relativePath}: {lineCount}")

        if skippedFileList:
            self._appendResultLine("")
            self._appendResultLine("=" * 80)
            self._appendResultLine("跳过文件明细")
            self._appendResultLine("=" * 80)

            for filePath in skippedFileList:
                relativePath = self._toRelativePathText(filePath, targetDir)
                self._appendResultLine(relativePath)

    def _countPythonFiles(
            self,
            targetDir: Path,
            excludeStringList: List[str]
    ) -> Tuple[List[Tuple[Path, int]], List[Path]]:
        '''统计Python文件行数'''

        fileLineCountList: List[Tuple[Path, int]] = []
        skippedFileList: List[Path] = []

        pyFilePathList = sorted(
            targetDir.rglob(self.PYTHON_FILE_PATTERN),
            key=lambda path: str(path).lower()
        )

        for filePath in pyFilePathList:
            if self._shouldSkipFile(
                    filePath=filePath,
                    targetDir=targetDir,
                    excludeStringList=excludeStringList
            ):
                skippedFileList.append(filePath)
                continue

            lineCount = self._countFileLines(filePath)
            fileLineCountList.append((filePath, lineCount))

        return fileLineCountList, skippedFileList

    def _collectExcludeStringList(self) -> List[str]:
        '''收集排除字符串列表'''

        excludeText = self.excludeTextEdit.text().strip()

        for separator in self.EXCLUDE_SEPARATOR_LIST:
            excludeText = excludeText.replace(separator, ";")

        return [
            item.strip()
            for item in excludeText.split(";")
            if item.strip()
        ]

    def _shouldSkipFile(
            self,
            filePath: Path,
            targetDir: Path,
            excludeStringList: List[str]
    ) -> bool:
        '''判断文件是否需要跳过'''

        if not excludeStringList:
            return False

        relativePathText = self._toRelativePathText(filePath, targetDir)

        for excludeString in excludeStringList:
            if excludeString in filePath.name:
                return True

            if excludeString in relativePathText:
                return True

        return False

    def _countFileLines(self, filePath: Path) -> int:
        '''统计单个文件行数'''

        try:
            with filePath.open("r", encoding="utf-8") as file:
                return sum(1 for _ in file)

        except UnicodeDecodeError:
            with filePath.open("r", encoding="gbk", errors="ignore") as file:
                return sum(1 for _ in file)

        except Exception:
            return 0

    def _toRelativePathText(self, filePath: Path, targetDir: Path) -> str:
        '''转换为相对路径字符串'''

        try:
            return str(filePath.relative_to(targetDir))

        except Exception:
            return str(filePath)

    def _appendResultLine(self, text: str):
        '''追加结果文本'''

        self.resultTextEdit.appendPlainText(text)