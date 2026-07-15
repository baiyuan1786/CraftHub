# CraftHub简介

### 📋 项目简介

​	工程人员在日常工作中通常会使用多种自动化脚本处理 CAD 绘图、Excel 数据整理、PDF 处理、文件统计等重复性任务。随着脚本数量增加，容易出现启动入口不统一、配置分散、工具难以查找、日志难以管理等问题。

​	CraftHub 用于为这些工具提供统一的桌面入口和运行环境。本说明书帮助使用者了解 CraftHub 的定位、启动方式、界面结构和通用操作流程，以便正确进入并管理各类子脚本。



### ✨ 主要特性

​	\- ✅ GUI集成：将命令行脚本转换为GUI格式

​	\- ✅ 可扩展性：可扩展添加新的脚本

​	\- ✅ 集成环境：工具无需配置环境，下载即用



### 📦 目前工具

​	\- ✅ AutoRoute: 路由计算工具

​	\- ✅ SplitImage: 照片分类工具，可以将照片分类到各站，各房间，各屏柜下

​	\- ✅ DrawingMaster: CAD绘图工具, 可以输入表格输出CAD图，目前支持IDN集成式绘图网络和DDN定向式绘图网络两种绘图范式

​	部分简化工具也被整合在工具栏中

另外还提供部分小工具

​	\- ✅ WebProxy:  网页代理工具

​	- ✅ FileCounter: 文件计数统计工具

​	\- ✅ XlsxCounter: 表格统计工具

​	\- ✅ CADBlockPrinter: CAD块批量打印工具

​	\- ✅ PythonCounter: python行数统计工具

### 🚀 快速开始

工具可以从源码部署或者内置内嵌python一键部署，无论走哪一步，都需要先克隆源码

你需要先安装git，然后在终端运行下面命令

```
git clone git@github.com:baiyuan1786/CraftHub.git
```

### 📖 一键部署

一键部署需要安装启动器文件和内嵌python， 请通过下面路径下载安装包

通过网盘分享的文件：launcher.zip
链接: https://pan.baidu.com/s/15kBSIZN5E4qrEspc7KwUmg?pwd=735a 提取码: 735a

然后将launcher文件夹解压在工具根目录下，通过laucher.bat即可启动工具

或者也可使用LauncherWithWindow.bat

### 📖 源码部署

首先需要下载python3.13.11，并配置好环境变量

打开终端管理员， CD到工具所在路径下，通过下面命令安装依赖即可

```
pip install -r requirements.txt
```

之后，通过下面命令运行工具

```
python main.py
```



## 📞 支持与联系

- 📧  V: gzq395642104