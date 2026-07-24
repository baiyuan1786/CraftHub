##########################################################################################################
#   Description: 扩展单行输入框
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from PyQt6.QtWidgets import QLineEdit, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal
from pathlib import Path
import os
from craftHub.tool import GLog

from typing import List, Literal, Optional

class ExtendedLineEdit(QLineEdit):
    """带右键菜单的增强版QLineEdit"""
    
    # 自定义信号
    fileSelected = pyqtSignal(Path)  # 文件选择信号
    fileOpened = pyqtSignal(Path)    # 文件打开信号
    
    def __init__(self,
                 parent=None):
        """初始化ExtendedLineEdit
        
        :param parent: 父级窗口
        """
        super().__init__(parent)
        
        # 创建右键菜单
        self._createContextMenu()
        
        # 连接信号
        self._connectSignals()
        self._updateActionsState()
    
    def _createContextMenu(self) -> None:
        """创建上下文菜单"""
        self.contextMenu = QMenu(self)
        
        # 选择文件操作
        selectFileAction = QAction("选择文件...", self)
        selectFileAction.triggered.connect(self._onSelectFile)
        self.contextMenu.addAction(selectFileAction)
        
        # 打开文件操作
        openFileAction = QAction("打开文件", self)
        openFileAction.triggered.connect(self._onOpenFile)
        self.contextMenu.addAction(openFileAction)
        
        # 打开文件夹操作
        openFolderAction = QAction("打开文件夹", self)
        openFolderAction.triggered.connect(self.onOpenContainingFolder)
        self.contextMenu.addAction(openFolderAction)
        
        # 分隔线
        self.contextMenu.addSeparator()
        
        # 复制操作
        copyAction = QAction("复制", self)
        copyAction.triggered.connect(self.copy)
        self.contextMenu.addAction(copyAction)
        
        # 粘贴操作
        pasteAction = QAction("粘贴", self)
        pasteAction.triggered.connect(self.paste)
        self.contextMenu.addAction(pasteAction)
        
        # 剪切操作
        cutAction = QAction("剪切", self)
        cutAction.triggered.connect(self.cut)
        self.contextMenu.addAction(cutAction)
        
        # 清除操作
        clearAction = QAction("清除", self)
        clearAction.triggered.connect(self.clear)
        self.contextMenu.addAction(clearAction)
    
    def _connectSignals(self) -> None:
        """连接信号"""
        # 更新打开文件操作的可用状态
        self.textChanged.connect(self._updateActionsState)
    
    def _updateActionsState(self) -> None:
        """更新动作状态"""
        # 根据输入决定"打开文件"是否可用
        hasText = bool(self.text().strip())
        
        for action in self.contextMenu.actions():
            if action.text() == "打开文件":
                action.setEnabled(hasText)
            if action.text() == "打开文件夹":
                action.setEnabled(hasText)
            
    
    def _onSelectFile(self) -> None:
        """处理选择文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        # 获取当前路径（如果已有路径则使用父目录）
        currentPath = self.text().strip()
        if currentPath and Path(currentPath).exists():
            startDir = str(Path(currentPath).parent)
        else:
            startDir = os.path.expanduser("~")
        
        # 打开文件对话框
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            startDir,
            "所有文件 (*.*)"
        )
        
        if filePath:
            # 更新LineEdit文本
            self.setText(filePath)
            
            # 发出信号
            self.fileSelected.emit(Path(filePath))
    
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
            
            # 使用系统默认程序打开文件
            import os
            os.startfile(str(filePath))
            
            # 发出信号
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
            folderPath = filePath.parent
            
            import os
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
                f"无法打开文件夹，请输入有效的路径"
            )
    
    def contextMenuEvent(self, event):
        """重写上下文菜单事件
        
        :param event: 上下文菜单事件
        """
        # 显示自定义右键菜单
        self.contextMenu.exec(event.globalPos())
    
    def addCustomAction(self,
                        actionText: str,
                        callback,
                        beforeAction: Optional[str] = None):
        """添加自定义菜单项
        
        :param actionText: 动作文本
        :param callback: 回调函数
        :param beforeAction: 在哪个动作之前插入（动作文本）
        """
        action = QAction(actionText, self)
        action.triggered.connect(callback)
        
        if beforeAction:
            # 查找目标动作的位置
            actions = self.contextMenu.actions()
            for i, existingAction in enumerate(actions):
                if existingAction.text() == beforeAction:
                    self.contextMenu.insertAction(existingAction, action)
                    return
        
        # 如果没有指定位置或没找到，添加到末尾
        self.contextMenu.addAction(action)
    
    def setFileFilters(self,
                       fileFilters: str = "所有文件 (*.*)"):
        """设置文件过滤器（用于选择文件对话框）
        
        :param fileFilters: 文件过滤器字符串
        """
        self._fileFilters = fileFilters
    
    def getSelectedPath(self) -> Path:
        """获取选择的路径
        
        :return: Path对象
        """
        return Path(self.text()) if self.text() else None # type: ignore # 
    
    def isValidFile(self) -> bool:
        """检查当前输入是否为有效文件
        
        :return: True如果是有效文件，否则False
        """
        if not self.text():
            return False
        
        try:
            return Path(self.text()).exists()
        except:
            return False

# 使用示例
class ExampleUsage:
    """示例用法"""
    
    def __init__(self):
        """初始化"""
        from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
        
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setWindowTitle("ExtendedLineEdit示例")
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加说明标签
        label = QLabel("右键点击输入框查看菜单:")
        layout.addWidget(label)
        
        # 创建增强版LineEdit
        self.lineEdit = ExtendedLineEdit()
        self.lineEdit.setPlaceholderText("请输入文件路径或右键选择文件...")
        
        # 设置文件过滤器（可选）
        self.lineEdit.setFileFilters("文本文件 (*.txt *.csv);;PDF文件 (*.pdf);;所有文件 (*.*)")
        
        # 连接信号
        self.lineEdit.fileSelected.connect(self.onFileSelected)
        self.lineEdit.fileOpened.connect(self.onFileOpened)
        
        layout.addWidget(self.lineEdit)
        
        # 添加自定义菜单项
        self.lineEdit.addCustomAction(
            actionText = "打开所在文件夹",
            callback = self.onOpenContainingFolder,
            beforeAction = "清除"
        )
        
        self.window.setLayout(layout)
    
    def onFileSelected(self, filePath: Path):
        """文件选择事件处理
        
        :param filePath: 选择的文件路径
        """
        GLog.logInfo(f"✅ 文件已选择: {filePath}")
        # 可以在这里添加额外的处理逻辑
    
    def onFileOpened(self, filePath: Path):
        """文件打开事件处理
        
        :param filePath: 打开的文件路径
        """
        GLog.logInfo(f"📂 文件已打开: {filePath}")
    
    def onOpenContainingFolder(self):
        """打开文件所在文件夹"""
        if self.lineEdit.isValidFile():
            filePath = self.lineEdit.getSelectedPath()
            folderPath = filePath.parent
            
            import os
            try:
                os.startfile(str(folderPath))
                GLog.logInfo(f"📁 已打开文件夹: {folderPath}")
            except Exception as e:
                GLog.logInfo(f"❌ 无法打开文件夹: {e}")
    
    def run(self):
        """运行示例"""
        self.window.show()
        self.app.exec()

# 测试代码
if __name__ == "__main__":
    # 运行示例
    example = ExampleUsage()
    example.run()


