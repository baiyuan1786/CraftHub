##########################################################################################################
#   Description: CraftHub菜单栏
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from typing import Callable, Dict, List, Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QMenuBar, QWidget, QMessageBox

class CraftHubMenu:
    '''CraftHub菜单栏'''

    def __init__(self, parent: QWidget, menuNameList: List[str]):
        """初始化CraftHub菜单栏

        :param parent:       父窗口
        :param menuNameList: 菜单名称列表
        """
        self.parent = parent
        self.menuBar = QMenuBar(parent=parent)
        self.menuDict: Dict[str, QMenu] = {}
        self.subMenuDict: Dict[str, QMenu] = {}

        self._buildMenuBar(menuNameList)

    def _buildMenuBar(self, menuNameList: List[str]):
        '''构建菜单栏'''

        for menuName in menuNameList:
            menu = QMenu(title=menuName, parent=self.parent)
            self.menuDict[menuName] = menu
            self.menuBar.addMenu(menu)

    def addAction(
            self,
            menuName: str,
            actionName: str,
            triggerFunc: Optional[Callable] = None,
            subMenuName: Optional[str] = None
    ) -> QAction:
        """添加菜单动作

        :param menuName:    一级菜单名称
        :param actionName:  动作名称
        :param triggerFunc: 触发函数
        :param subMenuName: 二级菜单名称
        :return:            QAction对象
        """
        if menuName not in self.menuDict:
            raise ValueError(f"菜单不存在: {menuName}")

        action = QAction(actionName, self.parent)

        if triggerFunc is not None:
            action.triggered.connect(triggerFunc)
        else:
            action.triggered.connect(self.emptyAction)

        if subMenuName is None:
            self.menuDict[menuName].addAction(action)
            return action

        subMenuKey = self._getSubMenuKey(menuName, subMenuName)

        if subMenuKey not in self.subMenuDict:
            subMenu = QMenu(subMenuName, self.parent)
            self.subMenuDict[subMenuKey] = subMenu
            self.menuDict[menuName].addMenu(subMenu)

        self.subMenuDict[subMenuKey].addAction(action)

        return action

    def addSeparator(self, menuName: str, subMenuName: Optional[str] = None):
        """添加菜单分隔线

        :param menuName:    一级菜单名称
        :param subMenuName: 二级菜单名称
        """
        if menuName not in self.menuDict:
            raise ValueError(f"菜单不存在: {menuName}")

        if subMenuName is None:
            self.menuDict[menuName].addSeparator()
            return

        subMenuKey = self._getSubMenuKey(menuName, subMenuName)

        if subMenuKey not in self.subMenuDict:
            subMenu = QMenu(subMenuName, self.parent)
            self.subMenuDict[subMenuKey] = subMenu
            self.menuDict[menuName].addMenu(subMenu)

        self.subMenuDict[subMenuKey].addSeparator()
        
    def emptyAction(self):
        '''空载映射'''
        QMessageBox.information(self.parent, "提示", "该模块尚未开发完成")

    def getMenuBar(self) -> QMenuBar:
        '''获取菜单栏'''

        return self.menuBar

    def _getSubMenuKey(self, menuName: str, subMenuName: str) -> str:
        """获取二级菜单键

        :param menuName:    一级菜单名称
        :param subMenuName: 二级菜单名称
        :return:            二级菜单键
        """
        return f"{menuName}/{subMenuName}"