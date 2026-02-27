##########################################################################################################
#   Description: 文件数量计算工具
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from page import Page

from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QMessageBox, QTabWidget
)

class FileCounterPage(Page):
    """文件数量统计工具页面"""
    
    def __init__(self):
        """初始化文件数量统计页面
        
        :param title: 页面标题
        :param dataPath: 数据文件路径
        """
        super().__init__(title = "PageCounter")
        self.initUI()
    
    def initUI(self):
        """初始化界面"""
        mainLayout = QVBoxLayout()
        
        # 文件夹路径输入区域
        pathLayout = QHBoxLayout()
        
        self.folderLabel = QLabel("文件夹路径:")
        pathLayout.addWidget(self.folderLabel)
        
        self.folderPathEdit = QLineEdit()
        self.folderPathEdit.setObjectName("folderPathEdit")
        self.folderPathEdit.setPlaceholderText("请选择或输入文件夹路径")
        pathLayout.addWidget(self.folderPathEdit, stretch=1)
        
        self.browseButton = QPushButton("浏览")
        self.browseButton.clicked.connect(self.onBrowseFolder)
        pathLayout.addWidget(self.browseButton)
        
        mainLayout.addLayout(pathLayout)
        
        # 操作按钮区域
        buttonLayout = QHBoxLayout()
        
        self.countButton = QPushButton("开始统计")
        self.countButton.clicked.connect(self.onCountFiles)
        buttonLayout.addWidget(self.countButton)
        
        self.clearButton = QPushButton("清空结果")
        self.clearButton.clicked.connect(self.onClearResults)
        buttonLayout.addWidget(self.clearButton)
        
        mainLayout.addLayout(buttonLayout)
        
        # 结果展示区域
        resultLabel = QLabel("统计结果:")
        mainLayout.addWidget(resultLabel)
        
        self.resultTextEdit = QTextEdit()
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.resultTextEdit.setReadOnly(True)
        mainLayout.addWidget(self.resultTextEdit, stretch=1)
        
        self.setLayout(mainLayout)
    
    def onBrowseFolder(self):
        """浏览文件夹"""
        folderPath = QFileDialog.getExistingDirectory(
            self, 
            "选择文件夹",
            str(Path.home())
        )
        
        if folderPath:
            self.folderPathEdit.setText(folderPath)
            self.save()  # 保存当前路径
    
    def onCountFiles(self):
        """开始统计文件"""
        folderPath = self.folderPathEdit.text().strip()
        
        if not folderPath:
            QMessageBox.warning(self, "警告", "请先选择文件夹路径")
            return
        
        folder = Path(folderPath)
        
        if not folder.exists():
            QMessageBox.warning(self, "错误", f"文件夹不存在: {folderPath}")
            return
        
        if not folder.is_dir():
            QMessageBox.warning(self, "错误", f"路径不是文件夹: {folderPath}")
            return
        
        try:
            result = self.countFilesInDirectory(folder)
            self.displayResults(result)
        except PermissionError:
            QMessageBox.warning(self, "权限错误", "没有权限访问某些文件夹")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"统计过程中发生错误: {str(e)}")
    
    def countFilesInDirectory(self, directory: Path) -> Dict:
        """递归统计文件夹中的文件
        
        :param directory: 要统计的文件夹路径
        :return: 包含文件类型和数量的字典
        """
        fileTypes = {}
        totalFiles = 0
        
        # 使用walk方法递归遍历
        for filePath in directory.rglob("*"):
            if filePath.is_file():  # 只统计文件，忽略文件夹
                totalFiles += 1
                
                # 获取文件扩展名（小写）
                extension = filePath.suffix.lower()
                if not extension:  # 如果没有扩展名，标记为"未知类型"
                    extension = "unknown"
                else:
                    extension = extension[1:]  # 去掉点号
                
                # 更新该类型文件的数量
                fileTypes[extension] = fileTypes.get(extension, 0) + 1
        
        # 按数量降序排序
        sortedFileTypes = dict(
            sorted(fileTypes.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            "directory": str(directory),
            "fileTypes": sortedFileTypes,
            "totalFiles": totalFiles
            }
    
    def displayResults(self, result: Dict):
        """显示统计结果
        
        :param result: 统计结果字典
        """
        outputLines = []
        
        # 添加标题和摘要
        outputLines.append("=" * 50)
        outputLines.append(f"文件夹: {result['directory']}")
        outputLines.append("=" * 50)
        outputLines.append("")
        
        # 添加详细统计
        if result['totalFiles'] > 0:
            outputLines.append("文件类型统计:")
            outputLines.append("-" * 30)
            
            # 计算列宽
            maxTypeLen = max(len(ext) for ext in result['fileTypes'].keys())
            maxCountLen = max(len(str(count)) for count in result['fileTypes'].values())
            
            # 格式化的表头
            headerFormat = f"{{:<{maxTypeLen + 2}}} {{:>{maxCountLen + 2}}}"
            outputLines.append(headerFormat.format("类型", "数量"))
            outputLines.append("-" * (maxTypeLen + maxCountLen + 4))
            
            # 每行数据
            rowFormat = f"{{:<{maxTypeLen + 2}}} {{:>{maxCountLen + 2}}}"
            for fileType, count in result['fileTypes'].items():
                outputLines.append(rowFormat.format(fileType, count))
        else:
            outputLines.append("文件夹为空或没有文件")
        
        # 添加总计
        outputLines.append("")
        outputLines.append(f"总计: {result['totalFiles']} 个文件")
        outputLines.append("=" * 50)
        
        self.resultTextEdit.setText("\n".join(outputLines))
    
    def onClearResults(self):
        """清空结果"""
        self.resultTextEdit.clear()