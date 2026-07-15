##########################################################################################################
#   Description: xlsx列元素统计页面
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

import pandas as pd
from pathlib import Path
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QComboBox, QPlainTextEdit,
    QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QGridLayout
)

from page import Page
from path import PATH_HUB_ROOT

PATH_DATA = PATH_HUB_ROOT / "tool" / "xlsxCounter" / "data.yaml"

class XlsxCounter(Page):
    '''xlsx列元素统计页面'''

    def __init__(self):
        """页面初始化
        """
        super().__init__(title="Xlsx列元素统计", dataPath=PATH_DATA)

        self.initUI()
        self.load()

    def initUI(self):
        '''初始化页面UI'''

        self.xlsxPathEdit = QLineEdit()
        self.xlsxPathEdit.setObjectName("xlsxPathEdit")

        self.sheetComboBox = QComboBox()
        self.sheetComboBox.setObjectName("sheetComboBox")
        self.sheetComboBox.setEditable(True)

        self.columnComboBox = QComboBox()
        self.columnComboBox.setObjectName("columnComboBox")
        self.columnComboBox.setEditable(True)

        self.weightColumnComboBox = QComboBox()
        self.weightColumnComboBox.setObjectName("weightColumnComboBox")
        self.weightColumnComboBox.setEditable(True)
        
        self.resultTextEdit = QPlainTextEdit()
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.resultTextEdit.setReadOnly(True)

        self.selectFileBtn = QPushButton("选择文件")
        self.loadSheetBtn = QPushButton("读取Sheet")
        self.loadColumnBtn = QPushButton("读取列名")
        self.runBtn = QPushButton("开始统计")
        self.clearBtn = QPushButton("清空结果")

        self.selectFileBtn.clicked.connect(self.selectXlsxFile)
        self.loadSheetBtn.clicked.connect(self.loadSheetNames)
        self.loadColumnBtn.clicked.connect(self.loadColumnNames)
        self.runBtn.clicked.connect(self.runCounter)
        self.clearBtn.clicked.connect(self.resultTextEdit.clear)

        fileLayout = QHBoxLayout()
        fileLayout.addWidget(self.xlsxPathEdit)
        fileLayout.addWidget(self.selectFileBtn)

        gridLayout = QGridLayout()
        gridLayout.addWidget(QLabel("xlsx文件路径:"), 0, 0)
        gridLayout.addLayout(fileLayout, 0, 1)

        gridLayout.addWidget(QLabel("Sheet名称:"), 1, 0)
        gridLayout.addWidget(self.sheetComboBox, 1, 1)
        gridLayout.addWidget(self.loadSheetBtn, 1, 2)

        gridLayout.addWidget(QLabel("统计列名:"), 2, 0)
        gridLayout.addWidget(self.columnComboBox, 2, 1)
        gridLayout.addWidget(self.loadColumnBtn, 2, 2)

        gridLayout.addWidget(QLabel("权重列名:"), 3, 0)
        gridLayout.addWidget(self.weightColumnComboBox, 3, 1)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.runBtn)
        btnLayout.addWidget(self.clearBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(gridLayout)
        mainLayout.addLayout(btnLayout)
        mainLayout.addWidget(QLabel("统计结果:"))
        mainLayout.addWidget(self.resultTextEdit)

        self.setLayout(mainLayout)

    def selectXlsxFile(self):
        '''选择xlsx文件'''

        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "选择xlsx文件",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if filePath:
            self.xlsxPathEdit.setText(filePath)
            self.loadSheetNames()

    def loadSheetNames(self):
        '''读取xlsx文件Sheet名称'''

        try:
            xlsxPath = self.readPara(
                self.xlsxPathEdit,
                isPath=True,
                checkPath=True,
                notFoundStr="xlsx文件不存在"
            )

            if xlsxPath is None:
                return

            excelFile = pd.ExcelFile(xlsxPath)

            self.sheetComboBox.clear()
            self.sheetComboBox.addItems(excelFile.sheet_names)

        except Exception as e:
            QMessageBox.critical(self, "读取Sheet失败", str(e))

    def loadColumnNames(self):
        '''读取指定Sheet的列名'''

        try:
            xlsxPath = self.readPara(
                self.xlsxPathEdit,
                isPath=True,
                checkPath=True,
                notFoundStr="xlsx文件不存在"
            )
            sheetName = self.readPara(self.sheetComboBox)

            if xlsxPath is None or sheetName is None:
                return

            df = pd.read_excel(xlsxPath, sheetName, nrows=0) # type: ignore

            self.columnComboBox.clear()
            self.weightColumnComboBox.clear()

            columnNameList = [str(col) for col in df.columns]

            self.columnComboBox.addItems(columnNameList)

            self.weightColumnComboBox.addItem("")
            self.weightColumnComboBox.addItems(columnNameList)

        except Exception as e:
            QMessageBox.critical(self, "读取列名失败", str(e))

    def countColumnValues(self,
                        xlsxPath: Path,
                        sheetName: str,
                        columnName: str,
                        weightColumnName: str | None = None):
        """统计xlsx指定Sheet中指定列各元素出现次数

        :param xlsxPath: xlsx文件路径
        :param sheetName: Sheet名称
        :param columnName: 统计列名
        :param weightColumnName: 权重列名
        :return: 统计结果字典
        """

        df = pd.read_excel(
            xlsxPath,
            sheet_name=sheetName,
            dtype=str
        )

        if columnName not in df.columns:
            raise ValueError(f"列名不存在: {columnName}")

        if weightColumnName is not None and weightColumnName not in df.columns:
            raise ValueError(f"权重列不存在: {weightColumnName}")

        df[columnName] = df[columnName].astype(str).str.strip()
        df = df[df[columnName].notna()]
        df = df[df[columnName] != ""]

        if weightColumnName is None:
            df["_weight"] = 1
        else:
            df["_weight"] = pd.to_numeric(
                df[weightColumnName],
                errors="coerce"
            ).fillna(0)

        valueCountDict = (
            df.groupby(columnName)["_weight"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )

        return valueCountDict

    def formatResult(self,
                    valueCountDict: dict,
                    sheetName: str,
                    columnName: str,
                    weightColumnName: str | None = None):
        """格式化统计结果

        :param valueCountDict: 统计结果字典
        :param sheetName: Sheet名称
        :param columnName: 统计列名
        :return: 格式化后的字符串
        """

        lines = []
        lines.append("=" * 60)
        lines.append(f"Sheet名称: {sheetName}")
        lines.append(f"统计列名: {columnName}")
        lines.append(f"元素种类: {len(valueCountDict)}")
        lines.append(f"权重列名: {weightColumnName if weightColumnName else '未选择，默认权重为1'}")
        lines.append("=" * 60)

        for value, count in valueCountDict.items():
            lines.append(f"{value:<30} : {count:g}")

        lines.append("=" * 60)

        return "\n".join(lines)

    def runCounter(self):
        '''执行统计'''

        try:
            xlsxPath = self.readPara(
                self.xlsxPathEdit,
                isPath=True,
                checkPath=True,
                notFoundStr="xlsx文件不存在"
            )
            sheetName = self.readPara(self.sheetComboBox)
            columnName = self.readPara(self.columnComboBox)
            weightColumnName = self.readPara(self.weightColumnComboBox)

            if xlsxPath is None:
                raise ValueError("请选择xlsx文件")

            if sheetName is None:
                raise ValueError("请输入或选择Sheet名称")

            if columnName is None:
                raise ValueError("请输入或选择列名")

            valueCountDict = self.countColumnValues(
                xlsxPath=xlsxPath, # type: ignore
                sheetName=sheetName, # type: ignore
                columnName=columnName, # type: ignore
                weightColumnName=weightColumnName # type: ignore
            )

            resultText = self.formatResult(
                valueCountDict=valueCountDict,
                sheetName=sheetName, # type: ignore
                columnName=columnName, # type: ignore
                weightColumnName=weightColumnName # type: ignore
            )

            self.resultTextEdit.setPlainText(resultText)
            self.save()

        except Exception as e:
            QMessageBox.critical(self, "统计失败", str(e))