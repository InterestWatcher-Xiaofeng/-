@echo off
chcp 65001 >nul
title MediaCrawler GUI 启动器

echo.
echo ========================================
echo   🕷️ MediaCrawler GUI 启动器
echo ========================================
echo.

echo 📋 正在检查环境...

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python环境，请先安装Python
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 检查uv工具
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到uv工具，请先安装uv
    echo 📥 安装命令: pip install uv
    pause
    exit /b 1
)

echo ✅ uv工具检查通过

REM 检查依赖包
echo 📦 正在检查依赖包...
uv sync >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 依赖包同步失败，尝试手动安装...
    pip install customtkinter pillow
)

echo ✅ 依赖包检查完成

REM 检查GUI文件
if not exist "gui_app.py" (
    echo ❌ 未找到GUI应用文件 gui_app.py
    pause
    exit /b 1
)

echo ✅ GUI文件检查通过

echo.
echo 🚀 正在启动MediaCrawler GUI...
echo.

REM 启动GUI应用
python gui_app.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ GUI启动失败，错误代码: %errorlevel%
    echo 💡 请检查错误信息并重试
    pause
) else (
    echo.
    echo ✅ GUI已正常关闭
)

pause
