##########################################################################################################
#   Description: ddn接入层说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import List, Optional

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from ...common.graph import NewBlock, CADColor
from ..reader import DataUnitDDN


class LocalDDNLayer1Introduction(NewBlock):
    '''ddn定向式绘图网络说明'''

    COLOR_HIGHLIGHT = "红色"
    NEW_CABINET_SPECIFICATION = "高H2200*宽W600*深D600mm"
    NEW_ROUTER_NAME = "华为NE8000 M6"

    def __init__(
            self,
            doc: Drawing,
            data: DataUnitDDN
    ) -> None:
        """ddn定向式绘图网络说明

        :param doc: 文档
        :param data: DDN数据单元
        """
        super().__init__(doc)

        self.contentList: List[str] = []

        walkLine = data.get("walkLine")
        isNewPDU = data.get("DDNisNewPDU")
        installPnum = data.get("DDNInstallPnum")
        installPname = data.get("DDNInstallPName")
        installCabinetType = data.get("cabinetType")
        tk1 = data.get("powerCabinetTkA1")
        tk2 = data.get("powerCabinetTkA2")
        powerType = data.get("powerType")
        isPowerModify = data.get("isPowerModify")

        self.addContent("说明:", enter=True)
        self.addContent("1. 站点现状情况：", enter=True)

        ### 第一条
        self.addContent("  1)机房走线方式为")
        self.addContent(str(walkLine), highLight = True)
        self.addContent("。", enter=True)

        # 供电方式
        self.addContent("  2)机房供电方式为")

        if powerType == "独立":
            self.addContent("2套独立通信电源供电", highLight = True)
        elif powerType == "DC/DC":
            self.addContent("2套DC/DC电源供电", highLight = True)
        elif powerType == "DC/独立":
            self.addContent("1套独立通信电源和一套DC/DC电源供电", highLight = True)
        else:
            raise ValueError(f"未知供电类型 {powerType}")

        self.addContent("。", enter=True)

        # 安装方式
        if installCabinetType == "新增":
            self.addContent("  3)机房")
            self.addContent("有空余屏位安装新的机柜", highLight = True)
            self.addContent("。", enter=True)

        elif installCabinetType == "占用":
            self.addContent("  3)机房")

            if "备用" in installPname:
                self.addContent(f"现有{installPnum} 备用机柜，可用于安装本期新增设备", highLight = True)
            else:
                self.addContent(f"现有{installPnum} {installPname}，有空余空间安装本期新增设备", highLight = True)

            self.addContent("。", enter=True)

        else:
            raise ValueError(f"未知机柜安装类型 {installCabinetType}")

        ### 第二条
        self.addContent("2. 本期建设内容", enter=True)

        # 屏柜安装
        if installCabinetType == "占用":
            self.addContent("  1)本工程新增设备")
            self.addContent("均安装在现有机柜内", highLight = True)
            self.addContent("。", enter=True)
            self.addContent("  2)本工程新增内容：", enter=True)

            displayCabinetType = "现有"

        else:
            self.addContent("  1)本工程新增设备")
            self.addContent("均安装在新增机柜内", highLight = True)
            self.addContent("。", enter=True)
            self.addContent("  2)本工程新增内容：", enter=True)
            self.addContent(f"    新增1面设备机柜({self.NEW_CABINET_SPECIFICATION})，拟安装在{installPnum}位置。", enter=True)

            displayCabinetType = installCabinetType
            
        # 路由器安装
        self.addContent("  新增")
        if isNewPDU:
            self.addContent(f"1套接入层路由器/低端路由器({self.NEW_ROUTER_NAME})和一套直流PDU", highLight = True)
        else:
            self.addContent(f"1套接入层路由器/低端路由器({self.NEW_ROUTER_NAME})", highLight = True)
        self.addContent("，拟安装在")
        self.addContent(str(installPnum), highLight = True)
        self.addContent(str(displayCabinetType), highLight = True)
        self.addContent("机柜内。", enter=True)
        
        GCNETHslotList: list = data.get("GCNETHslotList")
        GCNETHslotListStr = "".join(GCNETHslotList)
        GCNexpansionCount = GCNETHslotListStr.count("<n>")
        
        
        # 保底网扩容
        if data.get("GCNisExpansion"):
            if GCNexpansionCount <= 0:
                raise ValueError(f"设置了扩容板卡，但是扩容数量为{GCNexpansionCount}")
            
            self.addContent("  在现有")
            self.addContent(f"传输新网B({data.get("GCNareaName")})设备上扩容{GCNexpansionCount}块B型以太网板卡", highLight = True, enter = True)
        
        
        # 链路开通
        self.addContent('  3)链路开通：详见 "组网链路需求表"。', enter=True)
        
        # PDU取电要求
        if isNewPDU:
            self.addContent("  4)PDU取电要求：")
            self.addContent("低端路由器", True)      
            self.addContent("新增PDU采用双直流供电，需要两套不同的电源各提供")
            self.addContent(f"一个{tk1}+一个{tk2}", highLight = True)
            self.addContent("直流开关端子。PDU至两套电源的电源线，应沿不同路由敷设。", enter=True)
        else:
            self.addContent("  4)PDU取电要求：新增设备直接从通信电源取电，无需新增PDU。", enter=True)


        # 设备取电要求
        if isNewPDU:
            self.addContent("  5)设备取电要求：")
            self.addContent("低端路由器", highLight = True)
            self.addContent("采用双直流供电，需要新增PDU A/B路各提供")
            self.addContent("1个10A", highLight = True)
            self.addContent("直流开关端子。设备至PDU A/B路的电源线，应沿不同路由敷设。", enter=True)

        else:
            self.addContent("  5)设备取电要求：")
            self.addContent("低端路由器", highLight = True)
            self.addContent("采用双直流供电，需要两套电源各提供")
            self.addContent(f"一个{tk1}+一个{tk2}", highLight = True)
            self.addContent("直流开关端子。设备至两套电源的电源线，应沿不同路由敷设。", enter=True)

        # 电源空开改造
        self.addContent("  6)")
        if not isPowerModify:
            self.addContent("本机房电源空开满足需求", highLight = True)
        else:
            self.addContent("本工程需另外立项对电源空开进行改造，将16A空开更换为32A, 对电源进行改造后, 才可以接入设备", highLight = True)
        self.addContent("。", enter=True)

        # 其他说明
        self.addContent("3. 本施工图图纸设备安装位置及线缆长度等为示意仅供参考，具体以施工勘测及施工现场为准。", enter=True)
        self.addContent("4. 本施工图图纸中的端口分配仅供参考，最终以调度安排为准；具体使用端口号以调度中心批复为准。", enter=True)
        self.addContent("5. 新增带电设备应可靠接地。", enter=True)

        hasEdgedIDF = bool(data.get("edgedIDFaltitudeU"))
        self.addContent("6. DC/DC设备容量有限，需在实施阶段进一步核实现有设备电流容量和新增设备电流容量，排除过载风险。", enter=hasEdgedIDF)

        # 新增IDF说明
        if hasEdgedIDF:
            self.addContent("7. 联络网线、联络光缆及配套IDF、ODF另外立项建设，不在本工程建设范围内。")

        self.addMtext(
            textContent=self.buildContent(),
            textFontHeight=4,
            textWidth=156.4668,
            textColor=CADColor.toIndex("白色"),
            textLineSpacingDistance=1,
            insertPoint=Vec2(0, 0),
            style="GEDITXT",
            attachment=7
        )

    def addContent(
            self,
            text: str,
            highLight: bool = False,
            enter: bool = False
    ) -> None:
        """向说明内容中添加文本

        :param text: 添加的文本内容
        :param highLight: 红色高亮
        :param enter: 添加文本后是否换行
        """
        if highLight:
            text = CADColor.colored(text, self.COLOR_HIGHLIGHT)

        self.contentList.append(text)

        if enter:
            self.contentList.append("\n")

    def buildContent(self) -> str:
        """生成完整说明文本"""

        return "".join(self.contentList)