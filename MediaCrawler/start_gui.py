#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MediaCrawler GUI 启动器
跨平台启动脚本，自动检查环境并启动GUI应用
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("\n" + "="*50)
    print("   🕷️ MediaCrawler GUI 启动器")
    print("="*50)
    print()

def check_python_version():
    """检查Python版本"""
    print("📋 正在检查Python版本...")
    
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        print("📥 请从 https://www.python.org/downloads/ 下载最新版本")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_required_packages():
    """检查必需的包"""
    print("📦 正在检查必需的包...")
    
    required_packages = [
        "customtkinter",
        "pillow",
        "playwright",
        "httpx",
        "asyncio"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "pillow":
                import PIL
            elif package == "customtkinter":
                import customtkinter
            elif package == "playwright":
                import playwright
            elif package == "httpx":
                import httpx
            elif package == "asyncio":
                import asyncio
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下包: {', '.join(missing_packages)}")
        print("📥 正在尝试自动安装...")
        
        try:
            # 尝试使用uv安装
            subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, 
                         check=True, capture_output=True)
            print("✅ 包安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 自动安装失败，请手动安装:")
            print(f"   pip install {' '.join(missing_packages)}")
            return False
    
    print("✅ 所有必需包已安装")
    return True

def check_gui_file():
    """检查GUI文件是否存在"""
    print("📄 正在检查GUI文件...")
    
    gui_file = Path(__file__).parent / "gui_app.py"
    
    if not gui_file.exists():
        print("❌ 未找到GUI应用文件 gui_app.py")
        print("   请确保文件存在于正确位置")
        return False
    
    print("✅ GUI文件检查通过")
    return True

def check_mediacrawler_files():
    """检查MediaCrawler核心文件"""
    print("🕷️ 正在检查MediaCrawler核心文件...")
    
    required_files = [
        "main.py",
        "config/__init__.py",
        "config/base_config.py",
        "cmd_arg/arg.py"
    ]
    
    missing_files = []
    base_path = Path(__file__).parent
    
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺少以下核心文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n请确保MediaCrawler项目文件完整")
        return False
    
    print("✅ MediaCrawler核心文件检查通过")
    return True

def start_gui():
    """启动GUI应用"""
    print("🚀 正在启动MediaCrawler GUI...")
    print()
    
    try:
        # 设置工作目录
        os.chdir(Path(__file__).parent)
        
        # 启动GUI应用
        from gui_app import main
        main()
        
        print("\n✅ GUI已正常关闭")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请检查依赖包是否正确安装")
        return False
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请检查错误信息并重试")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 环境检查
    checks = [
        check_python_version,
        check_required_packages,
        check_gui_file,
        check_mediacrawler_files
    ]
    
    for check in checks:
        if not check():
            print("\n❌ 环境检查失败，无法启动GUI")
            input("\n按回车键退出...")
            sys.exit(1)
        print()
    
    # 启动GUI
    if start_gui():
        print("🎉 感谢使用MediaCrawler!")
    else:
        print("\n💡 如果问题持续存在，请:")
        print("   1. 检查Python环境是否正确配置")
        print("   2. 确保所有依赖包已正确安装")
        print("   3. 查看项目文档获取更多帮助")
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 意外错误: {e}")
        input("\n按回车键退出...")
        sys.exit(1)
