##########################################################################################################
#   Description: 地图处理器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from craftHub.tool import gLog
from path import PATH_CNOCR

import cv2
import numpy as np

from cnocr import CnOcr
from pathlib import Path
from typing import Optional, Literal, List, Tuple

class MapHander:
    '''地图处理器,  
    对输入图片进行基础处理， 获取位置信息，名字信息， 连接线路信息'''
    
    blockSize = 33   # 邻域大小
    c = 1            # 常数减数
    minLineLen = 30  # 最小连线长度
    
    def __init__(self, imagePath: Path):
        try:
            imagePath = str(imagePath)
            if any(
                ('\u4e00' <= char <= '\u9fff') or    # 基本汉字
                ('\u3400' <= char <= '\u4dbf') or    # 扩展A区
                ('\u20000' <= char <= '\u2a6df')     # 扩展B区
                for char in imagePath):
                raise Exception("Path Can't Include Chinese Character")
            
            self.image = cv2.imread(str(imagePath))
            self.grayedImage = None
            self.binaryedImage = None
            
            # 初始化CnOcr
            self.ocr = CnOcr(det_model_name = "ch_PP-OCRv4_det",
                        rec_model_name = "densenet_lite_136-gru",
                        det_root = PATH_CNOCR / "model" / "det",
                        rec_root= PATH_CNOCR / "model" / "rec")
            
            gLog.logInfo("Load cnocr success")
            
        except Exception as e:
            gLog.logInfo(f"Load Image {imagePath} Failed: {str(e)}")
            raise e
            
    def grayed(self, savePath: Optional[Path] = None):
        '''将图片灰度化'''
        
        grayImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        if savePath is not None:
            cv2.imwrite(str(savePath), grayImage)
            gLog.logInfo(f"save grayed Image to {savePath}")
        self.grayedImage = grayImage
        
    def binarized(self, threshold:int = 127, method:Literal["simple", "otsu", "adaptive"] = 'adaptive', 
                  inverse:bool = True, savePath: Optional[Path] = None):
        """将图片二值化

        :param threshold:   二值化阈值, defaults to 127
        :param method:      二值化方式, defaults to 'simple'
        :param inverse:     是否反转, defaults to False
        :param savePath:    保存路径, defaults to None
        """
        
        if self.grayedImage is None:
            self.grayed()
        
        threshType = cv2.THRESH_BINARY_INV if inverse else cv2.THRESH_BINARY
        
        # 简单阈值法
        if method == 'simple':
            _, binary = cv2.threshold(self.grayedImage, threshold, 255, threshType)
        
        # Otsu自适应阈值
        elif method == 'otsu':
            threshold, binary = cv2.threshold(self.grayedImage, 0, 255, threshType + cv2.THRESH_OTSU)
        
        elif method == 'adaptive':

            # 选择自适应方法（高斯加权或平均值）
            adaptive_method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
            
            if threshType == cv2.THRESH_BINARY_INV:
                adaptive_method = cv2.ADAPTIVE_THRESH_MEAN_C
            
            binary = cv2.adaptiveThreshold(
                self.grayedImage, 255, adaptive_method,
                threshType, self.blockSize, self.c
            )
        
        else:
            raise ValueError(f"Unknow method: {method}")
        
        if savePath is not None:
            cv2.imwrite(str(savePath), binary)
            gLog.logInfo(f"save binaried Image to {savePath}")
        
        self.binaryedImage = binary
        
    def substationNodes(self, savePath: Optional[Path] = None):
        '''搜索变电站坐标'''
        
        # 获取二值图
        self.binarized()
        binaryedImage = self.binaryedImage.copy()

        # 开闭运算去噪
        kernel_open1 = np.ones((3,3), np.uint8)
        kernel_open2 = np.ones((6,6), np.uint8)
        kernel_close1 = np.ones((2,2), np.uint8)
        kernel_close2 = np.ones((10,10), np.uint8)

        # 先进行中值滤波
        binaryedImage = cv2.medianBlur(binaryedImage, ksize = 9)

        # 先闭再开再闭再开
        binaryedImage = cv2.morphologyEx(binaryedImage, cv2.MORPH_CLOSE, kernel_close1, iterations = 1)
        binaryedImage = cv2.morphologyEx(binaryedImage, cv2.MORPH_OPEN, kernel_open1, iterations = 3)
        binaryedImage = cv2.morphologyEx(binaryedImage, cv2.MORPH_CLOSE, kernel_close2, iterations = 1)    
        binaryedImage = cv2.morphologyEx(binaryedImage, cv2.MORPH_OPEN, kernel_open2, iterations = 3)
        
        # 查找轮廓信息
        contours, _ = cv2.findContours(binaryedImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 检查有效的变电站点
        substationNodes: List[Tuple[int, int]] = []
        for cnt in contours:
            
            perimeter = cv2.arcLength(cnt, True)    # 计算轮廓周长
            area = cv2.contourArea(cnt)             # 计算轮廓面积
            approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True) # 多边形近似

            # 找最小外接矩形
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            
            # 检测是否接近正方形
            x, y, w, h = cv2.boundingRect(approx)
            aspectRatio = float(w)/h
            
            if 0.85 <= aspectRatio <= 1.15 and area > 100:
                (x, y), _ = cv2.minEnclosingCircle(cnt)
                substationNodes.append((int(x), int(y)))
                
        gLog.logInfo(f"Get vaild substations count \'{len(substationNodes)}\'")
                
        # 将坐标画在图上看看
        if savePath is not None:
            debugImg = self.image.copy()
            for (x, y) in substationNodes:
                cv2.circle(debugImg, (x, y), 10, (0,0,255), 5)  # 10px红色圆点
            cv2.imwrite(str(savePath), debugImg)
            gLog.logInfo(f"save debug image to \'{savePath}\'")

        return substationNodes
    
    def substationOCR(self):
        '''对图片进行OCR处理'''
        
        ocrImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        results = self.ocr.ocr(ocrImage)
        gLog.logInfo("OCR success")
        return results
    
    # 线条检测有待优化
    def connectionDet(self, min_line_length: int = 30,
                          merge_distance: int = 15,
                          angular_threshold: float = 5.0) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        从二值图像中提取所有线段端点
        返回: 线段端点列表[(点1, 点2), ...]
        """
        if self.binaryedImage is None:
            self.binarized()
        
        # 2. 高级直线检测（LSD算法）
        lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
        lines = lsd.detect(self.binaryedImage)[0]
        
        # 3. 初始线段收集与处理
        segments = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = map(int, line[0])
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                
                # 过滤短线段
                if length >= min_line_length:
                    segments.append((((x1, y1), (x2, y2))))
        
        # 4. 线段合并（处理断线）
        merged_segments = []
        while segments:
            base = segments.pop(0)
            base_p1, base_p2 = base
            base_vec = np.array(base_p2) - np.array(base_p1)
            base_len = np.linalg.norm(base_vec)
            
            # 查找相邻线段
            merged = False
            for i in range(len(segments)):
                seg2 = segments[i]
                p3, p4 = seg2
                
                # 检查端点间距
                d12_34 = np.linalg.norm(np.array(base_p2) - np.array(p3))
                d12_43 = np.linalg.norm(np.array(base_p2) - np.array(p4))
                d21_34 = np.linalg.norm(np.array(base_p1) - np.array(p3))
                d21_43 = np.linalg.norm(np.array(base_p1) - np.array(p4))
                
                min_dist = min(d12_34, d12_43, d21_34, d21_43)
                
                # 计算角度相似度
                if min_dist < merge_distance:
                    candidate_vec = np.array(p4) - np.array(p3)
                    candidate_ang = np.degrees(np.arccos(
                        np.dot(base_vec, candidate_vec) / 
                        (base_len * np.linalg.norm(candidate_vec) + 1e-5)
                    ))
                    
                    # 角度差检查
                    if min(candidate_ang, 180-candidate_ang) < angular_threshold:
                        # 合并线段端点
                        all_points = [base_p1, base_p2, p3, p4]
                        
                        # 按合并后最长轴线排序
                        dx = abs(max(p[0] for p in all_points) - min(p[0] for p in all_points))
                        dy = abs(max(p[1] for p in all_points) - min(p[1] for p in all_points))
                        
                        if dx > dy:  # X方向为主
                            all_points.sort(key=lambda p: p[0])
                        else:        # Y方向为主
                            all_points.sort(key=lambda p: p[1])
                        
                        # 新线段取两端点
                        new_seg = (all_points[0], all_points[-1])
                        segments.pop(i)
                        merged = True
                        break
            
            merged_segments.append(base if not merged else new_seg)
        
        gLog.logInfo("Connection detect success")
        return merged_segments
