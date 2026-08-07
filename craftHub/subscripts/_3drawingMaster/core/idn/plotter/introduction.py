##########################################################################################################
#   Description: idn接入层说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...common.graph import NewBlock, CADColor, 红色下划线
from ..reader.reader import DataUnitIDN

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal

class LocalIDNLayer1Introduction(NewBlock):
    '''IDN集成式网络说明'''

    def __init__(self,
                 doc: Drawing,
                 data: DataUnitIDN):
        """IDN集成式网络说明

        :param doc: 文档
        :param data: IDN数据
        """
        super().__init__(doc)
        
        walkLine = data.get("walkLine")
        isNewPDU = data.get("isNewPDU")
        installPnum = data.get("installPnum")
        installCabinetType = data.get("installCabinetType")
        powerType = data.get("powerType")
        isPowerModify = data.get("isPowerModify")
        powerCabinetTkA1 = data.get("powerCabinetTkA1")
        powerCabinetTkA2 = data.get("powerCabinetTkA2")

        textContent = "说明:\n"
        textContent += "1. 站点现状情况：\n"
        textContent += "  1)机房走线方式为{}。\n".format(walkLine)
        
        if powerType == "独立":
            textContent += "  2)机房供电方式为2套独立通信电源供电。\n"
        elif powerType == "DC/DC":
            textContent += "  2)机房供电方式为2套DC/DC电源供电。\n"
        elif powerType == "DC/独立":
            textContent += "  2)机房供电方式为1套独立通信电源和一套DC/DC电源供电。\n"
        else:
            raise ValueError(f"未知供电类型 {powerType}")
            
        #textContent += "  3)机房有空余屏位可安装新的机柜。\n" 
        textContent += "2. 本期建设内容\n"

        # 屏柜占用 / 新增的修改
        if installCabinetType == "占用":
            textContent += "  1)本工程无需新增机柜，新增设备及配线架均安装在原有机柜内。\n" # 
            textContent += "  2)本工程新增内容：\n"
        else:
            textContent += "  1)本工程新增设备及配线架均安装在新增机柜内。\n" # 
            textContent += "  2)本工程新增内容：\n"
            textContent += "    新增1面机柜(H2200*W600*D600mm)，安装在{}；\n".format(installPnum)
            
        # 更改显示字符串
        if installCabinetType == "占用":
            installCabinetType = "原有" # type: ignore
            
        # 是否安装PDU的修改
        if not isNewPDU:
            textContent += "    新增1套低端路由器(中兴ZXR10 6800-6X)，安装在{}{}机柜内。\n".format(installPnum, installCabinetType)
            textContent += "  3)链路开通：详见链路需求表。\n"
            textContent += "  4)PDU取电要求：新增设备直接从通信电源取电，无需新增PDU。\n"
            textContent += "  5)设备取电要求：低端路由器采用双直流供电，需要两套电源分别提供1个{}和1个{}直流开关端子。设备至两套电源的电源线，应沿不同路由敷设。\n".format(powerCabinetTkA1, powerCabinetTkA2)
        else:
            textContent += "    新增1套低端路由器(中兴ZXR10 6800-6X)和一套直流PDU，安装在{}{}机柜内。\n".format(installPnum, installCabinetType)
            textContent += "  3)链路开通：详见链路需求表。\n"
            textContent += "  4)PDU取电要求：新增PDU采用双直流供电，需要两套不同的电源分别提供1个{}和1个{}直流开关端子。PDU至两套电源的电源线，应沿不同路由敷设。\n".format(powerCabinetTkA1, powerCabinetTkA2)
            textContent += "  5)设备取电要求：低端路由器采用双直流供电，需要新增PDU A/B路各提供1个16A直流开关端子。设备至PDU A/B路的电源线，应沿不同路由敷设。\n"
        
        if not isPowerModify:
            textContent += "  6)本机房电源空开满足需求。\n"
        else:
            textContent += "  6)本工程需对电源空开进行改造，将16A空开更换为32A。\n"

        textContent += "3. 本施工图图纸设备安装位置及线缆长度等为示意仅供参考，具体以施工勘测及施工现场为准。\n"
        textContent += "4. 本施工图中的使用纤芯仅供参考，最终以调度安排为准。\n"
        textContent += "5. 本施工图图纸中的端口分配仅供参考，最终以调度安排为准；具体使用端口号以调度中心批复为准。\n"
        textContent += "6. 新增带电设备应可靠接地。\n"
        textContent += "7. DC/DC设备容量有限，需在实施阶段进一步核实现有设备电流容量和新增设备电流容量，排除过载风险。\n"
        
        # 新增IDF说明
        if data.get("edgedIDFaltitudeU"):
            textContent += "8. 联络网线、联络光缆及配套IDF、ODF另外立项建设，不在本工程建设范围内。"

        self.addMtext(
            textContent = textContent,
            textFontHeight = 3.8,
            textWidth = 156.4668,
            textColor = CADColor.toIndex("白色"),
            textLineSpacingDistance = 1,
            insertPoint = Vec2(0, 0),
            style = "GEDITXT",
            attachment = 7
        )
        
        

        

        
