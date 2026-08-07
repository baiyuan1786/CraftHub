##########################################################################################################
#   Description: DeepSeek-OCR屏幕区域识别页面
#                支持输入API Key初始化OCR
#                支持注册Windows系统级热键
#                按热键后选择屏幕区域截图并调用DeepSeek-OCR
#                OCR成功后自动复制识别内容到剪切板
#
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################

import ctypes
import ctypes.wintypes
import datetime
import platform
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple

from PyQt6.QtCore import QObject, QPoint, QRect, QSize, Qt, QAbstractNativeEventFilter, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QRubberBand,
    QVBoxLayout,
)

from page import Page
from path import PATH_HUB_ROOT, PATH_ROOT

from craftHub.tool import DeepSeekOCR_SiliconFlow

class WindowsHotkeyNativeFilter(QAbstractNativeEventFilter):
    '''Windows系统级热键原生事件过滤器'''

    WM_HOTKEY = 0x0312

    def __init__(
            self,
            hotkeyId: int,
            callback
    ) -> None:
        '''初始化Windows系统级热键原生事件过滤器'''

        super().__init__()

        self.hotkeyId = hotkeyId
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        '''Windows原生事件过滤'''

        try:
            msgAddress = self._getMessageAddress(message)
            msg = ctypes.wintypes.MSG.from_address(msgAddress)

            if msg.message == self.WM_HOTKEY and int(msg.wParam) == self.hotkeyId:
                self.callback()
                return True, 0

        except Exception as error:
            print(f"系统级热键消息解析失败: {error}")

        return False, 0

    def _getMessageAddress(self, message) -> int:
        '''获取Windows MSG指针地址'''

        try:
            return int(message)

        except Exception:
            return message.__int__()


class GlobalHotkeyManager(QObject):
    '''Windows系统级热键管理器'''

    hotkeyPressedSignal = pyqtSignal()

    MOD_NOREPEAT = 0x4000
    HOTKEY_ID = 1001

    KEY_MAP: Dict[str, int] = {
        "BACKSPACE": 0x08,
        "TAB": 0x09,
        "ENTER": 0x0D,
        "ESC": 0x1B,
        "ESCAPE": 0x1B,
        "SPACE": 0x20,
        "PAGEUP": 0x21,
        "PAGEDOWN": 0x22,
        "END": 0x23,
        "HOME": 0x24,
        "LEFT": 0x25,
        "UP": 0x26,
        "RIGHT": 0x27,
        "DOWN": 0x28,
        "INSERT": 0x2D,
        "DELETE": 0x2E,
        "PRINTSCREEN": 0x2C,
        "PRTSC": 0x2C,
    }

    for _index in range(1, 25):
        KEY_MAP[f"F{_index}"] = 0x70 + _index - 1

    for _index in range(10):
        KEY_MAP[str(_index)] = 0x30 + _index

    for _char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        KEY_MAP[_char] = ord(_char)

    def __init__(self):
        '''初始化Windows系统级热键管理器'''

        super().__init__()

        self.isRegistered = False
        self.isFilterInstalled = False
        self.hotkeyText = ""

        self.user32 = ctypes.windll.user32 if self._isWindows() else None
        self.kernel32 = ctypes.windll.kernel32 if self._isWindows() else None

        self.nativeFilter = WindowsHotkeyNativeFilter(
            hotkeyId=self.HOTKEY_ID,
            callback=self._emitHotkeyPressed
        )

        if self._isWindows():
            assert self.user32 is not None
            self.user32.RegisterHotKey.argtypes = [
                ctypes.wintypes.HWND,
                ctypes.wintypes.INT,
                ctypes.wintypes.UINT,
                ctypes.wintypes.UINT,
            ]
            self.user32.RegisterHotKey.restype = ctypes.wintypes.BOOL

            self.user32.UnregisterHotKey.argtypes = [
                ctypes.wintypes.HWND,
                ctypes.wintypes.INT,
            ]
            self.user32.UnregisterHotKey.restype = ctypes.wintypes.BOOL

    def registerHotkey(self, hotkeyText: str):
        '''注册系统级热键'''

        if not self._isWindows():
            raise RuntimeError("系统级热键目前仅支持Windows")

        hotkeyText = hotkeyText.strip().upper()

        if not hotkeyText:
            raise ValueError("热键不能为空")

        vkCode = self._parseSingleHotkey(hotkeyText)

        self.unregisterHotkey()
        self._installNativeFilter()

        assert self.user32 is not None
        result = self.user32.RegisterHotKey(
            None,
            self.HOTKEY_ID,
            self.MOD_NOREPEAT,
            vkCode
        )

        if not result:
            assert self.kernel32 is not None
            errorCode = self.kernel32.GetLastError()
            self._removeNativeFilter()

            raise RuntimeError(
                f"注册系统级热键失败: {hotkeyText}，Windows错误码: {errorCode}。"
                f"可能该热键已经被其他程序占用。"
            )

        self.isRegistered = True
        self.hotkeyText = hotkeyText

    def unregisterHotkey(self):
        '''注销系统级热键'''

        if not self._isWindows():
            return

        if self.isRegistered:
            assert self.user32 is not None
            self.user32.UnregisterHotKey(
                None,
                self.HOTKEY_ID
            )

            self.isRegistered = False
            self.hotkeyText = ""

        self._removeNativeFilter()

    def _installNativeFilter(self):
        '''安装原生事件过滤器'''

        if self.isFilterInstalled:
            return

        QApplication.instance().installNativeEventFilter(self.nativeFilter) # type: ignore
        self.isFilterInstalled = True

    def _removeNativeFilter(self):
        '''移除原生事件过滤器'''

        if not self.isFilterInstalled:
            return

        QApplication.instance().removeNativeEventFilter(self.nativeFilter) # type: ignore
        self.isFilterInstalled = False

    def _emitHotkeyPressed(self):
        '''发送热键触发信号'''

        QTimer.singleShot(
            0,
            self.hotkeyPressedSignal.emit
        )

    def _parseSingleHotkey(self, hotkeyText: str) -> int:
        '''解析单一热键'''

        if "+" in hotkeyText:
            raise ValueError("当前只支持单一热键，不支持 Ctrl+F2 这类组合键")

        if hotkeyText not in self.KEY_MAP:
            raise ValueError(
                f"不支持的热键: {hotkeyText}。"
                f"建议使用 F1-F24、Esc、Space、PrintScreen 等单个按键。"
            )

        return self.KEY_MAP[hotkeyText]

    def _isWindows(self) -> bool:
        '''判断是否为Windows系统'''

        return platform.system().lower() == "windows"

class ScreenshotRegionDialog(QDialog):
    '''屏幕快照区域选择窗口'''

    MIN_SELECT_WIDTH = 5
    MIN_SELECT_HEIGHT = 5

    TIP_TEXT = "拖拽选择OCR区域，按 Esc 取消"
    TIP_LEFT = 20
    TIP_TOP = 20

    def __init__(
            self,
            virtualRect: QRect,
            screenshotPixmap: QPixmap
    ) -> None:
        '''初始化屏幕快照区域选择窗口'''

        super().__init__()

        self.virtualRect = virtualRect
        self.screenshotPixmap = screenshotPixmap

        self.selectedRect: Optional[QRect] = None
        self.selectOrigin = QPoint()
        self.rubberBand: Optional[QRubberBand] = None

        self._initWindow()
        self._initBackground()
        self._initTipLabel()

    def _initWindow(self):
        '''初始化窗口'''

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setModal(True)
        self.setGeometry(self.virtualRect)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)

    def _initBackground(self):
        '''初始化背景快照'''

        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(
            0,
            0,
            self.virtualRect.width(),
            self.virtualRect.height()
        )
        self.backgroundLabel.setPixmap(self.screenshotPixmap)
        self.backgroundLabel.setScaledContents(False)

    def _initTipLabel(self):
        '''初始化提示文本'''

        self.tipLabel = QLabel(self.TIP_TEXT, self)
        self.tipLabel.setStyleSheet(
            "QLabel {"
            "background-color: rgba(0, 0, 0, 180);"
            "color: white;"
            "padding: 8px;"
            "font-size: 14px;"
            "}"
        )
        self.tipLabel.move(self.TIP_LEFT, self.TIP_TOP)
        self.tipLabel.adjustSize()

    def keyPressEvent(self, event):
        '''按键事件'''

        if event.key() == Qt.Key.Key_Escape:
            self.selectedRect = None
            self.reject()
            return

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        '''鼠标按下事件'''

        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.selectOrigin = event.position().toPoint()

        if self.rubberBand is None:
            self.rubberBand = QRubberBand(
                QRubberBand.Shape.Rectangle,
                self
            )

        self.rubberBand.setGeometry(QRect(self.selectOrigin, QSize()))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        '''鼠标移动事件'''

        if self.rubberBand is None:
            return

        currentPoint = event.position().toPoint()
        self.rubberBand.setGeometry(
            QRect(self.selectOrigin, currentPoint).normalized()
        )

    def mouseReleaseEvent(self, event):
        '''鼠标释放事件'''

        if event.button() != Qt.MouseButton.LeftButton:
            return

        currentPoint = event.position().toPoint()
        localRect = QRect(self.selectOrigin, currentPoint).normalized()

        if (
                localRect.width() < self.MIN_SELECT_WIDTH or
                localRect.height() < self.MIN_SELECT_HEIGHT
        ):
            self.selectedRect = None
            self.reject()
            return

        globalRect = QRect(localRect)
        globalRect.translate(self.virtualRect.topLeft())

        self.selectedRect = globalRect
        self.accept()


class DeepSeekOcrScreenService(QObject):
    '''DeepSeek-OCR屏幕区域识别业务类'''

    logSignal = pyqtSignal(str)
    successSignal = pyqtSignal(str)
    errorSignal = pyqtSignal(str)

    _workerSuccessSignal = pyqtSignal(str)
    _workerErrorSignal = pyqtSignal(str)

    TEMP_DIR = PATH_ROOT / "temp" / "deepSeekOcr"
    SCREENSHOT_SUFFIX = ".png"

    TOP_RATIO = 1.0

    def __init__(self):
        '''初始化DeepSeek-OCR屏幕区域识别业务类'''

        super().__init__()

        self.apiKey = ""
        self.isRunning = False

        self._workerSuccessSignal.connect(self._handleWorkerSuccess)
        self._workerErrorSignal.connect(self._handleWorkerError)

    def setApiKey(self, apiKey: str):
        '''设置API Key'''

        self.apiKey = apiKey.strip()

    def captureAndOcr(self):
        '''框选屏幕区域并执行OCR'''

        if self.isRunning:
            self.errorSignal.emit("OCR正在执行中，请等待当前任务结束")
            return

        if not self.apiKey:
            self.errorSignal.emit("请先输入API Key并初始化OCR")
            return

        selectedRect = self._selectScreenRegion()

        if selectedRect is None:
            self.logSignal.emit("已取消区域选择")
            return

        try:
            imagePath = self._captureRectToImage(selectedRect)

        except Exception as error:
            self.errorSignal.emit(f"截图失败: {str(error)}")
            return

        self.isRunning = True

        self.logSignal.emit(f"截图完成: {imagePath}")
        self.logSignal.emit("正在调用DeepSeek-OCR...")

        thread = threading.Thread(
            target=self._runOcrInThread,
            args=(imagePath,),
            daemon=True
        )
        thread.start()

    def _selectScreenRegion(self) -> Optional[QRect]:
        '''选择屏幕区域'''

        try:
            screenshotPixmap, virtualRect = self._captureVirtualDesktopPixmap()

        except Exception as error:
            self.errorSignal.emit(f"获取屏幕快照失败: {str(error)}")
            return None

        dialog = ScreenshotRegionDialog(
            virtualRect=virtualRect,
            screenshotPixmap=screenshotPixmap
        )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:
            return None

        return dialog.selectedRect

    def _getVirtualScreenRect(self) -> QRect:
        '''获取虚拟屏幕区域'''

        screenList = QGuiApplication.screens()

        if not screenList:
            raise RuntimeError("无法获取屏幕信息")

        virtualRect = QRect(screenList[0].geometry())

        for screen in screenList[1:]:
            virtualRect = virtualRect.united(screen.geometry())

        return virtualRect

    def _captureVirtualDesktopPixmap(self) -> Tuple[QPixmap, QRect]:
        '''获取所有屏幕组成的虚拟桌面快照'''

        screenList = QGuiApplication.screens()

        if not screenList:
            raise RuntimeError("无法获取屏幕信息")

        virtualRect = self._getVirtualScreenRect()

        desktopPixmap = QPixmap(virtualRect.size())
        desktopPixmap.fill(Qt.GlobalColor.black)

        painter = QPainter(desktopPixmap)

        try:
            for screen in screenList:
                screenGeometry = screen.geometry()
                screenPixmap = screen.grabWindow(0) # type: ignore

                if screenPixmap.isNull():
                    continue

                targetRect = QRect(
                    screenGeometry.topLeft() - virtualRect.topLeft(),
                    screenGeometry.size()
                )

                painter.drawPixmap(
                    targetRect,
                    screenPixmap,
                    screenPixmap.rect()
                )

        finally:
            painter.end()

        return desktopPixmap, virtualRect

    def _captureRectToImage(self, rect: QRect) -> Path:
        '''截取指定屏幕区域为图片，支持多屏'''

        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        imagePath = self.TEMP_DIR / f"ocr_{timestamp}{self.SCREENSHOT_SUFFIX}"

        screenList = QGuiApplication.screens()

        if not screenList:
            raise RuntimeError("无法获取屏幕信息")

        targetPixmap = QPixmap(rect.size())
        targetPixmap.fill(Qt.GlobalColor.white)

        painter = QPainter(targetPixmap)

        try:
            hasCaptured = False

            for screen in screenList:
                screenGeometry = screen.geometry()
                intersectedRect = rect.intersected(screenGeometry)

                if intersectedRect.isEmpty():
                    continue

                localRect = QRect(intersectedRect)
                localRect.translate(
                    -screenGeometry.x(),
                    -screenGeometry.y()
                )

                screenPixmap = screen.grabWindow(
                    0, # type: ignore
                    localRect.x(),
                    localRect.y(),
                    localRect.width(),
                    localRect.height()
                )

                if screenPixmap.isNull():
                    continue

                targetRect = QRect(
                    intersectedRect.topLeft() - rect.topLeft(),
                    intersectedRect.size()
                )

                painter.drawPixmap(
                    targetRect,
                    screenPixmap,
                    screenPixmap.rect()
                )

                hasCaptured = True

        finally:
            painter.end()

        if not hasCaptured:
            raise RuntimeError("未能从任何屏幕中截取到有效图像")

        if not targetPixmap.save(str(imagePath), "PNG"):
            raise RuntimeError(f"截图保存失败: {imagePath}")

        return imagePath

    def _runOcrInThread(self, imagePath: Path):
        '''在线程中执行OCR'''

        try:
            ocrClient = DeepSeekOCR_SiliconFlow(apiKey=self.apiKey)
            textList = ocrClient.ocr(
                imagePath=str(imagePath),
                topRatio=self.TOP_RATIO
            )

            if not textList:
                raise RuntimeError("OCR未返回有效文本")

            resultText = "\n".join(
                text.strip()
                for text in textList
                if text.strip()
            )

            if not resultText:
                raise RuntimeError("OCR结果为空")

            self._workerSuccessSignal.emit(resultText)

        except Exception as error:
            self._workerErrorSignal.emit(str(error))

    def _handleWorkerSuccess(self, resultText: str):
        '''处理OCR成功结果'''

        self.isRunning = False
        QApplication.clipboard().setText(resultText) # type: ignore
        self.successSignal.emit(resultText)

    def _handleWorkerError(self, errorText: str):
        '''处理OCR失败结果'''

        self.isRunning = False
        self.errorSignal.emit(errorText)


class DeepSeekOcrPage(Page):
    '''DeepSeek-OCR屏幕区域识别页面'''

    PAGE_TITLE = "DeepSeek-OCR屏幕识别"
    PATH_DATA = PATH_HUB_ROOT / "tool" / "deepSeekOcr" / "data.yaml"

    DEFAULT_HOTKEY_TEXT = "F2"

    def __init__(self):
        '''初始化DeepSeek-OCR屏幕区域识别页面'''

        super().__init__(
            title=self.PAGE_TITLE,
            dataPath=self.PATH_DATA
        )

        self.ocrService = DeepSeekOcrScreenService()
        self.hotkeyManager = GlobalHotkeyManager()

        self.initUI()
        self._connectServiceSignals()
        self._connectHotkeySignals()

        self.load()
        self._syncConfigToService()

    def initUI(self):
        '''初始化界面'''

        self.apiKeyEdit = QLineEdit()
        self.apiKeyEdit.setObjectName("apiKeyEdit")
        self.apiKeyEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.apiKeyEdit.setPlaceholderText("请输入 SiliconFlow API Key")

        self.hotkeyEdit = QLineEdit()
        self.hotkeyEdit.setObjectName("hotkeyEdit")
        self.hotkeyEdit.setText(self.DEFAULT_HOTKEY_TEXT)
        self.hotkeyEdit.setPlaceholderText("请输入单个系统级热键，例如 F2")

        self.statusLabel = QLabel("状态: 未初始化")

        self.resultTextEdit = QPlainTextEdit()
        self.resultTextEdit.setObjectName("resultTextEdit")
        self.resultTextEdit.setReadOnly(True)

        self.initBtn = QPushButton("初始化OCR并注册热键")
        self.startBtn = QPushButton("手动开始区域OCR")
        self.clearBtn = QPushButton("清空结果")

        self.initBtn.clicked.connect(self.initOcr)
        self.startBtn.clicked.connect(self.startOcr)
        self.clearBtn.clicked.connect(self.resultTextEdit.clear)

        formLayout = QGridLayout()
        formLayout.addWidget(QLabel("API Key:"), 0, 0)
        formLayout.addWidget(self.apiKeyEdit, 0, 1, 1, 2)

        formLayout.addWidget(QLabel("系统级热键:"), 1, 0)
        formLayout.addWidget(self.hotkeyEdit, 1, 1)
        formLayout.addWidget(self.statusLabel, 1, 2)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.initBtn)
        btnLayout.addWidget(self.startBtn)
        btnLayout.addWidget(self.clearBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(btnLayout)
        mainLayout.addWidget(QLabel("OCR结果 / 日志:"))
        mainLayout.addWidget(self.resultTextEdit)

        self.setLayout(mainLayout)

    def initOcr(self):
        '''初始化OCR并注册系统级热键'''

        try:
            self._syncConfigToService(raiseError=True)
            self._registerGlobalHotkey()

            self.statusLabel.setText(
                f"状态: 已初始化，系统级热键 {self.hotkeyManager.hotkeyText} 已注册"
            )

            self._appendLog(
                f"OCR初始化完成，系统级热键 {self.hotkeyManager.hotkeyText} 已注册"
            )

            self.save()

        except Exception as error:
            QMessageBox.critical(
                self,
                "初始化失败",
                str(error)
            )
            self.statusLabel.setText("状态: 初始化失败")

    def startOcr(self):
        '''开始OCR'''

        try:
            self._syncConfigToService(raiseError=True)

        except Exception as error:
            QMessageBox.critical(
                self,
                "OCR配置异常",
                str(error)
            )
            return

        self.save()
        self.ocrService.captureAndOcr()

    def remove(self):
        '''页面移除回调'''

        self.hotkeyManager.unregisterHotkey()
        super().remove()

    def _connectServiceSignals(self):
        '''连接业务类信号'''

        self.ocrService.logSignal.connect(self._appendLog)
        self.ocrService.successSignal.connect(self._handleOcrSuccess)
        self.ocrService.errorSignal.connect(self._handleOcrError)

    def _connectHotkeySignals(self):
        '''连接系统级热键信号'''

        self.hotkeyManager.hotkeyPressedSignal.connect(self.startOcr)

    def _registerGlobalHotkey(self):
        '''注册系统级热键'''

        hotkeyText = self.hotkeyEdit.text().strip() or self.DEFAULT_HOTKEY_TEXT
        self.hotkeyManager.registerHotkey(hotkeyText)

    def _syncConfigToService(self, raiseError: bool = False):
        '''同步页面配置到业务类'''

        try:
            apiKey = self.apiKeyEdit.text().strip()

            if not apiKey:
                raise ValueError("API Key不能为空")

            self.ocrService.setApiKey(apiKey)

            if self.hotkeyManager.isRegistered:
                self.statusLabel.setText(
                    f"状态: 已初始化，系统级热键 {self.hotkeyManager.hotkeyText} 已注册"
                )
            else:
                self.statusLabel.setText("状态: 已初始化，热键未注册")

        except Exception as error:
            self.statusLabel.setText("状态: 配置异常")

            if raiseError:
                raise error

    def _handleOcrSuccess(self, resultText: str):
        '''处理OCR成功'''

        self.statusLabel.setText("状态: OCR成功，结果已复制到剪切板")

        self._appendLog("")
        self._appendLog("=" * 80)
        self._appendLog("OCR成功，结果已复制到剪切板")
        self._appendLog("=" * 80)
        self._appendLog(resultText)

    def _handleOcrError(self, errorText: str):
        '''处理OCR失败'''

        self.statusLabel.setText("状态: OCR失败")
        self._appendLog(f"OCR失败: {errorText}")

        QMessageBox.critical(
            self,
            "OCR失败",
            errorText
        )

    def _appendLog(self, text: str):
        '''追加日志'''

        self.resultTextEdit.appendPlainText(text)