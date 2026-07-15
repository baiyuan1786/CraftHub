##########################################################################################################
#   Description: 文件操作工具
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
from .log import GLog

import os
import pandas as pd
from pathlib import Path

class FileHander:
    '''文件处理器'''
    def __init__(self):
        pass    
    
    @staticmethod
    def dfSave(df: pd.DataFrame, 
               savePath: Path, 
               isOpen = False):
        """保存dataframe为一个xlsx文件

        :param df:              dataFrame
        :param savePath:        保存路径
        :param isOpen:          打开, defaults to False
        """    
        
        # 保存并打开文件
        with pd.ExcelWriter(str(savePath), engine = "xlsxwriter") as writer:
            df.to_excel(writer, sheet_name = "Sheet1", index = False)

            # 控制列宽
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]
            for i, col in enumerate(df.columns):
                maxLen = max(df[col].astype(str).apply(len).max(), len(col))
                worksheet.set_column(i, i, maxLen * 1.3)

        if isOpen:
            os.startfile(str(savePath))
        GLog.logInfo("save result in {0}".format(str(savePath)))
        

    @classmethod
    def isEmptyDir(cls, folderDir: Path) -> bool:
        """判断文件夹是否为空（不递归检查子文件夹）"""
        if not folderDir.is_dir():
            return False
        
        # 直接检查文件夹内容，不递归
        try:
            # 使用 os.scandir 更高效
            with os.scandir(folderDir) as it:
                return not any(it)  # 如果有任何内容返回 False
        except (PermissionError, OSError):
            # 如果无法访问，视为非空
            return False
    
    @classmethod
    def removeEmptyFolders(cls, 
                           folderDir: Path, 
                           recursive: bool = True) -> int:
        """
        递归删除空文件夹
        
        Args:
            folderDir: 起始文件夹路径
            recursive: 是否递归删除
        Returns:
            删除的文件夹数量
        """
        if not folderDir.is_dir():
            return 0
        
        removed_count = 0
        
        # 1. 先递归处理子文件夹（从底层开始）
        if recursive:
            # 使用 list() 复制，因为遍历过程中可能会修改目录
            for item in list(folderDir.iterdir()):
                if item.is_dir():
                    removed_count += cls.removeEmptyFolders(item, recursive=True)
        
        # 2. 尝试删除当前文件夹（如果是空的）
        try:
            if cls.isEmptyDir(folderDir):
                folderDir.rmdir()
                GLog.logInfo(f"✓ 删除空文件夹: {folderDir}")
                removed_count += 1
        except (OSError, PermissionError) as e:
            GLog.logInfo(f"✗ 无法删除 {folderDir}: {e}")
        
        return removed_count
    
    @classmethod
    def getImageNames(cls,
                      folderDir: Path):
        """递归获取指定文件夹下所有jpg图片的文件名

        :param folderDir: 要搜索的文件夹路径
        :return: 包含所有jpg图片文件名的列表（不包含路径）
        """        

        imageNames = []

        # 遍历文件夹中的所有内容
        for itemPath in folderDir.iterdir():
            
            # 如果是文件夹，递归搜索
            if itemPath.is_dir():
                imageNames.extend(cls.getImageNames(itemPath))
            # 如果是文件，检查是否为jpg或png图片
            elif itemPath.is_file():
                # 获取文件扩展名并转换为小写
                if itemPath.suffix in ['.jpg']:
                    imageNames.append(itemPath.name)
        
        return imageNames