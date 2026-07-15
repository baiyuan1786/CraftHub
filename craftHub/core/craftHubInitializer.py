##########################################################################################################
#   Description: CraftHub初始化器
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import shutil
from pathlib import Path
from typing import Dict, List

from path import PATH_LOG_ROOT, PATH_ROOT, PATH_SERIAL_LOG_ROOT, PATH_SUBSCRIPT

from ..tool import GLog

class CraftHubInitializer:
    '''CraftHub初始化器'''

    PY_CACHE_DIR_NAME = "__pycache__"

    README_FILE_STEM = "readme"
    DATA_FILE_NAME = "data.yaml"
    SET_FILE_NAME = "set.yaml"

    RESULT_PYCACHE_COUNT = "deletedPycacheCount"
    RESULT_LOG_COUNT = "deletedLogCount"
    RESULT_SENSITIVE_COUNT = "deletedSensitiveCount"
    RESULT_SETTING_COUNT = "deletedSettingCount"

    SENSITIVE_DIR_LIST: List[Path] = [
        PATH_SUBSCRIPT / "_1AutoRoute" / "doc" / "image",
        PATH_SUBSCRIPT / "_1AutoRoute" / "doc" / "imageTest",
    ]

    @classmethod
    def initialize(cls) -> Dict[str, int]:
        '''初始化CraftHub工具'''

        deletedPycacheCount = cls._deletePycacheDir()
        deletedLogCount = cls._deleteLogFiles()
        deletedSensitiveCount = cls._deleteSensitiveDirs()
        deletedSettingCount = cls._deleteSettingFiles()

        return {
            cls.RESULT_PYCACHE_COUNT: deletedPycacheCount,
            cls.RESULT_LOG_COUNT: deletedLogCount,
            cls.RESULT_SENSITIVE_COUNT: deletedSensitiveCount,
            cls.RESULT_SETTING_COUNT: deletedSettingCount,
        }

    @classmethod
    def _deletePycacheDir(cls) -> int:
        '''删除项目下所有__pycache__目录'''

        deletedCount = 0

        GLog.logInfo(f"尝试删除{cls.PY_CACHE_DIR_NAME}文件夹")

        for pycachePath in PATH_ROOT.rglob(cls.PY_CACHE_DIR_NAME):
            if not pycachePath.is_dir():
                continue

            try:
                shutil.rmtree(pycachePath)
                deletedCount += 1
                GLog.logInfo(f"✅ 已删除: {pycachePath}")
            except Exception as error:
                GLog.logInfo(f"❌ 删除失败 {pycachePath}: {error}")

        GLog.logInfo(f"总计删除了 {deletedCount} 个{cls.PY_CACHE_DIR_NAME}文件夹\n")

        return deletedCount

    @classmethod
    def _deleteLogFiles(cls) -> int:
        '''删除日志文件'''

        deletedCount = 0

        GLog.logInfo("尝试删除log文件")

        for logDir in [PATH_LOG_ROOT, PATH_SERIAL_LOG_ROOT]:
            if not logDir.exists():
                continue

            for logFile in logDir.iterdir():
                if not logFile.is_file():
                    continue

                if cls._isProtectedLogFile(logFile):
                    continue

                try:
                    logFile.unlink()
                    deletedCount += 1
                    GLog.logInfo(f"✅ 已删除: {logFile}")
                except Exception as error:
                    GLog.logInfo(f"❌ 删除失败 {logFile}: {error}")

        GLog.logInfo(f"总计删除了 {deletedCount} 个log文件\n")

        return deletedCount

    @classmethod
    def _deleteSensitiveDirs(cls) -> int:
        '''删除敏感文件夹'''

        deletedCount = 0

        GLog.logInfo("尝试删除敏感文件")

        for sensitiveDir in cls.SENSITIVE_DIR_LIST:
            if not sensitiveDir.exists():
                continue

            try:
                shutil.rmtree(sensitiveDir)
                deletedCount += 1
                GLog.logInfo(f"✅ 已删除: {sensitiveDir}")
            except Exception as error:
                GLog.logInfo(f"❌ 删除失败 {sensitiveDir}: {error}")

        GLog.logInfo(f"总计删除了 {deletedCount} 个敏感文件夹\n")

        return deletedCount

    @classmethod
    def _deleteSettingFiles(cls) -> int:
        '''删除用户配置文件'''

        deletedCount = 0

        GLog.logInfo("尝试删除用户配置文件")

        for settingFileName in [cls.DATA_FILE_NAME, cls.SET_FILE_NAME]:
            for settingPath in PATH_ROOT.rglob(settingFileName):
                if not settingPath.is_file():
                    continue

                try:
                    settingPath.unlink()
                    deletedCount += 1
                    GLog.logInfo(f"✅ 已删除: {settingPath}")
                except Exception as error:
                    GLog.logInfo(f"❌ 删除失败 {settingPath}: {error}")

        GLog.logInfo(f"总计删除了 {deletedCount} 个用户配置文件\n")

        return deletedCount

    @classmethod
    def _isProtectedLogFile(cls, logFile: Path) -> bool:
        '''判断日志文件是否受保护'''

        if logFile.stem == cls.README_FILE_STEM:
            return True

        if logFile.stem == GLog.logPath.stem:
            return True

        return False