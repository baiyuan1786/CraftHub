##########################################################################################################
#   Description: 处理单个变电站信息
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .datedOBJs import DatedImages, DatedVideos
from .room import Room

from craftHub.tool import DeepSeekOCR_SiliconFlow, gLog

import re
from datetime import datetime

from pathlib import Path
from typing import Optional, List, Tuple, Dict, Literal
from PyQt6.QtCore import pyqtSignal, QObject

class Substaion(QObject):
    '''变电站
    变电站 -> 复数个房间
    房间 -> 复数个屏柜
    屏柜 -> 复数个日期图片
    '''
    progress = pyqtSignal(int ,int, int) # 当前值 / 总值 / Level
    state = pyqtSignal(str, int) # 信息 / Level
    level = 1
    
    REC_NAME_MAX_COUNT = 3
    SAME_ROOM_THR = 60 * 10
    sitePattern = re.compile(r'^((?:1[0-9]{2}|[2-4][0-9]{2}|500|1[0-9]|[2-9][0-9]|10))([kK][vV])([\u4e00-\u9fa5a-zA-Z0-9]+?)(?:变电|变电站|站|变)')
    
    @classmethod
    def parseName(cls, 
                  datedImages: DatedImages,
                  ocrModel: DeepSeekOCR_SiliconFlow) -> Optional[str]:
        """解析变电站名称

        :param datedImages: 该变电站的全部名称
        :param ocrModel: OCR模型
        :return: 变电站名称 | None
        示例: 110kV千官站
        """        

        # 从照片解析
        for i in range(min(cls.REC_NAME_MAX_COUNT, len(datedImages))):
            gLog.enter()
            gLog.logInfo(f"解析站名 | \'{datedImages[i]}\'")
            result = ocrModel.ocr(str(datedImages[i]))
            
            if not result:
                continue
            result = [t.replace("千伏", "kV").replace("变电站", "站") for t in result]
            
            for text in result:
                match = cls.sitePattern.search(text)
                if match:
                    voltageNumber = match.group(1)
                    stationName = match.group(3)
                    
                    stationFullName = voltageNumber + "kV" + stationName + "站"
                    gLog.logInfo(f"解析站名 | 搜索到名称 \'{stationFullName}\'")
                    return stationFullName
                
        # 从父目录名字解析
        try:
            parentDirName = datedImages[0].path.parent.stem # type: ignore
            match = cls.sitePattern.search(parentDirName)
            if match:
                voltageNumber = match.group(1)
                stationName = match.group(3)
                stationFullName = voltageNumber + "kV" + stationName + "站"
                gLog.logInfo(f"解析站名 | 从父目录名字解析 | 搜索到名称 \'{stationFullName}\'")
                return stationFullName

        except Exception:
            gLog.logInfo(f"从父目录解析站名失败")

        gLog.logInfo(f"解析站名失败")
        return None
    
    def __init__(self, 
                 name: Optional[str],
                 datedImages: DatedImages,
                 datedVideos: DatedVideos):
        """描述单个站点

        :param name:    站点名, 由上一级创建
        :param datedImages: 待处理的图片列表
        :param datedVideos: 待处理的视频列表
        """          
        super().__init__()

        # 初始化基本信息
        self.name = name                                            # 变电站名称
        self.datedImages = datedImages                              # 待处理图片
        self.startDate = datedImages.startDate                      # 开始日期
        self.endDate = datedImages.endDate                          # 结束日期
        self.datedVideos = datedVideos.sliceByDate(self.startDate, self.endDate) # 待处理视频

        # 房间列表，需要进行分离构建
        self.roomList: List[Room] = []

    def splitBuild(self, 
                   topRatio: float,
                   ocrModel: DeepSeekOCR_SiliconFlow,
                   cabinetStr: str):
        '''分离构建房间列表
        分离构建房间列表时， 如果没有视频信息，那么所有照片将被加入到"本房间中"
        
        return: 房间列表
        '''
        roomStartDateList: List[datetime] = []  # ROOM开始时间列表
        roomNameList: List[str] = []            # ROOM名字列表
        roomList: List[Room] = []
        
        # 解析名字和开始时间
        for index, anchorVideo in enumerate(self.datedVideos):
            gLog.logInfo(f"站 \'{self.name}\' | 从视频解析房间名 {index}/{len(self.datedVideos)}| \'{anchorVideo}\'")
            
            self.progress.emit(index, len(self.datedVideos), self.level)
            self.state.emit("解析房间名", self.level)
            
            if index > 0 and abs(self.datedVideos[index]- self.datedVideos[index-1]) < self.SAME_ROOM_THR: # type: ignore
                gLog.logInfo(f"跳过解析该视频")
                continue
            
            newName, newDate = Room.parseNameAndDate(
                datedImages = self.datedImages,
                anchorVideo = anchorVideo,
                ocrModel = ocrModel
            )
            if newName is not None and newDate is not None:
                roomStartDateList.append(newDate)
                roomNameList.append(newName)
                gLog.logInfo(f"站 \'{self.name}\' | 解析到房间名称 \'{newName}\', 日期 \'{newDate}\'")

        # 创建空房间
        if len(roomNameList) > 0:
            # 开始图片为空房间
            newRoom = Room(
                name = None,
                datedImages = self.datedImages.sliceByDate(endDate = roomStartDateList[0]),
                datedVideos = self.datedVideos.sliceByDate(endDate = roomStartDateList[0])
            )
            roomList.append(newRoom)
        else:
            # 全部图片都是空房间
            newRoom = Room(
                name = None,
                datedImages = self.datedImages,
                datedVideos = self.datedVideos
            )
            roomList.append(newRoom)

        # 创建有名字的房间
        for index, (roomName, roomStartDate) in enumerate(zip(roomNameList, roomStartDateList)):
            
            self.progress.emit(index, len(roomNameList), self.level)
            self.state.emit("创建房间", self.level)
            
            if index == len(roomStartDateList) - 1:
                newRoom = Room(
                    name = roomName,
                    datedImages = self.datedImages.sliceByDate(startDate = roomStartDate),
                    datedVideos = self.datedVideos.sliceByDate(startDate = roomStartDate)
                )
            else:
                newRoom = Room(
                    name = roomName,
                    datedImages = self.datedImages.sliceByDate(startDate = roomStartDate, endDate = roomStartDateList[index + 1]),
                    datedVideos = self.datedVideos.sliceByDate(startDate = roomStartDate, endDate = roomStartDateList[index + 1])
                )

            roomList.append(newRoom)
    
        # 调用下一级分离构建
        
        for index, room in enumerate(roomList):
            # 信号转发
            self.progress.emit(index, len(roomList), self.level)
            self.state.emit(f"解析房间: {room.name}", self.level)
            
            room.progress.connect(self.progress.emit)
            room.state.connect(self.state.emit)

            room.splitBuild(
                topRatio = topRatio,
                ocrModel = ocrModel,
                cabinetStr = cabinetStr
            )
    
        self.roomList = roomList

    def save(self, 
             dstDir: Path, 
             withIndex: bool,
             moveMod: Literal["Copy", "Cut"] = "Copy"):
        """保存变电站内所有房间的图片

        :param dstDir:      目标文件夹
        :param withIndex:   带有Index索引
        :param moveMod:     移动模式, defaults to "Copy"
        """
        
        # 获取变电站文件夹名称
        if self.name is not None:
            substationDir = dstDir / self.name
        else:
            unKnowenIndex = 0
            substationDir = dstDir / f"unKnowenSta_{unKnowenIndex}"
            while substationDir.exists():
                unKnowenIndex += 1
                substationDir = dstDir / f"unKnowenSta_{unKnowenIndex}"
        
        # 逐个保存房间     
        for room in self.roomList:
            try:
                gLog.logInfo(f"保存房间: \'{room.name}\'")
                room.save(
                    dstDir = substationDir,
                    withIndex = withIndex,
                    moveMod = moveMod
                )
            except Exception as e:
                gLog.logInfo(f"保存房间失败: \'{str(e)}\'")
                continue

    def getBaseInfo(self, index: int):
        '''获取基本信息'''
        info = ""
        info += f"变电站_{index}: \'{self.name}\': " + "\n"
        info += f"       照片数量: \'{len(self.datedImages)}\' 张" + "\n"
        info += f"       视频数量: \'{len(self.datedVideos)}\' 个" + "\n"
        
        if self.startDate and self.endDate:
            info += f"       开始时间: \'{self.startDate.strftime("%Y%m%d_%H%M%S")}\'" + "\n"
            info += f"       结束时间: \'{self.endDate.strftime("%Y%m%d_%H%M%S")}\'"
        return info

    def showBaseInfo(self, index: int):
        '''输出基本信息'''
        gLog.logInfoWithNoTime(self.getBaseInfo(index))
        gLog.enter()
    

    
    







