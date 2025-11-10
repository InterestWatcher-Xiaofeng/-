#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawler GUI 启动器
跨平台启动脚本，自动检查环境并启动GUI应用
"""

import sys
import os
from pathlib import Path

# 🔥🔥🔥 最关键的修复：在导入任何模块之前，立即设置Playwright环境变量！
# 这必须是整个程序最先执行的代码，否则Playwright会从网络下载浏览器

# 立即检测运行环境并设置浏览器路径
if getattr(sys, 'frozen', False):
    # PyInstaller打包后
    _exe_dir = Path(sys.executable).parent
    _browsers_dir = _exe_dir / "_internal" / "playwright_browsers"
else:
    # 开发环境
    _exe_dir = Path(__file__).parent
    _browsers_dir = _exe_dir / "playwright_browsers"

# 🔥 强制设置环境变量（不使用 setdefault，直接覆盖）
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_browsers_dir)
os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "1"

print(f"🔧 环境变量已设置: PLAYWRIGHT_BROWSERS_PATH = {os.environ['PLAYWRIGHT_BROWSERS_PATH']}")
print(f"🔧 环境变量已设置: PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = {os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD']}")

# 🔥 严格验证浏览器是否存在
if not _browsers_dir.exists():
    error_msg = (
        f"❌ 致命错误: 浏览器目录不存在!\n\n"
        f"期望路径: {_browsers_dir}\n\n"
        f"解决方法:\n"
        f"1. 重新下载完整安装包\n"
        f"2. 完整解压所有文件(不要只解压exe)\n"
        f"3. 确保 _internal 文件夹和 exe 在同一目录\n"
        f"4. 解压到英文路径(无中文、无空格)"
    )
    print(error_msg)

    # 显示错误对话框
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("浏览器文件缺失", error_msg)
        root.destroy()
    except:
        pass

    sys.exit(1)

# 验证 chrome.exe 是否存在
_chrome_found = False
_chrome_path = None
for _sub in _browsers_dir.glob("chromium-*"):
    _chrome_exe = _sub / "chrome-win" / "chrome.exe"
    if _chrome_exe.exists():
        _chrome_found = True
        _chrome_path = _chrome_exe
        print(f"✅ 找到便携式浏览器: {_chrome_exe}")
        break

if not _chrome_found:
    error_msg = (
        f"❌ 致命错误: 浏览器文件不完整!\n\n"
        f"浏览器目录: {_browsers_dir}\n"
        f"未找到: chrome.exe\n\n"
        f"解决方法:\n"
        f"1. 重新下载完整安装包\n"
        f"2. 使用WinRAR/7-Zip完整解压\n"
        f"3. 关闭杀毒软件后重试\n"
        f"4. 确保解压时没有跳过任何文件\n"
        f"5. 检查 _internal\\playwright_browsers 文件夹是否完整"
    )
    print(error_msg)

    # 显示错误对话框
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("浏览器文件损坏", error_msg)
        root.destroy()
    except:
        pass

    sys.exit(1)

print(f"✅ 浏览器验证通过: {_chrome_path}")

# 🔥 关键修复：在文件顶部显式导入gui_app，确保PyInstaller能检测到
# 这个导入必须在这里，即使后面函数内部也有导入
# 否则PyInstaller无法检测到gui_app模块的依赖
import gui_app  # noqa: F401 (告诉linter这个导入是必需的)

def is_frozen():
    """检测是否为打包后的exe"""
    return getattr(sys, 'frozen', False)

def setup_environment():
    """设置运行环境（必须在导入任何第三方库之前调用）"""
    if is_frozen():
        # exe模式：使用exe所在目录
        base_path = Path(sys.executable).parent

        # 🔥 关键修复：设置工作目录到exe所在目录
        # 这样可以避免numpy从源码目录导入的问题
        os.chdir(base_path)

        # 🔥 确保_internal目录在sys.path中（PyInstaller打包的依赖位置）
        internal_path = base_path / '_internal'
        if internal_path.exists() and str(internal_path) not in sys.path:
            sys.path.insert(0, str(internal_path))
    else:
        # 开发模式：使用脚本所在目录
        base_path = Path(__file__).parent
        os.chdir(base_path)

    return base_path

def safe_print(*args, **kwargs):
    """安全的打印函数，在exe模式下不会报错"""
    try:
        print(*args, **kwargs)
    except:
        pass

def show_error_dialog(title, message):
    """显示错误对话框（仅在GUI可用时）"""
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # 如果GUI不可用，静默失败
        pass

def start_gui():
    """启动GUI应用"""
    try:
        # 启动GUI应用
        from gui_app import main
        main()

        return True

    except ImportError as e:
        error_msg = f"导入错误: {e}\n\n请检查依赖包是否正确安装"
        safe_print(f"❌ {error_msg}")
        show_error_dialog("导入错误", error_msg)
        return False

    except Exception as e:
        error_msg = f"启动失败: {e}\n\n请检查错误信息并重试"
        safe_print(f"❌ {error_msg}")
        show_error_dialog("启动失败", error_msg)
        return False

def main():
    """主函数"""
    # 🔥 第一步：设置环境（必须在导入任何第三方库之前）
    setup_environment()

    # 在开发模式下显示启动信息
    if not is_frozen():
        safe_print("\n" + "="*50)
        safe_print("   🕷️ MediaCrawler GUI 启动器")
        safe_print("="*50)
        safe_print()

    # 直接启动GUI（exe模式下所有依赖已打包）
    try:
        start_gui()
    except Exception as e:
        error_msg = f"意外错误: {e}"
        safe_print(f"\n❌ {error_msg}")
        show_error_dialog("意外错误", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print("\n\n👋 用户取消操作")
    except Exception as e:
        safe_print(f"\n❌ 意外错误: {e}")
        # 不使用input()，直接退出
        sys.exit(1)
