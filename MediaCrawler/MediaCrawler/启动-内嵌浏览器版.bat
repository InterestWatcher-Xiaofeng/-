@echo off
chcp 65001 >nul
echo ========================================
echo 🍁 红枫工具箱 - 内嵌浏览器版
echo ========================================
echo.

echo [1/3] 检查CEF依赖...
python -c "from cefpython3 import cefpython as cef; print('✅ CEF已安装，版本:', cef.GetVersion()['chrome_version'])" 2>nul

if %errorlevel% neq 0 (
    echo.
    echo ❌ CEF未安装！
    echo.
    echo 正在自动安装CEF依赖...
    pip install cefpython3==66.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 自动安装失败！
        echo.
        echo 请手动运行: 安装CEF依赖.bat
        pause
        exit /b 1
    )
)

echo.
echo [2/3] 检查Playwright浏览器...
python -c "import playwright" 2>nul

if %errorlevel% neq 0 (
    echo ❌ Playwright未安装！
    echo 请先运行: pip install -r requirements.txt
    pause
    exit /b 1
)

echo ✅ Playwright已安装

echo.
echo [3/3] 启动程序...
echo.
echo ========================================
echo ✅ 正在启动红枫工具箱...
echo ========================================
echo.

python start_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序启动失败！
    echo.
    echo 请检查:
    echo 1. Python环境是否正确
    echo 2. 依赖是否完整安装
    echo 3. 查看错误日志
    pause
)

