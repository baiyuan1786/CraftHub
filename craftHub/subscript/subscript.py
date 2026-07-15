##########################################################################################################
#   Description:    子脚本定义，规定子脚本属性
#                   子脚本必须包含下面的属性：
#                   名称
#                   作者
#                   版本号
#                   链接(GitHub)
#                   使用说明
#                   类型
#                   启用
#
#   Authors:        BaiYuan <V:gzq395642104>
##########################################################################################################

import os
from pathlib import Path
from typing import Any, Dict, Optional, Type

import yaml
from PyQt6.QtWidgets import QRadioButton, QTabWidget

from page import Page
from path import PATH_README

from ..tool.common import tryDo

class Subscript:
    '''子脚本大类，所有子脚本需要继承于此类'''

    YAML_ENCODING = "utf-8"

    FIELD_AUTHOR = "author"
    FIELD_VERSION = "version"
    FIELD_LINK = "link"
    FIELD_README = "readme"
    FIELD_TYPE = "type"
    FIELD_ENABLE = "enable"

    ENABLE_TRUE_TEXT = "T"

    REQUIRED_INFO_FIELD_LIST = [
        FIELD_AUTHOR,
        FIELD_VERSION,
        FIELD_LINK,
        FIELD_README,
        FIELD_TYPE,
        FIELD_ENABLE,
    ]

    def __init__(
            self,
            name: str,
            pageCls: Type[Page],
            infoPath: Path,
            descPath: Path
    ):
        """子脚本初始化

        :param name:     脚本名字
        :param pageCls:  子脚本页面类，用于实例化页面
        :param infoPath: info文件路径
        :param descPath: desc文件路径
        """
        self._checkPageClass(pageCls)

        self.name = name
        self.pageCls = pageCls

        self.author: Optional[str] = None
        self.version: Optional[str] = None
        self.link: Optional[str] = None
        self.readme: Optional[str] = None
        self.type: Optional[str] = None
        self.enable: bool = True
        self.description: str = ""

        self.infoPath = infoPath
        self.descriptionPath = descPath
        self.rootPath = infoPath.parent

        self._loadSubscriptInfo()

    def buildPage(self, tab: QTabWidget):
        """实例化页面并打开

        :param tab: 选卡项容器
        """

        page = self.pageCls(title=self.name)
        page.open(tab=tab)

    @tryDo(title="打开Info")
    def openInfo(self):
        '''打开info文件'''

        self._openPath(self.infoPath)

    @tryDo(title="打开Description")
    def openDesc(self):
        '''打开description文件'''

        self._openPath(self.descriptionPath)

    @tryDo(title="打开readme")
    def openReadme(self):
        '''打开readme文件'''

        if self.readme is None:
            raise ValueError("没有设置使用说明")

        readmePath = PATH_README / self.readme

        if not readmePath.exists():
            raise FileNotFoundError(f"没有找到使用说明: {readmePath}")

        self._openPath(readmePath)

    @tryDo(title="打开根路径")
    def openRoot(self):
        '''打开子脚本根路径'''

        self._openPath(self.rootPath)

    def setEnabled(self, button: QRadioButton):
        '''设置启用属性'''

        self.enable = button.text() == self.ENABLE_TRUE_TEXT

        data = self._readInfoData()
        data[self.FIELD_ENABLE] = self.enable
        self._writeInfoData(data)

    def _loadSubscriptInfo(self):
        '''加载子脚本信息'''

        try:
            self.description = self._readDescription()
            infoData = self._readInfoData()
            self._checkInfoData(infoData)
            self._applyInfoData(infoData)
        except Exception as error:
            raise Exception(f"[{self.name}] init failed: {str(error)}")

    def _readDescription(self) -> str:
        '''读取子脚本描述'''

        if not self.descriptionPath.exists():
            raise FileNotFoundError(f"没有找到description文件: {self.descriptionPath}")

        lineList = []

        with self.descriptionPath.open(mode="r", encoding=self.YAML_ENCODING) as file:
            for line in file:
                cleanLine = line.rstrip()

                if cleanLine.strip().startswith("#"):
                    continue

                lineList.append(cleanLine)

        return "\n".join(lineList)

    def _readInfoData(self) -> Dict[str, Any]:
        '''读取info文件数据'''

        if not self.infoPath.exists():
            raise FileNotFoundError(f"没有找到info文件: {self.infoPath}")

        with self.infoPath.open(mode="r", encoding=self.YAML_ENCODING) as file:
            data = yaml.safe_load(file) or {}

        if not isinstance(data, dict):
            raise TypeError(f"info文件格式错误，应为字典结构: {self.infoPath}")

        return data

    def _writeInfoData(self, data: Dict[str, Any]):
        '''写入info文件数据'''

        with self.infoPath.open(mode="w", encoding=self.YAML_ENCODING) as file:
            yaml.safe_dump(data, file, allow_unicode=True)

    def _checkInfoData(self, data: Dict[str, Any]):
        '''检查info文件数据'''

        for fieldName in self.REQUIRED_INFO_FIELD_LIST:
            if fieldName not in data:
                raise KeyError(f"Not find {fieldName} in {self.infoPath}")

    def _applyInfoData(self, data: Dict[str, Any]):
        '''应用info文件数据'''

        self.author = data[self.FIELD_AUTHOR]
        self.version = data[self.FIELD_VERSION]
        self.link = data[self.FIELD_LINK]
        self.readme = data[self.FIELD_README]
        self.type = data[self.FIELD_TYPE]
        self.enable = bool(data[self.FIELD_ENABLE])

    @staticmethod
    def _checkPageClass(pageCls: Type[Page]):
        '''检查页面类是否合法'''

        if not issubclass(pageCls, Page):
            raise TypeError("Must input Page class")

    @staticmethod
    def _openPath(path: Path):
        '''打开路径'''

        os.startfile(path)