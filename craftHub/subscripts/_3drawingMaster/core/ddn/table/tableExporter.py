##########################################################################################################
#   Description: ddn表格导出器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import List

import os
import pandas as pd

from craftHub.tool import GLog

from ...common.reader import DataUnit
from .cableLay import CableLayTable
from .network import NetworkLinkTable


class DDNTableExporter:
    '''ddn表格导出器, 一次导出所有表格到一个Excel文件中'''

    FILE_NAME_TEMPLATE = "DDN_{}_相关表格_{}.xlsx"

    CONFIG_KEY_CABLE_LAY = "cableLay"
    CONFIG_KEY_CABLE_LAY_SHEET = "cableLaySheet"
    CONFIG_KEY_NET_JUMP = "netJump"
    CONFIG_KEY_NET_JUMP_SHEET = "netJumpSheet"
    CONFIG_KEY_DEST = "dest"
    CONFIG_KEY_PROJECT = "project"

    def __init__(
            self,
            dataUnitFullList: List[DataUnit],
            dataUnitList: List[DataUnit],
            config: dict
    ) -> None:
        """初始化地区ddn表格导出器

        :param dataUnitFullList: 完整数据单元列表
        :param dataUnitList:     当前需要导出的数据单元列表
        :param config:           配置字典
        """

        self.dataUnitFullList = dataUnitFullList
        self.dataUnitList = dataUnitList
        self.config = config

        self._checkConfig()

        self.cableLayTable = self._buildCableLayTable()
        self.networkTable = self._buildNetworkTable()

    def export(self):
        '''导出所有表格到同一个Excel文件中'''

        destPath = self._destPath()

        with pd.ExcelWriter(destPath, engine="xlsxwriter") as writer:
            self.cableLayTable.export(writer, self.config[self.CONFIG_KEY_PROJECT])
            self.networkTable.export(writer, self.config[self.CONFIG_KEY_PROJECT])

        GLog.logInfo(f"{GLog.GREEN}ddn相关表格已保存至 '{destPath}'{GLog.END}")
        os.startfile(destPath)

    def _buildCableLayTable(self) -> CableLayTable:
        '''构建线缆敷设表'''

        return CableLayTable(
            dataUnitFullList=self.dataUnitFullList,
            dataUnitList=self.dataUnitList,
            referrenceExcelPath=self.config[self.CONFIG_KEY_CABLE_LAY],
            referrenceSheetName=self.config[self.CONFIG_KEY_CABLE_LAY_SHEET],
            referrenceExcelPath2=self.config[self.CONFIG_KEY_NET_JUMP],
            referrenceSheetName2=self.config[self.CONFIG_KEY_NET_JUMP_SHEET]
        )

    def _buildNetworkTable(self) -> NetworkLinkTable:
        '''构建组网链路表'''

        return NetworkLinkTable(
            dataUnitFullList=self.dataUnitFullList,
            dataUnitList=self.dataUnitList
        )

    def _destPath(self) -> Path:
        '''获取导出文件路径'''

        return self.config[self.CONFIG_KEY_DEST] / self.FILE_NAME_TEMPLATE.format(
            self.config[self.CONFIG_KEY_PROJECT],
            GLog.date()
        )

    def _checkConfig(self):
        '''检查配置字典'''

        requiredKeyList = [
            self.CONFIG_KEY_CABLE_LAY,
            self.CONFIG_KEY_CABLE_LAY_SHEET,
            self.CONFIG_KEY_NET_JUMP,
            self.CONFIG_KEY_NET_JUMP_SHEET,
            self.CONFIG_KEY_DEST,
            self.CONFIG_KEY_PROJECT
        ]

        for key in requiredKeyList:
            if key not in self.config:
                raise KeyError(f"ddn表格导出配置缺少字段: {key}")

        if not isinstance(self.config[self.CONFIG_KEY_DEST], Path):
            raise TypeError(
                f"配置项{self.CONFIG_KEY_DEST}必须是Path类型，"
                f"当前类型为{type(self.config[self.CONFIG_KEY_DEST])}"
            )