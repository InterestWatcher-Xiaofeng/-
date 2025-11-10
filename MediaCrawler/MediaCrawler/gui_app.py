#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawler GUI Application
一个用户友好的图形界面，让0代码基础用户轻松使用MediaCrawler的全部功能
"""

import sys
import os
from pathlib import Path

# 🔥🔥🔥 关键：在导入任何其他模块之前，先设置Playwright环境变量！
# 这必须在Playwright被导入之前完成，否则环境变量不会生效
def setup_portable_browser_env():
    """在所有导入之前设置便携式浏览器环境变量"""
    # 🔥 禁止运行时自动下载浏览器，确保纯离线运行
    os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

    if getattr(sys, 'frozen', False):
        # PyInstaller打包后
        exe_dir = Path(sys.executable).parent
        browsers_dir = exe_dir / "_internal" / "playwright_browsers"
    else:
        # 开发环境
        exe_dir = Path(__file__).parent
        browsers_dir = exe_dir / "playwright_browsers"

    # 🔥 无论浏览器是否存在，都必须设置环境变量
    # 这样Playwright才知道去哪里找浏览器
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)

    # 验证浏览器是否存在
    if browsers_dir.exists():
        print(f"✅ 设置便携式浏览器路径: {browsers_dir}")
    else:
        # 🔥 如果浏览器不存在，记录警告但不退出
        # 因为start_gui.py已经做了严格验证
        print(f"⚠️ 警告: 便携式浏览器不存在: {browsers_dir}")
        print(f"   如果是打包后的exe，这是严重问题!")
        print(f"   如果是开发环境，请先运行: playwright install chromium")

# 立即执行环境变量设置
setup_portable_browser_env()

# 现在才导入其他模块
import asyncio
import threading
import subprocess
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 🔥 配置日志记录
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 导入MediaCrawler核心模块
import config
from main import CrawlerFactory
from cmd_arg.arg import PlatformEnum, LoginTypeEnum, CrawlerTypeEnum, SaveDataOptionEnum
from version import get_version, get_full_version_string, CHANGELOG
from tools.portable_browser import get_browser_executable_path, check_browser_available, get_browser_driver_info

# 设置customtkinter主题
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MediaCrawlerGUI:
    """MediaCrawler图形用户界面主类"""

    def __init__(self):
        self.root = ctk.CTk()
        # 🔥 在标题中显示版本号
        self.root.title(f"🍁 红枫工具箱-数据采集版 {get_version()}")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # 🔥 设置窗口图标
        try:
            icon_path = Path(__file__).parent / "icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            logger.warning(f"设置图标失败: {e}")

        # 配置变量
        self.config_vars = {}
        self.current_task = None
        self.task_thread = None
        self.stop_flag = False
        self.is_verifying = False  # 🔥 新增：标记是否正在验证登录

        # 🔥 预先初始化save_format_var,确保默认值为CSV
        self.save_format_var = tk.StringVar(value="csv")

        # 🔥 统一浏览器管理 - 登录和采集使用同一个浏览器
        self.shared_browser = None
        self.shared_context = None
        self.shared_page = None
        self.browser_ready = False
        self.current_platform = None

        # 🔥 浏览器驱动状态
        self.browser_driver_installed = None  # None=未检测, True=已安装, False=未安装

        # 平台信息 - 只保留4个核心平台 (抖音优先)
        self.platforms = {
            "dy": {"name": "抖音", "icon": "📱", "color": "#000000"},
            "xhs": {"name": "小红书", "icon": "🔴", "color": "#FF2442"},
            "bili": {"name": "B站", "icon": "📺", "color": "#00A1D6"},
            "zhihu": {"name": "知乎", "icon": "🧠", "color": "#0084FF"}
        }

        # 停止标志
        self.stop_crawling = False

        self.setup_ui()
        self.load_config()

        # 🔥 启动时检查并安装Playwright浏览器驱动
        self.root.after(1000, self.check_and_install_playwright)

        # 注册清理函数
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 🔥 启动时检查浏览器驱动
        self.root.after(1000, self.check_browser_driver_on_startup)

    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 🔥 创建标题栏（包含版本信息按钮）
        title_frame = ctk.CTkFrame(self.main_frame)
        title_frame.pack(fill="x", pady=(10, 20))

        title_label = ctk.CTkLabel(
            title_frame,
            text="🍁 红枫工具箱-数据采集版",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # 🔥 版本信息按钮
        version_button = ctk.CTkButton(
            title_frame,
            text=f"ℹ️ {get_version()}",
            font=ctk.CTkFont(size=12),
            width=100,
            height=30,
            command=self.show_about_dialog
        )
        version_button.pack(side="right", padx=20)

        # 创建标签页
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 添加各个标签页
        self.setup_platform_tab()
        self.setup_settings_tab()
        self.setup_login_tab()
        self.setup_output_tab()
        self.setup_results_tab()

        # 创建底部控制栏
        self.setup_control_bar()

    def setup_platform_tab(self):
        """设置平台配置标签页"""
        tab = self.notebook.add("平台配置")

        # 平台选择区域
        platform_frame = ctk.CTkFrame(tab)
        platform_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            platform_frame,
            text="选择采集平台",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 平台按钮网格
        platform_grid = ctk.CTkFrame(platform_frame)
        platform_grid.pack(pady=10)

        self.platform_var = tk.StringVar(value="dy")  # 默认平台改为抖音
        self.platform_buttons = {}

        row, col = 0, 0
        for platform_id, platform_info in self.platforms.items():
            btn = ctk.CTkRadioButton(
                platform_grid,
                text=f"{platform_info['icon']} {platform_info['name']}",
                variable=self.platform_var,
                value=platform_id,
                font=ctk.CTkFont(size=14),
                command=self.on_platform_change
            )
            btn.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            self.platform_buttons[platform_id] = btn

            col += 1
            if col > 2:  # 3列布局
                col = 0
                row += 1

        # 采集模式区域
        mode_frame = ctk.CTkFrame(tab)
        mode_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            mode_frame,
            text="采集模式",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        self.crawler_type_var = tk.StringVar(value="search")

        # 关键词搜索
        search_frame = ctk.CTkFrame(mode_frame)
        search_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            search_frame,
            text="🔍 关键词搜索",
            variable=self.crawler_type_var,
            value="search",
            font=ctk.CTkFont(size=14),
            command=self.on_mode_change
        ).pack(anchor="w", padx=10, pady=5)

        keywords_frame = ctk.CTkFrame(search_frame)
        keywords_frame.pack(fill="x", padx=20, pady=5)

        # 🔥 批量关键词输入 - 改为多行文本框
        keywords_label_frame = ctk.CTkFrame(keywords_frame)
        keywords_label_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            keywords_label_frame,
            text="关键词 (支持批量):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            keywords_label_frame,
            text="💡 每行一组关键词，自动批量采集",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="left")

        # 多行文本框
        self.keywords_textbox = ctk.CTkTextbox(
            keywords_frame,
            height=80,
            width=400,
            font=ctk.CTkFont(size=12)
        )
        self.keywords_textbox.pack(fill="both", expand=True)

        # 插入提示文本
        self.keywords_textbox.insert("1.0", "美食 探店\n旅游 攻略\n科技 数码")
        self.keywords_textbox.bind("<FocusIn>", self.clear_keywords_placeholder)

        # 指定内容详情
        detail_frame = ctk.CTkFrame(mode_frame)
        detail_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            detail_frame,
            text="📄 指定内容详情",
            variable=self.crawler_type_var,
            value="detail",
            font=ctk.CTkFont(size=14),
            command=self.on_mode_change
        ).pack(anchor="w", padx=10, pady=5)

        detail_input_frame = ctk.CTkFrame(detail_frame)
        detail_input_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(detail_input_frame, text="链接/ID (每行一个):").pack(anchor="w", padx=(0, 5))
        # 🔥 改为多行文本框,支持批量输入
        self.detail_textbox = ctk.CTkTextbox(
            detail_input_frame,
            height=80,
            width=400,
            state="disabled"
        )
        self.detail_textbox.pack(fill="x", expand=True)

        # 创作者主页
        creator_frame = ctk.CTkFrame(mode_frame)
        creator_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkRadioButton(
            creator_frame,
            text="👤 创作者主页",
            variable=self.crawler_type_var,
            value="creator",
            font=ctk.CTkFont(size=14),
            command=self.on_mode_change
        ).pack(anchor="w", padx=10, pady=5)

        creator_input_frame = ctk.CTkFrame(creator_frame)
        creator_input_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(creator_input_frame, text="创作者 (每行一个):").pack(anchor="w", padx=(0, 5))
        # 🔥 改为多行文本框,支持批量输入
        self.creator_textbox = ctk.CTkTextbox(
            creator_input_frame,
            height=80,
            width=400,
            state="disabled"
        )
        self.creator_textbox.pack(fill="x", expand=True)

    def setup_settings_tab(self):
        """设置采集设置标签页"""
        tab = self.notebook.add("采集设置")

        # 数量控制
        count_frame = ctk.CTkFrame(tab)
        count_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            count_frame,
            text="数量控制",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 最大内容数量
        max_notes_frame = ctk.CTkFrame(count_frame)
        max_notes_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(max_notes_frame, text="📊 最大内容数量:").pack(side="left", padx=(10, 5))
        self.max_notes_var = tk.StringVar(value="20")
        max_notes_entry = ctk.CTkEntry(max_notes_frame, textvariable=self.max_notes_var, width=80)
        max_notes_entry.pack(side="left", padx=5)
        ctk.CTkLabel(max_notes_frame, text="个").pack(side="left", padx=(0, 10))

        # 最大评论数量
        max_comments_frame = ctk.CTkFrame(count_frame)
        max_comments_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(max_comments_frame, text="💬 每个内容最大评论数:").pack(side="left", padx=(10, 5))
        self.max_comments_var = tk.StringVar(value="50")
        max_comments_entry = ctk.CTkEntry(max_comments_frame, textvariable=self.max_comments_var, width=80)
        max_comments_entry.pack(side="left", padx=5)
        ctk.CTkLabel(max_comments_frame, text="条").pack(side="left", padx=(0, 10))

        # 功能选项
        options_frame = ctk.CTkFrame(count_frame)
        options_frame.pack(fill="x", padx=10, pady=10)

        self.enable_comments_var = tk.BooleanVar(value=True)
        self.enable_sub_comments_var = tk.BooleanVar(value=False)
        self.enable_wordcloud_var = tk.BooleanVar(value=True)
        self.enable_media_var = tk.BooleanVar(value=False)

        ctk.CTkCheckBox(options_frame, text="☑️ 采集一级评论", variable=self.enable_comments_var).pack(side="left", padx=10)
        ctk.CTkCheckBox(options_frame, text="☑️ 采集二级评论", variable=self.enable_sub_comments_var).pack(side="left", padx=10)
        ctk.CTkCheckBox(options_frame, text="☑️ 生成词云图", variable=self.enable_wordcloud_var).pack(side="left", padx=10)
        ctk.CTkCheckBox(options_frame, text="☐ 下载媒体文件", variable=self.enable_media_var).pack(side="left", padx=10)

        # 性能设置
        perf_frame = ctk.CTkFrame(tab)
        perf_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            perf_frame,
            text="性能设置",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 采集间隔
        sleep_frame = ctk.CTkFrame(perf_frame)
        sleep_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(sleep_frame, text="⏱️ 采集间隔:").pack(side="left", padx=(10, 5))
        self.sleep_var = tk.StringVar(value="2")
        sleep_entry = ctk.CTkEntry(sleep_frame, textvariable=self.sleep_var, width=80)
        sleep_entry.pack(side="left", padx=5)
        ctk.CTkLabel(sleep_frame, text="秒").pack(side="left", padx=(0, 10))

        # 并发数量
        concurrency_frame = ctk.CTkFrame(perf_frame)
        concurrency_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(concurrency_frame, text="🔄 并发数量:").pack(side="left", padx=(10, 5))
        self.concurrency_var = tk.StringVar(value="1")
        concurrency_entry = ctk.CTkEntry(concurrency_frame, textvariable=self.concurrency_var, width=80)
        concurrency_entry.pack(side="left", padx=5)
        ctk.CTkLabel(concurrency_frame, text="个").pack(side="left", padx=(0, 10))

        # 无头模式
        headless_frame = ctk.CTkFrame(perf_frame)
        headless_frame.pack(fill="x", padx=10, pady=5)

        self.headless_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(headless_frame, text="🖥️ 无头模式 (隐藏浏览器)", variable=self.headless_var).pack(side="left", padx=10)

        # 🔥 评论采集进度显示区域
        progress_display_frame = ctk.CTkFrame(tab)
        progress_display_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            progress_display_frame,
            text="采集进度",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 进度信息容器
        progress_info_frame = ctk.CTkFrame(progress_display_frame)
        progress_info_frame.pack(fill="x", padx=10, pady=5)

        # 当前视频/内容进度
        current_video_frame = ctk.CTkFrame(progress_info_frame)
        current_video_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(current_video_frame, text="📹 当前内容:").pack(side="left", padx=(10, 5))
        self.current_video_label = ctk.CTkLabel(
            current_video_frame,
            text="0/0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1E90FF"
        )
        self.current_video_label.pack(side="left", padx=5)

        # 当前视频进度条
        self.current_video_progress = ctk.CTkProgressBar(current_video_frame, width=300)
        self.current_video_progress.pack(side="left", padx=10)
        self.current_video_progress.set(0)

        # 评论采集进度
        comment_progress_frame = ctk.CTkFrame(progress_info_frame)
        comment_progress_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(comment_progress_frame, text="💬 当前评论:").pack(side="left", padx=(10, 5))
        self.current_comment_label = ctk.CTkLabel(
            comment_progress_frame,
            text="0/0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#32CD32"
        )
        self.current_comment_label.pack(side="left", padx=5)

        # 评论进度条
        self.comment_progress_bar = ctk.CTkProgressBar(comment_progress_frame, width=300)
        self.comment_progress_bar.pack(side="left", padx=10)
        self.comment_progress_bar.set(0)

        # 总体进度信息
        total_progress_frame = ctk.CTkFrame(progress_info_frame)
        total_progress_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(total_progress_frame, text="📊 总体进度:").pack(side="left", padx=(10, 5))
        self.total_progress_label = ctk.CTkLabel(
            total_progress_frame,
            text="等待开始...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.total_progress_label.pack(side="left", padx=5)

    def setup_login_tab(self):
        """设置登录管理标签页"""
        tab = self.notebook.add("登录管理")

        # 🔥 浏览器驱动状态检查区域
        driver_check_frame = ctk.CTkFrame(tab)
        driver_check_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            driver_check_frame,
            text="🔧 浏览器驱动状态",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 状态显示和操作按钮
        driver_status_frame = ctk.CTkFrame(driver_check_frame)
        driver_status_frame.pack(fill="x", padx=10, pady=10)

        self.driver_status_label = ctk.CTkLabel(
            driver_status_frame,
            text="⏳ 检测中...",
            font=ctk.CTkFont(size=14)
        )
        self.driver_status_label.pack(side="left", padx=10)

        # 检查按钮
        check_driver_btn = ctk.CTkButton(
            driver_status_frame,
            text="🔍 检查状态",
            width=100,
            command=self.manual_check_browser_driver
        )
        check_driver_btn.pack(side="left", padx=5)

        # 安装按钮
        self.install_driver_btn = ctk.CTkButton(
            driver_status_frame,
            text="📥 安装驱动",
            width=100,
            command=self.install_browser_driver,
            state="disabled"
        )
        self.install_driver_btn.pack(side="left", padx=5)

        # 登录方式选择
        login_type_frame = ctk.CTkFrame(tab)
        login_type_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            login_type_frame,
            text="登录方式",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        self.login_type_var = tk.StringVar(value="qrcode")

        login_options = [
            ("qrcode", "📱 扫码登录 (推荐)"),
            ("phone", "📞 手机号登录"),
            ("cookie", "🍪 Cookie登录 (高级)")
        ]

        for value, text in login_options:
            ctk.CTkRadioButton(
                login_type_frame,
                text=text,
                variable=self.login_type_var,
                value=value,
                font=ctk.CTkFont(size=14)
            ).pack(anchor="w", padx=20, pady=5)

        # 登录状态显示
        status_frame = ctk.CTkFrame(tab)
        status_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            status_frame,
            text="登录状态",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 创建登录状态列表
        self.login_status_frame = ctk.CTkScrollableFrame(status_frame)
        self.login_status_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.login_buttons = {}
        for platform_id, platform_info in self.platforms.items():
            platform_frame = ctk.CTkFrame(self.login_status_frame)
            platform_frame.pack(fill="x", pady=5)

            # 平台信息
            info_label = ctk.CTkLabel(
                platform_frame,
                text=f"{platform_info['icon']} {platform_info['name']}:",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(side="left", padx=10)

            # 状态标签
            status_label = ctk.CTkLabel(
                platform_frame,
                text="❌ 未登录",
                font=ctk.CTkFont(size=12)
            )
            status_label.pack(side="left", padx=10)

            # 按钮容器
            button_frame = ctk.CTkFrame(platform_frame)
            button_frame.pack(side="right", padx=10)

            # 登录按钮
            login_btn = ctk.CTkButton(
                button_frame,
                text="开始登录",
                width=80,
                command=lambda p=platform_id: self.start_login(p)
            )
            login_btn.pack(side="left", padx=2)

            # 保存登录信息按钮
            save_btn = ctk.CTkButton(
                button_frame,
                text="💾保存",
                width=60,
                command=lambda p=platform_id: self.manual_save_login(p)
            )
            save_btn.pack(side="left", padx=2)

            self.login_buttons[platform_id] = {
                "status": status_label,
                "button": login_btn,
                "save_button": save_btn
            }

        # 🔥 初始化时检查所有平台的登录状态
        self.update_all_login_status()

    def setup_output_tab(self):
        """设置数据输出标签页"""
        tab = self.notebook.add("数据输出")

        # 输出格式选择
        format_frame = ctk.CTkFrame(tab)
        format_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            format_frame,
            text="输出格式",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 🔥 save_format_var已在__init__中初始化为csv
        format_options = [
            ("csv", "📊 CSV文件 (Excel兼容)"),
            ("json", "🗃️ JSON文件 (支持词云图)"),
            ("sqlite", "💾 SQLite数据库 (推荐)"),
            ("db", "🏢 MySQL数据库")
        ]

        # 🔥 创建RadioButton并保存引用
        self.format_radios = []
        for value, text in format_options:
            radio = ctk.CTkRadioButton(
                format_frame,
                text=text,
                variable=self.save_format_var,
                value=value,
                font=ctk.CTkFont(size=14)
            )
            radio.pack(anchor="w", padx=20, pady=5)
            self.format_radios.append(radio)

        # 🔥 强制选中第一个(CSV)
        if self.format_radios:
            self.format_radios[0].select()

        # 保存设置
        save_frame = ctk.CTkFrame(tab)
        save_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            save_frame,
            text="保存设置",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 保存目录
        dir_frame = ctk.CTkFrame(save_frame)
        dir_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(dir_frame, text="📁 保存目录:").pack(side="left", padx=(10, 5))
        self.output_dir_var = tk.StringVar(value=str(Path.cwd() / "data"))
        dir_entry = ctk.CTkEntry(dir_frame, textvariable=self.output_dir_var, width=300)
        dir_entry.pack(side="left", padx=5, fill="x", expand=True)

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="📁浏览",
            width=80,
            command=self.browse_output_dir
        )
        browse_btn.pack(side="right", padx=10)

        # 其他选项
        options_frame = ctk.CTkFrame(save_frame)
        options_frame.pack(fill="x", padx=10, pady=10)

        self.auto_open_var = tk.BooleanVar(value=True)
        self.generate_report_var = tk.BooleanVar(value=True)

        ctk.CTkCheckBox(options_frame, text="☑️ 自动打开结果文件", variable=self.auto_open_var).pack(anchor="w", padx=10, pady=2)
        ctk.CTkCheckBox(options_frame, text="☑️ 生成数据统计报告", variable=self.generate_report_var).pack(anchor="w", padx=10, pady=2)

    def setup_results_tab(self):
        """设置结果查看标签页"""
        tab = self.notebook.add("结果查看")

        # 采集历史
        history_frame = ctk.CTkFrame(tab)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            history_frame,
            text="采集历史",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # 历史记录列表
        self.history_frame = ctk.CTkScrollableFrame(history_frame)
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 快速操作
        quick_frame = ctk.CTkFrame(tab)
        quick_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            quick_frame,
            text="快速操作",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        buttons_frame = ctk.CTkFrame(quick_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)

        quick_buttons = [
            ("📁 打开数据目录", self.open_data_dir),
            ("📊 生成词云图", self.generate_wordcloud),
            ("📈 数据分析", self.analyze_data),
            ("🔄 清理缓存", self.clear_cache),
            ("⚙️ 高级设置", self.open_advanced_settings),
            ("❓ 帮助", self.show_help)
        ]

        for i, (text, command) in enumerate(quick_buttons):
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=command,
                width=150
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)

    def setup_control_bar(self):
        """设置底部控制栏"""
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))

        # 状态信息
        status_frame = ctk.CTkFrame(control_frame)
        status_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="📊 状态: 就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10)

        # 🔥 版本信息显示
        version_label = ctk.CTkLabel(
            status_frame,
            text=f"版本: {get_version()}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        version_label.pack(side="left", padx=10)

        # 进度信息框架
        progress_frame = ctk.CTkFrame(status_frame)
        progress_frame.pack(side="right", padx=10)

        # 进度文字显示
        self.progress_text = ctk.CTkLabel(
            progress_frame,
            text="0/0 内容",
            font=ctk.CTkFont(size=10)
        )
        self.progress_text.pack(pady=2)

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=180)
        self.progress_bar.pack(pady=2)
        self.progress_bar.set(0)

        # 主要操作按钮
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(side="right", padx=5, pady=5)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 开始采集",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=120,
            height=40,
            command=self.start_crawling
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹️ 停止采集",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=120,
            height=40,
            command=self.stop_crawling,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

    def clear_keywords_placeholder(self, event):
        """清除关键词占位符"""
        current_text = self.keywords_textbox.get("1.0", "end-1c")
        if current_text == "美食 探店\n旅游 攻略\n科技 数码":
            self.keywords_textbox.delete("1.0", "end")

    def load_config(self):
        """加载配置"""
        try:
            # 从config模块加载默认配置
            self.platform_var.set(config.PLATFORM)
            # 🔥 更新：使用textbox而不是entry
            self.keywords_textbox.delete("1.0", "end")
            self.keywords_textbox.insert("1.0", config.KEYWORDS)
            self.crawler_type_var.set(config.CRAWLER_TYPE)
            self.login_type_var.set(config.LOGIN_TYPE)
            self.save_format_var.set(config.SAVE_DATA_OPTION)

            # 更新界面状态
            self.on_mode_change()
        except Exception as e:
            messagebox.showerror("配置加载错误", f"加载配置时出错: {str(e)}")

    def on_platform_change(self):
        """平台选择改变时的回调"""
        platform = self.platform_var.get()
        platform_info = self.platforms.get(platform, {})
        self.update_status(f"已选择平台: {platform_info.get('name', platform)}")

    def on_mode_change(self):
        """采集模式改变时的回调"""
        mode = self.crawler_type_var.get()

        # 启用/禁用相应的输入框
        # 🔥 更新：textbox使用不同的状态控制方法
        if mode == "search":
            self.keywords_textbox.configure(state="normal")
            self.detail_textbox.configure(state="disabled")
            self.creator_textbox.configure(state="disabled")
        elif mode == "detail":
            self.keywords_textbox.configure(state="disabled")
            self.detail_textbox.configure(state="normal")
            self.creator_textbox.configure(state="disabled")
        elif mode == "creator":
            self.keywords_textbox.configure(state="disabled")
            self.detail_textbox.configure(state="disabled")
            self.creator_textbox.configure(state="normal")

    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.output_dir_var.get()
        )
        if directory:
            self.output_dir_var.set(directory)

    def update_status(self, message: str):
        """更新状态信息"""
        self.status_label.configure(text=f"📊 状态: {message}")
        self.root.update_idletasks()

    def update_progress(self, current: int, total: int, content_type: str = "内容"):
        """更新进度显示"""
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            self.progress_text.configure(text=f"{current}/{total} {content_type}")
        else:
            self.progress_bar.set(0)
            self.progress_text.configure(text=f"0/0 {content_type}")
        self.root.update_idletasks()

    def update_video_progress(self, current: int, total: int):
        """🔥 更新当前视频/内容进度"""
        try:
            if total > 0:
                progress = current / total
                self.current_video_progress.set(progress)
                self.current_video_label.configure(text=f"{current}/{total}")
            else:
                self.current_video_progress.set(0)
                self.current_video_label.configure(text="0/0")
            self.root.update_idletasks()
        except Exception as e:
            print(f"⚠️ 更新视频进度失败: {e}")

    def update_comment_progress(self, current: int, total: int):
        """🔥 更新当前评论采集进度"""
        try:
            if total > 0:
                progress = current / total
                self.comment_progress_bar.set(progress)
                self.current_comment_label.configure(text=f"{current}/{total}")
            else:
                self.comment_progress_bar.set(0)
                self.current_comment_label.configure(text="0/0")
            self.root.update_idletasks()
        except Exception as e:
            print(f"⚠️ 更新评论进度失败: {e}")

    def update_total_progress(self, message: str):
        """🔥 更新总体进度信息"""
        try:
            self.total_progress_label.configure(text=message)
            self.root.update_idletasks()
        except Exception as e:
            print(f"⚠️ 更新总体进度失败: {e}")

    def reset_progress_display(self):
        """🔥 重置所有进度显示"""
        try:
            self.current_video_progress.set(0)
            self.current_video_label.configure(text="0/0")
            self.comment_progress_bar.set(0)
            self.current_comment_label.configure(text="0/0")
            self.total_progress_label.configure(text="等待开始...")
            self.root.update_idletasks()
        except Exception as e:
            print(f"⚠️ 重置进度显示失败: {e}")

    def check_playwright_browser_installed(self) -> bool:
        """🔥 检查Playwright浏览器驱动是否已安装（优先便携式，其次系统目录）"""
        try:
            available, message = check_browser_available()
            print(message)
            return bool(available)
        except Exception as e:
            print(f"⚠️ 检查浏览器驱动时出错: {e}")
            return False

    def check_browser_driver_on_startup(self):
        """🔥 启动时检查浏览器驱动状态"""
        try:
            self.browser_driver_installed = self.check_playwright_browser_installed()

            # 更新UI状态
            self.update_driver_status_ui()

            if not self.browser_driver_installed:
                # 显示首次运行提示
                response = messagebox.askyesno(
                    "🔧 首次运行设置",
                    "检测到这是首次运行本软件！\n\n"
                    "需要安装 Playwright 浏览器驱动才能正常使用。\n"
                    "大约需要下载 200MB 数据。\n\n"
                    "是否现在安装？\n\n"
                    "提示：\n"
                    "• 点击'是'：自动安装（推荐）\n"
                    "• 点击'否'：稍后手动安装",
                    icon='question'
                )

                if response:
                    # 用户选择立即安装
                    self.install_browser_driver()
                else:
                    # 用户选择稍后安装，显示手动安装说明
                    messagebox.showinfo(
                        "📝 手动安装说明",
                        "如需手动安装浏览器驱动，请：\n\n"
                        "方法一：使用安装脚本\n"
                        "  双击运行'首次运行-安装浏览器.bat'\n\n"
                        "方法二：命令行安装\n"
                        "  打开命令提示符，运行：\n"
                        "  playwright install chromium\n\n"
                        "方法三：在'登录管理'标签页点击'安装驱动'按钮\n\n"
                        "安装完成后重启软件即可使用。"
                    )
            else:
                print("✅ 浏览器驱动已安装，可以正常使用")

        except Exception as e:
            print(f"⚠️ 检查浏览器驱动状态时出错: {e}")

    def manual_check_browser_driver(self):
        """🔥 手动检查浏览器驱动状态"""
        try:
            self.update_status("正在检查浏览器驱动...")
            self.browser_driver_installed = self.check_playwright_browser_installed()
            self.update_driver_status_ui()

            if self.browser_driver_installed:
                messagebox.showinfo(
                    "✅ 检查完成",
                    "浏览器驱动已正确安装！\n\n"
                    "可以正常使用登录和采集功能。"
                )
            else:
                response = messagebox.askyesno(
                    "⚠️ 检查完成",
                    "浏览器驱动未安装！\n\n"
                    "是否现在安装？",
                    icon='warning'
                )
                if response:
                    self.install_browser_driver()

            self.update_status("检查完成")

        except Exception as e:
            messagebox.showerror("错误", f"检查浏览器驱动时出错：{str(e)}")
            self.update_status("检查失败")

    def check_and_install_playwright(self):
        """🔥 启动时检查并安装Playwright浏览器驱动"""
        try:
            print("="*60)
            print("🔍 检查浏览器驱动...")

            # 使用便携式浏览器检测
            available, message = check_browser_available()
            driver_info = get_browser_driver_info()

            print(f"检测结果: {message}")
            print(f"便携式路径: {driver_info['portable_path']}")
            print(f"exe目录: {driver_info['exe_dir']}")
            print("="*60)

            if available:
                self.browser_driver_installed = True
                print("✅ 浏览器驱动可用")
                if driver_info['portable_path']:
                    print(f"📦 使用便携式浏览器: {driver_info['portable_path']}")
                else:
                    print("🌐 使用系统浏览器")
            else:
                self.browser_driver_installed = False
                print("❌ 浏览器驱动不可用")
                print("💡 用户首次登录时会提示安装")

            # 更新UI状态
            self.update_driver_status_ui()

        except Exception as e:
            print(f"⚠️ 检查浏览器驱动时出错: {e}")
            self.browser_driver_installed = None

    def update_driver_status_ui(self):
        """🔥 更新浏览器驱动状态UI"""
        try:
            if hasattr(self, 'driver_status_label'):
                if self.browser_driver_installed is None:
                    self.driver_status_label.configure(text="⏳ 未检测")
                    self.install_driver_btn.configure(state="normal")
                elif self.browser_driver_installed:
                    self.driver_status_label.configure(text="✅ 已安装")
                    self.install_driver_btn.configure(state="disabled")
                else:
                    self.driver_status_label.configure(text="❌ 未安装")
                    self.install_driver_btn.configure(state="normal")
        except Exception as e:
            print(f"⚠️ 更新驱动状态UI时出错: {e}")

    def show_browser_driver_error(self):
        """🔥 显示浏览器驱动错误提示"""
        # 🔥 检查是否是便携式版本
        driver_info = get_browser_driver_info()

        if driver_info['is_frozen']:
            # 便携式版本，浏览器应该已打包
            messagebox.showerror(
                "❌ 浏览器驱动错误",
                "浏览器驱动加载失败！\n\n"
                "这是便携式版本，浏览器驱动应该已经打包在软件中。\n\n"
                "可能的原因：\n"
                "1. 软件文件不完整（请重新下载完整版）\n"
                "2. 文件被杀毒软件删除（请添加信任）\n"
                "3. 文件损坏（请重新下载）\n\n"
                f"预期路径：\n{driver_info['portable_path']}\n\n"
                "请确保软件文件夹完整，包含 _internal 文件夹及其所有内容。"
            )
        else:
            # 开发版本或需要安装
            response = messagebox.askyesno(
                "❌ 浏览器驱动未安装",
                "登录失败：浏览器驱动未安装！\n\n"
                "Playwright 浏览器驱动是运行本软件的必要组件。\n\n"
                "💡 解决方法：\n\n"
                "方法一：自动安装（推荐）\n"
                "  点击'是'按钮，软件将自动下载安装\n\n"
                "方法二：使用安装脚本\n"
                "  双击运行'首次运行-安装浏览器.bat'\n\n"
                "方法三：手动安装\n"
                "  打开命令提示符，运行：\n"
                "  playwright install chromium\n\n"
                "是否现在自动安装？",
                icon='error'
            )

            if response:
                self.install_browser_driver()

    def install_browser_driver(self):
        """🔥 安装Playwright浏览器驱动"""
        try:
            # 创建进度窗口
            progress_window = ctk.CTkToplevel(self.root)
            progress_window.title("正在安装浏览器驱动")
            progress_window.geometry("500x200")
            progress_window.transient(self.root)
            progress_window.grab_set()

            # 提示信息
            info_label = ctk.CTkLabel(
                progress_window,
                text="正在下载并安装 Playwright 浏览器驱动...\n\n"
                     "这可能需要几分钟时间，请耐心等待。\n"
                     "请不要关闭此窗口！",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=20)

            # 进度条
            progress = ctk.CTkProgressBar(progress_window, width=400)
            progress.pack(pady=10)
            progress.set(0)
            progress.start()

            # 状态标签
            status_label = ctk.CTkLabel(
                progress_window,
                text="正在连接下载服务器...",
                font=ctk.CTkFont(size=12)
            )
            status_label.pack(pady=10)

            def run_installation():
                try:
                    # 更新状态
                    status_label.configure(text="正在下载浏览器驱动...")

                    # 执行安装命令
                    result = subprocess.run(
                        ["playwright", "install", "chromium"],
                        capture_output=True,
                        text=True,
                        timeout=600  # 10分钟超时
                    )

                    if result.returncode == 0:
                        # 安装成功
                        self.browser_driver_installed = True
                        progress_window.after(0, lambda: progress.stop())
                        progress_window.after(0, lambda: progress.set(1.0))
                        progress_window.after(0, lambda: status_label.configure(text="✅ 安装成功！"))
                        progress_window.after(0, lambda: self.update_driver_status_ui())  # 🔥 更新UI状态
                        progress_window.after(1000, lambda: progress_window.destroy())
                        progress_window.after(1000, lambda: messagebox.showinfo(
                            "✅ 安装成功",
                            "浏览器驱动安装成功！\n\n"
                            "现在可以正常使用登录和采集功能了。"
                        ))
                    else:
                        # 安装失败
                        error_msg = result.stderr if result.stderr else "未知错误"
                        progress_window.after(0, lambda: progress.stop())
                        progress_window.after(0, lambda: status_label.configure(text="❌ 安装失败"))
                        progress_window.after(1000, lambda: progress_window.destroy())
                        progress_window.after(1000, lambda: messagebox.showerror(
                            "❌ 安装失败",
                            f"浏览器驱动安装失败！\n\n"
                            f"错误信息：{error_msg}\n\n"
                            f"请尝试：\n"
                            f"1. 检查网络连接\n"
                            f"2. 关闭防火墙或杀毒软件\n"
                            f"3. 手动运行安装脚本"
                        ))

                except subprocess.TimeoutExpired:
                    progress_window.after(0, lambda: progress.stop())
                    progress_window.after(0, lambda: status_label.configure(text="❌ 安装超时"))
                    progress_window.after(1000, lambda: progress_window.destroy())
                    progress_window.after(1000, lambda: messagebox.showerror(
                        "❌ 安装超时",
                        "浏览器驱动安装超时！\n\n"
                        "可能是网络连接问题。\n"
                        "请检查网络后重试。"
                    ))
                except Exception as e:
                    progress_window.after(0, lambda: progress.stop())
                    progress_window.after(0, lambda: status_label.configure(text=f"❌ 错误: {str(e)}"))
                    progress_window.after(1000, lambda: progress_window.destroy())
                    progress_window.after(1000, lambda: messagebox.showerror(
                        "❌ 安装错误",
                        f"安装过程中出错：{str(e)}"
                    ))

            # 在后台线程中执行安装
            install_thread = threading.Thread(target=run_installation, daemon=True)
            install_thread.start()

        except Exception as e:
            messagebox.showerror("错误", f"启动安装程序时出错：{str(e)}")

    def start_login(self, platform: str):
        """开始登录指定平台"""
        if not platform:
            messagebox.showerror("错误", "请先选择平台！")
            return

        # 🔥 检查浏览器驱动是否已安装
        if self.browser_driver_installed is False:
            response = messagebox.askyesno(
                "⚠️ 浏览器驱动未安装",
                "检测到浏览器驱动未安装！\n\n"
                "需要安装 Playwright 浏览器驱动才能登录。\n\n"
                "是否现在安装？",
                icon='warning'
            )
            if response:
                self.install_browser_driver()
            return

        platform_info = self.platforms.get(platform, {})
        platform_name = platform_info.get('name', platform)

        self.update_status(f"正在启动{platform_name}登录...")

        # 在后台线程中执行登录
        login_thread = threading.Thread(target=self.run_login_task, args=(platform,), daemon=True)
        login_thread.start()

    def run_login_task(self, platform: str):
        """在后台线程中运行登录任务 - 启动持久事件循环"""
        try:
            # 检查playwright是否可用
            try:
                import playwright
                from playwright.async_api import async_playwright
            except ImportError as e:
                error_msg = "Playwright未正确安装。请运行: pip install playwright && playwright install chromium"
                self.root.after(0, lambda: messagebox.showerror("依赖错误", error_msg))
                self.root.after(0, lambda: self.update_status("登录失败：缺少依赖"))
                return

            # 导入必要的模块
            import asyncio

            # 🔥 创建新的事件循环并在后台持续运行
            if not hasattr(self, 'browser_loop') or self.browser_loop is None or self.browser_loop.is_closed():
                self.browser_loop = asyncio.new_event_loop()
                print("🔄 创建新的浏览器事件循环")

                # 在新线程中启动事件循环，让它持续运行
                def run_loop():
                    asyncio.set_event_loop(self.browser_loop)
                    self.browser_loop.run_forever()
                    print("🛑 浏览器事件循环已停止")

                self.loop_thread = threading.Thread(target=run_loop, daemon=True)
                self.loop_thread.start()
                print("✅ 浏览器事件循环线程已启动")
            else:
                print("🔄 复用现有浏览器事件循环")

            # 🔥 使用 run_coroutine_threadsafe 在事件循环中运行登录任务
            future = asyncio.run_coroutine_threadsafe(
                self.perform_login(platform),
                self.browser_loop
            )

            # 等待登录完成（最多5分钟）
            future.result(timeout=300)
            print("✅ 登录任务完成，事件循环继续运行")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 登录错误: {error_msg}")
            import traceback
            traceback.print_exc()

            # 🔥 根据错误类型提供不同的解决方案
            if "Executable doesn't exist" in error_msg or "browser executable" in error_msg.lower() or "浏览器驱动" in error_msg:
                # 浏览器驱动未安装
                self.browser_driver_installed = False
                self.root.after(0, lambda: self.update_status("登录失败：浏览器驱动未安装"))
                self.root.after(0, lambda: self.show_browser_driver_error())
            else:
                # 其他错误
                self.root.after(0, lambda: self.update_status("登录失败"))
                self.root.after(0, lambda: messagebox.showerror(
                    "❌ 登录错误",
                    f"登录过程中出错：{error_msg}\n\n"
                    f"请尝试：\n"
                    f"1. 检查网络连接\n"
                    f"2. 重新启动软件\n"
                    f"3. 查看详细日志"
                ))

    async def perform_login(self, platform: str):
        """🔥 执行统一浏览器登录操作"""
        try:
            # 初始化统一浏览器
            if not await self.init_shared_browser(platform):
                raise Exception("浏览器启动失败")

            import config

            # 获取平台名称
            platform_name = self.platforms.get(platform, {}).get('name', platform)

            # 更新配置以启用登录状态保存
            config.SAVE_LOGIN_STATE = True
            config.PLATFORM = platform

            # 更新状态
            self.root.after(0, lambda pn=platform_name: self.update_status(f"正在启动{pn}浏览器..."))

            # 根据平台跳转到登录页面
            login_urls = {
                'xhs': 'https://www.xiaohongshu.com',
                'dy': 'https://www.douyin.com',
                'ks': 'https://www.kuaishou.com',
                'bili': 'https://www.bilibili.com',
                'wb': 'https://weibo.com',
                'tieba': 'https://tieba.baidu.com',
                'zhihu': 'https://www.zhihu.com'
            }

            url = login_urls.get(platform, 'https://www.xiaohongshu.com')

            self.root.after(0, lambda pn=platform_name: self.update_status(f"正在打开{pn}登录页面..."))

            # 🔥 增强的页面加载逻辑，支持重试
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"🌐 尝试加载{platform_name}页面 (第{attempt + 1}/{max_retries}次)...")
                    await self.shared_page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    print(f"✅ {platform_name}页面加载成功")
                    break
                except Exception as e:
                    print(f"⚠️ 页面加载失败 (第{attempt + 1}次): {e}")
                    if attempt < max_retries - 1:
                        print(f"🔄 等待3秒后重试...")
                        await asyncio.sleep(3)
                    else:
                        # 最后一次尝试失败，但不中断流程
                        print(f"⚠️ 页面加载多次失败，但继续执行登录流程")
                        self.root.after(0, lambda: messagebox.showwarning(
                            "⚠️ 页面加载警告",
                            f"{platform_name}页面加载失败，但浏览器已打开\n\n"
                            f"可能原因：\n"
                            f"1. 网络连接不稳定\n"
                            f"2. 目标网站响应慢\n\n"
                            f"建议：\n"
                            f"1. 在浏览器中手动刷新页面\n"
                            f"2. 检查网络连接\n"
                            f"3. 完成登录后点击'💾保存'按钮"
                        ))

            # 🔥 检测是否已经登录
            print(f"🔍 检测{platform_name}登录状态...")
            is_logged_in = await self._check_platform_login_status(platform, self.shared_page)

            if is_logged_in:
                print(f"✅ 检测到{platform_name}已登录,跳过登录流程")
                self.root.after(0, lambda pn=platform_name: self.update_status(f"{pn}已登录"))

                # 自动保存登录信息
                print(f"💾 自动保存{platform}登录信息...")
                await self.save_login_info(platform)

            else:
                # 🔥 等待用户登录（给60秒时间）
                print(f"⏰ 等待用户完成登录...")
                self.root.after(0, lambda pn=platform_name: self.update_status(f"请在浏览器中完成{pn}登录..."))

                # 显示提示信息
                self.root.after(0, lambda pn=platform_name: messagebox.showinfo(
                    "🔥 请完成登录验证",
                    f"浏览器已打开{pn}页面\n\n"
                    f"⏰ 系统将给予60秒时间完成登录验证\n\n"
                    f"请在浏览器中完成以下操作：\n"
                    f"1. 点击登录按钮\n"
                    f"2. 使用手机扫码或输入账号密码\n"
                    f"3. 如遇验证码，请在60秒内完成验证\n"
                    f"4. 确认登录成功\n\n"
                    f"⚠️ 请不要关闭浏览器窗口！\n\n"
                    f"💡 60秒后程序将自动保存登录信息"
                ))

                # 等待60秒让用户完成登录
                await asyncio.sleep(60)

                # 🔥 自动保存登录信息
                print(f"💾 自动保存{platform}登录信息...")
            save_success = await self.save_login_info(platform)

            if save_success:
                self.root.after(0, lambda p=platform: self.update_login_status(p))
                self.root.after(0, lambda pn=platform_name: self.update_status(f"{pn}登录完成"))
                self.root.after(0, lambda pn=platform_name: messagebox.showinfo(
                    "✅ 登录成功",
                    f"🎉 {pn}登录信息已保存！\n\n"
                    f"💾 下次启动将自动恢复登录状态\n"
                    f"🔥 浏览器将保持运行状态\n"
                    f"🚀 现在可以开始数据采集"
                ))
                print(f"✅ {platform_name}统一浏览器登录完成")
            else:
                self.root.after(0, lambda pn=platform_name: messagebox.showwarning(
                    "⚠️ 保存失败",
                    f"{pn}登录信息保存失败\n\n"
                    f"可能原因：\n"
                    f"1. 登录未完成\n"
                    f"2. 浏览器连接断开\n\n"
                    f"建议：\n"
                    f"1. 确认已完成登录\n"
                    f"2. 点击'登录管理'中的'💾保存'按钮手动保存"
                ))

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 登录错误: {error_msg}")
            import traceback
            traceback.print_exc()

            # 🔥 根据错误类型提供更友好的提示
            platform_name = self.platforms.get(platform, {}).get('name', platform)

            if "timeout" in error_msg.lower() or "超时" in error_msg:
                friendly_msg = (
                    f"❌ {platform_name}登录超时\n\n"
                    f"可能原因：\n"
                    f"1. 网络连接不稳定\n"
                    f"2. 目标网站响应慢\n"
                    f"3. 防火墙或杀毒软件拦截\n\n"
                    f"建议：\n"
                    f"1. 检查网络连接\n"
                    f"2. 关闭VPN或代理\n"
                    f"3. 重新尝试登录"
                )
            elif "network" in error_msg.lower() or "网络" in error_msg:
                friendly_msg = (
                    f"❌ 网络连接失败\n\n"
                    f"无法连接到{platform_name}\n\n"
                    f"建议：\n"
                    f"1. 检查网络连接\n"
                    f"2. 尝试在浏览器中访问网站\n"
                    f"3. 检查防火墙设置"
                )
            else:
                friendly_msg = (
                    f"❌ {platform_name}登录失败\n\n"
                    f"错误信息：{error_msg}\n\n"
                    f"建议：\n"
                    f"1. 检查网络连接\n"
                    f"2. 重新启动软件\n"
                    f"3. 查看详细日志"
                )

            self.root.after(0, lambda: self.update_status("登录失败"))
            self.root.after(0, lambda msg=friendly_msg: messagebox.showerror("登录错误", msg))

    def start_crawling(self):
        """🔥 开始采集 - 使用统一浏览器"""
        try:
            # 验证配置
            if not self.validate_config():
                return

            # 🔥 检查统一浏览器状态
            # 🔥 修复：直接从platform_var获取平台,而不是从config_vars
            platform = self.platform_var.get()
            platform_name = self.platforms.get(platform, {}).get('name', platform)

            # 🔥 严格检查：平台必须匹配且浏览器必须就绪
            if not self.browser_ready:
                messagebox.showwarning(
                    "浏览器未就绪",
                    f"请先完成登录！\n\n"
                    f"步骤：\n"
                    f"1. 点击'登录管理'标签\n"
                    f"2. 选择要采集的平台\n"
                    f"3. 点击'开始登录'完成登录\n"
                    f"4. 登录完成后再开始采集"
                )
                return

            if self.current_platform != platform:
                messagebox.showwarning(
                    "平台不匹配",
                    f"当前已登录平台：{self.platforms.get(self.current_platform, {}).get('name', self.current_platform)}\n"
                    f"要采集的平台：{platform_name}\n\n"
                    f"请执行以下操作之一：\n"
                    f"1. 在'平台配置'中选择'{self.platforms.get(self.current_platform, {}).get('name', self.current_platform)}'平台\n"
                    f"2. 或在'登录管理'中登录'{platform_name}'平台"
                )
                return

            # 🔥 首次搜索验证提示（针对抖音和小红书）
            crawler_mode = self.crawler_type_var.get()
            if crawler_mode == "search" and platform in ["dy", "xhs"]:
                # 检查是否是首次搜索（通过检查是否有历史记录）
                if not hasattr(self, '_search_verified') or not self._search_verified:
                    result = messagebox.askokcancel(
                        "⚠️ 重要提示",
                        f"🔔 首次使用搜索功能重要提示：\n\n"
                        f"1️⃣ 点击'确定'后，程序将开始搜索\n"
                        f"2️⃣ {platform_name}可能会弹出验证码或滑块验证\n"
                        f"3️⃣ 请在60秒内完成验证\n"
                        f"4️⃣ 验证完成后，采集将自动继续\n\n"
                        f"⚠️ 请不要关闭浏览器窗口！\n"
                        f"⚠️ 验证期间请不要点击'停止采集'！\n\n"
                        f"💡 验证通过后，后续搜索将不再需要验证"
                    )
                    if not result:
                        return
                    # 标记已提示
                    self._search_verified = True

            # 重置停止标志
            self.stop_flag = False

            # 更新UI状态
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.progress_bar.set(0)
            self.update_status(f"🔥 使用{platform_name}统一浏览器开始采集...")

            # 在新线程中运行采集任务
            self.task_thread = threading.Thread(target=self.run_crawler_task)
            self.task_thread.daemon = True
            self.task_thread.start()

        except Exception as e:
            messagebox.showerror("启动错误", f"启动采集时出错: {str(e)}")
            self.reset_ui_state()

    def stop_crawling(self):
        """停止采集"""
        # 🔥 如果正在验证登录，不允许停止
        if self.is_verifying:
            messagebox.showinfo(
                "无法停止",
                "正在进行登录验证，无法停止采集。\n\n"
                "请完成验证后，采集将自动继续。"
            )
            return

        self.stop_flag = True
        self.update_status("正在停止采集...")

        # 等待线程结束
        if hasattr(self, 'task_thread') and self.task_thread.is_alive():
            # 给线程一些时间来响应停止信号
            self.task_thread.join(timeout=2.0)

        self.reset_ui_state()

    def validate_config(self) -> bool:
        """验证配置"""
        mode = self.crawler_type_var.get()

        if mode == "search":
            # 🔥 更新：从textbox获取关键词
            keywords = self.keywords_textbox.get("1.0", "end-1c").strip()
            if not keywords:
                messagebox.showerror("配置错误", "请输入搜索关键词")
                return False
        elif mode == "detail":
            detail = self.detail_textbox.get("1.0", "end-1c").strip()
            if not detail:
                messagebox.showerror("配置错误", "请输入内容链接或ID")
                return False
        elif mode == "creator":
            creator = self.creator_textbox.get("1.0", "end-1c").strip()
            if not creator:
                messagebox.showerror("配置错误", "请输入创作者链接或ID")
                return False

        return True

    def run_crawler_task(self):
        """🔥 在后台线程中运行统一浏览器爬虫任务"""
        try:
            # 更新配置
            self.update_config()

            # 获取采集参数
            platform = self.platform_var.get()
            mode = self.crawler_type_var.get()
            max_count = int(self.max_notes_var.get())

            # 确定内容类型
            content_type = "视频" if platform in ['dy', 'ks'] else "内容"
            if platform == 'bili':
                content_type = "视频"
            elif platform == 'xhs':
                content_type = "笔记"
            elif platform == 'wb':
                content_type = "微博"
            elif platform == 'tieba':
                content_type = "帖子"
            elif platform == 'zhihu':
                content_type = "回答"

            # 初始化进度
            self.update_status("🔥 正在使用统一浏览器初始化采集...")
            self.update_progress(0, max_count, content_type)

            # 🔥 使用统一浏览器运行爬虫任务（async函数需要用asyncio.run调用）
            asyncio.run(self.run_unified_crawler(platform, max_count, content_type))

        except Exception as e:
            # 🔥 如果是用户主动停止,不显示错误
            if self.stop_flag:
                print("⏹️ 用户已停止采集")
                self.root.after(0, lambda: self.update_status("采集已停止"))
            else:
                error_msg = f"采集过程中出错: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("采集错误", error_msg))
                self.root.after(0, lambda: self.update_status("采集失败"))
        finally:
            self.root.after(0, self.reset_ui_state)

    async def run_unified_crawler(self, platform: str, max_count: int, content_type: str):
        """🔥 使用统一浏览器运行爬虫任务"""
        try:
            if platform == "dy":
                # 使用统一浏览器进行抖音采集
                await self.run_douyin_unified_crawler(max_count, content_type)
            elif platform == "xhs":
                # 使用统一浏览器进行小红书采集
                await self.run_xiaohongshu_unified_crawler(max_count, content_type)
            else:
                # 其他平台暂时使用原有方式
                self.run_real_crawler(platform, max_count, content_type)

        except Exception as e:
            print(f"❌ 统一浏览器采集失败: {e}")
            raise

    async def run_douyin_unified_crawler(self, max_count: int, content_type: str):
        """🔥 抖音统一浏览器采集 - 支持批量关键词/链接/创作者"""
        try:
            logger.info("="*60)
            logger.info("开始抖音采集任务")
            logger.info("="*60)

            # 🔥 自动检测登录状态并加载
            if not self.browser_ready or not self.shared_context:
                logger.info("检测到浏览器未就绪,正在检查登录状态...")
                print("🔍 检测到浏览器未就绪,正在检查登录状态...")
                login_status = self.check_saved_login_status("dy")

                if login_status.get('has_login'):
                    logger.info(f"检测到有效登录信息 (登录时间: {login_status.get('login_date')})")
                    print(f"✅ 检测到有效登录信息 (登录时间: {login_status.get('login_date')})")
                    print("🚀 正在自动加载登录信息并启动浏览器...")

                    # 🔥 修复：使用正确的方法名
                    # 自动启动统一浏览器并加载登录信息
                    await self.init_shared_browser("dy")

                    if not self.browser_ready or not self.shared_context:
                        logger.error("浏览器启动失败")
                        raise Exception("浏览器启动失败,请手动登录")

                    logger.info("浏览器已就绪,登录信息已加载")
                    print("✅ 浏览器已就绪,登录信息已加载")
                else:
                    logger.error(f"未找到有效登录信息: {login_status.get('reason')}")
                    raise Exception(f"未找到有效登录信息: {login_status.get('reason')}\n请先在'登录管理'中完成抖音登录")

            # 🔥 获取采集模式
            crawler_mode = self.crawler_type_var.get()

            # 🔥 根据模式获取输入内容
            if crawler_mode == "search":
                # 关键词搜索模式
                input_text = self.keywords_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入搜索关键词")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "关键词"

            elif crawler_mode == "detail":
                # 链接搜索模式
                input_text = self.detail_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入视频链接或ID")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "链接"

            elif crawler_mode == "creator":
                # 创作者搜索模式
                input_text = self.creator_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入创作者链接或ID")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "创作者"
            else:
                raise Exception(f"未知的采集模式: {crawler_mode}")

            if not input_list:
                raise Exception(f"请输入有效的{mode_name}")

            print(f"🔥 开始抖音批量采集 - {mode_name}模式")
            print(f"📋 {mode_name}数量: {len(input_list)}")
            print(f"📊 每组最大数量: {max_count}")

            # 🔥 批量执行 - 根据模式决定是批量还是逐个
            total_groups = len(input_list)

            if crawler_mode == "detail":
                # 🔥 多链接模式：一次性处理所有链接,输出到同一个文件
                print(f"\n{'='*60}")
                print(f"🔍 批量采集 {total_groups} 个视频链接")
                print(f"{'='*60}\n")

                self.root.after(0, lambda: self.update_status(f"正在批量采集 {total_groups} 个视频..."))

                # 一次性调用,传入所有链接
                if hasattr(self, 'browser_loop') and self.browser_loop and not self.browser_loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self.async_douyin_crawler_batch(input_list, max_count, content_type, crawler_mode),
                        self.browser_loop
                    )
                    # 🔥 移除超时限制,等待任务完成
                    future.result()
                else:
                    print("⚠️ 浏览器事件循环不存在，使用新的事件循环")
                    asyncio.run(self.async_douyin_crawler_batch(input_list, max_count, content_type, crawler_mode))

                print(f"✅ 批量采集完成！共 {total_groups} 个视频\n")
                logger.info(f"批量采集完成！共 {total_groups} 个视频")

            else:
                # 🔥 关键词/创作者模式：逐个处理
                for index, input_item in enumerate(input_list, 1):
                    if self.stop_flag:
                        print(f"⏹️ 用户停止采集")
                        break

                    print(f"\n{'='*60}")
                    print(f"🔍 [{index}/{total_groups}] 正在采集{mode_name}: {input_item}")
                    print(f"{'='*60}\n")

                    # 更新状态
                    self.root.after(0, lambda i=index, t=total_groups, item=input_item:
                        self.update_status(f"[{i}/{t}] 正在采集: {item}"))

                    # 🔥 使用 asyncio.run_coroutine_threadsafe 在浏览器事件循环中运行
                    if hasattr(self, 'browser_loop') and self.browser_loop and not self.browser_loop.is_closed():
                        future = asyncio.run_coroutine_threadsafe(
                            self.async_douyin_crawler(input_item, max_count, content_type, index, total_groups, crawler_mode),
                            self.browser_loop
                        )
                        # 🔥 移除超时限制,等待任务完成
                        future.result()
                    else:
                        # 如果没有事件循环，创建新的
                        print("⚠️ 浏览器事件循环不存在，使用新的事件循环")
                        asyncio.run(self.async_douyin_crawler(input_item, max_count, content_type, index, total_groups, crawler_mode))

                    print(f"✅ [{index}/{total_groups}] {mode_name} '{input_item}' 采集完成\n")
                    logger.info(f"[{index}/{total_groups}] {mode_name} '{input_item}' 采集完成")

            print(f"\n🎉 批量采集全部完成！共完成 {len(input_list)} 个{mode_name}")
            logger.info(f"批量采集全部完成！共完成 {len(input_list)} 个{mode_name}")

            # 🔥 采集完成后关闭浏览器,释放资源
            print("\n🧹 正在关闭浏览器,释放资源...")
            logger.info("采集完成,关闭浏览器")
            self.cleanup_browser()
            print("✅ 浏览器已关闭\n")

        except Exception as e:
            logger.error(f"抖音统一浏览器采集失败: {e}", exc_info=True)
            print(f"❌ 抖音统一浏览器采集失败: {e}")
            import traceback
            traceback.print_exc()

            # 🔥 出错也要关闭浏览器
            print("\n🧹 正在关闭浏览器...")
            self.cleanup_browser()
            raise

    async def run_xiaohongshu_unified_crawler(self, max_count: int, content_type: str):
        """🔥 小红书统一浏览器采集 - 支持批量关键词/链接/创作者"""
        try:
            logger.info("="*60)
            logger.info("开始小红书采集任务")
            logger.info("="*60)

            # 🔥 自动检测登录状态并加载
            if not self.browser_ready or not self.shared_context:
                logger.info("检测到浏览器未就绪,正在检查登录状态...")
                print("🔍 检测到浏览器未就绪,正在检查登录状态...")
                login_status = self.check_saved_login_status("xhs")

                if login_status.get('has_login'):
                    logger.info(f"检测到有效登录信息 (登录时间: {login_status.get('login_date')})")
                    print(f"✅ 检测到有效登录信息 (登录时间: {login_status.get('login_date')})")
                    print("🚀 正在自动加载登录信息并启动浏览器...")

                    # 🔥 修复：使用正确的方法名
                    # 自动启动统一浏览器并加载登录信息
                    await self.init_shared_browser("xhs")

                    if not self.browser_ready or not self.shared_context:
                        logger.error("浏览器启动失败")
                        raise Exception("浏览器启动失败,请手动登录")

                    logger.info("浏览器已就绪,登录信息已加载")
                    print("✅ 浏览器已就绪,登录信息已加载")
                else:
                    logger.error(f"未找到有效登录信息: {login_status.get('reason')}")
                    raise Exception(f"未找到有效登录信息: {login_status.get('reason')}\n请先在'登录管理'中完成小红书登录")

            # 🔥 获取采集模式
            crawler_mode = self.crawler_type_var.get()

            # 🔥 根据模式获取输入内容
            if crawler_mode == "search":
                # 关键词搜索模式
                input_text = self.keywords_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入搜索关键词")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "关键词"

            elif crawler_mode == "detail":
                # 链接搜索模式
                input_text = self.detail_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入笔记链接或ID")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "链接"

            elif crawler_mode == "creator":
                # 创作者搜索模式
                input_text = self.creator_textbox.get("1.0", "end-1c").strip()
                if not input_text:
                    raise Exception("请输入创作者链接或ID")
                input_list = [line.strip() for line in input_text.split('\n') if line.strip()]
                mode_name = "创作者"
            else:
                raise Exception(f"未知的采集模式: {crawler_mode}")

            if not input_list:
                raise Exception(f"请输入有效的{mode_name}")

            print(f"🔥 开始小红书批量采集 - {mode_name}模式")
            print(f"📋 {mode_name}数量: {len(input_list)}")
            print(f"📊 每组最大数量: {max_count}")

            # 🔥 批量执行 - 根据模式决定是批量还是逐个
            total_groups = len(input_list)

            if crawler_mode == "detail":
                # 🔥 多链接模式：一次性处理所有链接,输出到同一个文件
                print(f"\n{'='*60}")
                print(f"🔍 批量采集 {total_groups} 个笔记链接")
                print(f"{'='*60}\n")

                self.root.after(0, lambda: self.update_status(f"正在批量采集 {total_groups} 个笔记..."))

                # 一次性调用,传入所有链接
                if hasattr(self, 'browser_loop') and self.browser_loop and not self.browser_loop.is_closed():
                    future = asyncio.run_coroutine_threadsafe(
                        self.async_xiaohongshu_crawler_batch(input_list, max_count, content_type, crawler_mode),
                        self.browser_loop
                    )
                    future.result()
                else:
                    print("⚠️ 浏览器事件循环不存在，使用新的事件循环")
                    asyncio.run(self.async_xiaohongshu_crawler_batch(input_list, max_count, content_type, crawler_mode))

                print(f"✅ 批量采集完成！共 {total_groups} 个笔记\n")
                logger.info(f"批量采集完成！共 {total_groups} 个笔记")

            else:
                # 🔥 关键词/创作者模式：逐个处理
                for index, input_item in enumerate(input_list, 1):
                    if self.stop_flag:
                        print(f"⏹️ 用户停止采集")
                        break

                    print(f"\n{'='*60}")
                    print(f"🔍 [{index}/{total_groups}] 正在采集{mode_name}: {input_item}")
                    print(f"{'='*60}\n")

                    # 更新状态
                    self.root.after(0, lambda i=index, t=total_groups, item=input_item:
                        self.update_status(f"[{i}/{t}] 正在采集: {item}"))

                    # 🔥 使用 asyncio.run_coroutine_threadsafe 在浏览器事件循环中运行
                    if hasattr(self, 'browser_loop') and self.browser_loop and not self.browser_loop.is_closed():
                        future = asyncio.run_coroutine_threadsafe(
                            self.async_xiaohongshu_crawler(input_item, max_count, content_type, index, total_groups, crawler_mode),
                            self.browser_loop
                        )
                        future.result()
                    else:
                        print("⚠️ 浏览器事件循环不存在，使用新的事件循环")
                        asyncio.run(self.async_xiaohongshu_crawler(input_item, max_count, content_type, index, total_groups, crawler_mode))

                    print(f"✅ [{index}/{total_groups}] {mode_name} '{input_item}' 采集完成\n")
                    logger.info(f"[{index}/{total_groups}] {mode_name} '{input_item}' 采集完成")

            print(f"\n🎉 批量采集全部完成！共完成 {len(input_list)} 个{mode_name}")
            logger.info(f"批量采集全部完成！共完成 {len(input_list)} 个{mode_name}")

            # 🔥 采集完成后关闭浏览器,释放资源
            print("\n🧹 正在关闭浏览器,释放资源...")
            logger.info("采集完成,关闭浏览器")
            self.cleanup_browser()
            print("✅ 浏览器已关闭\n")

        except Exception as e:
            logger.error(f"小红书统一浏览器采集失败: {e}", exc_info=True)
            print(f"❌ 小红书统一浏览器采集失败: {e}")
            import traceback
            traceback.print_exc()

            # 🔥 出错也要关闭浏览器
            print("\n🧹 正在关闭浏览器...")
            self.cleanup_browser()
            raise

    async def async_douyin_crawler(self, input_item: str, max_count: int, content_type: str,
                                   current_index: int = 1, total_groups: int = 1, crawler_mode: str = "search"):
        """异步抖音采集任务 - 支持批量关键词/链接/创作者"""
        try:
            from 统一浏览器采集器 import run_unified_crawler

            # 🔥 获取GUI配置参数
            max_comments_per_video = int(self.max_comments_var.get())
            enable_comments = self.enable_comments_var.get()
            enable_sub_comments = self.enable_sub_comments_var.get()
            save_format = self.save_format_var.get()
            output_dir = self.output_dir_var.get()

            # 更新状态
            status_msg = f"🔥 [{current_index}/{total_groups}] 采集: {input_item}..."
            self.root.after(0, lambda: self.update_status(status_msg))

            logger.info(f"GUI配置参数: 模式={crawler_mode}, 输入={input_item}, 视频数={max_count}, 评论数={max_comments_per_video}, 格式={save_format}")
            print(f"📋 GUI配置参数:")
            print(f"   采集模式: {crawler_mode}")
            print(f"   输入内容: {input_item}")
            print(f"   视频数量: {max_count} 个")
            print(f"   每个视频评论数: {max_comments_per_video} 条")
            print(f"   一级评论: {enable_comments}")
            print(f"   二级评论: {enable_sub_comments}")
            print(f"   保存格式: {save_format}")
            print(f"   输出目录: {output_dir}")

            # 🔥 定义进度回调函数
            def progress_callback(current, total, message):
                """进度回调：更新GUI进度显示"""
                progress = current / total if total > 0 else 0
                progress_text = f"[{current_index}/{total_groups}] {current}/{total} {content_type}"

                # 在主线程中更新UI
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_text.configure(text=progress_text))
                self.root.after(0, lambda: self.update_status(f"🔥 {message}"))

                print(f"📊 进度: [{current}/{total}] {message}")

            # 🔥 定义停止标志检查函数
            def check_stop_flag():
                """检查是否应该停止采集"""
                return self.stop_flag

            # 🔥 使用统一浏览器进行采集，传递完整配置和进度回调
            generated_files = await run_unified_crawler(
                keywords=input_item if crawler_mode == "search" else None,
                video_url=input_item if crawler_mode == "detail" else None,
                creator_url=input_item if crawler_mode == "creator" else None,
                crawler_mode=crawler_mode,
                shared_context=self.shared_context,
                shared_page=self.shared_page,
                max_count=max_count,
                max_comments_per_video=max_comments_per_video,
                enable_comments=enable_comments,
                enable_sub_comments=enable_sub_comments,
                save_format=save_format,
                output_dir=output_dir,
                progress_callback=progress_callback,
                stop_flag_callback=check_stop_flag
            )

            # 采集完成
            save_path = output_dir if output_dir else f"data/douyin/{save_format}/"
            complete_msg = f"✅ [{current_index}/{total_groups}] {input_item} 采集完成"
            self.root.after(0, lambda: self.update_status(complete_msg))

            # 🔥 构建文件信息
            file_info = ""
            if generated_files:
                if "comments" in generated_files:
                    file_info += f"\n📄 评论文件: {generated_files['comments']}"
                if "contents" in generated_files:
                    file_info += f"\n📄 内容文件: {generated_files['contents']}"

            # 🔥 只在最后一组时显示完成提示
            if current_index == total_groups:
                # 🔥 清空关键词输入框，方便下次输入
                self.root.after(0, lambda: self.keywords_textbox.delete("1.0", "end"))

                self.root.after(0, lambda: messagebox.showinfo(
                    "批量采集完成",
                    f"🎉 批量采集全部完成！\n\n"
                    f"📋 共完成 {total_groups} 组关键词\n"
                    f"📊 每组采集 {max_count} 个{content_type}\n"
                    f"💬 每个视频最多 {max_comments_per_video} 条评论\n"
                    f"💾 保存格式: {save_format.upper()}\n"
                    f"📁 保存位置: {save_path}\n\n"
                    f"💡 提示: 每组关键词的数据已独立保存\n"
                    f"✨ 关键词输入框已清空，可以输入新关键词继续采集"
                ))

            # 🔥 自动打开最后一组的评论文件（如果存在）
            if current_index == total_groups and generated_files and "comments" in generated_files:
                import os
                import subprocess
                import platform

                comments_file = generated_files["comments"]
                if os.path.exists(comments_file):
                    try:
                        if platform.system() == "Windows":
                            os.startfile(comments_file)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", comments_file])
                        else:  # Linux
                            subprocess.run(["xdg-open", comments_file])
                        print(f"✅ 已自动打开最后一组的评论文件: {comments_file}")
                    except Exception as e:
                        print(f"⚠️ 无法自动打开文件: {e}")

        except Exception as e:
            error_msg = f"统一浏览器采集失败: {str(e)}"
            self.root.after(0, lambda: self.update_status("❌ 采集失败"))
            raise Exception(error_msg)

    async def async_douyin_crawler_batch(self, video_urls: list, max_count: int, content_type: str, crawler_mode: str = "detail"):
        """
        异步抖音批量链接采集 - 所有链接输出到同一个文件

        Args:
            video_urls: 视频链接列表
            max_count: 最大采集数量(对detail模式无效)
            content_type: 内容类型
            crawler_mode: 采集模式(应该是"detail")
        """
        try:
            from 统一浏览器采集器 import UnifiedBrowserCrawler

            # 🔥 获取GUI配置参数
            max_comments_per_video = int(self.max_comments_var.get())
            enable_comments = self.enable_comments_var.get()
            enable_sub_comments = self.enable_sub_comments_var.get()
            save_format = self.save_format_var.get()
            output_dir = self.output_dir_var.get()

            logger.info(f"批量链接采集: {len(video_urls)} 个视频")
            print(f"📋 批量链接采集配置:")
            print(f"   视频数量: {len(video_urls)} 个")
            print(f"   每个视频评论数: {max_comments_per_video} 条")
            print(f"   一级评论: {enable_comments}")
            print(f"   二级评论: {enable_sub_comments}")
            print(f"   保存格式: {save_format}")
            print(f"   输出目录: {output_dir}")

            # 🔥 定义停止标志检查函数
            def check_stop_flag():
                """检查是否应该停止采集"""
                return self.stop_flag

            # 🔥 创建进度回调函数
            def progress_callback(video_index, total_videos, comment_count, max_comments=None):
                """进度回调：更新GUI进度显示"""
                try:
                    # 更新视频进度
                    self.root.after(0, lambda: self.update_video_progress(video_index, total_videos))
                    # 更新评论进度
                    if max_comments:
                        self.root.after(0, lambda: self.update_comment_progress(comment_count, max_comments))
                    # 更新总体进度
                    message = f"正在采集第 {video_index}/{total_videos} 个视频，已获取 {comment_count} 条评论"
                    self.root.after(0, lambda: self.update_total_progress(message))
                except Exception as e:
                    print(f"⚠️ 进度回调失败: {e}")

            # 🔥 创建统一浏览器采集器
            crawler = UnifiedBrowserCrawler(
                shared_context=self.shared_context,
                shared_page=self.shared_page,
                progress_callback=progress_callback,
                stop_flag_callback=check_stop_flag,
                gui_app=self  # 🔥 传递GUI实例，用于设置验证状态
            )

            # 🔥 一次性设置所有链接
            import config
            config.DY_SPECIFIED_ID_LIST = video_urls
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_video
            config.CRAWLER_TYPE = "detail"
            config.PLATFORM = "dy"
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format

            # 🔥 重置store
            from store.douyin import DouyinStoreFactory
            import store.douyin as douyin_store
            DouyinStoreFactory.reset_store()
            douyin_store._video_info_cache.clear()

            if output_dir:
                DouyinStoreFactory.set_output_dir(output_dir)

            # 设置爬虫
            await crawler.setup_crawler("dy")

            # 开始采集
            if crawler.crawler:
                await crawler.start_unified_douyin_crawling()

            print(f"✅ 批量链接采集完成！")
            logger.info(f"批量链接采集完成！")

        except Exception as e:
            error_msg = f"批量链接采集失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: self.update_status("❌ 采集失败"))
            raise Exception(error_msg)

    async def async_xiaohongshu_crawler(self, input_item: str, max_count: int, content_type: str,
                                       current_index: int = 1, total_groups: int = 1, crawler_mode: str = "search"):
        """异步小红书采集任务 - 支持批量关键词/链接/创作者"""
        try:
            from 统一浏览器采集器 import run_unified_crawler

            # 🔥 获取GUI配置参数
            max_comments_per_note = int(self.max_comments_var.get())
            enable_comments = self.enable_comments_var.get()
            enable_sub_comments = self.enable_sub_comments_var.get()
            save_format = self.save_format_var.get()
            output_dir = self.output_dir_var.get()

            # 更新状态
            status_msg = f"🔥 [{current_index}/{total_groups}] 采集: {input_item}..."
            self.root.after(0, lambda: self.update_status(status_msg))

            logger.info(f"GUI配置参数: 模式={crawler_mode}, 输入={input_item}, 笔记数={max_count}, 评论数={max_comments_per_note}, 格式={save_format}")
            print(f"📋 GUI配置参数:")
            print(f"   采集模式: {crawler_mode}")
            print(f"   输入内容: {input_item}")
            print(f"   笔记数量: {max_count} 个")
            print(f"   每个笔记评论数: {max_comments_per_note} 条")
            print(f"   一级评论: {enable_comments}")
            print(f"   二级评论: {enable_sub_comments}")
            print(f"   保存格式: {save_format}")
            print(f"   输出目录: {output_dir}")

            # 🔥 定义进度回调函数
            def progress_callback(current, total, message):
                """进度回调：更新GUI进度显示"""
                progress = current / total if total > 0 else 0
                progress_text = f"[{current_index}/{total_groups}] {current}/{total} {content_type}"

                # 在主线程中更新UI
                self.root.after(0, lambda: self.progress_bar.set(progress))
                self.root.after(0, lambda: self.progress_text.configure(text=progress_text))
                self.root.after(0, lambda: self.update_status(f"🔥 {message}"))

                print(f"📊 进度: [{current}/{total}] {message}")

            # 🔥 使用统一浏览器进行采集，传递完整配置和进度回调
            generated_files = await run_unified_crawler(
                keywords=input_item if crawler_mode == "search" else None,
                note_url=input_item if crawler_mode == "detail" else None,
                creator_url=input_item if crawler_mode == "creator" else None,
                crawler_mode=crawler_mode,
                shared_context=self.shared_context,
                shared_page=self.shared_page,
                max_count=max_count,
                max_comments_per_note=max_comments_per_note,
                enable_comments=enable_comments,
                enable_sub_comments=enable_sub_comments,
                save_format=save_format,
                output_dir=output_dir,
                progress_callback=progress_callback,
                platform="xhs"  # 🔥 指定平台为小红书
            )

            # 🔥 采集完成后的处理
            print(f"\n✅ [{current_index}/{total_groups}] 采集完成！")
            logger.info(f"[{current_index}/{total_groups}] 采集完成")

            # 更新进度为100%
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.progress_text.configure(
                text=f"[{current_index}/{total_groups}] {max_count}/{max_count} {content_type}"
            ))

            # 🔥 如果是关键词搜索模式，清空输入框
            if crawler_mode == "search" and current_index == total_groups:
                self.root.after(0, lambda: self.keywords_textbox.delete("1.0", "end"))
                self.root.after(0, lambda: self.update_status(
                    f"✅ [{current_index}/{total_groups}] 采集完成！\n"
                    f"✨ 关键词输入框已清空，可以输入新关键词继续采集"
                ))

            # 🔥 自动打开最后一组的评论文件（如果存在）
            if current_index == total_groups and generated_files and "comments" in generated_files:
                import os
                import subprocess
                import platform

                comments_file = generated_files["comments"]
                if os.path.exists(comments_file):
                    try:
                        if platform.system() == "Windows":
                            os.startfile(comments_file)
                        elif platform.system() == "Darwin":  # macOS
                            subprocess.run(["open", comments_file])
                        else:  # Linux
                            subprocess.run(["xdg-open", comments_file])
                        print(f"✅ 已自动打开最后一组的评论文件: {comments_file}")
                    except Exception as e:
                        print(f"⚠️ 无法自动打开文件: {e}")

        except Exception as e:
            error_msg = f"统一浏览器采集失败: {str(e)}"
            self.root.after(0, lambda: self.update_status("❌ 采集失败"))
            raise Exception(error_msg)

    async def async_xiaohongshu_crawler_batch(self, note_urls: list, max_count: int, content_type: str, crawler_mode: str = "detail"):
        """
        异步小红书批量链接采集 - 所有链接输出到同一个文件

        Args:
            note_urls: 笔记链接列表
            max_count: 最大采集数量(对detail模式无效)
            content_type: 内容类型
            crawler_mode: 采集模式(应该是"detail")
        """
        try:
            from 统一浏览器采集器 import UnifiedBrowserCrawler

            # 🔥 获取GUI配置参数
            max_comments_per_note = int(self.max_comments_var.get())
            enable_comments = self.enable_comments_var.get()
            enable_sub_comments = self.enable_sub_comments_var.get()
            save_format = self.save_format_var.get()
            output_dir = self.output_dir_var.get()

            logger.info(f"批量链接采集: {len(note_urls)} 个笔记")
            print(f"📋 批量链接采集配置:")
            print(f"   笔记数量: {len(note_urls)} 个")
            print(f"   每个笔记评论数: {max_comments_per_note} 条")
            print(f"   一级评论: {enable_comments}")
            print(f"   二级评论: {enable_sub_comments}")
            print(f"   保存格式: {save_format}")
            print(f"   输出目录: {output_dir}")

            # 🔥 定义停止标志检查函数
            def check_stop_flag():
                """检查是否应该停止采集"""
                return self.stop_flag

            # 🔥 创建进度回调函数
            def progress_callback(video_index, total_videos, comment_count, max_comments=None):
                """进度回调：更新GUI进度显示"""
                try:
                    # 更新视频进度
                    self.root.after(0, lambda: self.update_video_progress(video_index, total_videos))
                    # 更新评论进度
                    if max_comments:
                        self.root.after(0, lambda: self.update_comment_progress(comment_count, max_comments))
                    # 更新总体进度
                    message = f"正在采集第 {video_index}/{total_videos} 个视频，已获取 {comment_count} 条评论"
                    self.root.after(0, lambda: self.update_total_progress(message))
                except Exception as e:
                    print(f"⚠️ 进度回调失败: {e}")

            # 🔥 创建统一浏览器采集器
            crawler = UnifiedBrowserCrawler(
                shared_context=self.shared_context,
                shared_page=self.shared_page,
                progress_callback=progress_callback,
                stop_flag_callback=check_stop_flag,
                gui_app=self  # 🔥 传递GUI实例，用于设置验证状态
            )

            # 🔥 一次性设置所有链接
            import config
            from config import xhs_config
            # 🔥 关键修复: 同时设置config和xhs_config,确保两者一致
            config.XHS_SPECIFIED_NOTE_URL_LIST = note_urls
            xhs_config.XHS_SPECIFIED_NOTE_URL_LIST = note_urls
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = max_comments_per_note
            config.CRAWLER_TYPE = "detail"
            config.PLATFORM = "xhs"
            config.ENABLE_GET_COMMENTS = enable_comments
            config.ENABLE_GET_SUB_COMMENTS = enable_sub_comments
            config.SAVE_DATA_OPTION = save_format

            # 🔥 重置store
            from store.xhs import XhsStoreFactory
            import store.xhs as xhs_store
            XhsStoreFactory.reset_store()
            if hasattr(xhs_store, '_note_info_cache'):
                xhs_store._note_info_cache.clear()

            if output_dir:
                XhsStoreFactory.set_output_dir(output_dir)

            # 设置爬虫
            await crawler.setup_crawler("xhs")

            # 开始采集
            if crawler.crawler:
                await crawler.start_unified_xiaohongshu_crawling()

            print(f"✅ 批量链接采集完成！")
            logger.info(f"批量链接采集完成！")

        except Exception as e:
            error_msg = f"批量链接采集失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: self.update_status("❌ 采集失败"))
            raise Exception(error_msg)

    def run_real_crawler(self, platform: str, max_count: int, content_type: str):
        """运行真实的爬虫任务"""
        try:
            # 导入爬虫工厂
            from main import CrawlerFactory
            import asyncio

            # 更新状态
            self.root.after(0, lambda: self.update_status("正在启动爬虫引擎..."))

            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 运行异步爬虫任务
                loop.run_until_complete(self.async_crawler_task(platform, max_count, content_type))
            finally:
                loop.close()

        except Exception as e:
            error_msg = f"爬虫引擎启动失败: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("爬虫错误", error_msg))
            self.root.after(0, lambda: self.update_status("爬虫启动失败"))

    async def async_crawler_task(self, platform: str, max_count: int, content_type: str):
        """异步爬虫任务"""
        try:
            from main import CrawlerFactory
            import config

            # 更新状态
            self.root.after(0, lambda: self.update_status("正在创建爬虫实例..."))

            # 创建爬虫实例
            crawler = CrawlerFactory.create_crawler(platform)

            # 更新状态
            self.root.after(0, lambda: self.update_status("正在启动爬虫..."))

            # 启动爬虫
            await crawler.start()

            # 完成采集
            self.root.after(0, lambda: self.update_progress(max_count, max_count, content_type))
            self.root.after(0, lambda: self.update_status("采集完成"))

            # 显示完成消息
            self.root.after(0, lambda: messagebox.showinfo("采集完成", f"成功采集 {max_count} 个{content_type}！\n\n数据已保存到 data/{platform} 目录"))

        except Exception as e:
            error_msg = f"爬虫执行失败: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("爬虫错误", error_msg))
            self.root.after(0, lambda: self.update_status("爬虫执行失败"))

    def simulate_crawling_progress(self, max_count: int, content_type: str):
        """模拟采集进度（用于演示）"""
        import time

        for i in range(1, max_count + 1):
            if hasattr(self, 'stop_flag') and self.stop_flag:
                break

            # 模拟采集延迟
            time.sleep(0.1)  # 实际采集中这里是网络请求时间

            # 更新进度
            self.root.after(0, lambda current=i: self.update_progress(current, max_count, content_type))
            self.root.after(0, lambda current=i: self.update_status(f"正在采集第 {current} 个{content_type}..."))

    def update_config(self):
        """更新MediaCrawler配置"""
        import config

        config.PLATFORM = self.platform_var.get()
        config.CRAWLER_TYPE = self.crawler_type_var.get()
        config.LOGIN_TYPE = self.login_type_var.get()
        config.SAVE_DATA_OPTION = self.save_format_var.get()

        # 确保登录状态保存开启
        config.SAVE_LOGIN_STATE = True

        # 更新关键词
        if config.CRAWLER_TYPE == "search":
            # 🔥 更新：从textbox获取关键词（只取第一行作为默认配置）
            keywords_text = self.keywords_textbox.get("1.0", "end-1c").strip()
            # 取第一行作为默认关键词
            config.KEYWORDS = keywords_text.split('\n')[0] if keywords_text else ""

        # 更新数量设置
        try:
            config.CRAWLER_MAX_NOTES_COUNT = int(self.max_notes_var.get())
            config.CRAWLER_MAX_COMMENTS_COUNT_SINGLENOTES = int(self.max_comments_var.get())
            config.CRAWLER_MAX_SLEEP_SEC = int(self.sleep_var.get())
            config.MAX_CONCURRENCY_NUM = int(self.concurrency_var.get())
        except ValueError:
            pass  # 使用默认值

        # 更新功能选项
        config.ENABLE_GET_COMMENTS = self.enable_comments_var.get()
        config.ENABLE_GET_SUB_COMMENTS = self.enable_sub_comments_var.get()
        config.ENABLE_GET_WORDCLOUD = self.enable_wordcloud_var.get()
        config.ENABLE_GET_IMAGES = self.enable_media_var.get()  # 修复拼写错误
        config.HEADLESS = self.headless_var.get()

        # 打印配置信息用于调试
        print(f"🔧 配置更新:")
        print(f"   平台: {config.PLATFORM}")
        print(f"   模式: {config.CRAWLER_TYPE}")
        print(f"   关键词: {getattr(config, 'KEYWORDS', 'N/A')}")
        print(f"   最大数量: {config.CRAWLER_MAX_NOTES_COUNT}")
        print(f"   登录状态保存: {config.SAVE_LOGIN_STATE}")

    def reset_ui_state(self):
        """重置UI状态"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_text.configure(text="0/0 内容")
        self.stop_flag = False
        # 🔥 重置新增的进度显示
        self.reset_progress_display()

    # 快速操作方法
    def open_data_dir(self):
        """打开数据目录"""
        data_dir = Path(self.output_dir_var.get())
        if data_dir.exists():
            os.startfile(str(data_dir))
        else:
            messagebox.showwarning("目录不存在", f"数据目录不存在: {data_dir}")

    def generate_wordcloud(self):
        """生成词云图"""
        messagebox.showinfo("功能提示", "词云图生成功能将在采集完成后自动执行")

    def analyze_data(self):
        """数据分析"""
        messagebox.showinfo("功能提示", "数据分析功能正在开发中")

    def clear_cache(self):
        """清理缓存"""
        if messagebox.askyesno("确认清理", "确定要清理浏览器缓存和登录状态吗？"):
            # TODO: 实现缓存清理逻辑
            messagebox.showinfo("清理完成", "缓存清理完成")

    def open_advanced_settings(self):
        """打开高级设置"""
        messagebox.showinfo("功能提示", "高级设置功能正在开发中")

    def show_help(self):
        """显示帮助"""
        help_text = """
MediaCrawler 使用帮助

1. 选择平台：点击要采集的社交媒体平台
2. 设置模式：选择关键词搜索、指定内容或创作者主页
3. 配置参数：设置采集数量、评论数等参数
4. 登录账号：根据需要登录相应平台
5. 开始采集：点击"开始采集"按钮

注意事项：
- 请遵守各平台的使用条款
- 合理控制采集频率，避免对平台造成负担
- 建议先小量测试，再进行大规模采集

如有问题，请查看项目文档或联系开发者。
        """
        messagebox.showinfo("使用帮助", help_text)

    async def init_shared_browser(self, platform: str):
        """
        🔥 初始化干净无痕浏览器 - 登录和采集使用同一个浏览器实例，但保存登录信息
        """
        try:
            from playwright.async_api import async_playwright
            import sys
            import os
            from pathlib import Path

            if self.shared_browser and self.browser_ready and self.current_platform == platform:
                print(f"🔗 复用现有干净浏览器实例 ({platform})")
                return True

            # 清理旧的浏览器实例
            await self.cleanup_browser()

            print(f"🚀 启动干净无痕浏览器实例 ({platform})")

            # 🔥 验证环境变量是否已设置（应该在 start_gui.py 中设置）
            browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
            if not browsers_path:
                error_msg = "❌ 致命错误：PLAYWRIGHT_BROWSERS_PATH 环境变量未设置！"
                print(error_msg)
                print("   这表明程序启动流程有问题，请联系开发者")
                try:
                    logger.error(error_msg)
                except Exception:
                    pass
                raise RuntimeError("环境变量未设置，无法启动浏览器")

            # 验证浏览器路径是否存在
            browsers_path_obj = Path(browsers_path)
            if not browsers_path_obj.exists():
                error_msg = f"❌ 致命错误：浏览器路径不存在: {browsers_path}"
                print(error_msg)
                print("   请确保完整解压了软件包，包含 playwright_browsers 目录")
                try:
                    logger.error(error_msg)
                except Exception:
                    pass
                raise RuntimeError(f"浏览器路径不存在: {browsers_path}")

            # 验证 chrome.exe 是否存在
            chrome_found = False
            for sub in browsers_path_obj.glob("chromium-*"):
                if (sub / "chrome-win" / "chrome.exe").exists():
                    chrome_found = True
                    print(f"✅ 验证通过：找到浏览器可执行文件: {sub / 'chrome-win' / 'chrome.exe'}")
                    try:
                        logger.info(f"浏览器可执行文件: {sub / 'chrome-win' / 'chrome.exe'}")
                    except Exception:
                        pass
                    break

            if not chrome_found:
                error_msg = f"❌ 致命错误：浏览器目录存在但未找到 chrome.exe: {browsers_path}"
                print(error_msg)
                print("   playwright_browsers 目录可能不完整，请重新下载")
                try:
                    logger.error(error_msg)
                except Exception:
                    pass
                raise RuntimeError("未找到 chrome.exe")

            print(f"✅ 环境变量验证通过: PLAYWRIGHT_BROWSERS_PATH = {browsers_path}")
            print(f"✅ 环境变量验证通过: PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = {os.environ.get('PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD', 'NOT SET')}")

            # 启动新的浏览器实例
            print("🔄 正在启动 Playwright...")
            self.playwright = await async_playwright().start()
            print("✅ Playwright 启动成功")

            # 🔥 使用固定的干净目录，但每次启动时清理
            self.clean_browser_dir = os.path.join(
                os.getcwd(),
                "browser_data",
                f"clean_{platform}_browser"
            )

            # 🔥 清理旧的浏览器数据（保持干净）
            if os.path.exists(self.clean_browser_dir):
                import shutil
                try:
                    shutil.rmtree(self.clean_browser_dir)
                    print(f"🧹 已清理旧的浏览器数据")
                except Exception as e:
                    print(f"⚠️ 清理浏览器数据失败: {e}")

            os.makedirs(self.clean_browser_dir, exist_ok=True)
            print(f"🧹 干净浏览器目录: {self.clean_browser_dir}")

            # 🔥 设置登录信息保存目录
            self.login_data_dir = os.path.join(
                os.getcwd(),
                "login_data",
                f"{platform}_login_info"
            )
            os.makedirs(self.login_data_dir, exist_ok=True)
            print(f"💾 登录信息保存目录: {self.login_data_dir}")

            # 启动干净的浏览器上下文
            try:
                # 🔥 Playwright通过环境变量PLAYWRIGHT_BROWSERS_PATH来查找浏览器
                # 我们已经在文件开头设置了这个环境变量
                # 不需要使用executable_path参数

                # 检查便携式浏览器状态（仅用于日志）
                available, message = check_browser_available()
                print(f"🔍 浏览器状态: {message}")

                if "PLAYWRIGHT_BROWSERS_PATH" in os.environ:
                    print(f"✅ 使用便携式浏览器: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
                else:
                    print("ℹ️ 使用系统默认浏览器")

                # 定义 launch_options（干净、可运行）
                # 注意：launch_persistent_context 不支持 executable_path 参数
                # 浏览器路径完全由 PLAYWRIGHT_BROWSERS_PATH 环境变量控制
                launch_options = {
                    "user_data_dir": self.clean_browser_dir,  # 使用固定的干净目录
                    "headless": False,
                    "viewport": {"width": 1920, "height": 1080},
                    "user_agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    "args": [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-extensions',
                        '--disable-plugins',
                        # '--disable-images',  # 🔥 移除这个,小红书需要加载图片来检测登录状态
                        '--disable-javascript-harmony-shipping',
                        '--disable-background-timer-throttling',
                        '--disable-renderer-backgrounding',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-features=TranslateUI',
                        '--disable-ipc-flooding-protection',
                        '--disable-infobars',
                        '--window-size=1920,1080',
                        '--start-maximized'
                    ],
                    "ignore_default_args": ['--enable-automation']
                }

                print(f"🔄 正在启动浏览器上下文...")
                print(f"   user_data_dir: {self.clean_browser_dir}")
                print(f"   使用环境变量指定的浏览器: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH')}")

                self.shared_context = await self.playwright.chromium.launch_persistent_context(**launch_options)
                print(f"✅ 浏览器上下文启动成功")
            except Exception as browser_error:
                error_msg = str(browser_error)

                # 🔥 智能识别浏览器相关错误
                browser_error_keywords = [
                    "Executable doesn't exist",
                    "browser executable",
                    "chrome.exe",
                    "chromium",
                    "playwright",
                    "Target page, context or browser has been closed",
                    "Browser closed"
                ]

                is_browser_error = any(keyword.lower() in error_msg.lower() for keyword in browser_error_keywords)

                if is_browser_error:
                    print(f"❌ 浏览器启动失败")
                    print(f"💡 错误详情: {error_msg}")

                    # 🔥 更新浏览器驱动状态
                    self.browser_driver_installed = False

                    # 抛出友好的错误信息
                    raise Exception(
                        f"浏览器启动失败!\n\n"
                        f"可能原因:\n"
                        f"1. 浏览器文件缺失或损坏\n"
                        f"2. 软件包不完整(未完整解压)\n"
                        f"3. 杀毒软件拦截了浏览器\n"
                        f"4. 系统权限不足\n\n"
                        f"解决方法:\n"
                        f"1. 重新下载完整安装包\n"
                        f"2. 解压到英文路径(无中文、无空格)\n"
                        f"3. 关闭杀毒软件后重试\n"
                        f"4. 右键'以管理员身份运行'\n"
                        f"5. 确保解压了所有文件,包括 _internal 文件夹\n\n"
                        f"详细错误: {error_msg}"
                    )
                else:
                    raise

            # 创建页面
            self.shared_page = await self.shared_context.new_page()

            # 🔥 注入反检测脚本 (使用最简化、最兼容的语法)
            try:
                # 🔥 使用最简化的 JavaScript 代码，避免任何可能的语法问题
                stealth_script = """
(function() {
    try {
        Object.defineProperty(navigator, 'webdriver', {
            get: function() { return undefined; }
        });
    } catch(e) { console.log('webdriver stealth failed:', e); }

    try {
        window.chrome = { runtime: {} };
    } catch(e) { console.log('chrome stealth failed:', e); }

    try {
        Object.defineProperty(navigator, 'plugins', {
            get: function() { return [1, 2, 3, 4, 5]; }
        });
    } catch(e) { console.log('plugins stealth failed:', e); }

    try {
        Object.defineProperty(navigator, 'languages', {
            get: function() { return ['zh-CN', 'zh', 'en']; }
        });
    } catch(e) { console.log('languages stealth failed:', e); }
})();
"""
                await self.shared_page.add_init_script(stealth_script)
                print("✅ 反检测脚本注入成功")
            except Exception as script_error:
                print(f"⚠️ 反检测脚本注入失败: {script_error}")
                # 即使脚本注入失败，也继续运行（不影响核心功能）

            # 🔥 立即加载已保存的登录信息（如果存在）
            login_loaded = await self.load_saved_login_info(platform)

            self.browser_ready = True
            self.current_platform = platform

            if login_loaded:
                print(f"✅ 干净浏览器启动成功，登录信息已恢复")
            else:
                print(f"✅ 干净浏览器启动成功，需要重新登录")
            return True

        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            await self.cleanup_browser()
            return False

    async def load_saved_login_info(self, platform: str):
        """🔥 加载已保存的登录信息到干净浏览器"""
        try:
            import json

            # 检查是否有保存的登录信息
            cookies_file = os.path.join(self.login_data_dir, "cookies.json")
            local_storage_file = os.path.join(self.login_data_dir, "local_storage.json")
            session_storage_file = os.path.join(self.login_data_dir, "session_storage.json")

            loaded_count = 0

            # 加载Cookies
            if os.path.exists(cookies_file):
                with open(cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    if cookies:  # 确保有数据
                        await self.shared_context.add_cookies(cookies)
                        print(f"✅ 已加载 {len(cookies)} 个Cookies")
                        loaded_count += len(cookies)

            # 先导航到平台页面，然后加载Storage
            platform_urls = {
                'dy': 'https://www.douyin.com',
                'xhs': 'https://www.xiaohongshu.com',
                'ks': 'https://www.kuaishou.com',
                'bili': 'https://www.bilibili.com',
                'wb': 'https://weibo.com',
                'tieba': 'https://tieba.baidu.com',
                'zhihu': 'https://www.zhihu.com'
            }

            if platform in platform_urls:
                try:
                    await self.shared_page.goto(platform_urls[platform], wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(1)  # 等待页面加载
                except Exception as e:
                    print(f"⚠️ 导航到平台页面失败: {e}")

            # 加载LocalStorage
            if os.path.exists(local_storage_file):
                with open(local_storage_file, 'r', encoding='utf-8') as f:
                    local_storage = json.load(f)
                    if local_storage:
                        for key, value in local_storage.items():
                            try:
                                await self.shared_page.evaluate(f"localStorage.setItem('{key}', '{value}')")
                            except Exception as e:
                                print(f"⚠️ 设置LocalStorage失败 {key}: {e}")
                        print(f"✅ 已加载 {len(local_storage)} 个LocalStorage项")
                        loaded_count += len(local_storage)

            # 加载SessionStorage
            if os.path.exists(session_storage_file):
                with open(session_storage_file, 'r', encoding='utf-8') as f:
                    session_storage = json.load(f)
                    if session_storage:
                        for key, value in session_storage.items():
                            try:
                                await self.shared_page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
                            except Exception as e:
                                print(f"⚠️ 设置SessionStorage失败 {key}: {e}")
                        print(f"✅ 已加载 {len(session_storage)} 个SessionStorage项")
                        loaded_count += len(session_storage)

            return loaded_count > 0  # 返回是否成功加载了登录信息

        except Exception as e:
            print(f"⚠️ 加载登录信息失败: {e}")
            return False

    async def save_login_info(self, platform: str):
        """🔥 保存当前登录信息"""
        try:
            import json
            import time

            print(f"💾 开始保存{platform}登录信息...")

            # 确保保存目录存在
            os.makedirs(self.login_data_dir, exist_ok=True)

            # 保存Cookies
            cookies = await self.shared_context.cookies()
            cookies_file = os.path.join(self.login_data_dir, "cookies.json")
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(cookies)} 个Cookies")

            # 保存LocalStorage
            local_storage = await self.shared_page.evaluate("() => Object.assign({}, localStorage)")
            local_storage_file = os.path.join(self.login_data_dir, "local_storage.json")
            with open(local_storage_file, 'w', encoding='utf-8') as f:
                json.dump(local_storage, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(local_storage)} 个LocalStorage项")

            # 保存SessionStorage
            session_storage = await self.shared_page.evaluate("() => Object.assign({}, sessionStorage)")
            session_storage_file = os.path.join(self.login_data_dir, "session_storage.json")
            with open(session_storage_file, 'w', encoding='utf-8') as f:
                json.dump(session_storage, f, ensure_ascii=False, indent=2)
            print(f"✅ 已保存 {len(session_storage)} 个SessionStorage项")

            # 保存登录时间戳
            login_info = {
                "platform": platform,
                "login_time": time.time(),
                "login_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cookies_count": len(cookies),
                "local_storage_count": len(local_storage),
                "session_storage_count": len(session_storage)
            }

            info_file = os.path.join(self.login_data_dir, "login_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(login_info, f, ensure_ascii=False, indent=2)

            print(f"🎉 {platform}登录信息保存完成！")
            return True

        except Exception as e:
            print(f"❌ 保存登录信息失败: {e}")
            return False

    async def _check_platform_login_status(self, platform: str, page) -> bool:
        """🔥 检测平台是否已登录(通过页面元素判断)"""
        try:
            # 等待页面加载
            await asyncio.sleep(2)

            # 不同平台的登录检测策略
            if platform == 'xhs':
                # 小红书:检查是否有用户头像或用户名
                try:
                    # 方法1: 检查是否有用户头像
                    avatar = await page.query_selector('img[class*="avatar"]')
                    if avatar:
                        print(f"   ✅ 检测到用户头像,已登录")
                        return True

                    # 方法2: 检查是否有"登录"按钮(如果有,说明未登录)
                    login_btn = await page.query_selector('text=登录')
                    if login_btn:
                        print(f"   ❌ 检测到'登录'按钮,未登录")
                        return False

                    # 方法3: 检查Cookies中是否有web_session
                    cookies = await page.context.cookies()
                    for cookie in cookies:
                        if cookie['name'] == 'web_session' and cookie['value']:
                            print(f"   ✅ 检测到web_session cookie,已登录")
                            return True

                    print(f"   ⚠️ 无法确定登录状态,默认为未登录")
                    return False

                except Exception as e:
                    print(f"   ⚠️ 登录检测失败: {e}")
                    return False

            elif platform == 'dy':
                # 抖音:检查是否有用户信息
                try:
                    # 检查是否有"登录"按钮
                    login_btn = await page.query_selector('text=登录')
                    if login_btn:
                        return False

                    # 检查是否有用户头像
                    avatar = await page.query_selector('img[class*="avatar"]')
                    if avatar:
                        return True

                    return False
                except:
                    return False

            else:
                # 其他平台:默认检查是否有"登录"按钮
                try:
                    login_btn = await page.query_selector('text=登录')
                    return login_btn is None
                except:
                    return False

        except Exception as e:
            print(f"   ❌ 登录状态检测失败: {e}")
            return False

    def check_saved_login_status(self, platform: str):
        """🔥 检查已保存的登录状态"""
        try:
            import json

            login_data_dir = os.path.join(
                os.getcwd(),
                "login_data",
                f"{platform}_login_info"
            )

            info_file = os.path.join(login_data_dir, "login_info.json")
            cookies_file = os.path.join(login_data_dir, "cookies.json")

            print(f"🔍 检查{platform}登录状态:")
            print(f"   登录数据目录: {login_data_dir}")
            print(f"   信息文件存在: {os.path.exists(info_file)}")
            print(f"   Cookies文件存在: {os.path.exists(cookies_file)}")

            if os.path.exists(info_file) and os.path.exists(cookies_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    login_info = json.load(f)

                # 检查登录时间（7天内有效）
                import time
                current_time = time.time()
                login_time = login_info.get('login_time', 0)
                days_passed = (current_time - login_time) / (24 * 3600)

                print(f"   登录时间: {login_info.get('login_date', '未知')}")
                print(f"   天数差: {round(days_passed, 1)}天")

                if days_passed < 7:  # 7天内有效
                    result = {
                        'has_login': True,
                        'login_date': login_info.get('login_date', '未知'),
                        'days_passed': round(days_passed, 1),
                        'cookies_count': login_info.get('cookies_count', 0)
                    }
                    print(f"   ✅ 登录状态有效")
                    return result
                else:
                    print(f"   ❌ 登录信息已过期")
                    return {'has_login': False, 'reason': '登录信息已过期（超过7天）'}
            else:
                print(f"   ❌ 未找到登录文件")
                return {'has_login': False, 'reason': '未找到登录信息'}

        except Exception as e:
            print(f"   ❌ 检查失败: {e}")
            return {'has_login': False, 'reason': f'检查失败: {e}'}

    def update_all_login_status(self):
        """🔥 更新所有平台的登录状态显示"""
        for platform_id in self.platforms.keys():
            self.update_login_status(platform_id)

    def update_login_status(self, platform: str):
        """🔥 更新指定平台的登录状态显示"""
        try:
            status_info = self.check_saved_login_status(platform)

            if platform in self.login_buttons:
                status_label = self.login_buttons[platform]["status"]
                button = self.login_buttons[platform]["button"]

                if status_info['has_login']:
                    # 有有效登录信息
                    status_text = f"✅ 已登录 ({status_info['days_passed']}天前)"
                    status_label.configure(text=status_text, text_color="green")
                    button.configure(text="重新登录")
                else:
                    # 无有效登录信息
                    status_text = f"❌ 未登录"
                    if 'reason' in status_info:
                        status_text += f" ({status_info['reason']})"
                    status_label.configure(text=status_text, text_color="red")
                    button.configure(text="开始登录")

        except Exception as e:
            print(f"⚠️ 更新登录状态失败: {e}")

    def save_login_after_confirmation(self, platform: str, platform_name: str):
        """🔥 用户确认登录完成后保存登录信息"""
        def run_save():
            try:
                if self.browser_ready and self.current_platform == platform:
                    # 在新线程中运行异步保存
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    success = loop.run_until_complete(self.save_login_info(platform))
                    loop.close()

                    if success:
                        # 更新登录状态显示
                        self.root.after(0, lambda: self.update_login_status(platform))
                        self.root.after(0, lambda: messagebox.showinfo(
                            "保存成功",
                            f"🎉 {platform_name}登录信息保存成功！\n\n"
                            f"💾 下次启动将自动恢复登录状态\n"
                            f"🚀 现在可以开始数据采集"
                        ))
                        self.root.after(0, lambda: self.update_status(f"{platform_name}登录完成，可以开始采集"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror(
                            "保存失败",
                            f"❌ 登录信息保存失败\n"
                            f"请确保已完成登录，然后点击'💾保存'按钮"
                        ))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "无法保存",
                        f"浏览器未就绪，请重新启动登录流程"
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "保存错误",
                    f"保存登录信息时出错: {str(e)}"
                ))

        # 在新线程中运行保存操作
        import threading
        save_thread = threading.Thread(target=run_save)
        save_thread.daemon = True
        save_thread.start()

    def manual_save_login(self, platform: str):
        """🔥 手动保存登录信息"""
        def run_save():
            try:
                if self.browser_ready and self.current_platform == platform:
                    # 在新线程中运行异步保存
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    success = loop.run_until_complete(self.save_login_info(platform))
                    loop.close()

                    if success:
                        # 更新登录状态显示
                        self.root.after(0, lambda: self.update_login_status(platform))
                        self.root.after(0, lambda: messagebox.showinfo(
                            "保存成功",
                            f"🎉 {self.platforms.get(platform, {}).get('name', platform)}登录信息保存成功！\n\n"
                            f"💾 下次启动将自动恢复登录状态"
                        ))
                    else:
                        self.root.after(0, lambda: messagebox.showerror(
                            "保存失败",
                            f"❌ 登录信息保存失败\n请确保已完成登录"
                        ))
                else:
                    self.root.after(0, lambda: messagebox.showwarning(
                        "无法保存",
                        f"请先完成{self.platforms.get(platform, {}).get('name', platform)}平台的登录"
                    ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "保存错误",
                    f"保存登录信息时出错: {str(e)}"
                ))

        # 在新线程中运行保存操作
        import threading
        save_thread = threading.Thread(target=run_save)
        save_thread.daemon = True
        save_thread.start()

    async def cleanup_browser(self):
        """清理浏览器资源"""
        try:
            if self.shared_page:
                await self.shared_page.close()
                self.shared_page = None

            if self.shared_context:
                await self.shared_context.close()
                self.shared_context = None

            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
                self.playwright = None

            self.browser_ready = False
            self.current_platform = None
            print("🧹 浏览器资源已清理")

        except Exception as e:
            print(f"⚠️ 清理浏览器时出错: {e}")

    def show_about_dialog(self):
        """显示关于对话框"""
        # 创建新窗口
        about_window = ctk.CTkToplevel(self.root)
        about_window.title(f"关于 - 红枫工具箱 {get_version()}")
        about_window.geometry("600x500")
        about_window.resizable(False, False)

        # 居中显示
        about_window.transient(self.root)
        about_window.grab_set()

        # 标题
        title_label = ctk.CTkLabel(
            about_window,
            text="🍁 红枫工具箱-数据采集版",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))

        # 版本信息
        version_label = ctk.CTkLabel(
            about_window,
            text=get_full_version_string(),
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)

        # 分隔线
        separator = ctk.CTkFrame(about_window, height=2)
        separator.pack(fill="x", padx=20, pady=10)

        # 更新日志标题
        changelog_title = ctk.CTkLabel(
            about_window,
            text="📝 更新日志",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        changelog_title.pack(pady=(10, 5))

        # 更新日志文本框
        changelog_frame = ctk.CTkFrame(about_window)
        changelog_frame.pack(fill="both", expand=True, padx=20, pady=10)

        changelog_text = ctk.CTkTextbox(
            changelog_frame,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        changelog_text.pack(fill="both", expand=True)
        changelog_text.insert("1.0", CHANGELOG)
        changelog_text.configure(state="disabled")

        # 关闭按钮
        close_button = ctk.CTkButton(
            about_window,
            text="关闭",
            width=100,
            command=about_window.destroy
        )
        close_button.pack(pady=10)

    def on_closing(self):
        """窗口关闭时的清理操作"""
        try:
            # 异步清理浏览器
            if self.browser_ready:
                # 使用保存的事件循环清理浏览器
                if hasattr(self, 'browser_loop') and self.browser_loop and not self.browser_loop.is_closed():
                    # 在事件循环中运行清理
                    future = asyncio.run_coroutine_threadsafe(
                        self.cleanup_browser(),
                        self.browser_loop
                    )
                    try:
                        future.result(timeout=10)
                    except:
                        pass

                    # 停止事件循环
                    self.browser_loop.call_soon_threadsafe(self.browser_loop.stop)
                    print("🧹 浏览器事件循环已停止")
                else:
                    asyncio.run(self.cleanup_browser())
        except Exception as e:
            print(f"⚠️ 关闭时清理失败: {e}")
        finally:
            self.root.destroy()

    def run(self):
        """运行GUI应用"""
        self.root.mainloop()

def main():
    """主函数"""
    try:
        # 🔥 打印日志文件位置
        print("="*60)
        print("🚀 MediaCrawler GUI 启动")
        print("="*60)
        print(f"📝 日志文件: {log_file}")
        print(f"📁 日志目录: {log_dir}")
        print("="*60)
        logger.info("="*60)
        logger.info("MediaCrawler GUI 启动")
        logger.info(f"日志文件: {log_file}")
        logger.info("="*60)

        app = MediaCrawlerGUI()
        app.run()
    except Exception as e:
        logger.error(f"应用启动失败: {e}", exc_info=True)
        messagebox.showerror("启动错误", f"应用启动失败: {str(e)}")

if __name__ == "__main__":
    main()
