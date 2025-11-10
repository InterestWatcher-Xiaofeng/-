# 红枫工具箱 - 数据采集版 V2.0

> 基于 [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) 开发的可视化数据采集工具

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com/InterestWatcher-Xiaofeng/MediaCrawler/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/InterestWatcher-Xiaofeng/MediaCrawler)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## ⚠️ 重要说明

**当前版本（V2.0）仅支持抖音平台的数据采集功能！**

其他平台（小红书、B站、知乎）的功能暂未开放，敬请期待后续版本更新。

---

## ✨ 主要功能

### 🎯 核心功能
- ✅ **抖音评论采集**：批量采集抖音视频评论数据
- ✅ **可视化界面**：简洁易用的GUI操作界面
- ✅ **数据导出**：自动导出为CSV格式，包含9个关键字段

### 🔐 V2.0 新增功能
- ✅ **登录信息持久化**：自动保存登录状态，重启无需重新登录
- ✅ **智能登录验证**：自动检测并提示用户完成登录验证
- ✅ **无干扰采集**：无头浏览器模式，消除黑色窗口干扰
- ✅ **实时进度显示**：可视化进度条，实时显示采集进度

---

## 📦 下载安装

### 方式1：下载发布版（推荐）

1. 前往 [Releases](https://github.com/InterestWatcher-Xiaofeng/MediaCrawler/releases) 页面
2. 下载最新版本的 `红枫工具箱-V2.0.zip`
3. 解压到任意目录
4. 双击运行 `红枫工具箱/启动红枫工具箱.bat`

### 方式2：从源码构建

```bash
# 克隆仓库
git clone https://github.com/InterestWatcher-Xiaofeng/MediaCrawler.git
cd MediaCrawler/MediaCrawler

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 运行GUI
python start_gui.py

# 或打包为exe
python -m PyInstaller MediaCrawler-GUI.spec --clean
```

---

## 🚀 快速开始

### 1️⃣ 启动软件

双击运行：`红枫工具箱/启动红枫工具箱.bat`

### 2️⃣ 登录账号

1. 选择平台：**抖音**
2. 点击"登录账号"按钮
3. 在弹出的浏览器中扫码登录
4. 完成手机号验证（如果需要）

### 3️⃣ 配置采集

- **输入视频链接**：每行一个抖音视频URL
- **设置最大评论数**：建议500-1000
- **选择输出目录**：数据保存位置

### 4️⃣ 开始采集

点击"开始采集"按钮，观察进度条实时更新

---

## 📊 数据格式

采集的数据保存为CSV文件，包含以下字段：

| 字段名 | 说明 |
|--------|------|
| 视频链接 | 视频的完整URL |
| 视频标题 | 视频的标题 |
| 评论内容 | 评论的文字内容 |
| 评论者昵称 | 发表评论的用户昵称 |
| 评论者IP | 评论者的IP属地 |
| 点赞数 | 评论的点赞数量 |
| 评论时间 | 评论发表的时间 |
| 子评论数量 | 该评论的回复数量 |
| 评论ID | 评论的唯一标识符 |

---

## 🛡️ 登录验证处理

如果采集过程中弹出验证提示：

```
检测到可能需要登录验证！

请在浏览器中完成以下操作：
1. 扫码登录（如果需要）
2. 完成手机号验证（如果需要）
3. 完成滑动验证码（如果需要）

验证完成后，采集将自动继续。
```

**处理方法**：
- 在浏览器中完成相应的验证操作
- 等待60秒后，采集会自动继续
- 验证期间"停止采集"按钮无效

---

## 🐛 常见问题

<details>
<summary><b>Q1: 软件无法启动？</b></summary>

**解决方法**：
1. 确认系统是Windows 10/11 (64位)
2. 关闭杀毒软件或添加信任
3. 以管理员身份运行
</details>

<details>
<summary><b>Q2: 登录后仍提示需要验证？</b></summary>

**解决方法**：
1. 完成浏览器中的所有验证步骤
2. 等待60秒后自动继续
3. 如果仍失败，删除`browser_data`目录重新登录
</details>

<details>
<summary><b>Q3: 采集速度很慢？</b></summary>

**解决方法**：
1. 检查网络连接
2. 减少最大评论数
3. 避免同时采集过多视频
</details>

<details>
<summary><b>Q4: 进度条不更新？</b></summary>

**解决方法**：
1. 等待几秒，进度条会延迟更新
2. 检查是否正在进行登录验证
3. 重启软件重试
</details>

---

## 🔄 版本历史

### V2.0 (2025-01-08)
- ✅ 新增：登录信息持久化
- ✅ 新增：智能登录验证提示
- ✅ 新增：无头浏览器模式（消除黑色窗口）
- ✅ 新增：实时进度显示
- ✅ 优化：验证期间禁止停止采集
- ⚠️ 限制：仅支持抖音平台

### V1.2.5 (2025-01-07)
- ✅ 初始版本
- ✅ 支持抖音、小红书、B站、知乎
- ✅ 基础评论采集功能

---

## 📁 项目结构

```
MediaCrawler/
├── MediaCrawler/
│   ├── start_gui.py              # GUI启动入口
│   ├── gui_app.py                # GUI主程序
│   ├── 统一浏览器采集器.py        # 统一浏览器采集器
│   ├── MediaCrawler-GUI.spec     # PyInstaller打包配置
│   ├── config/
│   │   └── base_config.py        # 基础配置
│   ├── media_platform/
│   │   └── douyin/               # 抖音平台爬虫
│   └── 红枫工具箱-发布版/         # 发布版本
│       ├── 红枫工具箱/            # 可执行文件
│       ├── 版本说明.md            # 详细版本说明
│       └── README.txt            # 使用说明
└── README.md                     # 本文件
```

---

## 🙏 致谢

本项目基于以下开源项目开发：

- [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) - 核心爬虫引擎
- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 现代化Tkinter UI库

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## ⚠️ 免责声明

- 本软件仅供学习和研究使用
- 请遵守相关平台的服务条款
- 请勿用于商业用途或非法用途
- 使用本软件产生的任何后果由使用者自行承担

---

## 📞 联系方式

- **GitHub Issues**: [提交问题](https://github.com/InterestWatcher-Xiaofeng/MediaCrawler/issues)
- **Email**: 158789466+InterestWatcher-Xiaofeng@users.noreply.github.com

---

**红枫工具箱 V2.0 - 让数据采集更简单！** 🚀

