# CraftHub

> 面向工程技术人员的桌面自动化工具平台，用统一的图形界面管理和运行 CAD、Excel、PDF、文件处理等工程辅助工具。

## 📋 项目简介

工程人员在日常工作中通常会使用多种自动化脚本处理 CAD 绘图、Excel 数据整理、PDF 处理、文件统计等重复性任务。随着脚本数量增加，容易出现启动入口不统一、配置分散、工具难以查找、日志难以管理等问题。

CraftHub 基于 **Python + PyQt6** 开发，为各类工程辅助工具提供统一的桌面入口、页面管理、配置管理和运行环境。用户可以在 CraftHub 的 Home 页面中查看、打开和管理已安装的子脚本，也可以按照统一规范继续扩展新的工具。

CraftHub 本身主要负责工具管理和运行。各子脚本的具体功能、输入要求和操作方法，请以对应的独立使用说明为准。

工具链接: https://github.com/baiyuan1786/CraftHub

## ✨ 主要特性

- ✅ **统一入口**：集中展示、打开和管理多个工程辅助工具。
- ✅ **图形化操作**：将原本分散的命令行脚本整合为 PyQt6 页面。
- ✅ **标签页管理**：支持同时打开多个工具页面并快速切换。
- ✅ **配置持久化**：自动保存常用页面参数，并支持 YAML 配置导入、导出。
- ✅ **日志管理**：统一记录工具运行信息和异常，便于定位问题。
- ✅ **可扩展架构**：通过 `Subscript` 和 `Page` 基类快速接入新工具。
- ✅ **集成运行环境**：发布版可使用内嵌 Python，减少环境配置工作。

## 📦 已集成工具

### 主要子脚本

| 工具 | 功能简介 |
|---|---|
| AutoRoute | 工程路由计算和辅助规划工具。 |
| SplitImage | 工勘照片、视频自动分类工具。 |
| DrawingMaster | 根据工程数据辅助生成 CAD 图纸。 |

### 辅助工具

| 工具 | 功能简介 |
|---|---|
| WebProxy | 网页代理辅助工具。 |
| FileCounter | 文件数量统计工具。 |
| XlsxCounter | Excel 指定字段统计工具。 |
| CadBlockPrinter | CAD 图框或块参照批量打印工具。 |
| PythonCounter | Python 项目代码行数统计工具。 |

部分轻量功能会直接集成在 CraftHub 的工具栏或菜单中。实际可用工具以当前版本 Home 页面显示内容为准。

## 🚀 快速开始

CraftHub 目前支持两种部署方式：

1. 使用内嵌 Python 的发布版；
2. 使用本地 Python 环境从源码运行。

无论采用哪种方式，均需要先获取项目源码。

### 1. 获取源码

请先安装 Git，然后执行：

```bash
git clone https://github.com/baiyuan1786/CraftHub.git
cd CraftHub
```

如果克隆库提示无法访问信息， 例如 fatal: unable to access ，说明需要配置网络代理，你需要配置网络代理以使得能访问git库， 或者直接下载本工具zip

已经配置 GitHub SSH 密钥的用户也可以使用 SSH 地址：

```bash
git clone git@github.com:baiyuan1786/CraftHub.git
```

## 📖 方式一：发布版部署

发布版适合不希望单独配置 Python 环境的用户。

### 下载启动器

通过网盘下载启动器及内嵌 Python 环境：

- 文件：`launcher.zip`
- 链接：<https://pan.baidu.com/s/15kBSIZN5E4qrEspc7KwUmg?pwd=735a>
- 提取码：`735a`

### 安装步骤

1. 下载并解压 `launcher.zip`；
2. 将解压后的 `launcher` 文件夹放到 CraftHub 项目根目录；
3. 根据发布包中实际提供的启动文件运行 CraftHub。

推荐启动方式：

- `Launcher.exe`：直接启动图形界面；
- `LauncherWithWindow.bat`：同时打开命令行窗口，便于查看运行日志和错误信息。

首次使用或排查问题时，推荐使用 `LauncherWithWindow.bat`。

## 📖 方式二：源码部署

源码部署适合开发、调试或二次扩展 CraftHub。

### 环境要求

- Windows 10 或 Windows 11；
- Python 3.13.11，建议使用与项目开发环境一致的版本；
- Git；
- 能够正常安装 `requirements.txt` 中的依赖。

### 安装依赖

在 CraftHub 根目录打开终端，执行：

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 启动程序

```bash
python main.py
```

若电脑中安装了多个 Python 版本，请确认 `python` 命令指向正确环境。

## 🧭 基本使用流程

1. 启动 CraftHub；
2. 在 Home 页面查看已安装的子脚本；
3. 选择目标工具并点击“打开”；
4. 在新标签页中填写参数并运行工具；
5. 通过标签页切换或关闭已打开的工具；
6. 如运行异常，通过日志或命令行窗口查看详细信息。

各子脚本的输入要求、配置方式和操作步骤，请查看对应的独立使用说明。CraftHub 的主使用说明只介绍平台本身，不代替各子脚本说明。

## 🧩 工具扩展

CraftHub 使用统一的子脚本和页面架构：

```text
Subscript
    └── 保存工具名称、作者、版本、说明和页面入口

Page
    └── 提供图形界面、配置保存、参数读取和页面生命周期管理

业务模块
    └── 实现具体的数据读取、处理和文件输出
```

开发新工具时，通常需要：

1. 新建子脚本目录；
2. 创建继承自 `Page` 的工具页面；
3. 创建继承自 `Subscript` 的子脚本定义；
4. 配置 `info` 和 `description` 文件；
5. 将工具放入 `subscripts` 目录，由 CraftHub 自动扫描加载。

详细要求请查看《CraftHub 使用说明》中的“工具开发规范”章节。

## ⚙️ 配置说明

CraftHub 页面配置通常使用 YAML 文件保存。

页面基类能够自动保存以下常用控件的值：

- `QLineEdit`
- `QComboBox`
- `QPlainTextEdit`
- `QCheckBox`

部分页面支持配置导入和导出，可用于：

- 备份常用参数；
- 在不同项目之间切换配置；
- 将配置复制到其他电脑；
- 向其他用户提供统一预设。

## ❓ 常见问题

### 1. 双击后没有任何反应

优先使用 `LauncherWithWindow.bat` 启动，并查看命令行中的错误信息。

### 2. Home 页面没有显示某个工具

请检查：

- 对应子脚本目录是否存在；
- 子脚本信息文件是否完整；
- `enable` 是否设置为 `true`；
- 启动日志中是否存在子脚本初始化失败的信息。

### 3. 源码运行时提示缺少模块

确认已经在正确的 Python 环境中执行：

```bash
python -m pip install -r requirements.txt
```

### 4. 配置没有保存

请检查：

- 页面是否设置配置文件路径；
- 配置目录是否具有写入权限；
- 需要保存的控件是否设置了唯一的 `objectName`；
- YAML 文件是否损坏。

### 5. 某个子脚本无法正常运行

CraftHub 只提供统一运行入口。部分子脚本可能还依赖 AutoCAD、网络服务、第三方 API 或指定格式的输入文件，请查看对应子脚本的使用说明。

## ⚠️ 使用提示

- CraftHub 当前主要面向 Windows 环境。
- 在处理工程文件前，建议备份原始数据。
- 不同子脚本可能具有独立的运行环境和输入要求。
- 自动化工具不能保证所有结果百分之百正确，重要输出应由使用者复核。
- 项目功能会持续调整，实际功能以当前发布版本为准。

## 📞 支持与联系

- 微信：`gzq395642104`

提交问题时，建议同时提供：

- CraftHub 版本；
- 工具名称；
- 操作步骤；
- 错误截图；
- 命令行或日志中的错误信息。
