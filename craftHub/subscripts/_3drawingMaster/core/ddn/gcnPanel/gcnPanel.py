##########################################################################################################
#   Description: GCN网面板图
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from typing import List, Optional, Literal, Dict

from ezdxf.document import Drawing
from ...common.graph import 灰色边框虚线, 本期占用机柜
from ...common.graph import CustomBlock, ExistedBlock, CADColor
from ...common.reader import DataUnit
from .gcnBoards import GCNETHboards

from ezdxf.math import Vec2

class GCNpanel(CustomBlock):
    '''GCN面板图完整版'''
    
    GCN_PANEL_BLOCK_NAME = "GCN_BOARD"
    
    INTRODUCTION_OFFSET = Vec2(15.2, 9.37)
    BOARD_OFFSET = Vec2(53.4, 110.5)
    BOARD_WIDTH = 151.75    # 整个面板图总宽度
    BOARD_HEIGHT= 50        # 面板图总高度
    
    FRAME_WIDTH = 249
    FRAME_HEIGHT = 236.8
    
    PANEL_ROW_HEIGHT = 4.5495             # 板卡行高
    PANEL_ORDER_WIDTH = 11.3737           # 序号方框宽度
    PANEL_NAME_WIDTH = 56.8684            # 名字方框宽度
    
    PANEL_LEFT_MID_OFFSET = PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH / 2            # 左边列板卡中点
    PANEL_RIGHT_MID_OFFSET = PANEL_ORDER_WIDTH * 2 + PANEL_NAME_WIDTH * 1.5     # 右边列板卡终点
    
    
    ETH_BOARD_NAME = "B3EMS10"            # 以太网板卡名字
    
    # 中心插入点定位字典
    LOCATION_MID_DICT: Dict[int, Vec2] = {
        1: Vec2(PANEL_LEFT_MID_OFFSET, PANEL_ROW_HEIGHT * (2 - 0.5)) + BOARD_OFFSET,
        3: Vec2(PANEL_LEFT_MID_OFFSET, PANEL_ROW_HEIGHT * (3 - 0.5)) + BOARD_OFFSET,
        5: Vec2(PANEL_LEFT_MID_OFFSET, PANEL_ROW_HEIGHT * (4 - 0.5)) + BOARD_OFFSET,
        2: Vec2(PANEL_RIGHT_MID_OFFSET, PANEL_ROW_HEIGHT * (2 - 0.5)) + BOARD_OFFSET,
        8: Vec2(PANEL_RIGHT_MID_OFFSET, PANEL_ROW_HEIGHT * (7 - 0.5)) + BOARD_OFFSET,
        10: Vec2(PANEL_RIGHT_MID_OFFSET, PANEL_ROW_HEIGHT * (8 - 0.5)) + BOARD_OFFSET,
        12: Vec2(PANEL_RIGHT_MID_OFFSET, PANEL_ROW_HEIGHT * (9 - 0.5)) + BOARD_OFFSET,
        14: Vec2(PANEL_RIGHT_MID_OFFSET, PANEL_ROW_HEIGHT * (10 - 0.5)) + BOARD_OFFSET,
    }
    
    # 左下点定位字典
    LOCATION_LEFTDOWN_DICT: Dict[int, Vec2] = {
        1: Vec2(0, PANEL_ROW_HEIGHT * 1) + BOARD_OFFSET,
        3: Vec2(0, PANEL_ROW_HEIGHT * 2) + BOARD_OFFSET,
        5: Vec2(0, PANEL_ROW_HEIGHT * 3) + BOARD_OFFSET,
        2: Vec2(PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH, PANEL_ROW_HEIGHT * 1) + BOARD_OFFSET,
        8: Vec2(PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH, PANEL_ROW_HEIGHT * 6) + BOARD_OFFSET,
        10: Vec2(PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH, PANEL_ROW_HEIGHT * 7) + BOARD_OFFSET,
        12: Vec2(PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH, PANEL_ROW_HEIGHT * 8) + BOARD_OFFSET,
        14: Vec2(PANEL_ORDER_WIDTH + PANEL_NAME_WIDTH, PANEL_ROW_HEIGHT * 9) + BOARD_OFFSET,
    }
    
    
    def __init__(self, doc: Drawing, data: DataUnit) -> None:
        super().__init__(doc)
        
        # 插入面板图
        gcnPanel = ExistedBlock(doc, self.GCN_PANEL_BLOCK_NAME) # 已存在块不要动
        gcnPanel.insertInto(self, self.BOARD_OFFSET)
        
        roomName = data.get("roomName")
        GCNPnum = data.get("GCNPnum")
        GCNPname = data.get("GCNPname")
        GCNareaName = data.get("GCNareaName")
        
        textContent = CADColor.colored(f"{roomName} {GCNPnum} {GCNPname}\n")
        textContent += f"传输新网B({CADColor.colored(GCNareaName)})设备\n"
        textContent += "(华为E6616)"
        
        
        # 插入文字说明
        self.addMtext(
            textContent = textContent,
            textFontHeight = 6,
            textWidth = 136.2,
            style = "gedi",
            attachment = 8,
            insertPoint = Vec2(self.BOARD_WIDTH / 2, self.BOARD_HEIGHT + 2) + self.BOARD_OFFSET
        )
        
        # 插入屏柜外框
        self.addRectangle(width = self.FRAME_WIDTH, height = self.FRAME_HEIGHT, line = 灰色边框虚线())
        
        # 插入额外说明
        self.addMtext(
            textContent = "说明: 传输设备板卡出线，详见“设备连接图”。",
            textFontHeight = 6,
            textWidth = 154,
            style = "gedi",
            attachment = 7,
            insertPoint = self.INTRODUCTION_OFFSET
        )

        # 插入顶部文字
        self.addMtext(
            textContent = "现有传输设备扩容板卡安装图",
            textFontHeight = 8,
            textWidth = 122,
            style = "gedi",
            attachment = 2,
            insertPoint = Vec2(self.FRAME_WIDTH / 2, self.FRAME_HEIGHT - 2)
        )
        
        # 插入以太网板卡
        ethBoards = GCNETHboards(
            data=data,
            validSlotList=list(self.LOCATION_MID_DICT.keys())
        )

        for ethBoardData in ethBoards.toBoardDataList():
            self.insertETHBoard(
                num=ethBoardData.slotNum,
                insertType=ethBoardData.insertType
            )
        
    def insertETHBoard(self, num: int, insertType: Literal["新增", "占用", "普通"]):
        '''插入以太网板卡B3EMS10'''

        if num not in self.LOCATION_MID_DICT:
            raise ValueError(f"第 \'{num}\' 号位置不可插入以太网板卡")
        
        # 获取插入文字
        if insertType == "新增":
            textContent = CADColor.colored(f"新增{self.ETH_BOARD_NAME}") 
        else:
            textContent = self.ETH_BOARD_NAME
        
        # 插入文字
        self.addMtext(
            textContent = textContent,
            textFontHeight = 3.37,
            textWidth = 30,
            style = "gedi",
            attachment = 5,
            insertPoint = self.LOCATION_MID_DICT[num]
        )

        # 插入矩形框
        if insertType == "新增":
            self.addRectangle(
                width = self.PANEL_ORDER_WIDTH + self.PANEL_NAME_WIDTH,
                height = self.PANEL_ROW_HEIGHT,
                line = 本期占用机柜(),
                insertPoint = self.LOCATION_LEFTDOWN_DICT[num]
            )
        elif insertType == "占用":
            self.addRectangle(
                width = self.PANEL_ORDER_WIDTH + self.PANEL_NAME_WIDTH,
                height = self.PANEL_ROW_HEIGHT,
                line = 本期占用机柜(),
                insertPoint = self.LOCATION_LEFTDOWN_DICT[num],
                isFill = True
            )
        
        
        
        
        
        
        
        
    