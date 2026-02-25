##########################################################################################################
#   Description: 划分变电站
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from .datedOBJs import DatedImages, DatedVideos
from .substation import Substaion

from craftHub.tool import DeepSeekOCR_SiliconFlow
from craftHub.tool import gLog

import heapq
from pathlib import Path
from typing import (Optional, List, Tuple, Dict, Literal)
from PyQt6.QtCore import pyqtSignal, QObject

class Substations(QObject):
    '''变电站组
    变电站组 -> 复数个变电站
    变电站 -> 复数个房间
    房间 -> 复数个屏柜
    屏柜 -> 复数个日期图片
    '''
    progress = pyqtSignal(int ,int, int) # 当前值 / 总值 / Level
    state = pyqtSignal(str, int) # 信息 / Level
    level = 0

    def __init__(self, 
                 datedImages: DatedImages,
                 datedVideos: DatedVideos,
                 substationCount: int,
                 ):
        """构建变电站集合

        :param datedImages: 需处理的图片
        :param datedVideos: 需处理的视频
        :param substationCount: 将划分的变电站数量
        """        
        super().__init__()
        
        # 保存基本信息
        self.datedImages = datedImages
        self.datedVideos = datedVideos
        self.substationCount = substationCount

        # 变电站列表，需要进行分离构建
        self.substationList: List[Substaion] = []
        
    def splitBuildAndSave(self, 
                        topRatio: float,
                        ocrModel: DeepSeekOCR_SiliconFlow,
                        cabinetStr: str,
                        dstDir: Path, 
                        withIndex: bool,
                        moveMod: Literal["Copy", "Cut"] = "Copy"):
        '''分离构建变电站列表
        找到时间间隔最大的N个间隔点, 将其切割为N个图片列表并直接构造变电站
        优化版本，使用 heapq.nlargest
        每构建出一个变电站，就对这个变电站进行保存

        return: 返回变电站列表
        '''

        n = len(self.datedImages)
        if n <= self.substationCount:
            raise ValueError("变电站数量异常")
        
        # 需要找到的分割点数量
        split_count = self.substationCount - 1
        
        # 收集所有间隔及其位置（从索引1开始）
        intervals = []
        for i in range(1, n):
            intervals.append(((self.datedImages[i]).interval, i)) # type: ignore
        
        # 如果间隔数量不足，使用所有间隔位置
        if len(intervals) <= split_count:
            split_points = [idx for _, idx in intervals]
        else:
            # 使用 nlargest 找到最大的 split_count 个间隔
            largest_intervals = heapq.nlargest(split_count, intervals, key=lambda x: x[0])
            split_points = [idx for _, idx in largest_intervals]
        
        # 排序并分割
        split_points.sort()

        result = []
        start = 0
        for split_point in split_points:
            result.append(self.datedImages[start:split_point])
            start = split_point
        result.append(self.datedImages[start:])
        
        # 构建变电站
        datedImagesList = [DatedImages(datedImageList = r) for r in result]
        substationList: List[Substaion] = []

        # 找出变电站基本信息
        for index, d in enumerate(datedImagesList):
            
            self.progress.emit(index, len(datedImagesList), self.level)
            self.state.emit(f"解析变电站名字和日期", self.level)

            newName = Substaion.parseName(d, ocrModel)
            newSubstation = Substaion(name = newName,
                                      datedImages = d,
                                      datedVideos = self.datedVideos.sliceByDate(d.startDate, d.endDate)
                                      )

            substationList.append(newSubstation)
            
        # 显示信息
        for index, s in enumerate(substationList):
            s.showBaseInfo(index)
            
        # 分离构建变电站
        for index, newSubstation in enumerate(substationList):
            self.progress.emit(index, len(datedImagesList), self.level)
            self.state.emit(f"分离构建变电站: {newSubstation.name}", self.level)
    
            # 信号转发
            newSubstation.progress.connect(self.progress.emit)
            newSubstation.state.connect(self.state.emit)
            
            # 每构建一个变电站就保存一个
            newSubstation.splitBuild(
                topRatio = topRatio,
                ocrModel = ocrModel,
                cabinetStr = cabinetStr
            )
            newSubstation.save(
                dstDir = dstDir,
                withIndex = withIndex,
                moveMod = moveMod) # type: ignore

        self.substationList = substationList



