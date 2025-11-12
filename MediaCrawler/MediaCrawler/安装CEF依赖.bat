@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 红枫工具箱 - CEF浏览器依赖安装
echo ========================================
echo.

echo [1/3] 正在安装 cefpython3...
pip install cefpython3==66.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

if %errorlevel% neq 0 (
    echo.
    echo ❌ 安装失败！尝试使用官方源...
    pip install cefpython3==66.1
)

echo.
echo [2/3] 验证安装...
python -c "from cefpython3 import cefpython as cef; print('✅ CEF版本:', cef.GetVersion())"

if %errorlevel% neq 0 (
    echo.
    echo ❌ 验证失败！请检查Python环境
    pause
    exit /b 1
)

echo.
echo [3/3] 安装完成！
echo.
echo ========================================
echo ✅ CEF浏览器依赖安装成功！
echo ========================================
echo.
echo 现在可以运行 start_gui.py 启动程序
echo.
pause

