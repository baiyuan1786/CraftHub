##########################################################################################################
#   Description: 使用云端DeepSeek-OCR工具
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
import base64
import datetime
import re
import time
import requests
import io

from .log import gLog
from PIL import Image
from colorama import Fore, Style
from typing import Optional, List
from PyQt6.QtWidgets import (QFileDialog, QMessageBox)

DEBUG = True

class DeepSeekOCR_SiliconFlow:
    url = "https://api.siliconflow.cn/v1/chat/completions"
    model = "deepseek-ai/DeepSeek-OCR"
    ocrTimes = 5

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

        :param imagePath: 图片路径
        :param topRatio: 顶部比例
        """        

        # 打开图片
        with Image.open(imagePath) as img:
            # 获取图片尺寸
            width, height = img.size
            
            # 计算上半部分的高度
            top_height = int(height * topRatio)
            
            # 裁剪上半部分
            top_half = img.crop((0, 0, width, top_height))
            
            # 将裁剪后的图片保存到内存中的字节流
            buffer = io.BytesIO()
            
            # 保持原图片格式，如果无法保存则用PNG格式
            try:
                top_half.save(buffer, format = img.format or 'PNG')
            except:
                top_half.save(buffer, format='PNG')
            
            # 编码为base64
            img_bytes = buffer.getvalue()
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            buffer.close()
            
            return base64_str


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
                gLog.logInfo(f"Try OCR...")
                response = requests.post(self.url, json = payload, headers = headers, timeout = 20)
                response.raise_for_status()
                data = response.json()
                
                if DEBUG:
                    gLog.logInfoWithNoTime(data)
                
                # 检查响应是否包含结果
                if "choices" in data and data["choices"]:
                    content = data["choices"][0]["message"]["content"]
                    texts = re.findall(r'<\|ref\|>(.*?)<\|\/ref\|>', content)   # 提取所有<|ref|>...<|/ref|>中的文本
                else:
                    raise ValueError("没有获取到OCR结果")
            except Exception as e:
                gLog.logInfo(f"{Fore.YELLOW}OCR请求异常, 第 {i + 1} 次重试...{str(e)}{Style.RESET_ALL}")
                time.sleep(10)
            else:
                gLog.logInfo(f"{Fore.GREEN}OCR成功{Style.RESET_ALL}")
                return texts
        
        gLog.logInfo(f"{Fore.RED}OCR重试 {self.ocrTimes} 次后仍失败，放弃请求{Style.RESET_ALL}")
        return None
