##########################################################################################################
#   Description: 带有日期参数的图片类和视频类集合
#                用于处理复数图片
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .datedOBJ import DatedOBJ, DatedImage, DatedVideo

from craftHub.tool import FileHander
from craftHub.tool import gLog

import os
from pathlib import Path
from datetime import datetime
from typing import List, Literal, Optional

class DatedOBJs:
    '''带有日期属性的文件集合'''
    def __init__(self, 
                 suffix: Optional[str] = None,
                 srcDir: Optional[Path] = None,
                 datedOBJList: Optional[List] = None,
                 dateOBJType = DatedOBJ):
        """
        :param suffix: 匹配文件后缀 defaults to None
        :param srcDir: 输入源文件夹时，将读取源文件夹中的所有, defaults to None
        :param datedOBJList: 也支持输入文件列表直接初始化, defaults to None
        """     
        
        if not issubclass(dateOBJType, DatedOBJ):
            raise TypeError("数据类型只能是DatedOBJ的子类")
       
        # 源文件夹初始化
        if srcDir is not None:
            datedOBJList = []
            for imageName in os.listdir(srcDir):
                if suffix and not imageName.endswith(suffix):
                    continue
                
                try:
                    datedOBJList.append(dateOBJType(imageName, srcDir))
                except Exception:
                    pass

            datedOBJList.sort(key = lambda x: x.date)
            self.datedOBJList = datedOBJList

        # 日期图片列表初始化
        elif datedOBJList is not None:
            self.datedOBJList = datedOBJList
            
        # 空的日期文件
        else:
            self.datedOBJList = []
 
        self.startDate = self.datedOBJList[0].date if self.datedOBJList else None
        self.endDate = self.datedOBJList[-1].date if self.datedOBJList else None
        self.dateOBJType = dateOBJType
        
    def save(self, 
             dstDir: Path, 
             moveMod: Literal["Copy", "Cut"]):
        """保存文件
        将每一个文件都移动到目标目录下

        :param dstDir:  目标文件夹
        :param moveMod: 移动模式
        """   
        if not self.__bool__():
            return

        os.makedirs(dstDir, exist_ok = True)
        for d in self.datedOBJList:
            d.save(dstDir, moveMod)

    def append(self, datedOBJ: DatedOBJ):
        self.datedOBJList.append(datedOBJ)

    def __getitem__(self, key):
        """支持索引和切片"""
    
        if isinstance(key, slice):
            return DatedOBJs(datedOBJList = self.datedOBJList[key.start:key.stop:key.step],
                             dateOBJType = self.dateOBJType) # 处理切片
        elif isinstance(key, int):
            return self.datedOBJList[key] # 处理整数索引
        else:
            raise TypeError("索引必须是整数或切片")
        
    def __setitem__(self, index, value):
        """支持 obj[index] = value 赋值"""
        self.datedOBJList[index] = value
    
    def __delitem__(self, index):
        """支持 del obj[index] 删除"""
        del self.datedOBJList[index]
    
    def __len__(self):
        """支持 len(obj)"""
        return len(self.datedOBJList)  

    def __iter__(self):
        """返回迭代器"""
        return iter(self.datedOBJList)

    def __bool__(self):
        return len(self.datedOBJList) > 0

class DatedImages(DatedOBJs):
    '''带有日期属性的图片列表'''
    def __init__(self, 
                 srcDir: Optional[Path] = None,
                 datedImageList: Optional[List[DatedImage]] = None):
        '''读取源文件夹之中所有格式匹配的图片'''

        super().__init__(suffix = ".jpg",
                         srcDir = srcDir,
                         datedOBJList = datedImageList,
                         dateOBJType = DatedImage)
 
        self._setInterval()

    def append(self, datedImage: DatedImage | Path):
        if isinstance(datedImage, Path):
            self.datedOBJList.append(DatedImage(name = datedImage.name, srcDir = datedImage.parent))  
        else:
            self.datedOBJList.append(datedImage)  

    def _setInterval(self):
        '''为列表之中的每一张图片设置间隔'''
        for index, datedImage in enumerate(self.datedOBJList):
            if index == 0:
                continue
            datedImage.setInterval(self.datedOBJList[index - 1].date)

    def filter(self, dstDir: Path):
        '''过滤目标文件夹之中存在的图片'''
        
        dstImageList = FileHander.getImageNames(folderDir = dstDir)
        countSrc = len(self.datedOBJList)
        countDst = len(dstImageList)

        self.datedOBJList = [f for f in self.datedOBJList if not f.exists(dstImageList)]
        countNow = len(self.datedOBJList)
        countExisted = countSrc - countNow

        gLog.logInfo(f"设置 | 源文件夹: \'{countSrc}\' 张照片")
        gLog.logInfo(f"设置 | 目标文件夹: \'{countDst}\' 张照片")
        gLog.logInfo(f"设置 | 已存在: \'{countExisted}\' 张照片")
        gLog.logInfo(f"设置 | 筛选后剩余: \'{countNow}\' 张照片")
        
    def sliceByDate(self, 
                    startDate: Optional[datetime] = None, 
                    endDate: Optional[datetime] = None):
        """按时间切片
        开始或者结束时间为空时表示不限制
        使用左闭右开区间

        :param startDate: 开始时间, defaults to None
        :param endDate: 结束时间, defaults to None
        """        

        if startDate is None and endDate is None:
            return DatedImages(datedImageList = self.datedOBJList)
        elif startDate is None:
            return DatedImages(datedImageList = [d for d in self.datedOBJList if d.date < endDate])
        elif endDate is None:
            return DatedImages(datedImageList = [d for d in self.datedOBJList if d.date >= startDate])
        else:
            return DatedImages(datedImageList = [d for d in self.datedOBJList if d.date >= startDate and d.date < endDate])

class DatedVideos(DatedOBJs):
    '''带有日期属性的Video列表'''
    def __init__(self, 
                 srcDir: Optional[Path] = None,
                 datedVideoList: Optional[List[DatedVideo]] = None):
        '''读取源文件夹所有符合条件的Video'''
        
        super().__init__(suffix = ".mp4",
                         srcDir = srcDir,
                         datedOBJList = datedVideoList,
                         dateOBJType = DatedVideo)

    def append(self, datedVideo: DatedVideo | Path):
        if isinstance(datedVideo, Path):
            self.datedOBJList.append(DatedVideo(name = datedVideo.name, srcDir = datedVideo.parent))  
        else:
            self.datedOBJList.append(datedVideo)  

    def sliceByDate(self, 
                    startDate: Optional[datetime] = None, 
                    endDate: Optional[datetime] = None):
        """按照时间对视频切片
        开始或者结束时间为空时表示不限制

        :param startDate: 开始时间, defaults to None
        :param endDate: 结束时间, defaults to None
        """        
        
        if startDate is None and endDate is None:
            return DatedVideos(datedVideoList = self.datedOBJList)
        elif startDate is None:
            return DatedVideos(datedVideoList = [d for d in self.datedOBJList if d.date < endDate])
        elif endDate is None:
            return DatedVideos(datedVideoList = [d for d in self.datedOBJList if d.date >= startDate])
        else:
            return DatedVideos(datedVideoList = [d for d in self.datedOBJList if d.date >= startDate and d.date < endDate])