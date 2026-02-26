##########################################################################################################
#   Description: 网页代理模块
#   Authors:     BaiYuan <395642104@qq.com>
##########################################################################################################
from page import Page
from path import PATH_HUB_ROOT

import subprocess
import sys
import os
from typing import Optional
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QComboBox, QLabel, 
                             QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt

PATH_DATA = PATH_HUB_ROOT / "tool" / "webProxy" / "data.yaml"

class ProxyBrowserLauncherGUI(Page):
    def __init__(self):
        super().__init__(title = "WebProxy", dataPath = PATH_DATA)
        self.proxyLauncher = None
        self.initUI()
    
    def initUI(self):
        self.setGeometry(300, 300, 400, 300)
        
        # 代理设置组
        proxyGroup = QGroupBox("代理服务器设置", self)
        proxyLayout = QVBoxLayout()
        
        # IP地址输入
        ipLayout = QHBoxLayout()
        ipLayout.addWidget(QLabel("代理IP:"))
        self.ipInput = QLineEdit("192.168.1.100")
        self.ipInput.setObjectName("ipInput")
        ipLayout.addWidget(self.ipInput)
        proxyLayout.addLayout(ipLayout)
        
        # 端口输入
        portLayout = QHBoxLayout()
        portLayout.addWidget(QLabel("代理端口:"))
        self.portInput = QLineEdit("8080")
        self.portInput.setObjectName("portInput")
        portLayout.addWidget(self.portInput)
        proxyLayout.addLayout(portLayout)
        
        # URL输入
        urlLayout = QHBoxLayout()
        urlLayout.addWidget(QLabel("初始URL:"))
        self.urlInput = QLineEdit("https://www.baidu.com")
        self.urlInput.setObjectName("urlInput")
        urlLayout.addWidget(self.urlInput)
        proxyLayout.addLayout(urlLayout)
        
        proxyGroup.setLayout(proxyLayout)
        
        # 浏览器选择组
        browserGroup = QGroupBox("浏览器选择", self)
        browserLayout = QVBoxLayout()
        
        self.browserCombo = QComboBox()
        self.browserCombo.addItems(["自动选择", "Google Chrome", "Microsoft Edge"])
        self.browserCombo.setObjectName("browserCombo")
        browserLayout.addWidget(self.browserCombo)
        
        browserGroup.setLayout(browserLayout)
        
        # 按钮组
        buttonLayout = QHBoxLayout()
        
        self.launchButton = QPushButton("启动浏览器")
        self.launchButton.clicked.connect(self.launchBrowser)
        self.launchButton.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        
        self.testButton = QPushButton("测试代理")
        self.testButton.clicked.connect(self.testProxy)
        
        buttonLayout.addWidget(self.launchButton)
        buttonLayout.addWidget(self.testButton)
        
        # 主布局
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(proxyGroup)
        mainLayout.addWidget(browserGroup)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        
        self.load()
    
    def getBrowserType(self) -> str:
        """获取选择的浏览器类型"""
        selection = self.browserCombo.currentText()
        if selection == "Google Chrome":
            return "chrome"
        elif selection == "Microsoft Edge":
            return "edge"
        else:
            return "auto"
    
    def launchBrowser(self):
        """启动浏览器"""
        try:
            proxyIp = self.ipInput.text().strip()
            proxyPort = int(self.portInput.text().strip())
            url = self.urlInput.text().strip() or None
            
            self.proxyLauncher = BrowserProxyLauncher(proxyIp, proxyPort)
            
            success = self.proxyLauncher.launchBrowserWithProxy(
                browserType=self.getBrowserType(),
                url=url
            )
            
            if success:
                QMessageBox.information(self, "成功", "浏览器启动成功！")
            else:
                QMessageBox.warning(self, "错误", "浏览器启动失败，请检查配置！")
                
        except ValueError:
            QMessageBox.critical(self, "错误", "端口号必须是数字！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发生错误: {str(e)}")
    
    def testProxy(self):
        """测试代理连接（简单实现）"""
        proxyIp = self.ipInput.text().strip()
        proxyPort = self.portInput.text().strip()
        
        if proxyIp and proxyPort:
            QMessageBox.information(self, "测试", 
                                  f"代理设置:\nIP: {proxyIp}\n端口: {proxyPort}\n\n请确保代理服务器正在运行。")
        else:
            QMessageBox.warning(self, "错误", "请填写完整的代理信息！")

# 增强版的BrowserProxyLauncher类
class BrowserProxyLauncher:
    def __init__(self, proxy_ip: str, proxy_port: int):
        self.proxyIp = proxy_ip
        self.proxyPort = proxy_port
        self.proxyServer = f"{proxy_ip}:{proxy_port}"
    
    def launchChromeWithProxy(self, url: Optional[str] = None) -> bool:
        """启动Chrome浏览器并设置代理"""
        try:
            # Chrome命令行参数
            chromeArgs = [
                f"--proxy-server={self.proxyServer}",
                "--no-first-run",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-translate"
            ]
            
            if url:
                chromeArgs.append(url)
            
            # 平台特定的命令
            if sys.platform == "win32":
                # Windows
                chromePaths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                ]
                for path in chromePaths:
                    if os.path.exists(path):
                        subprocess.Popen([path] + chromeArgs)
                        print(f"Chrome启动成功，使用代理: {self.proxyServer}")
                        return True
            else:
                # Linux/macOS
                chromeExecutables = ["google-chrome", "chrome", "google-chrome-stable"]
                for executable in chromeExecutables:
                    try:
                        subprocess.Popen([executable] + chromeArgs)
                        print(f"Chrome启动成功，使用代理: {self.proxyServer}")
                        return True
                    except FileNotFoundError:
                        continue
            
            return False
            
        except Exception as e:
            print(f"启动Chrome时出错: {e}")
            return False
    
    def launchEdgeWithProxy(self, url: Optional[str] = None) -> bool:
        """启动Edge浏览器并设置代理"""
        try:
            # Edge命令行参数
            edgeArgs = [
                f"--proxy-server=http://{self.proxyServer}",
                f"--proxy-bypass-list=<-loopback>"
            ]
            
            if url:
                edgeArgs.append(url)
            
            # 平台特定的命令
            if sys.platform == "win32":
                # Windows
                edgePaths = [
                    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
                ]
                for path in edgePaths:
                    if os.path.exists(path):
                        subprocess.Popen([path] + edgeArgs)
                        print(f"Edge启动成功，使用代理: {self.proxyServer}")
                        return True
            else:
                # Linux/macOS
                edgeExecutables = ["microsoft-edge", "msedge"]
                for executable in edgeExecutables:
                    try:
                        subprocess.Popen([executable] + edgeArgs)
                        print(f"Edge启动成功，使用代理: {self.proxyServer}")
                        return True
                    except FileNotFoundError:
                        continue
            
            return False
            
        except Exception as e:
            print(f"启动Edge时出错: {e}")
            return False
    
    def launchBrowserWithProxy(self, browserType: str = "auto", url: Optional[str] = None) -> bool:
        """启动浏览器"""
        browserType = browserType.lower()
        
        if browserType == "chrome":
            return self.launchChromeWithProxy(url)
        elif browserType == "edge":
            return self.launchEdgeWithProxy(url)
        elif browserType == "auto":
            if self.launchEdgeWithProxy(url):
                return True
            elif self.launchChromeWithProxy(url):
                return True
            else:
                return False
        else:
            return False