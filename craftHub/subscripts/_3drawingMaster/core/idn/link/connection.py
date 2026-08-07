##########################################################################################################
#   Description: IDN集成式网络说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...common.graph import NewBlock, CADColor, Line
from ...common.graph import 本期新增电源线, 本期新增跳纤, 本期新增网线, 现有互联六类电缆, 逻辑连线示意, 现有设备, 灰色边框虚线, 现有互联光缆
from .connectionPanel import IDN设备连接面板图, Area3DeviceConnectionPanel, ODFPConnectionPanel
from .connectionPanel import ODFJumpUnit, GCNUnitConnectionPanel
from .powerLink import IDNPowerLink
from ..reader.reader import DataUnitIDN

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal, List, Optional, Dict

class ConnectionMap(NewBlock):
    '''IDN集成式网络连接图
    本图使用多个连接面板图拼接组合而形成,
    '''
    def __init__(self,
                 doc: Drawing,
                 data: DataUnitIDN
                 ):
        """连接图初始化

        :param doc: 文档
        :param data: 数据单元
        """        
        
        devPortList: List = data.get("area3DevPortList")
        devNumList: List = data.get("area3DevNumList")
        devNameList: List = data.get("area3DevNameList")
        pNumList: List = data.get("area3pNumList")
        pNameList: List = data.get("area3pNameList")
        self.data = data
        
        if len(devPortList) != len(devNumList) or\
            len(devNumList) != len(devNameList) or\
            len(devNameList) != len(pNumList) or\
            len(pNumList) != len(pNameList):
                
            raise ValueError("输入的设备描述参数不是等长度")
        elif len(devPortList) <= 1:
            raise ValueError("输入设备过少，请检查输入")
        
        
        super().__init__(doc)

        self.deviceConPanel = IDN设备连接面板图(doc = doc, installPnum = data.get("installPnum"))
        self.deviceConPanel.insertInto(self.block, Vec2(0, 0))  # 以设备基点作为块基点
        
        self._buildPowerLink(data)
        
        self._buildArea3Link(devPortList = devPortList[1:],
                             devNumList = devNumList[1:],
                             devNameList = devNameList[1:],
                             pNumList = pNumList[1:],
                             pNameList = pNameList[1:],
                             data = data
                             )
        
        self._buildIDNLink(devNum = devNumList[0] if devNumList[0] is not None else "", # type: ignore
                           devName = devNameList[0] if devNameList[0] is not None else "idn交换机",
                           IDNopticalModNum = data.get("IDNopticalModNum"))
        

        self._buildODFLink(data)

        self._buildGCNLink(data)

    def _addBusinessCut(self, 
                        point: Vec2,
                        line: Line):
        '''增加业务断开说明'''
        
        downOffset = Vec2(0, 17)
        self.addLine(point,
                        point - downOffset,
                        line = line,
                        fork = True)
        self.addMtext(textContent = "业务割接时断开与旧网\n的所有组网链路",
                        textFontHeight = 2.16,
                        textWidth = 22.2,
                        style = "GEDITXT",
                        insertPoint = point - downOffset - Vec2(0, 4))
       
    def _buildPowerLink(self, data: DataUnitIDN):
        """构建电源连接图"""
        
        powerLink = IDNPowerLink(doc = self.doc,
                              powerCabinetPNum1 = data.get("powerCabinetPnum1"),
                              powerCabinetPName1 = data.get("powerCabinetPname1"),
                              powerCabinetTkNum1 = data.get("powerCabinetTknum1"),
                              powerCabinetTkA1 = data.get("powerCabinetTkA1"),
                              powerCabinetPNum2 = data.get("powerCabinetPnum2"),
                              powerCabinetPName2 = data.get("powerCabinetPname2"),
                              powerCabinetTkNum2 = data.get("powerCabinetTknum2"),
                              powerCabinetTkA2 = data.get("powerCabinetTkA2"),
                              pduInstallPnum = data.get("installPnum"),
                              isUsePDU = data.get("isUsePDU"),
                              isNewPDU = data.get("isNewPDU"),
                              powerPoint1 = self.deviceConPanel.power1Point(),
                              powerPoint2 = self.deviceConPanel.power2Point(),
                              insertPoint = Vec2(0, self.deviceConPanel.height + 20)
                              )
        
        powerLink.insertInto(self.block)

    def _buildArea3Link(self,
                        devPortList: List[Optional[str]],
                        devNumList: List[Optional[str]],
                        devNameList: List[Optional[str]],
                        pNumList: List[Optional[str]],
                        pNameList: List[Optional[str]],
                        data: DataUnitIDN
                        ):
        """构建三区连接图

        :param devPortList: 设备端口列表
        :param devNumList:  设备号列表
        :param devNameList: 设备名列表
        :param pNumList:    屏号列表
        :param pNameList:   屏名列表
        :param data:        数据单元
        """        
        
        room2DevNum: int = data.get("area3InRoom2Num")
        room2Name: str = data.get("room2Name")
        isRoom2Photoed: bool = data.get("area3Room2Photo")
        jump1stIDF: bool = data.get("jump1stIDF")
        
        area4DevNumList: list = data.get("area4DevNumList")   
        area4DevNameList: list = data.get("area4DevNameList")   
        area4DevPortList: list = data.get("area4DevPortList")  
  
        if len(devPortList) != len(devNumList) or\
            len(devNumList) != len(devNameList) or\
            len(devNameList) != len(pNumList) or\
            len(pNumList) != len(pNameList):
                
            raise ValueError("输入的设备描述参数不是等长度")
        
        # 初始化普通设备
        area3DeviceList: List[Area3DeviceConnectionPanel] = []
        for index, (port, devNum, devName, pNum, pName) in enumerate(zip(devPortList, devNumList, devNameList, pNumList, pNameList)) :
            if "防火墙" not in devName and isinstance(port, str): # type: ignore
                port = port.replace("ETH", "端口")

            area3DeviceList.append(Area3DeviceConnectionPanel(self.doc, port, devNum, devName, pNum, pName))
        
        # 初始化四区设备
        area4DeviceList = [
            Area3DeviceConnectionPanel(self.doc, port, devNum, devName, None, None)
            for port, devNum, devName in zip(area4DevPortList, area4DevNumList, area4DevNameList)
        ]
        
        # 偏置参数
        rightOffset1 = Vec2(36, 0) # 第一个设备偏置
        rightOffset2 = Vec2(51, 0) # 第二个以及以后设备的偏置
        
        # 修改为连接到板卡2
        originalStart = self.deviceConPanel.board2Point() - Area3DeviceConnectionPanel.leftPoint() # 起始点
        offsetArea3 = originalStart + Vec2(0, 0)                                                   # 偏移起始点
        pointLeft = self.deviceConPanel.board2Point()
        
        pointLeftList: List[Vec2] = []      # 左侧点列表
        pointRightList: List[Vec2] = []     # 右侧点列表

        # 跳过首个IDF
        if jump1stIDF:
            if len(area3DeviceList) <= 1:
                raise ValueError("三区设备长度不足，不支持设置跳过jump1stIDF")
            area3DeviceList = area3DeviceList[1:]

        # 成端IDF
        if data.get("edgedIDFaltitudeU") is not None:
            if len(area4DeviceList) > 0:
                port = "端口1, 端口2"
                lineNum = 2
            else:
                port = "端口1"
                lineNum = 1
            
            idfConPanel = Area3DeviceConnectionPanel(self.doc, port, data.get("installPnum"), "另外立项建设IDF", isBuild = False)
            offsetArea3 += rightOffset1
            idfConPanel.insertInto(self.block, offsetArea3)

            pointRight = Area3DeviceConnectionPanel.leftPoint(offset = offsetArea3) # 更新右侧点
            self.addLine(pointLeft,
                        pointRight,
                        line = 本期新增网线().colored("灰色"),
                        num = lineNum,
                        offsetOrient = "y")
            pointLeft = Area3DeviceConnectionPanel.rightPoint(offset = offsetArea3) # 更新左侧点
        
        lastArea4NewDevice = None  # 上一个四区新设备（独立于三区的）
        
        # 构建连接
        for index, d in enumerate(area3DeviceList):

            if offsetArea3 == originalStart:
                offsetArea3 += rightOffset1
            else:
                offsetArea3 += rightOffset2

            d.insertInto(self.block, offsetArea3)
            pointRight = Area3DeviceConnectionPanel.leftPoint(offset = offsetArea3) # 更新右侧点
            lineNum = d.portNum()                                                   # 默认只画一条线
            

            # 检查四区设备列表开头
            if len(area4DeviceList) > 0:
                area4Device = area4DeviceList.pop(0)

                # 如果四区设备和当前三区设备是同一个设备
                if area4Device == d:
                    lineNum += area4Device.portNum()

                # 如果四区设备是新设备
                else:
                    offsetArea4 = offsetArea3 + Vec2(0, 24)
                    area4Device.insertInto(self.block, offsetArea4)

                    # 四区设备左侧点
                    pointRightArea4 = Area3DeviceConnectionPanel.leftPoint(offset = offsetArea4)

                    # 将该四区设备与上一个三区设备连接
                    if lastArea4NewDevice is None:
                        
                        self.addLine(pointLeft + Vec2(0, 1.5),
                                    pointRightArea4 + Vec2(0, 1.5),
                                    line = 本期新增网线() if index == 0 else 现有互联六类电缆(),
                                    text = None if index == 0 else "利旧现有线缆",
                                    polyLine = True,
                                    num = area4Device.portNum(),
                                    offsetOrient = "y")

                    # 将四区设备与上一个四区设备连接
                    else:
                        self.addLine(Vec2(pointLeft.x, pointRightArea4.y),
                                    pointRightArea4,
                                    line = 本期新增网线() if index == 0 else 现有互联六类电缆(),
                                    text = None if index == 0 else "利旧现有线缆",
                                    polyLine = False,
                                    num = area4Device.portNum(),
                                    offsetOrient = "y")

                    lastArea4NewDevice = area4Device

            # 添加三区连接线
            if index == 0:
                self.addLine(pointLeft,
                            pointRight,
                            line = 本期新增网线(),
                            note = "Ⅲ区业务",
                            num = lineNum,
                            offsetOrient = "y")

                self._addBusinessCut(
                    point = Area3DeviceConnectionPanel.downPoint(offset = offsetArea3),
                    line = 本期新增网线()
                )

            else:
                self.addLine(pointLeft,
                            pointRight,
                            line = 现有互联六类电缆(),
                            text = "利旧现有线缆",
                            num = lineNum,
                            offsetOrient = "y")

            # 更新左侧点
            pointLeft = Area3DeviceConnectionPanel.rightPoint(offset = offsetArea3)

            pointLeftList.append(pointLeft)
            pointRightList.append(pointRight)
            
            
        # 绘制主控室框
        room2height = 40 if data.get("GCNTargetStation") is None else 31
        if room2Name is not None and room2DevNum > 1:
            room2BasePoint = pointRightList[-1 * room2DevNum] - Vec2(10, 25)
            room2Width = room2DevNum * Area3DeviceConnectionPanel.getWidth() + (room2DevNum - 1) * 20.6 + 8 * 2
            
            self.addRectangle(room2Width, room2height, 灰色边框虚线() , room2BasePoint)
            self.addMtext(textContent = room2Name,
                            textFontHeight = 4.32,
                            textWidth = 24,
                            style = "GEDITXT",
                            insertPoint = room2BasePoint + Vec2(room2Width / 2, 5),
                            attachment = 8)

        elif room2Name is not None and room2DevNum == 1:
            room2BasePoint = pointRightList[-1 * room2DevNum] - Vec2(10, 25)
            room2Width = room2DevNum * Area3DeviceConnectionPanel.getWidth() + (room2DevNum - 1) * 20.6 + 8 * 2 + 12
            
            self.addRectangle(room2Width, room2height, 灰色边框虚线() , room2BasePoint)
            self.addMtext(textContent = room2Name,
                            textFontHeight = 4.32,
                            textWidth = 24,
                            style = "GEDITXT",
                            insertPoint = room2BasePoint + Vec2(room2Width - 2, 2),
                            attachment = 9)
            
        # 绘制到主控室箭头
        if (not isRoom2Photoed) and room2Name:
            # 添加逻辑连线
            self.addLine(pointLeft, 
                        pointLeft + Vec2(20.7, 0),
                        line = 逻辑连线示意(),
                        arrow = True,
                        text = "利旧现有线缆")
            
            # 填写说明
            self.addMtext(textContent = f"至{room2Name}现有设备",
                            textFontHeight = 2.52,
                            textWidth = 54,
                            style = "GEDITXT",
                            insertPoint = pointLeft + Vec2(20.7, 0) + Vec2(2, 0),
                            attachment = 4)
        
    def _buildIDNLink(self,
                      devNum: str,
                      devName: str,
                      IDNopticalModNum: Optional[int] = None):
        '''构建旧有idn连接'''
        
        # 下方连接线
        downOffset = Vec2(0, 50) # 往下偏移
        xOffset = Vec2(25, 0)    # 往右偏移
        IDFoffset = Vec2(15, -35) # IDF偏移
        
        upPoint = self.deviceConPanel.board6Point() - downOffset
        IDFPoint = self.deviceConPanel.board6Point() + IDFoffset
        
        # 连接原有idn交换机的线缆
        if IDNopticalModNum is None or IDNopticalModNum >= 2:
            self.addLine(self.deviceConPanel.board6Point(), 
                        upPoint, 
                        line = 本期新增跳纤(), 
                        note = "Ⅳ区业务",
                        num = 2,
                        offsetOrient = "x")
            portText = "采用单模短距光模块"

        else:
            # 需要连接一根网线到IDF
            if self.data.get("edgedIDFaltitudeU"):
                newIDFdevice = Area3DeviceConnectionPanel(self.doc, "端口4", self.data.get("installPnum"), "另外立项建设IDF", isBuild = False)
                newIDFdevice.insertInto(self.block, IDFPoint)
                
                self.addLine(self.deviceConPanel.board6Point() + Vec2(3, 5.2), 
                            newIDFdevice.upPoint(IDFPoint), 
                            line = 本期新增网线().colored("灰色"),
                            polyLine = True,
                            polyLineOrient = "y")
                self.addLine(newIDFdevice.downPoint(IDFPoint), 
                            upPoint + Vec2(3, 0), 
                            line = 本期新增网线(),
                            polyLine = True,
                            polyLineOrient = "y")
                self.addLine(self.deviceConPanel.board6Point(), 
                            upPoint, 
                            line = 本期新增跳纤(),
                            note = "Ⅳ区业务")
            
            else:
                # 加两根线
                self.addLine(self.deviceConPanel.board6Point(), 
                            upPoint, 
                            line = 本期新增跳纤(), 
                            note = "Ⅳ区业务",
                            num = 2,
                            offsetOrient = "x",
                            line2 = 本期新增网线(),
                            line2StartOffset = Vec2(0, 5.2))
            
            
            
            portText = "采用单模短距光模块 + 网口"
        
        IDNdevice = Area3DeviceConnectionPanel(doc = self.doc,
                                                port = portText,
                                                devNum = devNum,
                                                devName = devName,
                                                pNum = None,
                                                pName = None)
        
        IDNPoint = upPoint - Area3DeviceConnectionPanel.upPoint()
        
        IDNdevice.insertInto(self.block, IDNPoint)
        self._addBusinessCut(point = Area3DeviceConnectionPanel.downPoint(offset = IDNPoint), line = 本期新增跳纤())
        
        self.addLine(startPoint = Area3DeviceConnectionPanel.rightPoint(offset = IDNPoint),
                     endPoint = Area3DeviceConnectionPanel.rightPoint(offset = IDNPoint) + xOffset,
                     line = 逻辑连线示意(),
                     text = "利旧现有电缆",
                     arrow = True)
        
        self.addMtext(textContent = "至各综合数据网业务",
                        textFontHeight = 2.88,
                        textWidth = 28.93,
                        style = "GEDITXT",
                        insertPoint = Area3DeviceConnectionPanel.rightPoint(offset = IDNPoint) + xOffset + Vec2(2, 0),
                        attachment = 4)

    def _buildODFLink(self, data: DataUnitIDN):
        """构建ODF连接"""    
        

        
        # 数据解压缩
        odfLinkBoardList: List = data.get("odfLinkBoardList")
        odfLinkUnitNumList: List = data.get("odfLinkUnitNumList")
        odfLinkODFPfullNameList: List = data.get("odfLinkODFPfullNameList")
        odfLinkTerminateStrList: List = data.get("odfLinkTerminateStrList")
        odfJumpPList: List = data.get("odfJumpPList")
        odfJumpUnitList: List = data.get("odfJumpUnitList")
            
        if len(odfLinkBoardList) != len(odfLinkUnitNumList) or\
            len(odfLinkUnitNumList) != len(odfLinkODFPfullNameList) or\
            len(odfLinkODFPfullNameList) != len(odfLinkTerminateStrList):

            raise ValueError("输入的设备描述参数不是等长度")
        elif len(odfLinkBoardList) <= 0:
            raise ValueError("输入设备过少，请检查输入")
        
        # 此处需要筛选
        odfLinkBoardList_filter = []
        odfLinkUnitNumList_filter = []
        odfLinkODFPfullNameList_filter = []
        odfLinkTerminateStrList_filter = []
        
        for linkBoard, unitNum, pName, terminate in zip(odfLinkBoardList, odfLinkUnitNumList, odfLinkODFPfullNameList, odfLinkTerminateStrList):
            if unitNum is not None and pName is not None:
                odfLinkBoardList_filter.append(linkBoard)
                odfLinkUnitNumList_filter.append(unitNum)
                odfLinkODFPfullNameList_filter.append(pName)
                odfLinkTerminateStrList_filter.append(terminate)
        
        odfLinkBoardList = odfLinkBoardList_filter
        odfLinkUnitNumList = odfLinkUnitNumList_filter
        odfLinkODFPfullNameList = odfLinkODFPfullNameList_filter
        odfLinkTerminateStrList = odfLinkTerminateStrList_filter
        
        if len(odfLinkBoardList) == 0:
            return  # 没有设备需要绘制
        
        # 板到点映射字典
        boardPointDict = {
            3: self.deviceConPanel.board3Point(),
            4: self.deviceConPanel.board4Point(),
            1: self.deviceConPanel.board1Point(),
            6: self.deviceConPanel.board6PointRight()
        }
        boardLineDict = {
            3: 本期新增跳纤(),
            4: 本期新增跳纤(),
            1: 本期新增网线(),
            6: 本期新增跳纤()
        }
        
        if any([b not in boardPointDict for b in odfLinkBoardList]):
            raise ValueError(f"填写了未定义的板号: {odfLinkBoardList}")
        
        # 初始化ODF屏与ODF单元映射字典
        ODFPunitDict: Dict[str, List[str]] = {}
        for odfPname, odfUnitNum in zip(odfLinkODFPfullNameList, odfLinkUnitNumList):
            if odfPname not in ODFPunitDict:
                ODFPunitDict[odfPname] = []
                
            ODFPunitDict[odfPname].append(odfUnitNum)
            
        # 初始化ODF屏字典
        ODFPdict: Dict[str, ODFPConnectionPanel] = {}
        for odfPname, odfUnitNumList in ODFPunitDict.items():
            ODFPdict[odfPname] = ODFPConnectionPanel(doc = self.doc,
                                                     odfLinkODFPfullName = odfPname,
                                                     odfLinkUnitNumList = odfUnitNumList)
            
        # 放置ODF屏和ODF跳纤箱
        linkLineLen = 10
        ODFPoffsetDict: Dict[str, Vec2] = {} # 屏柜偏置字典
        
        # 插入位置(左上)
        # 需要重新计算偏置
        offset = Vec2(81.69, 77.8)
        if len(odfLinkBoardList) > 3:
            offset += Vec2(0, 7.3 * (len(odfLinkBoardList) - 3))
        
        for index, ODFconPanel in enumerate(ODFPdict.values()):
            
            # 从上到下构建偏置
            offset -= Vec2(0, ODFconPanel.height)

            ODFconPanel.insertInto(self.block, offset + Vec2(len(odfJumpPList) * (ODFJumpUnit.getWidth() + linkLineLen), 0))
            ODFPoffsetDict[ODFconPanel.name] = offset
            
            offset -= Vec2(0, 3) # ODF屏间距
            
        # 构建连接关系
        for odfindex, (linkBoard, unitNum, pName, terminate) in enumerate(zip(odfLinkBoardList, odfLinkUnitNumList, odfLinkODFPfullNameList, odfLinkTerminateStrList)) :
            
            if unitNum is None or pName is None:
                continue
            
            ODFconPanel = ODFPdict[pName]
            ODFconPanelOffset = ODFPoffsetDict[pName]

            # ODF单元左点和右点计算
            leftPoint = ODFconPanel.unitPoint(unitNum = unitNum, leftRight = "left", offSet = ODFconPanelOffset)
            rightPoint = ODFconPanel.unitPoint(unitNum = unitNum, leftRight = "right", offSet = ODFconPanelOffset)
            
            # 添加连接光纤
            self.addLine(boardPointDict[linkBoard], 
                        leftPoint,
                        line = boardLineDict[linkBoard])
            

            # 添加ODF跳纤箱连接线 / ODF跳纤箱
            ODFJumpUnitList = [ODFJumpUnit(self.doc, pName, unitName, ODFconPanel.height) for pName, unitName in zip(odfJumpPList, odfJumpUnitList)]
            if ODFJumpUnitList:
                jumUnitRightOffset = Vec2(0, 0)
                for index, jumpUnit in enumerate(ODFJumpUnitList):

                    jumUnitLefiOffset = leftPoint + Vec2((jumpUnit.width + linkLineLen)*index, 0) # 线右点, 单元左点
                    jumUnitRightOffset = jumUnitLefiOffset + Vec2(ODFJumpUnit.getWidth(), 0)
                    
                    if odfindex == 0:
                        jumpUnit.insertInto(self.block, ODFconPanelOffset + Vec2((jumpUnit.width + linkLineLen)*index, 0))
                    
                    # 构建白色连接线
                    if index < len(ODFJumpUnitList) - 1:
                        self.addLine(startPoint = jumUnitRightOffset - Vec2(3, 0),
                                     endPoint = jumUnitRightOffset + Vec2(linkLineLen, 0),
                                     line = 现有互联光缆(),
                                     text = "利旧线缆")
                        
                    # 构建紫色连线
                    else:
                        self.addLine(startPoint = jumUnitRightOffset - Vec2(3, 0),
                                     endPoint = jumUnitRightOffset + Vec2(linkLineLen, 0),
                                     line = 本期新增跳纤())
                        
                rightPoint = jumUnitRightOffset + Vec2(linkLineLen, 0) + (rightPoint - leftPoint)
            
            # 添加逻辑连线
            self.addLine(rightPoint, 
                        rightPoint + Vec2(20.7, 0),
                        line = 逻辑连线示意(),
                        arrow = True)
            
            # 填写说明
            self.addMtext(textContent = terminate,
                            textFontHeight = 2.52,
                            textWidth = 80,
                            style = "GEDITXT",
                            insertPoint = rightPoint + Vec2(20.7, 0) + Vec2(2, 0),
                            attachment = 4)
            
    def _buildGCNLink(self, data: DataUnitIDN):
        """构建GCN网连接"""
        
        GCNPnameList: List = data.get("GCNPnameList")
        GCNDevList: List = data.get("GCNDevList")
        GCNPortList: List = data.get("GCNPortList")
        GCNBoardName: str = data.get("GCNBoardName")
        GCNareaName: str = data.get("GCNareaName")

        GCNTargetStation: str = data.get("GCNTargetStation")
        terminate = f"至{GCNTargetStation}\n(GCN网 MSTP GE传输专线)"
        
        GCNDevLen = len(GCNPnameList)
        
        if GCNDevLen == 0:
            return
        
        offset = Vec2(82, 15) # 基础偏置
        lastGCNconnectionPanel = None # 上一个GCN网设备
        startPoint = self.deviceConPanel.board1Point()
        
        # 插入成端IDF
        if data.get("edgedIDFaltitudeU") is not None:
            port = "端口3"       
            idfConPanel = GCNUnitConnectionPanel(doc = self.doc,
                                                pFullName = data.get("installPnum") + data.get("installPName"),
                                                unitName = data.get("installPnum") + CADColor.colored("本期新增成端IDF"),
                                                portName = port,
                                                boardName = None,
                                                GCNareaName = None,
                                                insertPoint = offset)
            idfConPanel.insertInto(self.block)

            self.addLine(startPoint = self.deviceConPanel.board1Point(),
                            endPoint = idfConPanel.leftPoint(),
                            line = 本期新增网线())
            lastGCNconnectionPanel = idfConPanel
            offset += Vec2(idfConPanel.width + 10, 0)  
            startPoint = idfConPanel.rightPoint()
        
        
        for index, (GCNPname, GCNDev, GCNPort) in enumerate(zip(GCNPnameList, GCNDevList, GCNPortList)) :
            
            GCNconnectionPanel = GCNUnitConnectionPanel(doc = self.doc,
                                                        pFullName = GCNPname,
                                                        unitName = GCNDev,
                                                        portName = GCNPort,
                                                        boardName = GCNBoardName if index == GCNDevLen - 1 else None,
                                                        GCNareaName = GCNareaName if index == GCNDevLen - 1 else None,
                                                        insertPoint = offset)
            GCNconnectionPanel.insertInto(self.block)

            if index == 0:
                self.addLine(startPoint = startPoint,
                            endPoint = GCNconnectionPanel.leftPoint(),
                            line = 本期新增网线())

            else:
                # 添加连接线
                self.addLine(startPoint = lastGCNconnectionPanel.rightPoint(), # type: ignore
                             endPoint = GCNconnectionPanel.leftPoint(),
                             line = 现有互联六类电缆(),
                             text = "利旧现有电缆")
            
            # 最后一个设备
            if index == GCNDevLen - 1:
                # 添加蓝色逻辑线
                self.addLine(startPoint = GCNconnectionPanel.rightPoint(),
                             endPoint = GCNconnectionPanel.rightPoint() + Vec2(20, 0),
                             line = 逻辑连线示意(),
                             arrow = True)

                self.addMtext(textContent = terminate,
                                textFontHeight = 2.52,
                                textWidth = 80,
                                style = "GEDITXT",
                                insertPoint = GCNconnectionPanel.rightPoint() + Vec2(20, 0) + Vec2(2, 0),
                                attachment = 4)

            lastGCNconnectionPanel = GCNconnectionPanel
            offset += Vec2(GCNconnectionPanel.width + 10, 0)   
                
        
        
        
        
        

