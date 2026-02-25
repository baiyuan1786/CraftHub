##########################################################################################################
#   Description: 图片转换线程
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from ..core import Substations
from ..core.substation import Substaion
from ..core.datedOBJs import DatedImages, DatedVideos
from ..core.room import Room

from craftHub.tool import gLog
from craftHub.tool import DeepSeekOCR_SiliconFlow

import os
from pathlib import Path
from typing import Literal
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QButtonGroup, QPushButton)
from PyQt6.QtCore import QThread, pyqtSignal

class TransWorker(QThread):
    """执行_trans方法的工作线程"""
    
    started = pyqtSignal()                  # 开始信号
    finished = pyqtSignal()                 # 结束信号
    error = pyqtSignal(str)                 # 错误信号

    progress = pyqtSignal(int ,int, int)    # 当前值 / 总值 / Level
    state = pyqtSignal(str, int)            # 信息 / Level

    def __init__(self,
               srcDir: Path,
               dstDir: Path,
               apiKey: str,
               substationCount: int,
               topRatio: float,
               cabinetStr: str,
               withIndex: bool,
               splitMod: Literal["单文件夹模式", "多文件夹模式"],
               moveMod: Literal["Copy", "Cut"]
               ):
        """转换线程

        :param srcDir: 源文件夹
        :param dstDir: 目标文件夹
        :param apiKey: 硅基流动API
        :param substationCount: 变电站数量
        :param topRatio: 顶部比例
        :param cabinetStr: 屏柜匹配字符串
        :param withIndex: 带有索引
        :param splitMod: 分割模式
        :param moveMod: 移动模式
        """
        super().__init__()

        assert splitMod in ["单文件夹模式", "多文件夹模式"]
        assert moveMod in ["Copy", "Cut"]
        assert substationCount >= 0

        self.transMethod = lambda: self._trans(
               srcDir,
               dstDir,
               apiKey,
               substationCount,
               topRatio,
               cabinetStr,
               withIndex,
               splitMod,
               moveMod
        )
    
    def run(self):
        '''启动转换线程'''
        try:
            self.started.emit()
            self.transMethod()
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()
            
    def _trans(self,
               srcDir: Path,
               dstDir: Path,
               apiKey: str,
               substationCount: int,
               topRatio: float,
               cabinetStr: str,
               withIndex: bool,
               splitMod: Literal["单文件夹模式", "多文件夹模式"],
               moveMod: Literal["Copy", "Cut"],
               ):
        '''转换方法'''
            
        # 单文件夹模式或多文件夹模式
        if splitMod == "单文件夹模式":
            gLog.logInfo("设置 | 进入单文件夹模式")

            ocrModel = DeepSeekOCR_SiliconFlow(apiKey = apiKey) # 加载OCRModel
            datedImages = DatedImages(srcDir)                   # 读取图片集合
            datedImages.filter(dstDir)                          # 过滤图片
            if len(datedImages) == 0:
                raise ValueError("没有找到需要处理的图片")
            datedVideos = DatedVideos(srcDir).sliceByDate(datedImages.startDate, datedImages.endDate) # 读取视频集合

            gLog.logInfo(f"设置 | 需处理视频: \'{len(datedVideos)}\' 个")
            
            # 分割图片
            if substationCount > 1:
                gLog.logInfo("设置 | 分割到多个站")
                substations = Substations(datedImages,
                                          datedVideos,
                                          substationCount)
                
                # 连接信号
                substations.progress.connect(self.progress.emit)
                substations.state.connect(self.state.emit)
                
                substations.splitBuildAndSave(
                    topRatio = topRatio,
                    ocrModel = ocrModel,
                    cabinetStr = cabinetStr,
                    dstDir = dstDir,
                    withIndex = withIndex,
                    moveMod = moveMod)# type: ignore
            
            elif substationCount == 1:
                gLog.logInfo("设置 | 分割到单个站")
                sta = Substaion(
                    name = Substaion.parseName(datedImages, ocrModel),
                    datedImages = datedImages,
                    datedVideos = datedVideos
                )
                # 连接信号
                sta.progress.connect(self.progress.emit)
                sta.state.connect(self.state.emit)
                
                sta.splitBuild(
                    topRatio = topRatio,
                    ocrModel = ocrModel,
                    cabinetStr = cabinetStr
                )
                sta.save(
                    dstDir = dstDir,
                    withIndex = withIndex,
                    moveMod = moveMod) # type: ignore
            
            else:
                gLog.logInfo("设置 | 分割到单个房间")
                room = Room(
                    name = None,
                    datedImages = datedImages,
                    datedVideos = datedVideos)
                # 连接信号
                room.progress.connect(self.progress.emit)
                room.state.connect(self.state.emit)

                room.splitBuild(
                    topRatio = topRatio,
                    ocrModel = ocrModel,
                    cabinetStr = cabinetStr
                )
                room.save(dstDir = dstDir,
                          withIndex = withIndex,
                          moveMod = moveMod) # type: ignore

        else:
            gLog.logInfo("设置 | 进入多文件夹模式")
            
            # 获取文件夹
            srcDirList = [p for p in srcDir.iterdir() if p.is_dir()]
            if len(srcDirList) == 0:
                raise ValueError("源文件夹下没有子文件夹")
            
            # 逐个解析站
            for index, subDir in enumerate(srcDirList):
                self.progress.emit(index, len(srcDirList), 0)
                self.state.emit(f"构建变电站: {subDir}", 0)
                try:
                    self._trans(
                        srcDir = subDir,
                        dstDir = dstDir,
                        apiKey = apiKey,
                        substationCount = 1,
                        topRatio = topRatio,
                        cabinetStr = cabinetStr,
                        withIndex = withIndex,
                        splitMod = "单文件夹模式",
                        moveMod = moveMod
                    )
                except Exception as e:
                    gLog.logInfo(f"{gLog.RED}错误 | 文件夹转换出错: {subDir} | {str(e)}{gLog.END}")
                    
            
