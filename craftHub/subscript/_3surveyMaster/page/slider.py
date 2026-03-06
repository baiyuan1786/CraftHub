##########################################################################################################
#   Description: 滑块类
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import QPoint, Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QMouseEvent

class SwitchSlider(QWidget):
    """自定义滑块切换控件 - 只有两种状态"""

    stateChanged = pyqtSignal(bool)  # True: 左侧状态, False: 右侧状态
    
    def __init__(self, leftText = "信息录入", rightText = "信息读取", parent = None):
        super().__init__(parent)
        self.leftText = leftText
        self.rightText = rightText
        self.isLeftState = True  # 初始在左侧
        self.initUI()
    
    def initUI(self):
        # 设置固定大小
        self.setFixedSize(200, 50)
        
        # 创建滑块背景
        self.backgroundFrame = QFrame(self)
        self.backgroundFrame.setGeometry(0, 10, 200, 30)
        self.backgroundFrame.setStyleSheet("""
            QFrame {
                background-color: #e0e0e0;
                border-radius: 15px;
            }
        """)
        
        # 创建滑块
        self.slider = QFrame(self.backgroundFrame)
        self.slider.setGeometry(2, 2, 96, 26)
        self.slider.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 13px;
            }
        """)
        
        # 创建标签
        self.leftLabel = QLabel(self.leftText, self)
        self.leftLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.leftLabel.setGeometry(0, 0, 100, 50)
        
        self.rightLabel = QLabel(self.rightText, self)
        self.rightLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rightLabel.setGeometry(100, 0, 100, 50)
        
        # 设置初始状态
        self.updateLabels()
    
    def mousePressEvent(self, event: QMouseEvent):
        """点击切换状态"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleState()

    def toggleState(self):
        """切换滑块状态"""
        self.isLeftState = not self.isLeftState
        
        # 创建动画
        animation = QPropertyAnimation(self.slider, b"pos")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        if self.isLeftState:
            # 移动到左侧 (2, 2)
            animation.setEndValue(QPoint(2, 2))
        else:
            # 移动到右侧 (背景宽度 - 滑块宽度 - 2, 2)
            xPos = self.backgroundFrame.width() - self.slider.width() - 2
            animation.setEndValue(QPoint(xPos, 2))
        
        animation.start()
        self.updateLabels()
        
        # 发送状态改变信号
        self.stateChanged.emit(self.isLeftState)
    
    def updateLabels(self):
        """更新标签颜色"""
        if self.isLeftState:
            self.leftLabel.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            self.rightLabel.setStyleSheet("color: #666666; font-weight: normal; font-size: 14px;")
        else:
            self.leftLabel.setStyleSheet("color: #666666; font-weight: normal; font-size: 14px;")
            self.rightLabel.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
    
    def setState(self, isLeftState: bool):
        """设置滑块状态（不触发动画）"""
        if self.isLeftState != isLeftState:
            self.isLeftState = isLeftState
            if self.isLeftState:
                self.slider.move(2, 2)
            else:
                self.slider.move(self.backgroundFrame.width() - self.slider.width() - 2, 2)
            self.updateLabels()
    
    def getState(self) -> bool:
        """获取当前状态"""
        return self.isLeftState
    
    def setLeftText(self, text: str):
        """设置左侧文本"""
        self.leftText = text
        self.leftLabel.setText(text)
    
    def setRightText(self, text: str):
        """设置右侧文本"""
        self.rightText = text
        self.rightLabel.setText(text)


