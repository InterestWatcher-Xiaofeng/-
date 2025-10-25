@echo off
chcp 65001 >nul
echo ========================================
echo 红枫工具箱 - EXE打包脚本 V1.0.0
echo ========================================
echo.

echo [1/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✓ 清理完成
echo.

echo [2/4] 检查依赖...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ✗ 未安装 PyInstaller
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)
echo ✓ 依赖检查完成
echo.

echo [3/4] 开始打包...
pyinstaller MediaCrawler-GUI.spec --clean
if errorlevel 1 (
    echo ✗ 打包失败！
    pause
    exit /b 1
)
echo ✓ 打包完成
echo.

echo [4/4] 复制必要文件到dist目录...
if exist dist\红枫工具箱.exe (
    copy /y 使用说明.md dist\ >nul 2>&1
    echo ✓ 文件复制完成
    echo.
    echo ========================================
    echo 🎉 打包成功！
    echo ========================================
    echo.
    echo 可执行文件位置: dist\红枫工具箱.exe
    echo 使用说明: dist\使用说明.md
    echo.
    echo 提示: 首次运行需要安装 Playwright 浏览器
    echo       软件会自动提示安装
    echo.
) else (
    echo ✗ 未找到生成的exe文件
)

pause

