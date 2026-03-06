##########################################################################################################
#   Description: 从表格提取数据
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

import pandas as pd
from docx import Document

# 方法1.1：指定列范围（P-X列）
# 列P是第16列（A=0, B=1, ... P=15）


class BOM:
    '''材料表'''
    def __init__(self, excelPath: str) -> None:
        
        df = pd.read_excel(excelPath, 
                            sheet_name = 'Sheet1',
                            usecols = 'P:X',  # 指定P到X列
                            skiprows = 2,     # 跳过前2行（读取从第3行开始）
                            nrows = 98)       # 读取98行（3-100行）
class WordTable:
    '''Word表格'''
    def __init__(self, wordPath: str = r"E:\gzq\两网工勘工程\收资表\云浮\云浮材料表.xlsx") -> None:
        # 1. 读取整个文档
        doc = Document(wordPath)

        # 2. 获取所有表格
        tables = doc.tables
        print(f"文档中共有 {len(tables)} 个表格")

        # 3. 读取第一个表格
        if tables:
            table = tables[0]
            
            # 获取表格的行列数
            rows = len(table.rows)
            cols = len(table.columns)
            print(f"表格1: {rows} 行, {cols} 列")
            
            # 遍历表格内容
            data = []
            for i, row in enumerate(table.rows):
                row_data = []
                for j, cell in enumerate(row.cells):
                    text = cell.text.strip()
                    row_data.append(text)
                data.append(row_data)
                print(f"第{i+1}行: {row_data}")
            
            print(f"表格数据: {data}")
            
if __name__ == "__main__":

    # 测试Word表格读取
    wordTable = WordTable()
