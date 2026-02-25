##########################################################################################################
#   Description:    子脚本定义， 规定子脚本属性
#                   子脚本必须包含下面的属性：
#                   名称
#                   作者
#                   版本号
#                   链接(GitHub)
#                   使用说明
#                   类型
#                   启用
#
#   Authors:        BaiYuan <395642104@qq.com>
##########################################################################################################
from ..tool.common import tryDo
from page import Page
from path import PATH_README

import yaml
import os
from pathlib import Path
from typing import Type, Optional
from PyQt6.QtWidgets import QTabWidget, QRadioButton

class Subscript():
    '''子脚本大类, 所有子脚本需要继承于此类'''
    def __init__(self, 
                 name: str,
                 pageCls: Type[Page],
                 infoPath: Path,
                 descPath: Path):
        """子脚本初始化

        :param name: 脚本名字
        :param pageCls: 子脚本页面类, 用于实例化页面
        :param infoPath: info文件夹路径
        :param descPath: desc文件夹路径
        """             

        if not issubclass(pageCls, Page):
            raise TypeError("Must input Page class")
        
        self.pageCls = pageCls

        self.description: str = ""               # 简介
        self.name: str = name                    # 脚本名
        self.author: Optional[str] = None        # 作者
        self.version: Optional[str] = None       # 版本号
        self.link: Optional[str] = None          # 链接
        self.readme: Optional[str] = None        # 使用说明名称
        self.type: Optional[str] = None          # 类型(分类使用)
        self.enable: bool = True                 # 启用
        
        self.infoPath = infoPath            # info路径
        self.descriptionPath = descPath     # 描述路径
        self.rootPath = infoPath.parent     # info上级路径
        
        try:
            # 加载描述参数
            with self.descriptionPath.open(mode = "r", encoding = "utf-8") as f:
                for line in f:
                    line = line.rstrip()
                    if line.strip().startswith("#"):
                        continue
                    
                    self.description += line + "\n"
                    
            # 加载其他参数
            with self.infoPath.open(mode = "r", encoding = "utf-8") as f:
                data: dict = yaml.safe_load(f)
                
                for attr, name in zip(["author", "version", "link", "readme", "type", "enable"],
                                      ["author", "version", "link", "readme", "type", "enable"]):
                    if name not in data.keys():
                        raise KeyError(f"Not find {name} in {self.infoPath}")
                    setattr(self, attr, data[name])
            
        except Exception as e:
            raise Exception(f"[{self.name}] init failed: {str(e)}")

    def buildPage(self, tab: QTabWidget):
        """实例化页面并打开
        :param tab: 选卡项容器
        """
        myPage = self.pageCls(title = self.name)
        myPage.open(tab = tab)
        
    @tryDo(title = "打开Info")
    def openInfo(self):
        os.startfile(self.infoPath)
        
    @tryDo(title = "打开Description")
    def openDesc(self):
        os.startfile(self.descriptionPath)
        
    @tryDo(title = "打开readme")
    def openReadme(self):
        if self.readme is None:
            raise ValueError("没有设置使用说明")
        
        os.startfile(PATH_README / self.readme)
        
    @tryDo(title = "打开根路径")
    def openRoot(self):
        os.startfile(self.rootPath)

    def setEnabled(self, button: QRadioButton):
        '''设置激活属性'''
        
        self.enable = (button.text() == "T")
        
        with self.infoPath.open(mode = "r", encoding = "utf-8") as f:
            data: dict = yaml.safe_load(f)
            
        data["enable"] = self.enable

        with self.infoPath.open(mode = "w", encoding = "utf-8") as f:
            yaml.safe_dump(data, f)
            


