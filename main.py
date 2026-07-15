##########################################################################################################
#   Description: 程序启动
#   Authors:     BaiYuan <V:gzq395642104>
##########################################################################################################
import sys, os
from PyQt6.QtWidgets import QApplication
import zipfile

currentDir = os.path.dirname(os.path.abspath(__file__))
if currentDir not in sys.path:
    sys.path.insert(0, currentDir)
    
from craftHub import CraftHub, StartupBanner
from path import PATH_ROOT, PATH_DEPENDENCE, PATH_DEPENDENCEZIP

if __name__ == "__main__":
    if not PATH_DEPENDENCE.exists():
        if PATH_DEPENDENCEZIP.exists():
            with zipfile.ZipFile(str(PATH_DEPENDENCEZIP), "r") as zp:
                zp.extractall(str(PATH_ROOT))
        else:
            raise FileNotFoundError("Dependence not Found!")
    
    app = QApplication(sys.argv)
    StartupBanner.printBanner()
    mainWindow = CraftHub()
    mainWindow.show()
    sys.exit(app.exec())