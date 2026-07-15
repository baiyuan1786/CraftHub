##########################################################################################################
#   Description: CraftHub快捷方式创建器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import sys
from pathlib import Path
from typing import Optional

from path import PATH_DESKTOP, PATH_ROOT

try:
    import win32com.client
except ImportError:
    win32com = None


class ShortcutCreator:
    '''CraftHub快捷方式创建器'''

    MAIN_FILE_NAME = "main.py"
    SHORTCUT_FILE_NAME = "CraftHub.lnk"
    DESKTOP_ICON_RELATIVE_PATH = Path("doc") / "png" / "desktop.ico"

    SHORTCUT_DESCRIPTION = "CraftHub Application"

    WINDOWS_SCRIPT_SHELL = "WScript.Shell"


    @classmethod
    def createCraftHubShortcut(cls) -> Path:
        '''创建CraftHub桌面快捷方式'''

        cls._checkWin32ComAvailable()

        sourcePath = PATH_ROOT / cls.MAIN_FILE_NAME
        targetPath = PATH_DESKTOP / cls.SHORTCUT_FILE_NAME
        iconPath = PATH_ROOT / cls.DESKTOP_ICON_RELATIVE_PATH

        cls._checkSourceFile(sourcePath)
        cls._ensureDesktopDir()

        shell = win32com.client.Dispatch(cls.WINDOWS_SCRIPT_SHELL)  # type: ignore
        shortcut = shell.CreateShortCut(str(targetPath))

        shortcut.TargetPath = sys.executable
        shortcut.Arguments = f'"{sourcePath}"'
        shortcut.WorkingDirectory = str(sourcePath.parent)
        shortcut.IconLocation = cls._getIconLocation(iconPath)
        shortcut.Description = cls.SHORTCUT_DESCRIPTION
        shortcut.Save()

        return targetPath

    @staticmethod
    def _checkWin32ComAvailable():
        '''检查win32com是否可用'''

        if win32com is None:
            raise RuntimeError("未安装pywin32，无法创建Windows快捷方式")

    @staticmethod
    def _checkSourceFile(sourcePath: Path):
        '''检查启动源文件是否存在'''

        if not sourcePath.exists():
            raise FileNotFoundError(f"没有找到源文件: '{sourcePath}'")

    @staticmethod
    def _ensureDesktopDir():
        '''确保桌面目录存在'''

        PATH_DESKTOP.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _getIconLocation(iconPath: Path) -> str:
        '''获取快捷方式图标路径'''

        if not iconPath.exists():
            return ""

        return str(iconPath)