##########################################################################################################
#   Description: 页面基类
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Any, Dict, Optional

import yaml
import shutil
from PyQt6.QtWidgets import QCheckBox, QComboBox, QLineEdit, QMessageBox, QPlainTextEdit, QTabWidget, QWidget
from PyQt6.QtWidgets import QFileDialog

class Page(QWidget):
    '''工具页面基类'''

    EMPTY_PATH_TEXT = "."
    YAML_ENCODING = "utf-8"
    CONFIG_FILE_FILTER = "YAML配置文件 (*.yaml *.yml);;所有文件 (*)"

    def __init__(self, title: str, dataPath: Optional[Path] = None):
        """页面初始化

        :param title:    页面标题
        :param dataPath: 数据文件路径，输入数据文件路径可以使用页面的自动属性保存方法
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
        except Exception as error:
            QMessageBox.critical(
                tab,
                "PAGE_OPEN_ERROR",
                f"open '{self.title}' failed: {str(error)}"
            )

    def save(self):
        '''存储信息到文件中, 不会影响无关字段'''

        if self.dataPath is None:
            return

        try:
            self.dataPath.parent.mkdir(parents=True, exist_ok=True)

            oldData = {}

            if self.dataPath.exists():
                with self.dataPath.open("r", encoding=self.YAML_ENCODING) as file:
                    loadedData = yaml.safe_load(file) or {}

                if isinstance(loadedData, dict):
                    oldData = loadedData

            widgetData = self._collectWidgetData()

            oldData.update(widgetData)

            with self.dataPath.open("w", encoding=self.YAML_ENCODING) as file:
                yaml.safe_dump(oldData, file, allow_unicode=True)

        except Exception:
            pass

    def load(self):
        '''加载工具信息到组件中'''

        if self.dataPath is None:
            return

        if not self.dataPath.exists():
            return

        try:
            with self.dataPath.open("r", encoding=self.YAML_ENCODING) as file:
                data = yaml.safe_load(file) or {}

            self._applyWidgetData(data)
        except Exception:
            pass

    def exportData(self):
        '''交互式导出页面配置文件'''

        if self.dataPath is None:
            QMessageBox.warning(
                self,
                "导出配置失败",
                "当前页面没有配置文件路径，无法导出配置。"
            )
            return

        self.save()

        if not self.dataPath.exists():
            QMessageBox.warning(
                self,
                "导出配置失败",
                f"当前页面配置文件不存在:\n{self.dataPath}"
            )
            return

        exportPathText, _ = QFileDialog.getSaveFileName(
            self,
            "导出页面配置",
            str(self.dataPath.name),
            self.CONFIG_FILE_FILTER
        )

        if not exportPathText:
            return

        exportPath = Path(exportPathText)

        try:
            exportPath.parent.mkdir(parents=True, exist_ok=True)

            if self.dataPath.resolve() != exportPath.resolve():
                shutil.copy2(self.dataPath, exportPath)

            QMessageBox.information(
                self,
                "导出配置完成",
                f"页面配置已导出到:\n{exportPath}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "导出配置失败",
                str(error)
            )

    def importData(self):
        '''交互式导入页面配置文件'''

        if self.dataPath is None:
            QMessageBox.warning(
                self,
                "导入配置失败",
                "当前页面没有配置文件路径，无法导入配置。"
            )
            return

        importPathText, _ = QFileDialog.getOpenFileName(
            self,
            "导入页面配置",
            "",
            self.CONFIG_FILE_FILTER
        )

        if not importPathText:
            return

        importPath = Path(importPathText)

        if not importPath.exists():
            QMessageBox.warning(
                self,
                "导入配置失败",
                f"配置文件不存在:\n{importPath}"
            )
            return

        try:
            self.dataPath.parent.mkdir(parents=True, exist_ok=True)

            if importPath.resolve() != self.dataPath.resolve():
                shutil.copy2(importPath, self.dataPath)

            self.load()

            QMessageBox.information(
                self,
                "导入配置完成",
                f"页面配置已导入:\n{importPath}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "导入配置失败",
                str(error)
            )

    def remove(self):
        '''完全移除此组件'''

        self.save()

        for child in self.findChildren(QWidget):
            try:
                child.deleteLater()
            except Exception:
                pass

        self.deleteLater()

    def readPara(
            self,
            obj: object,
            isPath: bool = False,
            checkPath: bool = False,
            notFoundStr: str = "路径未找到"
    ) -> str | Path | None:
        """从某个控件对象中读取属性

        :param obj:         控件对象
        :param isPath:      是否以路径格式读取
        :param checkPath:   是否检查路径存在
        :param notFoundStr: 路径未找到时的提示字符串
        :return:            控件值、路径或None
        """

        value = self._readWidgetText(obj)

        if value == self.EMPTY_PATH_TEXT or not value:
            return None

        if not isPath:
            return value

        path = Path(value)

        if checkPath and not path.exists():
            raise FileNotFoundError(f"{notFoundStr}: {path}")

        return path

    def _collectWidgetData(self) -> Dict[str, Any]:
        '''收集页面控件数据'''

        data: Dict[str, Any] = {}

        for obj in self.findChildren(QLineEdit):
            self._saveWidgetValue(data, obj, obj.text())

        for obj in self.findChildren(QComboBox):
            self._saveWidgetValue(data, obj, obj.currentText())

        for obj in self.findChildren(QPlainTextEdit):
            self._saveWidgetValue(data, obj, obj.toPlainText())

        for obj in self.findChildren(QCheckBox):
            self._saveWidgetValue(data, obj, obj.isChecked())

        return data

    def _applyWidgetData(self, data: Dict[str, Any]):
        '''将数据应用到页面控件'''

        for obj in self.findChildren(QLineEdit):
            self._loadLineEditData(obj, data)

        for obj in self.findChildren(QComboBox):
            self._loadComboBoxData(obj, data)

        for obj in self.findChildren(QPlainTextEdit):
            self._loadPlainTextEditData(obj, data)

        for obj in self.findChildren(QCheckBox):
            self._loadCheckBoxData(obj, data)

    def _saveWidgetValue(self, data: Dict[str, Any], obj: QWidget, value: Any):
        '''保存单个控件值'''

        objectName = obj.objectName()

        if not objectName:
            return

        data[objectName] = value

    def _loadLineEditData(self, obj: QLineEdit, data: Dict[str, Any]):
        '''加载单行输入框数据'''

        objectName = obj.objectName()

        if objectName not in data:
            return

        obj.setText(str(data[objectName]))

    def _loadComboBoxData(self, obj: QComboBox, data: Dict[str, Any]):
        '''加载下拉框数据'''

        objectName = obj.objectName()

        if objectName not in data:
            return

        obj.setCurrentText(str(data[objectName]))

    def _loadPlainTextEditData(self, obj: QPlainTextEdit, data: Dict[str, Any]):
        '''加载多行文本框数据'''

        objectName = obj.objectName()

        if objectName not in data:
            return

        obj.setPlainText(str(data[objectName]))

    def _loadCheckBoxData(self, obj: QCheckBox, data: Dict[str, Any]):
        '''加载复选框数据'''

        objectName = obj.objectName()

        if objectName not in data:
            return

        obj.setChecked(bool(data[objectName]))

    def _readWidgetText(self, obj: object) -> str:
        '''从控件中读取文本'''

        if isinstance(obj, QLineEdit):
            return obj.text()

        if isinstance(obj, QComboBox):
            return obj.currentText()

        if isinstance(obj, QPlainTextEdit):
            return obj.toPlainText()

        raise NotImplementedError(f"使用了尚未支持的控件对象: '{type(obj).__name__}'")