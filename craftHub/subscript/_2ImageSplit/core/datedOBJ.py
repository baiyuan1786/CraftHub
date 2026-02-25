##########################################################################################################
#   Description: 带有日期参数的图片类和视频类， 该类是图片划分的基本单位
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from craftHub.tool import gLog

import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Literal

class DatedOBJ:
    '''带有日期参数的文件'''
    
    datePattern = re.compile(r"(\d{8})_(\d{6})")
    def __init__(self, 
                 name: str, 
                 srcDir: Path):
        """
        :param name: 文件名字
        :param srcDir: 文件的文件夹
        """        
        
        path = srcDir / name
        if not path.exists():
            raise FileNotFoundError(f"OBJ Not Found: {name}")
        if not path.is_file():
            raise TypeError(f"OBJ is Not a File: {name}")
        
        match = self.datePattern.search(name)
        if not match:
            raise TypeError(f"OBJ Not Matched: {name}")
        
        self.name = name
        self.path = path
        self.srcDir = srcDir
        self.date = datetime.strptime(f"{match.group(1)}_{match.group(2)}", "%Y%m%d_%H%M%S")

    def save(self, 
             dstDir: Path, 
             moveMod: Literal["Copy", "Cut"]):
        """保存文件
        可以选择复制移动和剪切移动两种方式

        :param dstDir:  目标文件夹
        :param moveMod: 移动模式
        """   
        dstPath = dstDir / self.name
        if dstPath.exists():
            return

        assert moveMod in ["Copy", "Cut"]

        if moveMod == "Copy":
            shutil.copy2(src = self.path, dst = dstPath)
        else:
            shutil.move(src = self.path, dst = dstPath)
            
    def __str__(self) -> str:
        return str(self.path)
    
    def __sub__(self, other):
        return (other.date - self.date).total_seconds()

class DatedImage(DatedOBJ):
    '''带有日期属性的图片
    图片是分类的基本单位
    '''
    def __init__(self, 
                 name: str, 
                 srcDir: Path):

        super().__init__(name, srcDir)
        
        if self.path.suffix not in [".jpg", ".png"]:
            raise TypeError("OBJ is Not a Image")
        
        self.interval: int = 0  # 距离上一张照片的时间间隔

    def exists(self, dstImageList: List[str]):
        '''在某字符列表中存在'''
        return self.name in dstImageList
    
    def setInterval(self, otherDate: datetime):
        self.interval = (self.date - otherDate).seconds


class DatedVideo(DatedOBJ):
    '''带有日期属性的Video
    这类Video通常是环境录像'''
    def __init__(self, name: str, srcDir: Path):
        super().__init__(name, srcDir)
        
        if self.path.suffix not in [".mp4"]:
            raise TypeError("OBJ is Not a Video")
