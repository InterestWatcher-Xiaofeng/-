#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
便携式浏览器管理模块
用于管理打包在软件文件夹中的Playwright浏览器驱动
"""

import os
import sys
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_exe_dir() -> Path:
    """
    获取exe所在目录
    
    Returns:
        Path: exe所在目录的路径
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的exe
        # sys.executable 是 红枫工具箱.exe 的路径
        exe_path = Path(sys.executable)
        return exe_path.parent
    else:
        # 开发环境
        return Path(__file__).parent.parent


def get_portable_browser_path() -> Optional[Path]:
    """
    获取便携式浏览器的可执行文件路径

    Returns:
        Optional[Path]: 浏览器可执行文件路径，如果不存在则返回None
    """
    exe_dir = get_exe_dir()

    # 🔥 PyInstaller打包后，数据文件在_internal文件夹中
    # 尝试两个可能的路径：
    # 1. 打包后: 红枫工具箱/_internal/playwright_browsers/chromium-1124/chrome-win/chrome.exe
    # 2. 开发环境: 红枫工具箱/playwright_browsers/chromium-1124/chrome-win/chrome.exe

    possible_paths = [
        exe_dir / "_internal" / "playwright_browsers" / "chromium-1124" / "chrome-win" / "chrome.exe",  # 打包后
        exe_dir / "playwright_browsers" / "chromium-1124" / "chrome-win" / "chrome.exe",  # 开发环境
    ]

    for browser_path in possible_paths:
        if browser_path.exists():
            logger.info(f"✅ 找到便携式浏览器: {browser_path}")
            return browser_path

    logger.warning(f"⚠️ 便携式浏览器不存在，已检查路径:")
    for path in possible_paths:
        logger.warning(f"   - {path}")
    return None


def get_browser_executable_path() -> Optional[str]:
    """
    获取浏览器可执行文件路径（字符串格式）
    
    优先使用便携式浏览器，如果不存在则返回None（使用系统默认）
    
    Returns:
        Optional[str]: 浏览器可执行文件路径，如果使用系统默认则返回None
    """
    portable_path = get_portable_browser_path()
    
    if portable_path:
        return str(portable_path)
    else:
        # 返回None，让Playwright使用系统默认路径
        # C:\Users\用户名\AppData\Local\ms-playwright\chromium-1124\chrome-win\chrome.exe
        logger.info("ℹ️ 使用系统默认浏览器路径")
        return None


def check_browser_available() -> tuple[bool, str]:
    """
    检查浏览器是否可用
    
    Returns:
        tuple[bool, str]: (是否可用, 状态消息)
    """
    # 1. 检查便携式浏览器
    portable_path = get_portable_browser_path()
    if portable_path:
        return True, f"✅ 便携式浏览器可用: {portable_path}"
    
    # 2. 检查系统默认浏览器
    # 尝试从环境变量或默认路径查找
    user_home = Path.home()
    system_browser_path = user_home / "AppData" / "Local" / "ms-playwright" / "chromium-1124" / "chrome-win" / "chrome.exe"
    
    if system_browser_path.exists():
        return True, f"✅ 系统浏览器可用: {system_browser_path}"
    
    # 3. 都不存在
    return False, "❌ 浏览器驱动不存在，需要安装Playwright浏览器"


def get_browser_driver_info() -> dict:
    """
    获取浏览器驱动信息
    
    Returns:
        dict: 浏览器驱动信息
    """
    portable_path = get_portable_browser_path()
    available, message = check_browser_available()
    
    info = {
        "available": available,
        "message": message,
        "portable_path": str(portable_path) if portable_path else None,
        "exe_dir": str(get_exe_dir()),
        "is_frozen": getattr(sys, 'frozen', False)
    }
    
    return info


def setup_playwright_env():
    """
    设置Playwright环境变量

    如果使用便携式浏览器，设置PLAYWRIGHT_BROWSERS_PATH环境变量
    """
    exe_dir = get_exe_dir()

    # 🔥 尝试两个可能的路径
    possible_dirs = [
        exe_dir / "_internal" / "playwright_browsers",  # 打包后
        exe_dir / "playwright_browsers",  # 开发环境
    ]

    for browsers_dir in possible_dirs:
        if browsers_dir.exists():
            # 设置环境变量，让Playwright使用便携式浏览器
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_dir)
            logger.info(f"✅ 设置PLAYWRIGHT_BROWSERS_PATH: {browsers_dir}")
            return

    logger.info("ℹ️ 未找到便携式浏览器目录，使用系统默认路径")


# 在模块导入时自动设置环境变量
setup_playwright_env()


if __name__ == "__main__":
    # 测试代码
    print("="*60)
    print("🔍 浏览器驱动检测")
    print("="*60)
    
    info = get_browser_driver_info()
    print(f"可用状态: {info['available']}")
    print(f"状态消息: {info['message']}")
    print(f"便携式路径: {info['portable_path']}")
    print(f"exe目录: {info['exe_dir']}")
    print(f"是否打包: {info['is_frozen']}")
    print("="*60)
    
    executable_path = get_browser_executable_path()
    print(f"浏览器可执行文件路径: {executable_path}")
    print("="*60)

