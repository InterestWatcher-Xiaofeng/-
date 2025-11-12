@echo off
chcp 65001 >nul
echo ========================================
echo   红枫工具箱 - 稳定版打包脚本 V2.1
echo   优化配置,确保其他设备稳定运行
echo ========================================
echo.

:: 设置颜色
color 0A

:: 检查Python环境
echo [1/8] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)
python --version
echo ✅ Python环境正常
echo.

:: 检查PyInstaller
echo [2/8] 检查PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未安装PyInstaller
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller已安装
echo.

:: 检查关键依赖
echo [3/8] 检查关键依赖...
python -c "import customtkinter, playwright, asyncio" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 缺少关键依赖
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)
echo ✅ 关键依赖已安装
echo.

:: 检查浏览器驱动
echo [4/8] 检查Playwright浏览器驱动...
if not exist "playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ❌ 错误: 未找到Playwright浏览器驱动
    echo 请先运行: playwright install chromium
    pause
    exit /b 1
)
echo ✅ 浏览器驱动已就绪
echo.

:: 清理旧的打包文件
echo [5/8] 清理旧的打包文件...
if exist "build" (
    echo 删除 build 目录...
    rmdir /s /q build
)
if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q dist
)
if exist "红枫工具箱.spec" (
    echo 删除旧的 spec 文件...
    del /q 红枫工具箱.spec
)
echo ✅ 清理完成
echo.

:: 开始打包
echo [6/8] 开始打包...
echo 使用配置文件: MediaCrawler-GUI.spec
echo 打包模式: --onedir (文件夹模式,启动更快)
echo.
echo ⏳ 打包中,请耐心等待 (预计3-5分钟)...
echo.

pyinstaller MediaCrawler-GUI.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ❌ 打包失败!
    echo 请检查错误信息
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成!
echo.

:: 验证打包结果
echo [7/8] 验证打包结果...
if not exist "dist\红枫工具箱\红枫工具箱.exe" (
    echo ❌ 错误: 未找到打包后的exe文件
    pause
    exit /b 1
)

if not exist "dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ❌ 错误: 浏览器驱动未正确打包
    pause
    exit /b 1
)

echo ✅ exe文件: dist\红枫工具箱\红枫工具箱.exe
echo ✅ 浏览器驱动: 已打包
echo.

:: 计算打包大小
echo [8/8] 计算打包大小...
for /f "tokens=3" %%a in ('dir "dist\红枫工具箱" /s /-c ^| find "个文件"') do set size=%%a
echo 📦 打包大小: %size% 字节
echo.

:: 创建使用说明
echo 创建使用说明...
(
echo ========================================
echo   红枫工具箱 V2.1 - 使用说明
echo ========================================
echo.
echo 📁 文件说明:
echo   红枫工具箱.exe - 主程序
echo   _internal\ - 依赖文件夹 ^(必须保留^)
echo.
echo 🚀 使用方法:
echo   1. 双击 红枫工具箱.exe 启动程序
echo   2. 首次运行会进行环境检查
echo   3. 选择平台和采集模式
echo   4. 点击"开始采集"
echo.
echo ⚠️ 注意事项:
echo   1. 不要删除 _internal 文件夹
echo   2. 不要移动 exe 文件到其他位置
echo   3. 解压到英文路径^(无中文、无空格^)
echo   4. 关闭杀毒软件后再运行
echo.
echo 🐛 遇到问题:
echo   1. 查看 crash_log.txt 错误日志
echo   2. 检查是否完整解压所有文件
echo   3. 检查是否有杀毒软件拦截
echo   4. 联系开发者获取帮助
echo.
echo ========================================
echo   版本: V2.1
echo   打包时间: %date% %time%
echo ========================================
) > "dist\红枫工具箱\使用说明.txt"

echo ✅ 使用说明已创建
echo.

:: 打包完成
echo ========================================
echo   🎉 打包完成!
echo ========================================
echo.
echo 📦 输出目录: dist\红枫工具箱\
echo 📄 主程序: 红枫工具箱.exe
echo 📝 使用说明: 使用说明.txt
echo.
echo 💡 下一步:
echo   1. 测试: 运行 dist\红枫工具箱\红枫工具箱.exe
echo   2. 打包: 将整个 dist\红枫工具箱\ 文件夹压缩为zip
echo   3. 分发: 发送给用户,要求完整解压后使用
echo.
echo ⚠️ 重要提示:
echo   - 必须将整个文件夹打包分发
echo   - 用户必须完整解压所有文件
echo   - 不能只发送exe文件
echo.
pause

