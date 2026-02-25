##########################################################################################################
#   Description: 变电站拓扑重构器
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from craftHub.tool import gLog
from ...substation import Substation

import os
import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from itertools import combinations
from typing import Tuple, List, Dict, Any, Optional

plt.rcParams['font.sans-serif'] = ['SimHei']    # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示负号

class MapedSubstation(Substation):
    '''增加了图形化支持的变电站'''
    
    neighborDistance = 40
    scoreThreshold = 0.4 # 置信度阈值
    def __init__(self, position: Tuple[int, int]):
        """图形化变电站的初始化

        :param position: 位置
        """        
        super().__init__()
        if isinstance(position, str):
            position = ast.literal_eval(position)
        self.position = position
        
    def distance(self, point: Tuple[int, int]):
        """计算当前点到某一点的距离

        :param point: 某一点
        """        
        return np.sqrt((point[0] - self.position[0])** 2 + (point[1] - self.position[1])** 2)
    
    def locateName(self, ocrResults: List[Dict[str, Any]], id: int):
        """定位变电站名称

        :param ocrResults: ocr结果
        :id: 序号
        """
        self.ID = id
        posx = self.position[0]
        posy = self.position[1]
        
        for result in ocrResults:
            name: str = result['text']
            position = result['position']
            score = result['score']
            
            if score < self.scoreThreshold:
                continue
            
            centerPosx = sum(point[0] for point in position) / len(position)
            centerPosy = sum(point[1] for point in position) / len(position)
            
            if (10 < (centerPosy - posy) < 40) and (-30 < (centerPosx - posx) < 30):
                self.name = name
                return
            
        self.name = "UNKNOWEN"

    def statics(self):
        pass

class MapedSubstations:
    '''变电站组, 包含一张地图的所有变电站
    专为处理图片准备的变电站类'''

    def __init__(self, positions: List[Tuple[int, int]], ocrResults: List[Dict[str, Any]], connections: List[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """从图像识别结果初始化变电站组

        :param positions: 变电站坐标组
        :param ocrResults: ocr结果组
        :param connections: 连接线组
        """        
     
        self.positions = positions
        self.ocrResults = ocrResults
        self.connections = connections
        self.substations: List[MapedSubstation] = [MapedSubstation(position) for position in self.positions]
        
        # 获取名称
        for index, substation in enumerate(self.substations):
            substation.locateName(self.ocrResults, index)
        
        # 名称去重
        nameList = []
        for subsation in self.substations:
            existCount = 0
            oldName = subsation.name
            while subsation.name in nameList:
                existCount += 1
                subsation.name = oldName + f"_{existCount}"

            nameList.append(subsation.name)   
        
        # 获取邻居
        for substation1, substation2 in combinations(self.substations, 2):
            if self.isNeighbor(substation1, substation2):
                substation1.addNb(substation2.name)
                substation2.addNb(substation1.name)

    def isNeighbor(self, substation1: MapedSubstation, substation2: MapedSubstation):
        """判断两个变电站是否是邻居

        :param substation1: 变电站1
        :param substation2: 变电站2
        """

        for connection in self.connections:
            
            point1 = connection[0]
            point2 = connection[1]
            
            if substation1.distance(point1) < MapedSubstation.neighborDistance and\
                substation2.distance(point2) < MapedSubstation.neighborDistance:
                return True
            
            elif substation1.distance(point2) < MapedSubstation.neighborDistance and\
                substation2.distance(point1) < MapedSubstation.neighborDistance:
                return True   
            
        return False

    def statics(self):
        '''展示识别结果'''
        print(f"一共检测到 {len(self.substations)} 个变电站")
        for substation in self.substations:
            substation.statics()
    
    def plot(self, saveFolder: Path = None, isOpen = False):
        '''画出变电站坐标图'''

        if saveFolder is not None and not saveFolder.is_dir():
            raise ValueError(f"savePath is not a folder: {saveFolder}")

        # 创建图形
        plt.figure(figsize=(12, 8))  # 设置图形大小
        plt.title("电力变电站分布图", fontsize = 16)

        # 创建坐标列表
        x_coords = [s.position[0] for s in self.substations]
        y_coords = [s.position[1] for s in self.substations]
        names = [s.name for s in self.substations]

        # 绘制变电站（红色圆点）
        plt.scatter(
            x_coords, 
            y_coords,
            c='red',  # 红色
            s=200,    # 点的大小
            alpha=0.7,  # 透明度
            edgecolors='black',  # 黑色边缘
            linewidths=1,       # 边缘线宽度
            marker='o'          # 圆形标记
        )

        # 添加变电站名称标签
        for x, y, name in zip(x_coords, y_coords, names):
            # 调整标签位置避免遮盖点（根据坐标系调整位移）
            label_x = x
            label_y = y + 15  # 增加y偏移使标签在点上方向
            
            plt.text(
                label_x, 
                label_y, 
                name,
                ha='center',      # 水平居中
                va='bottom',      # 垂直对齐底部
                fontsize=10,      # 字体大小
                fontweight='bold',# 粗体
                color='blue',     # 文本颜色
                bbox=dict(        # 文本背景框
                    facecolor='white', 
                    alpha=0.7,
                    edgecolor='black',
                    boxstyle='round,pad=0.3'
                )
            )
            
        # 增加对于连接线的绘图
        for connection in self.connections:
            xList = [connection[0][0], connection[1][0]]
            yList = [connection[0][1], connection[1][1]]
            
            plt.plot(xList, yList, "r", linestyle="--")
        
        # 添加标签和网格
        plt.xlabel("X坐标", fontsize=14)
        plt.ylabel("Y坐标", fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)  # 添加网格线

        # 优化布局和显示
        plt.tight_layout()
        
        # 反转y轴
        plt.ylim(max(y_coords), min(y_coords))

        # 保存图片（可选）
        if saveFolder is not None:
            savePath = saveFolder / f"substationsMap_{gLog.date()}.png"
            plt.savefig(str(savePath), dpi = 300, bbox_inches = 'tight')
            gLog.logInfo(f"Save substation map to {savePath}")
            if isOpen:
                os.startfile(savePath)
            
    def toExcel(self, saveFolder: Path, isOpen = False):
        '''导出excel表格'''
        if not saveFolder.is_dir():
            raise ValueError(f"savePath is not a folder: {saveFolder}")
        
        idList = [sta.ID for sta in self.substations]
        nameList = [sta.name for sta in self.substations]
        positionList = [sta.position for sta in self.substations]

        nbNamesList = [[nbLink.name for nbLink in sta.nbLinks] for sta in self.substations]
        asonsList = [[nbLink.ason for nbLink in sta.nbLinks] for sta in self.substations]
        weightsList = [[nbLink.weight for nbLink in sta.nbLinks] for sta in self.substations]
        fiberPointsList = [[nbLink.fiberPoints for nbLink in sta.nbLinks] for sta in self.substations]
        
        mydf = pd.DataFrame({
                "ID": idList,
                "Name": nameList,
                "Postion": positionList,
                "Neighbors" : nbNamesList,
                "Asons" : asonsList,
                "Weights" : weightsList,
                "FiberPoints" : fiberPointsList
            })

        savePath = saveFolder / f"adj_{gLog.date()}.xlsx"
        
        # 保存并打开文件
        with pd.ExcelWriter(savePath, engine = "xlsxwriter") as writer:
            mydf.to_excel(writer, sheet_name = "Sheet1", index = False)

            # 控制列宽
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            for i, col in enumerate(mydf.columns):
                maxLen = max(mydf[col].astype(str).apply(len).max(), len(col))
                worksheet.set_column(i, i, maxLen * 1.3)
                
        gLog.logInfo(f"Save excel to {savePath}")
        if isOpen:
            os.startfile(savePath)



