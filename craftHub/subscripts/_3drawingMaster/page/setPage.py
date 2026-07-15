##########################################################################################################
#   Description: 设置页面
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ..subPath import PATH_SET
from ..ui.Ui_drawingMasterSet import Ui_DMset
from ..core import DrawingMasterCore

from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QButtonGroup, QWidget, QDialog)

import yaml
from typing import Dict
from craftHub.tool import GLog

class DrawingMasterConfig:
    """绘图大师配置, 文件接口"""

    # 弃用
    DEFAULT_CONFIG = {
        "convas": "",
        "project": "默认项目",
        "plotter": "",
        "date": "",
        "blockCount": 0,
        "insertCableLay": False,
        "insertNetLink": False,
        "oleType": "xlBitmap"
    }

    @classmethod
    def getConfig(cls) -> dict:
        """从配置文件读取配置"""
        
        if not PATH_SET.exists():
            raise FileNotFoundError("还未进行过设置！")
        
        try:
            with PATH_SET.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            config = cls.DEFAULT_CONFIG.copy()
            config.update(data)
            return config

        except Exception as e:
            GLog.logInfo(f"绘图大师设置 | 加载文件错误: {str(e)}")
            return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def saveConfig(cls, data: dict):
        """保存配置到文件"""

        try:
            # 无关字段不能丢弃
            if PATH_SET.exists():
                with PATH_SET.open("r", encoding="utf-8") as file:
                    oldConfig = yaml.safe_load(file) or {}
            else:
                oldConfig = {}

            config = cls.DEFAULT_CONFIG.copy()
            config.update(oldConfig)
            config.update(data)

            PATH_SET.parent.mkdir(parents=True, exist_ok=True)

            with PATH_SET.open("w", encoding="utf-8") as file:
                yaml.safe_dump(config, file, allow_unicode=True)

        except Exception as error:
            GLog.logInfo(f"绘图大师设置 | 保存文件错误: {str(error)}")

class DrawingMasterSetPage(QDialog, Ui_DMset):

    '''绘图大师设置页面'''
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        Ui_DMset.__init__(self)
        self.setupUi(self)          # 加载UI
        self.setWindowTitle("设置")
        self._loadWidgetAttr()
    
    def _configItems(self):
        """集中声明所有配置项：key、组件、默认值、读取函数、写入函数"""
        return {
            "convas": {
                "widget": self.lineEdit_convas,
                "default": "",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "project": {
                "widget": self.lineEdit_project,
                "default": "默认项目",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "plotter": {
                "widget": self.combobox_plotter,
                "default": "",
                "get": lambda w: w.currentText(),
                "set": lambda w, v: w.setCurrentText(str(v)),
            },
            "date": {
                "widget": self.lineEdit_date,
                "default": "",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "blockCount": {
                "widget": self.lineEdit_blockCount,
                "default": 0,
                "get": lambda w: int(w.text() or 0),
                "set": lambda w, v: w.setText(str(v)),
            },
            "insertCableLay": {
                "widget": self.checkBox_InsertCableLay,
                "default": False,
                "get": lambda w: w.isChecked(),
                "set": lambda w, v: w.setChecked(bool(v)),
            },
            "insertNetLink": {
                "widget": self.checkBox_InsertNetLink,
                "default": False,
                "get": lambda w: w.isChecked(),
                "set": lambda w, v: w.setChecked(bool(v)),
            },
            "oleType": {
                "widget": self.combobox_oleType,
                "default": "xlBitmap",
                "get": lambda w: w.currentText(),
                "set": lambda w, v: w.setCurrentText(str(v)),
            },
            "exportFormat": {
                "widget": self.combobox_exportFormat,
                "default": "dxf",
                "get": lambda w: w.currentText(),
                "set": lambda w, v: w.setCurrentText(str(v)),
            },
            "approve": {
                "widget": self.lineEdit_approve,
                "default": "approve",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "review1": {
                "widget": self.lineEdit_review1,
                "default": "review1",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "check": {
                "widget": self.lineEdit_check,
                "default": "check",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "design": {
                "widget": self.lineEdit_design,
                "default": "design",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "draw": {
                "widget": self.lineEdit_draw,
                "default": "draw",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "approveNum": {
                "widget": self.lineEdit_approveNum,
                "default": "approveNum",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "review1Num": {
                "widget": self.lineEdit_review1Num,
                "default": "review1Num",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "checkNum": {
                "widget": self.lineEdit_checkNum,
                "default": "checkNum",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "designNum": {
                "widget": self.lineEdit_designNum,
                "default": "designNum",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "drawNum": {
                "widget": self.lineEdit_drawNum,
                "default": "drawNum",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "layout": {
                "widget": self.combobox_layout,
                "default": "grid",
                "get": lambda w: w.currentText(),
                "set": lambda w, v: w.setCurrentText(str(v)),
            },
            # IDN配置
            "idnName": {
                "widget": self.plainTextEdit_idnName,
                "default": "默认idn设备名",
                "get": lambda w: w.toPlainText(),
                "set": lambda w, v: w.setPlainText(str(v)),
            },
            "idnHeightU": {
                "widget": self.lineEdit_idnHeightU,
                "default": 4,
                "get": lambda w: int(w.text()),
                "set": lambda w, v: w.setText(str(v)),
            },
            "idnPanel": {
                "widget": self.lineEdit_idnPanel,
                "default": "默认idn设备面板图",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "idnConnection": {
                "widget": self.lineEdit_idnConnection,
                "default": "默认idn连接面板图",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            
            # DDN配置
            "ddnName": {
                "widget": self.plainTextEdit_ddnName,
                "default": "默认ddn设备名",
                "get": lambda w: w.toPlainText(),
                "set": lambda w, v: w.setPlainText(str(v)),
            },
            "ddnHeightU": {
                "widget": self.lineEdit_ddnHeightU,
                "default": 4,
                "get": lambda w: int(w.text()),
                "set": lambda w, v: w.setText(str(v)),
            },
            "ddnPanel": {
                "widget": self.lineEdit_ddnPanel,
                "default": "默认ddn设备面板图",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "ddnConnection": {
                "widget": self.lineEdit_ddnConnection,
                "default": "默认ddn连接面板图",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            
            # 其他块配置
            "frameLeft": {
                "widget": self.lineEdit_frameLeft,
                "default": "左图框示例",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "frameRight": {
                "widget": self.lineEdit_frameRight,
                "default": "右图框示例",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            "legend": {
                "widget": self.lineEdit_legend,
                "default": "图例示例",
                "get": lambda w: w.text(),
                "set": lambda w, v: w.setText(str(v)),
            },
            
        }

    def _loadWidgetAttr(self):
        '''加载组件属性'''

        self.combobox_plotter.addItems(list(DrawingMasterCore.PLOTTER_PROFILE_DICT.keys()))
        self.combobox_plotter.setEditable(False)
        
        self.combobox_oleType.addItems(DrawingMasterCore.OLE_TYPES)
        self.combobox_exportFormat.addItems(DrawingMasterCore.EXPORT_FORMATS)
        self.combobox_layout.addItems(DrawingMasterCore.LAYOUT_FORMATS)
        self.load()

    def save(self):
        """保存信息到文件"""
        try:
            data = {}

            for key, item in self._configItems().items():
                widget = item["widget"]
                data[key] = item["get"](widget)

            DrawingMasterConfig.saveConfig(data)

        except Exception as e:
            GLog.logInfo(f"绘图大师设置 | 保存文件错误: {str(e)}")
        
    def load(self):
        """从文件加载信息"""
        
        try:
            data = DrawingMasterConfig.getConfig()
        except Exception:
            data = {}

        try:
            for key, item in self._configItems().items():
                widget = item["widget"]
                value = data.get(key, item["default"])
                item["set"](widget, value)

        except Exception as e:
            GLog.logInfo(f"绘图大师设置 | 加载文件错误: {str(e)}")
        
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

