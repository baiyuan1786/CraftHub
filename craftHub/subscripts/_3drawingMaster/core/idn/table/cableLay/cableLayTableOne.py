##########################################################################################################
#   Description: 一个站中的所有连接
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .link import *
from ....common.reader import DataUnit
from ..idnSearcher import IDNSearcher
from ....common.meta import Device, ExistedDevice

from typing import List
import pandas as pd

class cableLayTableOne:
    '''单个站的线缆敷设表'''
    def __init__(self, data: DataUnit) -> None:
        self.substationName: str = data.get("substationName")
        self.walkLine = data.get("walkLine")
        self.data = data
        
        self.linkList: List[Link] = []  # 连接列表
        self.lightLineUsedNum = 0       # 光速寻线以太网线使用数量
        self.PDULineUsedNum = 0         # PDU原厂配套线使用数量

        # 构建四大连接
        # 注：缺少四区防火墙连接， 跳纤连接， 本屏和其他设备的电线连接
        self._buildPowerLink(data)
        self._buildOldDevPowerLink(data)
        self._buildGroudLink(data)
        self._buildFiberLink(data)
        self._buildNetLink(data)
        
    def newLink(self, link: Link):
        
        # 最多允许使用两根光速寻线以太网线
        if isinstance(link, 光速寻线以太网线缆):
            if self.lightLineUsedNum < 2:
                self.linkList.append(link)
                self.lightLineUsedNum += 1
                return
            else:
                substituteLink = 普通网线(
                    startPos = link.startPos,
                    endPos = link.endPos,
                    note = link.note + ", 线缆乙供"
                )
                self.linkList.append(substituteLink)
                return
            
        if isinstance(link, 直流电源线_原厂配套):
            self.PDULineUsedNum += 1
            if self.PDULineUsedNum > 8:
                raise ValueError("使用了超过8根PDU出线！！")

        self.linkList.append(link)

    def _buildOldDevPowerLink(self, data: DataUnit):
        '''建立与旧设备的电源线连接'''

        panelDeviceNameList: List = data.get("panelDeviceNameList")
        panelDeviceAltitudeUList: List = data.get("panelDeviceAltitudeUList")
        panelDeviceHeightUList: List = data.get("panelDeviceHeightUList")
        
        oldDevList: List[ExistedDevice] = [ExistedDevice(name, altitude, height)
                                           for name, altitude, height in zip(panelDeviceNameList, panelDeviceAltitudeUList, panelDeviceHeightUList)] 
        
        if not oldDevList:
            return
        if not data.get("isNewPDU"):
            return

        # 筛选连接设备
        oldDevCPList = [dev for dev in oldDevList if dev.signType in ["CP1", "CP2", "CP8"]]

        # 添加原有设备与新增PDU的连接
        for oldDevCP in oldDevCPList:
            # 连接2根线
            if oldDevCP.signType == "CP2":
                self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('installPnum')} 新增直流PDU A路",
                                        endPos = f"现有设备 {oldDevCP.name} 电源模块1",
                                        current = oldDevCP.current
                                        ))
                self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('installPnum')} 新增直流PDU B路",
                                        endPos = f"现有设备 {oldDevCP.name} 电源模块2",
                                        current = oldDevCP.current
                                        ))
                
            # 连接1根线
            elif oldDevCP.signType == "CP1":
                self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('installPnum')} 新增直流PDU",
                                        endPos = f"现有设备 {oldDevCP.name} 电源模块",
                                        current = oldDevCP.current
                                        ))
                
            # 连接八根线
            elif oldDevCP.signType == "CP8":
                self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('installPnum')} 新增直流PDU A路",
                                        endPos = f"现有设备 {oldDevCP.name} 电源模块1",
                                        current = oldDevCP.current,
                                        num = 4
                                        ))
                self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('installPnum')} 新增直流PDU B路",
                                        endPos = f"现有设备 {oldDevCP.name} 电源模块2",
                                        current = oldDevCP.current,
                                        num = 4
                                        ))
    
    def _buildPowerLink(self, data: DataUnit):
        '''电源线部分的连接'''
        if data.get("isNewPDU"):
            self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('powerCabinetPnum1')} {data.get('powerCabinetPname1')}",
                                        endPos = f"{data.get('installPnum')} 新增直流PDU A路",
                                        current = data.get("powerCabinetTkA1")
                                        ))
            self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('powerCabinetPnum2')} {data.get('powerCabinetPname2')}",
                                        endPos = f"{data.get('installPnum')} 新增直流PDU B路",
                                        current = data.get("powerCabinetTkA2")
                                        ))
            self.newLink(直流电源线_原厂配套(startPos = f"{data.get('installPnum')} 新增直流PDU A路",
                                       endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块1",
                                       ))
            self.newLink(直流电源线_原厂配套(startPos = f"{data.get('installPnum')} 新增直流PDU B路",
                                       endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块2",
                                       ))
            
        elif data.get("isUsePDU"):
            self.newLink(直流电源线_原厂配套(startPos = f"{data.get('installPnum')} 本屏现有PDU A路",
                                       endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块1",
                                       ))
            self.newLink(直流电源线_原厂配套(startPos = f"{data.get('installPnum')} 本屏现有PDU B路",
                                       endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块2",
                                       ))
            
        else:
            self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('powerCabinetPnum1')} {data.get('powerCabinetPname1')}",
                                            endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块1",
                                            current = data.get("powerCabinetTkA1")
                                        ))
            self.newLink(直流电源线_阻燃导线(startPos = f"{data.get('powerCabinetPnum2')} {data.get('powerCabinetPname2')}",
                                            endPos = f"{data.get('installPnum')} 新增低端路由器 电源模块2",
                                            current = data.get("powerCabinetTkA2")
                                        ))
            
    def _buildGroudLink(self, data: DataUnit):
        '''接地线部分连接'''

        # 2接地线部分
        if data.get("isNewPDU"):
            self.newLink(接地线(startPos = f"{data.get('installPnum')} 新增直流PDU",
                             endPos = "本机柜接地排"))
            
        self.newLink(接地线(startPos = f"{data.get('installPnum')} 新增低端路由器",
                            endPos = "本机柜接地排"))
        
        if data.get("installCabinetType") == "新增":
            self.newLink(机柜接地线(startPos = f"{data.get('installPnum')} 新增机柜",
                             endPos = "本机柜接地排"))

    def _buildFiberLink(self, data: DataUnit):
        '''铠装跳纤部分
        注意： 不处理跳纤链路部分
        '''

        # 3铠装跳纤部分 / ODF链路
        assert isinstance(data.get("odfLinkODFPfullNameList"), list)
        assert isinstance(data.get("odfLinkTerminateStrList"), list)
        for odfTerminate, odfFullName in zip(data.get("odfLinkTerminateStrList"), data.get("odfLinkODFPfullNameList")):
            # 无跳纤
            if (not data.get("odfJumpPList")) or (not data.get("odfJumpUnitList")):
                self.newLink(铠装跳纤(specification = "单模LC-FC",
                                    startPos = f"{data.get('installPnum')} 新增低端路由器",
                                    endPos = f"{odfFullName}",
                                    num = 2,
                                    note = f"通往{odfTerminate}"))
                
            # 有跳纤
            else:
                odfJumpUnitList = data.get("odfJumpUnitList") or []
                
                self.newLink(铠装跳纤(specification = "单模LC-FC",
                                    startPos = f"{data.get('installPnum')} 新增低端路由器",
                                    endPos = f"{odfJumpUnitList[0].split(" ")[0] if odfJumpUnitList else ''} ODF配线单元",
                                    num = 2,
                                    note = f"通往{odfTerminate}"))
                
                self.newLink(铠装跳纤(specification = "单模FC-FC",       # 两个都是ODF，填双FC
                                    startPos = f"{odfJumpUnitList[-1].split(" ")[0] if odfJumpUnitList else ''} ODF配线单元",
                                    endPos = f"{odfFullName}", # 直接填写ODF屏号
                                    num = 2,
                                    note = f"通往{odfTerminate}"))
                
        # 至原有idn交换机光纤
        IDNopticalModNum = data.get("IDNopticalModNum")
        if IDNopticalModNum is not None and IDNopticalModNum < 2:
            fiberNum = 2
        else:
            fiberNum = 4
            
        area3DevNumList = data.get("area3DevNumList") or []
        
        self.newLink(铠装跳纤(specification = "单模LC-LC",
                            startPos = f"{data.get('installPnum')} 新增低端路由器",
                            endPos = f"{area3DevNumList[0] if area3DevNumList else ''} idn交换机",
                            num = fiberNum,
                            note = f"至原有idn交换机",))
    
    def _buildNetLink(self, data: DataUnit):
        '''网线连接部分'''
        
        # 至三区防火墙设备
        area3DevNumList = data.get("area3DevNumList") or []
        area3DevNameList = data.get("area3DevNameList") or []
        area3DevPortList = data.get("area3DevPortList") or []
        area4DevNumList = data.get("area4DevNumList") or []
        area4DevNameList = data.get("area4DevNameList") or []
        area4DevPortList = data.get("area4DevPortList") or []
        
        
        startDev = f"{data.get('installPnum')} 新增低端路由器" # 路由器起始点
        
        # 路由器电口成端(16个)
        if data.get("edgedIDFaltitudeU"):
            self.newLink(普通网线(startPos = startDev,
                                 endPos = f"{data.get('installPnum')} 新增路由器成端IDF",
                                 note = "路由器电口成端",
                                 num = 16))
            startDev = f"{data.get('installPnum')} 新增路由器成端IDF" # 起始点替换为成端IDF
        
        # 至三区防火墙
        area3Index = 1 if len(area3DevNumList) > 1 and len(area3DevNameList) > 1 and not data.get("jump1stIDF") else 2
        if len(area3DevNumList) <= area3Index:
            raise ValueError(f"area3设备列表长度不足, 至少长度{area3Index + 1}")
        
        self.newLink(光速寻线以太网线缆(startPos = startDev,
                                      endPos = f"{area3DevNumList[area3Index]} {area3DevNameList[area3Index]}",
                                      note = f"至III区防火墙设备",
                                      num = area3DevPortList[area3Index].count(",") + 1))
        
        # GCN网出线(可能有)
        if data.get("GCNPnameList"):
            self.newLink(光速寻线以太网线缆(startPos = startDev,
                                        endPos = data.get("GCNPnameList")[0], # GCN网链路第一个屏
                                        note = f"GCN网出线 至{data.get('GCNTargetStation')}"))
        
        # 至四区防火墙(可能有)
        if area4DevNumList:
            self.newLink(光速寻线以太网线缆(startPos = startDev,
                                        endPos = f"{area4DevNumList[0]} {area4DevNameList[0]}",
                                        note = f"至四区防火墙",
                                        num= area4DevPortList[0].count(",") + 1))
        
        # 至原idn交换机网线(可能有)
        if data.get("IDNopticalModNum") is not None and data.get("IDNopticalModNum") < 2:
            self.newLink(光速寻线以太网线缆(startPos = startDev,
                                        endPos = f"{area3DevNumList[0] if area3DevNumList else ''} idn交换机",
                                        note = f"至原有idn交换机",))

    def readExcel(self, subDF: DataFrame):
        '''读取已有表格， 尝试读取表格中已有的数据，填写线缆长度'''
        
        # 检查数据帧中和连接相同的部分，然后获取这部分的数据
        # 此连接包含所有连接，包括跳纤链路的连接
        for index, row in subDF.iterrows():
            for link in self.linkList:
                link.readRowArgs(row = row)

    def insertFiberJumpLinkList(self, fiberJumpLinkList: List[FiberJumpLink]):
        '''插入跳纤链路表列表'''

        fiberJumpLinkListToInsert = [f for f in fiberJumpLinkList if f.substationName == self.substationName] # 待插入跳纤链路列表

        self.linkList += fiberJumpLinkListToInsert
        self.linkList.sort(key = lambda a: a.order)  # 按order排序
    
    @classmethod
    def toFiberJumpLinkList(cls,
                            data: DataUnit, 
                            dataFullList: List[DataUnit]):
        '''转换跳纤列表'''
        
        fiberJumpList = data.get("fiberJumpList")
        odfLinkTerminateStrList = data.get("odfLinkTerminateStrList")
        searcher = IDNSearcher(dataUnitFullList = dataFullList)
        linkList: List[FiberJumpLink] = []
        
        # 遍历多条链路
        for jumpStr, odfLinkTerminate in zip(fiberJumpList, odfLinkTerminateStrList):
            
            # 获取完整ODF链路
            ODFLinkList = [data.get("substationName")]
            if jumpStr is not None:
                ODFLinkList += [searcher.searchName(sta) for sta in jumpStr.split("/")] 
            
            ODFLinkList.append(odfLinkTerminate)
            
            # 构造链路表
            for index, sta in enumerate(ODFLinkList):
                
                # 开始和结束站跳过
                if index == 0 or index == len(ODFLinkList) - 1:
                    continue
                
                staStart = ODFLinkList[index - 1]
                staEnd = ODFLinkList[index + 1]

                newLink = FiberJumpLink(
                    substationName = sta, # 当前站
                    startSta = staStart,
                    endSta = staEnd,
                    startStaLayer = searcher.searchLayer(staStart),
                    endStaLayer = searcher.searchLayer(staEnd),
                    walkLine = searcher.search(sta, "walkLine")  # type: ignore
                )
                
                linkList.append(newLink)
                
        return linkList
    
    def toDF(self):
        '''转换为DataFrame'''
        
        dfList = [SubTitle(substationName = self.substationName).toDF()]
        dfList += [link.toDF(substationName = self.substationName, walkLine = self.walkLine) for link in self.linkList]
        return pd.concat(dfList)

        

        



