##########################################################################################################
#   Description: 表格插入器GUI页面
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################

from pathlib import Path
from typing import Any, Optional

from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QComboBox,
    QLineEdit,
    QMessageBox
)

from .ui.Ui_tableInserter import Ui_Form
from .main import TableInserterMain
from .worker import TableInserterWorker

from path import PATH_TOOL
from craftHub.tool import GLog
from page import Page


PATH_DATA = (
    PATH_TOOL
    / "tableInserter"
    / "data"
    / "data.yaml"
)


class TableInserterPage(Page, Ui_Form):
    '''表格插入器GUI页面'''

    INSERT_MODE_FIXED_POINT = "fixedPoint"
    INSERT_MODE_SINGLE_SIGN = "singleSign"
    INSERT_MODE_DOUBLE_SIGN = "doubleSign"

    SIZE_MODE_FIXED_WIDTH = "fixedWidth"
    SIZE_MODE_FIXED_HEIGHT = "fixedHeight"
    SIZE_MODE_MAX_SIZE = "maxSize"

    INSERT_TYPE_OLE_EMBED = "OLE_EMBED"
    INSERT_TYPE_XL_PICTURE = "xlPicture"
    INSERT_TYPE_XL_BITMAP = "xlBitmap"

    # 按照当前内部约定：
    # 上、左、下、右分别转换为2、4、8、6。
    ATTACHMENT_TOP = 2
    ATTACHMENT_LEFT = 4
    ATTACHMENT_BOTTOM = 8
    ATTACHMENT_RIGHT = 6

    INSERT_BUTTON_TEXT = "Insert"
    INSERT_RUNNING_BUTTON_TEXT = "正在插入..."

    VALID_EXCEL_SUFFIX_SET = {
        ".xlsx",
        ".xlsm",
        ".xls"
    }

    MAX_SIZE_VALUE = 1000000000.0
    SIZE_DECIMAL_COUNT = 6

    def __init__(self):
        # 初始化页面
        Page.__init__(
            self,
            "tableInserter",
            PATH_DATA
        )

        Ui_Form.__init__(self)
        self.setupUi(self)

        # 必须保存线程引用，防止线程运行过程中被回收
        self.insertWorker: Optional[
            TableInserterWorker
        ] = None

        self._initializeComboBoxes()
        self._initializeValidators()
        self._connectSignals()

        self._updateInsertModeWidgets()
        self._updateSizeModeWidgets()
        self.load()

    def _initializeComboBoxes(self) -> None:
        '''初始化所有组合框选项'''

        self._initializeInsertModeComboBox()
        self._initializeSizeModeComboBox()
        self._initializeAttachmentComboBoxes()
        self._initializeOLETypeComboBox()

    def _initializeInsertModeComboBox(self) -> None:
        '''初始化插入模式组合框'''

        self.comboBox_insertMod.clear()

        self.comboBox_insertMod.addItem(
            "固定点插入",
            self.INSERT_MODE_FIXED_POINT
        )

        self.comboBox_insertMod.addItem(
            "单标记模式",
            self.INSERT_MODE_SINGLE_SIGN
        )

        self.comboBox_insertMod.addItem(
            "双标记模式",
            self.INSERT_MODE_DOUBLE_SIGN
        )

        self.comboBox_insertMod.setCurrentIndex(-1)

    def _initializeSizeModeComboBox(self) -> None:
        '''初始化尺寸控制模式组合框'''

        self.comboBox_sizeMod.clear()

        self.comboBox_sizeMod.addItem(
            "固定宽度",
            self.SIZE_MODE_FIXED_WIDTH
        )

        self.comboBox_sizeMod.addItem(
            "固定高度",
            self.SIZE_MODE_FIXED_HEIGHT
        )

        self.comboBox_sizeMod.addItem(
            "限制宽度和高度",
            self.SIZE_MODE_MAX_SIZE
        )

        self.comboBox_sizeMod.setCurrentIndex(-1)

    def _initializeAttachmentComboBoxes(self) -> None:
        '''初始化方向组合框'''

        attachmentItemList = [
            (
                "上",
                self.ATTACHMENT_TOP
            ),
            (
                "左",
                self.ATTACHMENT_LEFT
            ),
            (
                "下",
                self.ATTACHMENT_BOTTOM
            ),
            (
                "右",
                self.ATTACHMENT_RIGHT
            )
        ]

        comboBoxList = [
            self.comboBox_attachment1,
            self.comboBox_attachment2,
            self.comboBox_attachmentTable
        ]

        for comboBox in comboBoxList:
            comboBox.clear()

            for displayName, attachment in (
                    attachmentItemList
            ):
                comboBox.addItem(
                    displayName,
                    attachment
                )

            comboBox.setCurrentIndex(-1)

    def _initializeOLETypeComboBox(self) -> None:
        '''初始化OLE类型组合框'''

        self.comboBox_oleType.clear()

        self.comboBox_oleType.addItem(
            "OLE嵌入对象",
            self.INSERT_TYPE_OLE_EMBED
        )

        self.comboBox_oleType.addItem(
            "Excel矢量图片",
            self.INSERT_TYPE_XL_PICTURE
        )

        self.comboBox_oleType.addItem(
            "Excel位图",
            self.INSERT_TYPE_XL_BITMAP
        )

        self.comboBox_oleType.setCurrentIndex(-1)

    def _initializeValidators(self) -> None:
        '''初始化尺寸输入框校验器'''

        sizeLineEditList = [
            self.lineEdit_fixedWidth,
            self.lineEdit_fixedHeight,
            self.lineEdit_maxWidth,
            self.lineEdit_maxHeight
        ]

        for lineEdit in sizeLineEditList:
            validator = QDoubleValidator(
                0.0,
                self.MAX_SIZE_VALUE,
                self.SIZE_DECIMAL_COUNT,
                lineEdit
            )

            validator.setNotation(
                QDoubleValidator.Notation.StandardNotation
            )

            lineEdit.setValidator(
                validator
            )

    def _connectSignals(self) -> None:
        '''连接组合框状态变化信号'''

        self.comboBox_insertMod.currentIndexChanged.connect(
            self._updateInsertModeWidgets
        )

        self.comboBox_sizeMod.currentIndexChanged.connect(
            self._updateSizeModeWidgets
        )

        # pushButton已经在Ui_Form.setupUi()中连接了insertGUImain，
        # 这里不能重复连接，否则单击一次会执行两次。

    def _updateInsertModeWidgets(self) -> None:
        '''根据插入模式启用或禁用定位参数控件'''

        insertMode = (
            self.comboBox_insertMod.currentData()
        )

        attachment1Enabled = insertMode in {
            self.INSERT_MODE_SINGLE_SIGN,
            self.INSERT_MODE_DOUBLE_SIGN
        }

        sign2Enabled = (
            insertMode
            == self.INSERT_MODE_DOUBLE_SIGN
        )

        self._setWidgetsEnabled(
            attachment1Enabled,
            self.label_5,
            self.comboBox_attachment1
        )

        self._setWidgetsEnabled(
            sign2Enabled,
            self.label_9,
            self.lineEdit_sign2
        )

        self._setWidgetsEnabled(
            sign2Enabled,
            self.label_7,
            self.comboBox_attachment2
        )

        # 表格自身的插入基点方向在所有模式下都需要
        self._setWidgetsEnabled(
            True,
            self.label_8,
            self.comboBox_attachmentTable
        )

    def _updateSizeModeWidgets(self) -> None:
        '''根据尺寸模式启用或禁用尺寸参数控件'''

        sizeMode = (
            self.comboBox_sizeMod.currentData()
        )

        fixedWidthEnabled = (
            sizeMode
            == self.SIZE_MODE_FIXED_WIDTH
        )

        fixedHeightEnabled = (
            sizeMode
            == self.SIZE_MODE_FIXED_HEIGHT
        )

        maxSizeEnabled = (
            sizeMode
            == self.SIZE_MODE_MAX_SIZE
        )

        self._setWidgetsEnabled(
            fixedWidthEnabled,
            self.label_13,
            self.lineEdit_fixedWidth
        )

        self._setWidgetsEnabled(
            fixedHeightEnabled,
            self.label_12,
            self.lineEdit_fixedHeight
        )

        self._setWidgetsEnabled(
            maxSizeEnabled,
            self.label_15,
            self.lineEdit_maxWidth
        )

        self._setWidgetsEnabled(
            maxSizeEnabled,
            self.label_14,
            self.lineEdit_maxHeight
        )

    @staticmethod
    def _setWidgetsEnabled(
            enabled: bool,
            *widgetList
    ) -> None:
        '''统一设置一组控件的启用状态'''

        for widget in widgetList:
            widget.setEnabled(enabled)

    def insertGUImain(self) -> None:
        '''读取GUI参数并启动表格插入线程'''

        if (
                self.insertWorker is not None
                and self.insertWorker.isRunning()
        ):
            QMessageBox.warning(
                self,
                "任务正在运行",
                "表格插入任务正在运行，请勿重复启动。"
            )

            return

        try:
            tableInserterMain = (
                self._createTableInserterMain()
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "输入参数错误",
                str(e)
            )

            return

        self._setRunningState(
            isRunning=True
        )

        self.insertWorker = TableInserterWorker(
            tableInserterMain=tableInserterMain
        )

        self.insertWorker.succeeded.connect(
            self._onInsertSucceeded
        )

        self.insertWorker.failed.connect(
            self._onInsertFailed
        )

        self.insertWorker.finished.connect(
            self._onInsertFinished
        )

        self.insertWorker.start()

    def _createTableInserterMain(
            self
    ) -> TableInserterMain:
        '''读取并校验GUI参数，创建业务主类'''

        cadPath = self._readCADPath()
        excelPath = self._readExcelPath()
        sheetName = self._readSheetName()

        insertMode = self._readRequiredComboData(
            comboBox=self.comboBox_insertMod,
            parameterName="插入模式"
        )

        sizeMode = self._readRequiredComboData(
            comboBox=self.comboBox_sizeMod,
            parameterName="尺寸控制模式"
        )

        insertType = self._readRequiredComboData(
            comboBox=self.comboBox_oleType,
            parameterName="OLE类型"
        )

        searchBlockReference = (
            self.checkBox_searchBlockReference.isChecked()
        )

        tableAttachment = int(
            self._readRequiredComboData(
                comboBox=self.comboBox_attachmentTable,
                parameterName="表格插入基点方向"
            )
        )

        attachment1 = self.ATTACHMENT_TOP
        attachment2 = self.ATTACHMENT_TOP
        sign2: Optional[str] = None

        if insertMode in {
                self.INSERT_MODE_SINGLE_SIGN,
                self.INSERT_MODE_DOUBLE_SIGN
        }:
            attachment1 = int(
                self._readRequiredComboData(
                    comboBox=self.comboBox_attachment1,
                    parameterName="第一标记方向"
                )
            )

        if (
                insertMode
                == self.INSERT_MODE_DOUBLE_SIGN
        ):
            sign2 = (
                self.lineEdit_sign2.text().strip()
            )

            if not sign2:
                raise ValueError(
                    "双标记模式必须输入第二标记值。"
                )

            attachment2 = int(
                self._readRequiredComboData(
                    comboBox=self.comboBox_attachment2,
                    parameterName="第二标记方向"
                )
            )

        fixedWidth: Optional[float] = None
        fixedHeight: Optional[float] = None
        maxWidth: Optional[float] = None
        maxHeight: Optional[float] = None

        if (
                sizeMode
                == self.SIZE_MODE_FIXED_WIDTH
        ):
            fixedWidth = self._readPositiveFloat(
                lineEdit=self.lineEdit_fixedWidth,
                parameterName="固定宽度"
            )

        elif (
                sizeMode
                == self.SIZE_MODE_FIXED_HEIGHT
        ):
            fixedHeight = self._readPositiveFloat(
                lineEdit=self.lineEdit_fixedHeight,
                parameterName="固定高度"
            )

        elif (
                sizeMode
                == self.SIZE_MODE_MAX_SIZE
        ):
            maxWidth = self._readPositiveFloat(
                lineEdit=self.lineEdit_maxWidth,
                parameterName="最大宽度"
            )

            maxHeight = self._readPositiveFloat(
                lineEdit=self.lineEdit_maxHeight,
                parameterName="最大高度"
            )

        else:
            raise ValueError(
                f"未知尺寸控制模式: {sizeMode}"
            )

        return TableInserterMain(
            cadPath=cadPath,
            excelPath=excelPath,
            sheetName=sheetName,
            insertMode=insertMode,
            attachment1=attachment1, # type: ignore
            sign2=sign2,
            attachment2=attachment2, # type: ignore
            insertType=insertType,
            tableAttachment=tableAttachment, # type: ignore
            sizeMode=sizeMode,
            fixedWidth=fixedWidth,
            fixedHeight=fixedHeight,
            maxWidth=maxWidth,
            maxHeight=maxHeight,
            searchBlockReference=searchBlockReference
        )

    def _readCADPath(self) -> Path:
        '''读取并校验CAD文件路径'''

        rawPath = (
            self.lineEdit_cadPath.text().strip()
        )

        if not rawPath:
            raise ValueError(
                "请输入CAD文件路径。"
            )

        cadPath = Path(rawPath)

        if not cadPath.exists():
            raise FileNotFoundError(
                f"CAD文件不存在: {cadPath}"
            )

        if not cadPath.is_file():
            raise ValueError(
                f"CAD路径不是文件: {cadPath}"
            )

        if cadPath.suffix.lower() != ".dxf":
            raise ValueError(
                "当前表格插入器只支持DXF文件。"
            )

        return cadPath

    def _readExcelPath(self) -> Path:
        '''读取并校验Excel文件路径'''

        rawPath = (
            self.lineEdit_excelPath.text().strip()
        )

        if not rawPath:
            raise ValueError(
                "请输入Excel文件路径。"
            )

        excelPath = Path(rawPath)

        if not excelPath.exists():
            raise FileNotFoundError(
                f"Excel文件不存在: {excelPath}"
            )

        if not excelPath.is_file():
            raise ValueError(
                f"Excel路径不是文件: {excelPath}"
            )

        if (
                excelPath.suffix.lower()
                not in self.VALID_EXCEL_SUFFIX_SET
        ):
            raise ValueError(
                "Excel文件仅支持.xlsx、.xlsm和.xls格式。"
            )

        return excelPath

    def _readSheetName(self) -> str:
        '''读取并校验Sheet名称'''

        sheetName = (
            self.lineEdit_sheetName.text().strip()
        )

        if not sheetName:
            raise ValueError(
                "请输入Excel Sheet名称。"
            )

        return sheetName

    @staticmethod
    def _readRequiredComboData(
            comboBox: QComboBox,
            parameterName: str
    ) -> Any:
        '''读取必须选择的组合框数据'''

        if comboBox.currentIndex() < 0:
            raise ValueError(
                f"请选择{parameterName}。"
            )

        currentData = comboBox.currentData()

        if currentData is None:
            raise ValueError(
                f"请选择{parameterName}。"
            )

        return currentData

    @staticmethod
    def _readPositiveFloat(
            lineEdit: QLineEdit,
            parameterName: str
    ) -> float:
        '''读取并校验大于0的浮点数'''

        rawValue = lineEdit.text().strip()

        if not rawValue:
            raise ValueError(
                f"请输入{parameterName}。"
            )

        try:
            value = float(rawValue)

        except ValueError as e:
            raise ValueError(
                f"{parameterName}必须是数字: "
                f"{rawValue}"
            ) from e

        if value <= 0:
            raise ValueError(
                f"{parameterName}必须大于0。"
            )

        return value

    def _setRunningState(
            self,
            isRunning: bool
    ) -> None:
        '''设置任务运行期间的按钮状态'''

        self.pushButton.setEnabled(
            not isRunning
        )

        if isRunning:
            self.pushButton.setText(
                self.INSERT_RUNNING_BUTTON_TEXT
            )

        else:
            self.pushButton.setText(
                self.INSERT_BUTTON_TEXT
            )

    def _onInsertSucceeded(
            self,
            totalCount: int,
            locatedCount: int,
            insertedCount: int
    ) -> None:
        '''处理表格插入成功信号'''

        skippedCount = (
            totalCount
            - insertedCount
        )

        QMessageBox.information(
            self,
            "表格插入完成",
            (
                f"表格插入任务已经完成。\n\n"
                f"表格总数：{totalCount}\n"
                f"成功定位：{locatedCount}\n"
                f"成功插入：{insertedCount}\n"
                f"未插入：{skippedCount}\n\n"
                f"CAD文件保持打开且尚未自动保存，"
                f"请检查插入结果后手动保存。"
            )
        )

    def _onInsertFailed(
            self,
            errorMessage: str,
            errorTraceback: str
    ) -> None:
        '''处理表格插入失败信号'''

        GLog.logInfo(
            f"{GLog.YELLOW}"
            f"表格插入失败:\n"
            f"{errorTraceback}"
            f"{GLog.END}"
        )

        QMessageBox.critical(
            self,
            "表格插入失败",
            errorMessage
        )

    def _onInsertFinished(self) -> None:
        '''处理表格插入线程结束'''

        self._setRunningState(
            isRunning=False
        )

        if self.insertWorker is None:
            return

        worker = self.insertWorker
        self.insertWorker = None

        worker.deleteLater()