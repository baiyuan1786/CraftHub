##########################################################################################################
#   Description: 文件操作工具
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from .log import gLog

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
        gLog.logInfo("save result in {0}".format(str(savePath)))
        
    @classmethod
    def isEmptyDir(cls, 
                   folderDir: Path):
        """递归地判断是否是空的文件夹

        :param folderDir: 文件夹路径
        :return: _description_
        """        
        
        if not folderDir.is_dir():
            return False
        
        for dir in folderDir.iterdir():
            if not cls.isEmptyDir(dir):
                return False
            
        return True
        
    @classmethod
    def removeEmptyFolders(cls, 
                           folderDir: Path):
        """递归删除空文件夹

        :param folderDir: 需要删除的文件夹
        :return: _description_
        """      
        if not folderDir.is_dir():
            return

        # 递归删除文件夹
        for dir in folderDir.iterdir():
            if cls.isEmptyDir(dir):
                cls.removeEmptyFolders(dir)
        
        if cls.isEmptyDir(folderDir):
            folderDir.rmdir()
            gLog.logInfo(f"Removed {folderDir}")

    
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