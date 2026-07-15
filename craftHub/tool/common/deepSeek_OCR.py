##########################################################################################################
#   Description: 使用云端DeepSeek-OCR工具
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
import base64
import datetime
import re
import time
import requests
import io
import os

from path import PATH_ROOT
from .log import GLog
from PIL import Image
from colorama import Fore, Style
from typing import Optional, List
from PyQt6.QtWidgets import (QFileDialog, QMessageBox)

DEBUG = True

class DeepSeekOCR_SiliconFlow:
    url = "https://api.siliconflow.cn/v1/chat/completions"
    model = "deepseek-ai/DeepSeek-OCR"
    ocrTimes = 5
    imageMaxSize = 2 * 1024 * 1024 # 超过该大小的图片将被压缩

    def __init__(self, apiKey: str):
        self.apiKey = apiKey
    
    def _payLoad(self, imagePath: str, topRatio: float):
        """获取推送到服务器的payload

        :param imagePath: 图片路径
        :param topRatio: 顶部比例
        """        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:application/pdf;base64," + self._encodeImage(imagePath, topRatio)
                            }
                        },
                        {
                            "type": "text",
                            "text": "<image>\n<|grounding|>OCR this image."
                        }
                    ]
                }
            ]
        }
        return payload
    
    def _encodeImage(self, imagePath: str, topRatio: float):
        """将图片编码为base64字符串
        可以只使用上半图片来节约token，提升速度
        当图片大小大于2M时，将图片转换为灰度图再转换base64编码

        :param imagePath: 图片路径
        :param topRatio: 顶部比例
        """        

        # 检查文件大小
        fileSize = os.path.getsize(imagePath)
        GLog.logInfo(f"图片压缩 | 转换前大小 {fileSize}")
        if fileSize > self.imageMaxSize:
            img = self._compressImage(imagePath = imagePath)
        else:
            img = Image.open(imagePath)
        
        # 获取图片尺寸
        width, height = img.size
        
        # 计算上半部分的高度
        topHeight = int(height * topRatio)
        
        # 裁剪上半部分
        topHalf = img.crop((0, 0, width, topHeight))
        
        # 将裁剪后的图片保存到内存中的字节流
        buffer = io.BytesIO()
        
        # 保持原图片格式，如果无法保存则用PNG格式
        try:
            topHalf.save(buffer, format = img.format or 'PNG')
        except:
            topHalf.save(buffer, format='PNG')
            
        GLog.logInfo(f"图片压缩 | 转换后大小 {buffer.tell()}")
        
        # 编码为base64
        imgBytes = buffer.getvalue()
        base64Str = base64.b64encode(imgBytes).decode('utf-8')
        buffer.close()
        
        return base64Str

    def _compressImage(self, imagePath: str):
        """压缩图片大小，将长宽变为原来的一半
        
        :param imagePath: 图片路径
        :return: 压缩后的图片对象
        """
        with Image.open(imagePath) as img:
            # 获取原始图片尺寸
            originalWidth, originalHeight = img.size
            
            # 计算新尺寸（长宽各减半）
            newWidth = originalWidth // 2
            newHeight = originalHeight // 2
            
            # 确保最小尺寸为1
            newWidth = max(1, newWidth)
            newHeight = max(1, newHeight)
            
            # 调整图片尺寸
            compressedImg = img.resize((newWidth, newHeight), Image.Resampling.LANCZOS)
            
            # 保持原格式
            compressedImg.format = img.format
            
            return compressedImg

    def _headers(self):
        """获取推送到服务器的头部信息
        """        
        headers = {
            "Authorization": f"Bearer {self.apiKey}",
            "Content-Type": "application/json"
        }
        return headers

    def ocr(self, imagePath: str, topRatio: float = 1) -> Optional[List[str]]:
        """调用云端模型进行OCR, 获取结果

        :param imagePath: 图片路径
        :param topRatio: 顶部比例
        """        
        
        headers = self._headers()
        payload = self._payLoad(imagePath, topRatio)
        
        for i in range(self.ocrTimes):
            try:
                GLog.logInfo(f"Try OCR...")
                response = requests.post(self.url, json = payload, headers = headers, timeout = 20)
                response.raise_for_status()
                data = response.json()
                
                if DEBUG:
                    GLog.logInfoWithNoTime(data)
                
                # 检查响应是否包含结果
                if "choices" in data and data["choices"]:
                    content = data["choices"][0]["message"]["content"]
                    texts = re.findall(r'<\|ref\|>(.*?)<\|\/ref\|>', content)   # 提取所有<|ref|>...<|/ref|>中的文本
                else:
                    raise ValueError("没有获取到OCR结果")
            except Exception as e:
                GLog.logInfo(f"{Fore.YELLOW}OCR请求异常, 第 {i + 1} 次重试...{str(e)}{Style.RESET_ALL}")
                time.sleep(10)
            else:
                GLog.logInfo(f"{Fore.GREEN}OCR成功{Style.RESET_ALL}")
                return texts
        
        GLog.logInfo(f"{Fore.RED}OCR重试 {self.ocrTimes} 次后仍失败，放弃请求{Style.RESET_ALL}")
        return None
