##########################################################################################################
#   Description: 设置页面
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from ..subPath import PATH_SET, PATH_PATTERN

from ui.imageSplit.Ui_imageSplitSetDialog import Ui_Seting

import yaml
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QButtonGroup, QWidget, QDialog)

class ImageSplitSetPage(QDialog, Ui_Seting):
    '''自动化路由计算器页面构建'''
    
    @staticmethod
    def getConfig()->dict:
        """返回一个配置字典

        :return: 
            {
                "withIndex": bool,
                "topRatio": float,
                "apiKey": str,
                "cabinetStr": str,
                "moveMod": str,
            }
        """        
        try:
            with PATH_SET.open("r", encoding = "utf-8") as f:
                return yaml.safe_load(f)
            
        except Exception:
            data = {
                "withIndex": True,
                "topRatio": 0.3,
                "apiKey": "",
                "cabinetStr": "",
                "moveMod": "Copy",
            }
            return data
            
    
    def __init__(self, parent):
        
        QDialog.__init__(self, parent)
        Ui_Seting.__init__(self)
        self.setupUi(self)          # 加载UI
        self.setWindowTitle("设置")
        self._loadWidgetAttr()

    def _loadWidgetAttr(self):
        '''加载组件属性'''

        self.buttonGroup_moveMod = QButtonGroup(self)
        self.buttonGroup_moveMod.addButton(self.radioButton_copy, 1)
        self.buttonGroup_moveMod.addButton(self.radioButton_cut, 2)
        self.radioButton_copy.setChecked(True)
        self.comboBox_topRatio.addItems([str(i / 10) for i in range(1, 11, 1)])

        with PATH_PATTERN.open("r", encoding = "utf-8") as f:
            for line in f:
                self.comboBox_pattern.addItem(line.strip())

        self.comboBox_topRatio.setEditable(False)
        self.comboBox_pattern.setEditable(True)
        
        self.load()

    def save(self):
        '''保存信息到文件'''
        try:
            withIndex = self.checkBox_withIndex.isChecked()                     # index
            topRatio = float(self.comboBox_topRatio.currentText())              # 顶部比例
            apiKey = self.lineEdit_apiKey.text()                                # 硅基流动API
            cabinetStr = self.comboBox_pattern.currentText().strip()            # 匹配模式
            checkedButton = self.buttonGroup_moveMod.checkedButton()
            moveMod = checkedButton.text() if checkedButton else "Copy"         # 移动模式
                
            data: dict = {
                "withIndex": withIndex,
                "topRatio": topRatio,
                "apiKey": apiKey,
                "cabinetStr": cabinetStr,
                "moveMod": moveMod,
            }

            with PATH_SET.open("w", encoding = "utf-8") as f:
                yaml.safe_dump(data, f)
        except Exception:
            pass
        
    def load(self):
        '''从文件加载信息'''
        try:
            with PATH_SET.open("r", encoding = "utf-8") as f:
                data = yaml.safe_load(f)
                
                self.checkBox_withIndex.setChecked(data["withIndex"])
                self.comboBox_topRatio.setCurrentText(str(data["topRatio"]))
                self.lineEdit_apiKey.setText(data["apiKey"])
                self.comboBox_pattern.setCurrentText(data["cabinetStr"])
                
                if data["moveMod"] == "Copy":
                    self.radioButton_copy.setChecked(True)
                else:
                    self.radioButton_cut.setChecked(True)
  
        except Exception:
            
            # 使用默认配置
            self.checkBox_withIndex.setChecked(True)
            self.comboBox_topRatio.setCurrentText(str(0.3))
            self.lineEdit_apiKey.setText("请输入API")
            self.comboBox_pattern.setCurrentIndex(0)
            self.radioButton_copy.setChecked(True)
        
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

