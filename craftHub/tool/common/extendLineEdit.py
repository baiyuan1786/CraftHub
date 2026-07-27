##########################################################################################################
#   Description: 扩展单行输入框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from PyQt6.QtWidgets import QLineEdit, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal

from pathlib import Path
import os
from typing import Optional

from .log import GLog


class ExtendedLineEdit(QLineEdit):
    """带右键菜单的增强版QLineEdit"""

    fileSelected = pyqtSignal(Path)      # 文件选择信号
    folderSelected = pyqtSignal(Path)    # 文件夹选择信号
    fileOpened = pyqtSignal(Path)        # 文件打开信号

    def __init__(self, parent=None):
        """初始化ExtendedLineEdit"""
        super().__init__(parent)

        self._fileFilters = "所有文件 (*.*)"

        self._createContextMenu()
        self._connectSignals()
        self._updateActionsState()

    def _createContextMenu(self) -> None:
        """创建上下文菜单"""

        self.contextMenu = QMenu(self)

        selectFileAction = QAction("选择文件...", self)
        selectFileAction.triggered.connect(self._onSelectFile)
        self.contextMenu.addAction(selectFileAction)

        selectFolderAction = QAction("选择文件夹...", self)
        selectFolderAction.triggered.connect(self._onSelectFolder)
        self.contextMenu.addAction(selectFolderAction)

        openFileAction = QAction("打开文件", self)
        openFileAction.triggered.connect(self._onOpenFile)
        self.contextMenu.addAction(openFileAction)

        openFolderAction = QAction("打开文件夹", self)
        openFolderAction.triggered.connect(self.onOpenContainingFolder)
        self.contextMenu.addAction(openFolderAction)

        self.contextMenu.addSeparator()

        copyAction = QAction("复制", self)
        copyAction.triggered.connect(self.copy)
        self.contextMenu.addAction(copyAction)

        pasteAction = QAction("粘贴", self)
        pasteAction.triggered.connect(self.paste)
        self.contextMenu.addAction(pasteAction)

        cutAction = QAction("剪切", self)
        cutAction.triggered.connect(self.cut)
        self.contextMenu.addAction(cutAction)

        clearAction = QAction("清除", self)
        clearAction.triggered.connect(self.clear)
        self.contextMenu.addAction(clearAction)

    def _connectSignals(self) -> None:
        """连接信号"""
        self.textChanged.connect(self._updateActionsState)

    def _updateActionsState(self) -> None:
        """更新动作状态"""

        hasText = bool(self.text().strip())

        for action in self.contextMenu.actions():
            if action.text() == "打开文件":
                action.setEnabled(hasText)

            if action.text() == "打开文件夹":
                action.setEnabled(hasText)

    def _onSelectFile(self) -> None:
        """处理选择文件"""

        from PyQt6.QtWidgets import QFileDialog

        currentPath = self.text().strip()

        if currentPath and Path(currentPath).exists():
            if Path(currentPath).is_file():
                startDir = str(Path(currentPath).parent)
            else:
                startDir = currentPath
        else:
            startDir = os.path.expanduser("~")

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            startDir,
            self._fileFilters
        )

        if filePath:
            path = Path(filePath)
            self.setText(str(path))
            self.fileSelected.emit(path)

    def _onSelectFolder(self) -> None:
        """处理选择文件夹"""

        from PyQt6.QtWidgets import QFileDialog

        currentPath = self.text().strip()

        if currentPath and Path(currentPath).exists():
            if Path(currentPath).is_dir():
                startDir = currentPath
            else:
                startDir = str(Path(currentPath).parent)
        else:
            startDir = os.path.expanduser("~")

        folderPath = QFileDialog.getExistingDirectory(
            self,
            "选择文件夹",
            startDir
        )

        if folderPath:
            path = Path(folderPath)
            self.setText(str(path))
            self.folderSelected.emit(path)

    def _onOpenFile(self) -> None:
        """处理打开文件"""

        filePathText = self.text().strip()

        if not filePathText:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "警告",
                "请输入有效的文件路径"
            )
            return

        try:
            filePath = Path(filePathText)

            if not filePath.exists():
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "警告",
                    f"文件不存在: {filePath}"
                )
                return

            os.startfile(str(filePath))
            self.fileOpened.emit(filePath)

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "错误",
                f"无法打开文件: {str(e)}"
            )

    def onOpenContainingFolder(self):
        """打开文件所在文件夹"""

        if self.isValidFile():

            filePath = self.getSelectedPath()
            assert filePath is not None
            folderPath = filePath.parent

            try:
                os.startfile(str(folderPath))
                GLog.logInfo(f"📁 已打开文件夹: {folderPath}")

            except Exception as e:
                GLog.logInfo(f"❌ 无法打开文件夹: {e}")

        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "错误",
                "无法打开文件夹，请输入有效路径"
            )

    def contextMenuEvent(self, event):
        """重写上下文菜单事件"""
        self.contextMenu.exec(event.globalPos())

    def addCustomAction(
            self,
            actionText: str,
            callback,
            beforeAction: Optional[str] = None
    ):
        """添加自定义菜单项"""

        action = QAction(actionText, self)
        action.triggered.connect(callback)

        if beforeAction:
            for existingAction in self.contextMenu.actions():
                if existingAction.text() == beforeAction:
                    self.contextMenu.insertAction(
                        existingAction,
                        action
                    )
                    return

        self.contextMenu.addAction(action)

    def setFileFilters(
            self,
            fileFilters: str = "所有文件 (*.*)"
    ):
        """设置文件过滤器"""
        self._fileFilters = fileFilters

    def getSelectedPath(self) -> Optional[Path]:
        """获取当前路径"""

        if self.text():
            return Path(self.text())

        return None

    def isValidFile(self) -> bool:
        """检查当前路径是否存在"""

        if not self.text():
            return False

        try:
            return Path(self.text()).exists()
        except Exception:
            return False