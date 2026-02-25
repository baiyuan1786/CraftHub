##########################################################################################################
#   Description: 单个屏柜类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .datedOBJs import DatedImages, DatedVideos
from .datedOBJ import DatedImage, DatedVideo

from craftHub.tool import gLog
from craftHub.tool import DeepSeekOCR_SiliconFlow

import os
import re
from pathlib import Path
from typing import Optional, List, Literal

CABINET_LEN_MAX = 20

class Cabinet:
    '''单个屏柜
    屏柜 -> 复数个日期图片
    '''
    @classmethod
    def parseName(cls, 
                  datedImage: DatedImage, 
                  topRatio: float, 
                  ocrModel: DeepSeekOCR_SiliconFlow,
                  cabinetStr: str) -> Optional[str]:
        """解析屏柜名称

        :param datedImage: 带日期的图片
        :param topRatio: 顶部比例
        :param ocrModel: OCR模型
        :param cabinetStr: 正则表达式模式字符串
        :return: 屏柜名或None
        """        

        cabinetCandidates: List[str] = [] # 候选列表

        # 进行OCR识别
        result:List[str]|None = ocrModel.ocr(str(datedImage), topRatio)
        if not result:
            return None
        result = [s.replace(" ", "") for s in result]   # 去除空格
        
        # 生成匹配模式
        cabinetStr1 = cabinetStr.strip()
        cabinetStr2 = cabinetStr.strip()
        if not cabinetStr1.startswith("^"):
            cabinetStr1 = "^" + cabinetStr1
        if not cabinetStr1.endswith("$"):
            cabinetStr1 = cabinetStr1 + "$"
        
        patternSingle = re.compile(cabinetStr1) # 单个匹配模式
        patternCombo = re.compile(cabinetStr2)  # 组合匹配模式

        # 单个结果匹配
        gLog.logInfo(f"解析屏柜名 | 尝试单结果匹配...", end = "")
        for text in result:
            isMatch = False
            for match in patternSingle.finditer(text):
                cabinetName = match.group(0).strip()
                cabinetCandidates.append(cabinetName)
                isMatch = True

            if isMatch:
                gLog.logInfoWithNoTime(f"成功")
                break
        else:
            gLog.logInfoWithNoTime(f"失败")
            
        # 组合结果匹配
        if not cabinetCandidates:
            gLog.logInfo(f"解析屏柜名 | 尝试组合匹配...", end = "")

            comboxStr = ""
            for text in result:
                comboxStr += text
                if not ("屏" in comboxStr or "柜" in comboxStr):
                    continue

                isMatch = False
                for match in patternSingle.finditer(comboxStr):
                    
                    cabinetName = match.group(0).strip()
                    cabinetCandidates.append(cabinetName)
                    isMatch = True
                
                comboxStr = ""
                if isMatch:
                    gLog.logInfoWithNoTime(f"成功")
                    break

            else:
                gLog.logInfoWithNoTime(f"失败")

        # 尝试全字匹配
        if not cabinetCandidates:
            gLog.logInfo(f"解析屏柜名 | 尝试全字匹配: {"".join(result)}...", end = "")

            isMatch = False
            for match in patternCombo.finditer("".join(result)):
                cabinetName = match.group(0).strip()
                cabinetCandidates.append(cabinetName)
                isMatch = True
            if isMatch:
                gLog.logInfoWithNoTime("成功")
            else:
                gLog.logInfoWithNoTime("失败")
                
            
        # 进行长度筛选
        cabinetCandidates = [c for c in cabinetCandidates if len(c) < CABINET_LEN_MAX]
        if not cabinetCandidates:
            selected = None
        elif len(cabinetCandidates) > 1:
            selected = f"Mixed_" + cabinetCandidates[0]
        else:
            selected = cabinetCandidates[0]

        gLog.logInfo(f"解析屏柜名 | 解析到屏柜: {selected} ")
        return selected
    
    def __init__(self, name: str):
        self.name = name
        self.datedImages = DatedImages() # 屏柜图片集
        
    def __len__(self):
        return len(self.datedImages)
        
    def append(self, image: DatedImage):
        '''对屏柜图片集添加图片'''
        self.datedImages.append(image)
        
    def save(self,
             dstDir: Path,
             index: Optional[int] = None,
             moveMod: Literal["Copy", "Cut"] = "Copy"):
        """保存屏柜文件
        屏柜文件将会被保存在dstDir下属的 xxPxxx屏 文件夹下

        :param dstDir:  目标文件夹
        :param index:   索引, defaults to None
        :param moveMod: 移动模式, defaults to "Copy"
        """

        cabinetDir = dstDir / f"{index}_{self.name}" if index is not None else dstDir / self.name
        os.makedirs(cabinetDir, exist_ok = True)
        
        self.datedImages.save(
            dstDir = cabinetDir,
            moveMod = moveMod
        )                