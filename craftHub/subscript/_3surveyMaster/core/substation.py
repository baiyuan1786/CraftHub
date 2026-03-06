##########################################################################################################
#   Description: 变电站类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

from typing import List, Dict, Optional, Literal


class Substation:
    '''变电站类'''
    def __init__(self, 
                 name: str,
                 maintenanceCenter: Optional[str] = None,
                 schedulingDataNetwork_ProvincialNetwork_Level: Optional[str] = None,
                 schedulingDataNetwork_RegionalNetwork_Level: Optional[str] = None,
                 integratedDataNetwork_ProvincialNetwork_Level: Optional[str] = None,
                 integratedDataNetwork_RegionalNetwork_Level: Optional[str] = None,
                 provincialLocalInterconnection: Optional[str] = None,
                 ):
        """数据管理使用的变电站类

        :param name: 名称
        :param maintenanceCenter: 巡维中心, defaults to None
        :param schedulingDataNetwork_ProvincialNetwork_Level: 调度数据网络_省级网络_级别, defaults to None
        :param schedulingDataNetwork_RegionalNetwork_Level: 调度数据网络_区域网络_级别, defaults to None
        :param integratedDataNetwork_ProvincialNetwork_Level: 综合数据网络_省级网络_级别, defaults to None
        :param integratedDataNetwork_RegionalNetwork_Level: 综合数据网络_区域网络_级别, defaults to None
        :param provincialLocalInterconnection: 省地互联, defaults to None
        """
        
        # 初始化属性
        self.name = name
        self.maintenanceCenter = maintenanceCenter
        self.schedulingDataNetwork_ProvincialNetwork_Level = schedulingDataNetwork_ProvincialNetwork_Level
        self.schedulingDataNetwork_RegionalNetwork_Level = schedulingDataNetwork_RegionalNetwork_Level  
        self.integratedDataNetwork_ProvincialNetwork_Level = integratedDataNetwork_ProvincialNetwork_Level
        self.integratedDataNetwork_RegionalNetwork_Level = integratedDataNetwork_RegionalNetwork_Level
        self.provincialLocalInterconnection = provincialLocalInterconnection