##########################################################################################################
#   Description: 单个房间类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .cabinet import Cabinet
from .datedOBJs import DatedImages, DatedVideos
from .datedOBJ import DatedImage, DatedVideo

from craftHub.tool import DeepSeekOCR_SiliconFlow, gLog

import os
import re

from pathlib import Path
from typing import Optional, List, Tuple, Dict, Literal
from PyQt6.QtCore import pyqtSignal, QObject

class Room(QObject):
    '''一个房间
    房间 -> 复数个屏柜
    屏柜 -> 复数个日期图片
    '''
    progress = pyqtSignal(int ,int, int)    # 当前值 / 总值 / Level
    state = pyqtSignal(str, int)            # 信息 / Level
    level = 2
    
    roomPattern = re.compile(r'[\u4e00-\u9fa5]{2,5}(?:房|室|机房)')
    envDirName = "环境"                     # 环境文件夹名称
    ANCHOR_RANGE = 60 * 2                   # 锚定范围

    @classmethod
    def parseNameAndDate(cls, 
                   datedImages: DatedImages,
                   anchorVideo: Optional[DatedVideo],
                   ocrModel: DeepSeekOCR_SiliconFlow):
        """解析房间名字和房间开始时间
        搜索锚定视频一定时间范围内的图片， 寻找符合正则标准的名字

        :param datedImages: 待处理图片
        :param anchorVideo: 锚定视频
        :param ocrModel: OCR模型
        :return: 名字 + 开始日期 | None + Nome
        """        

        if anchorVideo is None:
            return None, None
        
        anchorDate = anchorVideo.date   # 锚定时间
        handleImages = [
            d for d in datedImages 
            if abs((d.date - anchorDate).total_seconds()) <= cls.ANCHOR_RANGE
        ]
        handleImages.sort(key = lambda d: d.date)

        # 从待处理照片当中搜寻名字
        for index, image in enumerate(handleImages):
            gLog.logInfo(f"解析房间名 {index}/{len(handleImages)} | \'{image}\'")
            result = ocrModel.ocr(imagePath = str(image))
            if not result:
                continue
            
            for text in result:
                match = cls.roomPattern.search(text)
                if match:
                    name = match.group()
                    date = image.date
                    return name, date
                
        return None, None
    
    def __init__(self,
                 name: Optional[str],
                 datedImages: DatedImages,
                 datedVideos: Optional[DatedVideos] = None,
                 ):
        """初始化房间信息, 无需过滤房间信息, 外部已经完成过滤
        
        :param name: 房间名, 上一级解析完成之后直接输入
        :param datedImages: 待处理的图片
        :param datedVideos: 待处理的视频, defaults to None
        """        
        super().__init__()
        
        # 基础信息
        self.name = name
        self.datedImages = datedImages
        self.datedVideos = datedVideos

        # 屏柜字典，需要进行分离构建
        self.cabinetDict: Dict[str, Cabinet] = {}   # 屏柜字典
        self.datedEnvImages = DatedImages()         # 环境照片
  
    def splitBuild(self, 
                   topRatio: float,
                   ocrModel: DeepSeekOCR_SiliconFlow,
                   cabinetStr: str):
        """分离构建屏柜

        :param topRatio: 顶部比例
        :param ocrModel: OCR模型
        :param cabinetStr: 屏柜匹配字符串
        """        

        currentCabinet:Optional[Cabinet] = None     # 当前屏柜
        
        for index, datedImage in enumerate(self.datedImages):
            self.state.emit(f"解析图片: {datedImage}", self.level)
            self.progress.emit(index, len(self.datedImages), self.level)

            try:
                gLog.enter()
                gLog.logInfo(f"房间 \'{self.name}\' | 解析屏柜名 \'{index}/{len(self.datedImages) - 1}\' | {datedImage}")

                newName = Cabinet.parseName(datedImage,
                                            topRatio,
                                            ocrModel,
                                            cabinetStr)

                # 发现屏柜
                if newName is not None:
                    gLog.logInfo(f"解析屏柜名 | 获取到新屏柜: {newName}")
                    if newName not in self.cabinetDict:
                        newCabinet = Cabinet(name = newName)
                        self.cabinetDict[newName] = newCabinet # 添加新屏柜到字典中
                    else:
                        pass
                    currentCabinet = self.cabinetDict[newName]

                # 不是屏柜，但已有当前屏柜
                if isinstance(currentCabinet, Cabinet):
                    gLog.logInfo(f"解析屏柜名 | 添加到屏柜: {currentCabinet.name} 中")
                    currentCabinet.append(image = datedImage)
                    
                # 没有当前屏柜，扔到其他文件夹下
                else:
                    gLog.logInfo(f"解析屏柜名 | 添加到环境文件中")
                    self.datedEnvImages.append(datedImage)


            except Exception as e:
                gLog.logInfo(f"解析屏柜名 | 检查屏柜出现错误，已停止: {str(e)}")
    
                # 丢弃当前屏柜:
                if isinstance(currentCabinet, Cabinet):
                    currentCabiName = currentCabinet.name
                    if currentCabiName in self.cabinetDict:
                        self.cabinetDict.pop(currentCabiName)
                        gLog.logInfo(f"解析屏柜名 | 丢弃当前屏柜: {currentCabiName}")
                break

        gLog.logInfo(f"房间 \'{self.name}\' | 获取到屏柜 \'{len(self.cabinetDict.keys())}\' 个")
        gLog.logInfo(f"房间 \'{self.name}\' | 获取到环境照片 \'{len(self.datedEnvImages)}\' 张")


    def save(self, 
             dstDir: Path, 
             withIndex: bool,
             moveMod: Literal["Copy", "Cut"] = "Copy"):
        """保存文件到目标文件夹
        如果是空房间, 那么直接保存到目标文件夹下
        如果不是空房间, 那么将在目标文件夹下创建该房间名字的文件夹，再保存在该文件夹下

        :param dstDir:      目标文件夹
        :param withIndex:   带有Index索引
        :param moveMod:     移动模式, defaults to "Copy"
        """

        roomDir = dstDir if self.name is None else dstDir / self.name    # 房间目录, 空房间将不创建新文件夹，直接保存在当前文件夹下
        envDir = roomDir / self.envDirName                               # 房间目录下的环境文件
        os.makedirs(roomDir, exist_ok = True)                            # 创建目录树
    
        # 保存环境文件
        try:
            gLog.logInfo(f"房间 \'{self.name}\' | 保存环境文件...")
            if self.datedEnvImages:
                self.datedEnvImages.save(
                    dstDir = envDir,
                    moveMod = moveMod
                )
            if self.datedVideos:
                self.datedVideos.save(
                    dstDir = envDir,
                    moveMod = moveMod
                )
        except Exception as e:
            gLog.logInfo(f"环境文件保存失败: {str(e)}")

        # 逐个保存屏柜文件
        for index, cabinet in enumerate(self.cabinetDict.values()) :
            try:
                gLog.logInfo(f"房间 \'{self.name}\' | 保存屏柜 \'{cabinet.name}\', 共 \'{len(cabinet)}\' 张")
                cabinet.save(dstDir = roomDir,
                             index = index if withIndex else None,
                             moveMod = moveMod)

            except Exception as e:
                gLog.logInfo(f"屏柜保存失败: {str(e)}")