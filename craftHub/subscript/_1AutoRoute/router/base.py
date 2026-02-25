##########################################################################################################
#   Description: 路由实现
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from ..substation import Substation
from craftHub.tool import gLog

import heapq
import ast
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class PowerGridGraph:
    '''电网路由计算器， 加载拓扑，根据目标起点和目标终点计算最短路径'''
    
    def __init__(self, excelPath: Path):
        """从excel文件初始化路由计算器

        :param excelPath: excel文件, 必须是 xlsx格式
        :raises FileNotFoundError: _description_
        """        
        if excelPath.suffix != ".xlsx":
            raise FileNotFoundError(f"The file you choosed is not .xlsx file: {excelPath}")
        
        # 加载数据
        try:
            substationDf = pd.read_excel(excelPath, sheet_name = 0)
        except Exception as e:
            raise Exception(f"Load Excel failed: {str(e)}")
        
        # 检查列
        for col in ["ID", "Name", "Neighbors", "Asons", "Weights", "FiberPoints"]:
            if col not in substationDf.columns:
                raise ValueError(f"Find no \'{col}\' column in excel")
        
        # 解析数据
        self.substations: List[Substation] = []
        for _, row in substationDf.iterrows():
            try:
                newsubstation = Substation(ID = int(row["ID"]),
                                        name = row["Name"],
                                        nbNames = ast.literal_eval(row["Neighbors"]),
                                        nbAsons = ast.literal_eval(row["Asons"]),
                                        nbWeights = ast.literal_eval(row["Weights"]),
                                        nbFiberPointsList = ast.literal_eval(row["FiberPoints"]))
            except Exception as e:
                raise Exception(f"Init row {row} failed: {str(e)}")
            
            newsubstation.statics()
            self.substations.append(newsubstation)
 
        self.substationDict: Dict[str, Substation] = {s.name: s for s in self.substations}
        
        gLog.logInfo(f"Load \'{len(self.substations)}\' substations from {excelPath}")
        gLog.logInfo("Load Graph success")
        
    def substationNames(self):
        '''获取变电站名称列表'''
        return list(self.substationDict.keys())

    @staticmethod
    def pathToStr(path: List[Substation], useFiberPoints: bool = False):
        def findPath(sta1: Substation, sta2: Substation, useFiberPoints: bool = False)->str:
            """获取站点1到站点2的路径字符串(不包括尾部)

            :param sta1: 站点1
            :param sta2: 站点2
            :param useFiberPoints: 使用跳纤链路, defaults to False
            :return: _description_
            """        
            
            pathStr = sta1.name + "->"
            for nbLink in sta1.nbLinks:
                if nbLink.name == sta2.name:
                    if nbLink.fiberPoints is not None and useFiberPoints:
                        
                        pathStr += "->".join(nbLink.fiberPoints)
                    break
            else:
                raise ValueError(f"sta \'{sta1.name}\' have not neighbor \'{sta2.name}\'")
            
            if not pathStr.endswith("->"):
                pathStr += "->"
            
            return pathStr

        pathStr = ""
        for index in range(len(path)):
            if(index == len(path) - 1):
                pathStr += path[index].name
            else:
                pathStr += findPath(path[index], path[index + 1], useFiberPoints)
        
        return pathStr

    def _autoHandleSta(self, staName: str):
        """自动处理sta的 '站' 字

        :param staName: 站点名字
        """        
        if staName not in self.substationNames():
            if staName.endswith("站") and (staName[:-1]) in self.substationNames():            
                staName = staName[:-1]
            elif ((staName + "站") in self.substationNames()):            
                staName += "站"

        return staName

    def findShortestPath(self, 
                         startName: str, 
                         endName: str, 
                         onlyAson: bool = False,
                         forbiddenPaths: Optional[List[List[str]]] = None) -> Tuple[int, List[Substation]]:
        """使用Dijkstra算法查找最短路径

        :param startName:       起始变电站名称
        :param endName:         目标变电站名称
        :param onlyAson:        只使用ason链路
        :param forbiddenPaths:  禁止使用路径, defaults to None
        :return: (最短路径长度, 路径变电站名称列表)
        """        
        
        # 输入名校准
        startName = self._autoHandleSta(startName)
        endName = self._autoHandleSta(endName)

        if forbiddenPaths is None:
            forbiddenPaths = []
    
        forbiddenPathsModify = []
        for forbiddenPath in forbiddenPaths:
            forbiddenPathsModify.append([self._autoHandleSta(sta) for sta in forbiddenPath])
        forbiddenPaths = forbiddenPathsModify
                
        # 验证输入
        if startName == endName:
            raise ValueError("start and end can not be setted same")
        if (startName not in self.substationNames()):            
            raise ValueError(f"start \'{startName}\' is out of the graph")
        if (endName not in self.substationNames()):
            raise ValueError(f"end \'{endName}\' is out of the graph")
        
        # 计算禁止对
        forbiddenPairs: List[Tuple[int, int]] = []
        for forbiddenPath in forbiddenPaths:
            for index, sta in enumerate(forbiddenPath):
                if index == len(forbiddenPath) -1:
                    break
                newPair = (sta, forbiddenPath[index + 1])
                forbiddenPairs.append(newPair)
        
        # 初始化数据结构
        shortestDistances = {node: float('inf') for node in self.substationNames()} # 最短路径结构
        previousNodes: Dict[str, Optional[Substation]] = {node: None for node in self.substationNames()}             # 前驱节点结构
        minHeap: List[Tuple[int, str]] = []                                         # 最小堆
        
        # 设置起点
        shortestDistances[startName] = 0
        heapq.heappush(minHeap, (0, startName))
        
        # Dijkstra算法主循环
        while minHeap:
            currentDist, currentNodeName = heapq.heappop(minHeap)
            
            # 如果到达终点则结束
            if currentNodeName == endName:
                break
                
            # 遍历邻居链路
            currentNode = self.substationDict[currentNodeName]
            for nbLink in currentNode.nbLinks:
                nbName = nbLink.name
                edgeWeight = nbLink.weight
                
                # ason禁用
                if onlyAson and not nbLink.ason:
                    continue
    
                # 路径禁用
                isForbidden = False
                for pair in forbiddenPairs:
                    if nbName in pair and currentNodeName in pair:
                        isForbidden = True
                        break
                if isForbidden:
                    continue
    
                # 更新信息
                distance = currentDist + edgeWeight
                if distance < shortestDistances[nbName]:
                    shortestDistances[nbName] = distance
                    previousNodes[nbName] = currentNode
                    heapq.heappush(minHeap, (distance, nbName))
        
        # 回溯路径
        minDisPath: List[Substation] = []
        currentNode = self.substationDict[endName]

        while currentNode is not None:
            minDisPath.append(currentNode)
            currentNode = previousNodes.get(currentNode.name, None)
        
        minDisPath.reverse()
        
        try:
            return int(shortestDistances[endName]), minDisPath
        except Exception as e:
            raise Exception(f"No Path find between \'{startName}\' and \'{endName}\'")
    
    def findSeveralPaths(self, startName: str, 
                         endName: str, 
                         maxCount: int = 3, 
                         onlyAson: bool = False,
                         forbiddenPaths: Optional[List[List[str]]] = None):
        """获取数条从起始路径到终点路径的不重合路径

        :param startName:   起始点
        :param endName:     终点
        :param onlyAson:    只使用ason链路
        :param maxCount:    最大获取数量
        :param forbiddenPaths: 禁用路径, defaults to None
        """
        
        if forbiddenPaths is None:
            forbiddenPaths = []
            
        hopCounts = []
        mainPaths: List[List[Substation]] = []
        
        for count in range(maxCount):
            try:
                hopCount, mainPath = self.findShortestPath(startName, 
                                                           endName, 
                                                           onlyAson,
                                                           forbiddenPaths)
            except Exception as e:
                gLog.logInfo(f"Get mainPath \'{count}\' failed, return")
                if count == 0:
                    raise e
                break
            else:
                forbiddenPaths.append([s.name for s in mainPath])
                hopCounts.append(hopCount)
                mainPaths.append(mainPath)
                gLog.logInfo(f"Get mainPath \'{count}\' success")
                
        return hopCounts, mainPaths