##########################################################################################################
#   Description: idn接入层说明
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from ...graph import NewBlock, CADColor, 红色下划线

from ezdxf.document import Drawing
from ezdxf.math import Vec2

from typing import Literal

class LocalIDNLayer1Introduction(NewBlock):
    '''IDN集成式网络说明'''

    def __init__(self,
                 doc: Drawing,
                 walkLine: Literal["下走线", "上走线", "电缆层走线"],
                 isNewPDU: bool,
                 installPnum: str,
                 installCabinetType:  Literal["新增", "占用"]):
        """IDN集成式网络说明

        :param doc: 文档
        :param walkLine: 走线方式
        :param isNewPDU: 是否安装PDU
        :param installPnum: 安装屏位号
        :param installCabinetType: 安装屏柜类型
        """
        super().__init__(doc)

        textContent = "说明:\n"
        textContent += "1. 站点现状情况：\n"
        textContent += "  1)机房走线方式为{}。\n".format(walkLine)
        textContent += "  2)机房供电方式为2套独立通信电源供电。\n"
        textContent += "  3)机房有空余屏位可安装新的机柜。\n"         # 后面再改
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
            textContent += "  5)设备取电要求：低端路由器采用双直流供电，需要两套电源各提供1个不小于16A直流开关端子。设备至两套电源的电源线，应沿不同路由敷设。\n"
            textContent += "  6)本机房电源空开满足需求。\n"
        else:
            textContent += "    新增1套低端路由器(中兴ZXR10 6800-6X)和一套直流PDU，安装在{}{}机柜内。\n".format(installPnum, installCabinetType)
            textContent += "  3)链路开通：详见链路需求表。\n"
            textContent += "  4)PDU取电要求：新增PDU采用双直流供电，需要两套不同的电源各提供1个不小于16A直流开关端子。PDU至两套电源的电源线，应沿不同路由敷设。\n"
            textContent += "  5)设备取电要求：低端路由器采用双直流供电，需要新增PDU A/B路各提供1个16A直流开关端子。设备至PDU A/B路的电源线，应沿不同路由敷设。\n"
            textContent += "  6)本机房电源空开满足需求。\n"

        textContent += "3. 本施工图图纸设备安装位置及线缆长度等为示意仅供参考，具体以施工勘测及施工现场为准。\n"
        textContent += "4. 本施工图中的使用纤芯仅供参考，最终以调度安排为准。\n"
        textContent += "5. 本施工图图纸中的端口分配仅供参考，最终以调度安排为准；具体使用端口号以调度中心批复为准。\n"
        textContent += "6. 新增带电设备应可靠接地。\n"
        textContent += "7. DC/DC设备容量有限，需在实施阶段进一步核实现有设备电流容量和新增设备电流容量，排除过载风险。"

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
        
        

        

        
