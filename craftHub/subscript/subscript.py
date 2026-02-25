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
from page import Page

import yaml
from pathlib import Path
from typing import Type
from PyQt6.QtWidgets import QTabWidget

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
        self.author: str = "void"                # 作者
        self.version: str = "void"               # 版本号
        self.link: str = "void"                  # 链接
        self.readme: str = "void"                # 使用说明名称
        self.type: str = "void"                  # 类型(分类使用)
        self.enable: bool = True                 # 启用
        
        self.infoPath = infoPath            # info路径
        self.descriptionPath = descPath     # 描述路径
        
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