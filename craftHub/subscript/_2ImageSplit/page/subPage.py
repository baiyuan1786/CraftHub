##########################################################################################################
#   Description: 自动路由定位工具页面创建函数
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from ..subPath import PATH_DATA, PATH_PATTERN
from .transThread import TransWorker
from .setPage import ImageSplitSetPage

from ui.imageSplit.Ui_imageSplit import Ui_Form
from craftHub.tool import gLog, tryDo, FileHander
from page import Page

import os
import re
from pathlib import Path
from typing import List
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QButtonGroup)

class ImageSplitPage(Page, Ui_Form):
    '''自动化路由计算器页面构建'''
    
    def __init__(self, title: str):
        Page.__init__(self, title, PATH_DATA)
        Ui_Form.__init__(self)
        self.setupUi(self)          # 加载UI
        self._loadWidgetAttr()      # 加载组件属性

    def _loadWidgetAttr(self):
        '''加载组件属性'''

        self.comboBox_substationCount.addItems([str(i) for i in range(0, 6, 1)])      
        self.comboBox_splitMod.addItems(["单文件夹模式",
                                         "多文件夹模式"])

        self.comboBox_substationCount.setEditable(True)
        self.comboBox_splitMod.setEditable(False)
        
        self._updateSubstationCount(self.comboBox_splitMod.currentText())

        self.progressBar_sta.setVisible(False)
        self.progressBar_room.setVisible(False)
        self.progressBar_cabinet.setVisible(False)

        self.load()
        
    def _updateSubstationCount(self, text: str):
        '''更新变电站数量组件状态'''
        self.comboBox_substationCount.setEnabled(text == "单文件夹模式")
        

    @tryDo(title = "选择源文件夹")
    def _selectSrc(self):
        '''选择源文件夹'''
        folderName = QFileDialog.getExistingDirectory(
            parent = None,                      # 父窗口
            caption = "选择源文件夹",            # 对话框标题
            directory = "",                     # 初始目录
            options = QFileDialog.Option.ShowDirsOnly
        ) 
        
        if folderName:
            self.lineEdit_src.setText(folderName)

    @tryDo(title = "选择输出路径")
    def _selectOutput(self):
        '''选择输出路径'''
        folderName = QFileDialog.getExistingDirectory(
            parent = None,                      # 父窗口
            caption = "选择输出路径",            # 对话框标题
            directory = "",                     # 初始目录
            options = QFileDialog.Option.ShowDirsOnly
        ) 
        
        if folderName:
            self.lineEdit_dst.setText(folderName)
    
    @tryDo(title = "打开源文件夹")
    def _openSrc(self):
        srcDir = self.lineEdit_src.text()
        os.startfile(srcDir)
        
    @tryDo(title = "打开目标文件夹")
    def _openDst(self):
        dstDir = self.lineEdit_dst.text()
        os.startfile(dstDir)    
               
    @tryDo(title = "清理文件夹", info = "清理已完成")
    def _clear(self):
        '''清理空文件夹并消除index前缀''' 

        reply = QMessageBox.question(
            None,
            "清理确认",
            "将清除所有空文件夹并清理index前缀, 确认要进行吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return

        dstDir = Path(self.lineEdit_dst.text())
        FileHander.removeEmptyFolders(folderDir = dstDir)    # 清除空文件夹

        if not dstDir.exists():
            raise FileNotFoundError(f"错误: 文件夹 '{dstDir}' 不存在")
        
        pattern = re.compile(r'^(\d+)_(.+)$')
        
        def collect_folders_with_depth(root: Path) -> List[tuple]:
            """
            收集所有文件夹及其深度（从根目录开始的层级）
            返回列表，每个元素是(文件夹路径, 深度)
            """
            folders_with_depth = []
            
            def _collect(current: Path, depth: int):
                # 遍历当前目录下的所有项目
                for item in current.iterdir():
                    if item.is_dir():
                        folders_with_depth.append((item, depth))
                        # 递归进入子目录
                        _collect(item, depth + 1)
            
            _collect(root, 0)
            return folders_with_depth
        
        # 收集所有文件夹及其深度
        folders_with_depth = collect_folders_with_depth(dstDir)
        
        if not folders_with_depth:
            gLog.logInfo(f"目录 {dstDir} 下没有子文件夹")
            return
        
        # 按深度降序排序（从最深的文件夹开始处理）
        folders_with_depth.sort(key=lambda x: x[1], reverse=True)
        
        # 统计信息
        renamed_count = 0
        skipped_count = 0
        error_count = 0
        
        gLog.logInfo(f"开始处理目录: {dstDir}")
        gLog.logInfo(f"找到 {len(folders_with_depth)} 个文件夹")
        
        # 处理每个文件夹
        for folder_path, depth in folders_with_depth:
            folder_name = folder_path.name
            
            # 检查是否匹配数字前缀模式
            match = pattern.match(folder_name)
            if match:
                # 提取数字前缀和剩余部分
                prefix = match.group(1)
                rest = match.group(2)
                
                # 构建新名称
                new_name = rest
                
                # 如果新名称为空，使用默认名称
                if not new_name.strip():
                    new_name = f"renamed_{prefix}"
                
                # 构建新路径
                new_path = folder_path.parent / new_name
                
                # 检查新路径是否已存在
                if new_path.exists():
                    gLog.logInfo(f"警告: 目标路径已存在，跳过重命名: {folder_path} -> {new_path}")
                    skipped_count += 1
                    continue
                
                try:
                    # 执行重命名
                    folder_path.rename(new_path)
                    gLog.logInfo(f"✓ 重命名成功: {folder_name} -> {new_name} (深度: {depth})")
                    renamed_count += 1
                except PermissionError:
                    gLog.logInfo(f"✗ 权限不足，无法重命名: {folder_path}")
                    error_count += 1
                except Exception as e:
                    gLog.logInfo(f"✗ 重命名失败 {folder_path}: {e}")
                    error_count += 1
            else:
                # 不匹配模式，跳过
                skipped_count += 1
        
        # 输出统计信息
        gLog.enter()
        gLog.logInfo("="*50)
        gLog.logInfo("处理完成!")
        gLog.logInfo(f"总文件夹数: {len(folders_with_depth)}")
        gLog.logInfo(f"成功重命名: {renamed_count}")
        gLog.logInfo(f"跳过: {skipped_count}")
        gLog.logInfo(f"错误: {error_count}")
        gLog.logInfo("="*50)

    def _set(self):
        '''调整工具设置'''
        setPage = ImageSplitSetPage(parent = self)
        setPage.exec()
    
    def toFinished(self):
        '''清除所有状态'''
        self.progressBar_sta.setVisible(False)
        self.progressBar_room.setVisible(False)
        self.progressBar_cabinet.setVisible(False)
        
        self.label_sta.setText("")
        self.label_room.setText("")
        self.label_cabinet.setText("")
        
        self.progressBar_sta.setValue(0)
        self.progressBar_room.setValue(0)
        self.progressBar_cabinet.setValue(0)
        
        self.pushButton_trans.setEnabled(True)
        self.pushButton_trans.setText("Trans")
        gLog.logInfo("====================转换结束====================")
        
        QMessageBox.information(
            None,
            "提示",
            "图片切割已完成",
            QMessageBox.StandardButton.Ok
        )
        
    def toStarted(self):
        '''重置到开始状态'''
        
        gLog.logInfo("====================开始转换====================")
        self.progressBar_sta.setVisible(True)
        self.progressBar_room.setVisible(True)
        self.progressBar_cabinet.setVisible(True)
        
        self.label_sta.setText("变电站构建进度")
        self.label_room.setText("房间构建进度")
        self.label_cabinet.setText("屏柜构建进度")
        
        self.progressBar_sta.setFormat("0 / 0")
        self.progressBar_room.setFormat("0 / 0")
        self.progressBar_cabinet.setFormat("0 / 0")
        
        self.pushButton_trans.setEnabled(False)
        self.pushButton_trans.setText("Running")

    @tryDo(title = "转换图片线程启动")
    def _trans(self):
        '''切割大量图片文件到子文件夹中
        支持按照分割模式分割图片, 包括单个房间， 单个站点， 多个站点
        '''
        def showError(errorStr: str):
                QMessageBox.critical(
                None,
                "转换出错",
                errorStr,
                QMessageBox.StandardButton.Ok
            )
        def updateProgressBar(curIndex: int, len: int, level: int):
            if level == 0:
                self.progressBar_sta.setRange(0, len)
                self.progressBar_sta.setValue(curIndex)
                self.progressBar_sta.setFormat(f"{curIndex} / {len}")
            elif level == 1:
                self.progressBar_room.setRange(0, len)
                self.progressBar_room.setValue(curIndex)
                self.progressBar_room.setFormat(f"{curIndex} / {len}")
            else:
                self.progressBar_cabinet.setRange(0, len)
                self.progressBar_cabinet.setValue(curIndex)
                self.progressBar_cabinet.setFormat(f"{curIndex} / {len}")
                
        def updateState(state: str, level: int):
            if level == 0:
                self.label_sta.setText(state)
            elif level == 1:
                self.label_room.setText(state)
            else:
                self.label_cabinet.setText(state)
        
        # 加载信息
        srcDir = Path(self.lineEdit_src.text())                             # 源文件夹
        dstDir = Path(self.lineEdit_dst.text())                             # 目标文件夹
        splitMod = self.comboBox_splitMod.currentText()                     # 分割模式
        substationCount = int(self.comboBox_substationCount.currentText())  # 变电站个数
        
        setData = ImageSplitSetPage.getConfig()
        apiKey = setData["apiKey"]          # 硅基流动API
        topRatio = setData["topRatio"]      # 顶部率
        cabinetStr = setData["cabinetStr"]  # 匹配字符串
        withIndex = setData["withIndex"]    # 带有索引
        moveMod = setData["moveMod"]        # 移动模式
        
        # 检查信息
        if not os.path.exists(srcDir):
            raise FileNotFoundError("源文件夹不存在")
        if not os.path.exists(dstDir):
            raise FileNotFoundError("目标文件夹不存在")
        if not apiKey:
            raise ValueError("请输入硅基流动APIkey")
        if os.listdir(dstDir):
            reply = QMessageBox.question(
                None,
                "确认",
                f"输出文件夹 '{dstDir}' 不为空。\n是否继续? 继续将跳过已有的文件。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # 构建并启动线程
        worker = TransWorker(
            srcDir,
            dstDir,
            apiKey,
            substationCount,
            topRatio,
            cabinetStr,
            withIndex,
            splitMod, # type: ignore
            moveMod,  # type: ignore
        )
        worker.started.connect(self.toStarted)
        worker.finished.connect(self.toFinished)
        worker.error.connect(showError)
        worker.progress.connect(updateProgressBar)
        worker.state.connect(updateState)
        worker.start()

            

