##########################################################################################################
#   Description: 页面基类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
import yaml
from abc import abstractmethod
from typing import Optional, Literal
from pathlib import Path
from PyQt6.QtWidgets import (QTabWidget, QWidget, QMessageBox, QLineEdit, QComboBox, 
                             QPlainTextEdit, QCheckBox, QFileDialog)

class Page(QWidget):
    '''工具页面基类, 
    提供页面基础方法, 包括下面的方法
    1. open 在选卡项容器打开页面
    2. save 保存组件信息
    3. load 加载组件信息
    4. remove 移除组件
    '''
    @abstractmethod
    def __init__(self,
                 title: str,
                 dataPath: Optional[Path] = None):
        """页面初始化
        继承至此类的其他类需要重写此方法

        :param title: 页面标题
        :param dataPath: 数据文件路径， 输入数据文件路径可以使用页面的自动属性保存方法 , defaults to None
        """
        super().__init__()
        self.title = title
        self.dataPath = dataPath

    def open(self, tab: QTabWidget):
        """在选卡项容器打开该页面
        :param tab: 选卡项容器
        """        
        try:
            index = tab.addTab(self, self.title)
            tab.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(tab,
                                 "PAGE_OPEN_ERROR",
                                 f"open \'{self.title}\' failed: {str(e)}")

    def save(self):
        '''存储信息到文件中'''
        if self.dataPath is None:
            return
        
        try:
            data = {}
            for obj in self.findChildren(QLineEdit):
                data[obj.objectName()] = obj.text()
            
            for obj in self.findChildren(QComboBox):
                data[obj.objectName()] = obj.currentText()

            for obj in self.findChildren(QPlainTextEdit):
                data[obj.objectName()] = obj.toPlainText()
            
            for obj in self.findChildren(QCheckBox):
                data[obj.objectName()] = obj.isChecked()
            
            with self.dataPath.open("w", encoding = "utf-8") as f:
                yaml.safe_dump(data, f)
                # gLog.logInfo("[CraftHub]data safely saved")
        except Exception:
            pass
 
    def load(self):
        '''加载工具信息到组件中'''
        if self.dataPath is None:
            return
        
        try:
            with self.dataPath.open("r", encoding = "utf-8") as f:
                data = yaml.safe_load(f)
                # gLog.logInfo("[CraftHub]data safely loaded")
                
            for obj in self.findChildren(QLineEdit):
                obj.setText(data[obj.objectName()])
            
            for obj in self.findChildren(QComboBox):
                obj.setCurrentText(data[obj.objectName()])
                
            for obj in self.findChildren(QPlainTextEdit):
                obj.setPlainText(data[obj.objectName()])
                
            for obj in self.findChildren(QCheckBox):
                obj.setChecked(data[obj.objectName()])
                
        except Exception:
            pass
            
    def remove(self):
        '''完全移除此组件'''

        self.save()
        for child in self.findChildren(QWidget):
            try:
                # child.disconnect()
                child.deleteLater()
            except:
                pass
                
            self.deleteLater()
            
        