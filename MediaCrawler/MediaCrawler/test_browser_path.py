#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浏览器路径验证脚本
用于检查打包后的exe是否能正确找到浏览器文件
"""

import sys
import os
from pathlib import Path

def print_separator(char="=", length=70):
    """打印分隔线"""
    print(char * length)

def print_section(title):
    """打印章节标题"""
    print_separator()
    print(f"  {title}")
    print_separator()

def check_environment():
    """检查运行环境"""
    print_section("1. 运行环境检查")
    
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        print("✅ 运行环境: EXE打包模式")
        print(f"   EXE路径: {sys.executable}")
    else:
        print("✅ 运行环境: Python开发模式")
        print(f"   脚本路径: {__file__}")
    
    print(f"   Python版本: {sys.version}")
    print(f"   操作系统: {os.name}")
    
    return is_frozen

def check_directories(is_frozen):
    """检查目录结构"""
    print_section("2. 目录结构检查")
    
    if is_frozen:
        exe_dir = Path(sys.executable).parent
        browsers_dir = exe_dir / "_internal" / "playwright_browsers"
    else:
        exe_dir = Path(__file__).parent
        browsers_dir = exe_dir / "playwright_browsers"
    
    print(f"📁 程序目录: {exe_dir}")
    print(f"   存在? {exe_dir.exists()}")
    
    print(f"\n📁 浏览器目录: {browsers_dir}")
    print(f"   存在? {browsers_dir.exists()}")
    
    if browsers_dir.exists():
        # 计算目录大小
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(browsers_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    pass
        
        print(f"   文件数量: {file_count}")
        print(f"   总大小: {total_size / 1024 / 1024:.2f} MB")
    
    return exe_dir, browsers_dir

def check_chromium(browsers_dir):
    """检查Chromium浏览器"""
    print_section("3. Chromium浏览器检查")
    
    if not browsers_dir.exists():
        print("❌ 浏览器目录不存在,无法检查Chromium!")
        return False
    
    # 查找chromium目录
    chromium_dirs = list(browsers_dir.glob("chromium-*"))
    
    if not chromium_dirs:
        print("❌ 未找到chromium目录!")
        print(f"   在 {browsers_dir} 下没有找到 chromium-* 目录")
        return False
    
    print(f"✅ 找到 {len(chromium_dirs)} 个Chromium目录:")
    
    chrome_found = False
    for chromium_dir in chromium_dirs:
        print(f"\n📦 {chromium_dir.name}")
        
        # 检查chrome.exe
        chrome_exe = chromium_dir / "chrome-win" / "chrome.exe"
        
        if chrome_exe.exists():
            print(f"   ✅ chrome.exe 存在")
            print(f"   📍 路径: {chrome_exe}")
            
            try:
                file_size = chrome_exe.stat().st_size
                print(f"   📊 大小: {file_size / 1024 / 1024:.2f} MB")
                
                # 检查文件是否可执行
                if os.access(chrome_exe, os.X_OK):
                    print(f"   ✅ 文件可执行")
                else:
                    print(f"   ⚠️ 文件不可执行(可能需要管理员权限)")
                
                chrome_found = True
            except Exception as e:
                print(f"   ❌ 读取文件信息失败: {e}")
        else:
            print(f"   ❌ chrome.exe 不存在")
            print(f"   📍 期望路径: {chrome_exe}")
    
    return chrome_found

def check_environment_variables():
    """检查环境变量"""
    print_section("4. 环境变量检查")
    
    playwright_browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    playwright_skip_download = os.environ.get("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD")
    
    if playwright_browsers_path:
        print(f"✅ PLAYWRIGHT_BROWSERS_PATH 已设置")
        print(f"   值: {playwright_browsers_path}")
        print(f"   路径存在? {Path(playwright_browsers_path).exists()}")
    else:
        print(f"⚠️ PLAYWRIGHT_BROWSERS_PATH 未设置")
        print(f"   Playwright将使用默认路径")
    
    if playwright_skip_download:
        print(f"\n✅ PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD 已设置")
        print(f"   值: {playwright_skip_download}")
    else:
        print(f"\n⚠️ PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD 未设置")
        print(f"   Playwright可能会尝试下载浏览器")

def generate_report(is_frozen, exe_dir, browsers_dir, chrome_found):
    """生成诊断报告"""
    print_section("5. 诊断报告")
    
    issues = []
    warnings = []
    
    # 检查问题
    if not browsers_dir.exists():
        issues.append("浏览器目录不存在")
    
    if not chrome_found:
        issues.append("未找到chrome.exe")
    
    if not os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        warnings.append("PLAYWRIGHT_BROWSERS_PATH环境变量未设置")
    
    if not os.environ.get("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"):
        warnings.append("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD环境变量未设置")
    
    # 显示结果
    if not issues and not warnings:
        print("✅ 所有检查通过!")
        print("   浏览器文件完整,应该可以正常运行")
    else:
        if issues:
            print("❌ 发现以下问题:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        if warnings:
            print("\n⚠️ 发现以下警告:")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
    
    # 提供建议
    print("\n💡 建议:")
    if issues:
        print("   1. 重新下载完整安装包")
        print("   2. 使用WinRAR/7-Zip完整解压所有文件")
        print("   3. 确保解压到英文路径(无中文、无空格)")
        print("   4. 不要移动或删除任何文件")
    else:
        print("   1. 如果仍无法运行,请检查杀毒软件是否拦截")
        print("   2. 尝试右键'以管理员身份运行'")
        print("   3. 查看日志文件获取详细错误信息")

def main():
    """主函数"""
    print("\n")
    print("="*70)
    print("  🔍 红枫工具箱 - 浏览器路径验证工具")
    print("="*70)
    print()
    
    try:
        # 1. 检查运行环境
        is_frozen = check_environment()
        print()
        
        # 2. 检查目录结构
        exe_dir, browsers_dir = check_directories(is_frozen)
        print()
        
        # 3. 检查Chromium浏览器
        chrome_found = check_chromium(browsers_dir)
        print()
        
        # 4. 检查环境变量
        check_environment_variables()
        print()
        
        # 5. 生成诊断报告
        generate_report(is_frozen, exe_dir, browsers_dir, chrome_found)
        print()
        
    except Exception as e:
        print(f"\n❌ 检查过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    print_separator()
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    main()

