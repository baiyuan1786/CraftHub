##########################################################################################################
#   Description: 变电站和变电站组基本结构
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from craftHub.tool import gLog
from typing import Tuple, List, Dict, Any, Optional

ASON_DEFAULT = False
WEIGHT_DEFAULT = 1
FIBERPOINTS_DEFAULT = None

class NeighborLink:
    '''邻居链路
    维护关于某链路的属性'''
    def __init__(self, name: str, ason: bool = ASON_DEFAULT, weight: int = WEIGHT_DEFAULT,
                 fiberPoints: Optional[List[str]] = FIBERPOINTS_DEFAULT):
        """邻居链路初始化

        :param name: 邻居名
        :param ason: 是否是ason链路, defaults to False
        :param weight: 链路权重, defaults to 1
        :param fiberPoints: 跳纤点列表, defaults to None
        """        
        self.name = name
        self.ason = ason
        self.weight = weight
        self.fiberPoints = fiberPoints

class Substation:
    '''变电站基类
    使用本变电站 + 邻居链路集合维护'''
    
    def __init__(self, ID: Optional[int|str] = None, name: Optional[str] = None, 
                 nbNames: Optional[List[str]] = None, nbAsons: Optional[List[bool]] = None, 
                 nbWeights: Optional[List[str]] = None, nbFiberPointsList: Optional[List[List[str]]] = None):
        """变电站初始化

        :param ID: 变电站ID, defaults to None
        :param name: 变电站名称, defaults to None
        :param nbNames: 邻居名字列表, defaults to None
        :param nbAsons: 邻居ason能力列表, defaults to None
        :param nbWeights: 链路权重列表, defaults to None
        :param nbFiberPointsList: 链路跳纤点集合列表, defaults to None
        """
        
        self.ID = ID                                                # 变电站ID
        self.name = name                                            # 变电站名称
        
        # 邻居链路
        self.nbLinks: List[NeighborLink] = []
        nbNames = nbNames if nbNames else []
        nbCounts = len(nbNames)
        
        nbAsons = nbAsons if nbAsons else [ASON_DEFAULT] * nbCounts
        nbWeights = nbWeights if nbWeights else [WEIGHT_DEFAULT] * nbCounts
        nbFiberPointsList = nbFiberPointsList if nbFiberPointsList else [FIBERPOINTS_DEFAULT] * nbCounts

        if len(nbAsons) != nbCounts or len(nbWeights) != nbCounts or len(nbFiberPointsList) != nbCounts:
            raise ValueError("Input args length matched failed")
        
        for nbname, nbason, nbWeight, nbFiberPoints in zip(nbNames, nbAsons, nbWeights, nbFiberPointsList):
            self.nbLinks.append(NeighborLink(nbname, nbason, nbWeight, nbFiberPoints))

    def addNb(self, name: str, ason: bool = ASON_DEFAULT, weight: int = WEIGHT_DEFAULT,
                 fiberPoints: Optional[List[str]] = FIBERPOINTS_DEFAULT):
        '''添加一个新的邻居'''
        newNb = NeighborLink(name, ason, weight, fiberPoints)
        self.nbLinks.append(newNb)
        
    def statics(self, showNb = False):
        '''打印当前变电站信息'''
        print(f"ID: {self.ID}")
        print(f"StaName: {self.name}")
        print("")

        if showNb:
            for index, link in enumerate(self.nbLinks):
                print(f"    NeighborIndex: {index}")
                print(f"    NeighborName: {link.name}")
                print(f"    Ason: {link.ason}")
                print(f"    Weight: {link.weight}")
                print(f"    FiberPoints: {link.fiberPoints}\n")
