@echo off
chcp 65001 >nul
echo ========================================
echo 红枫工具箱 - 重新打包脚本
echo ========================================
echo.

echo [步骤1/5] 清理旧的打包文件...
if exist "build" (
    echo 删除 build 目录...
    rmdir /s /q build
)
if exist "dist" (
    echo 删除 dist 目录...
    rmdir /s /q dist
)
echo ✅ 清理完成
echo.

echo [步骤2/5] 检查浏览器文件是否存在...
if exist "playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ✅ 浏览器文件存在
    for %%A in ("playwright_browsers\chromium-1124\chrome-win\chrome.exe") do echo    大小: %%~zA 字节
) else (
    echo ❌ 浏览器文件不存在!
    echo.
    echo 请先安装Playwright浏览器:
    echo    playwright install chromium
    echo.
    pause
    exit /b 1
)
echo.

echo [步骤3/5] 开始打包...
echo 这可能需要几分钟,请耐心等待...
echo.
pyinstaller MediaCrawler-GUI.spec
echo.

if %errorlevel% neq 0 (
    echo ❌ 打包失败!
    echo 请检查错误信息
    pause
    exit /b 1
)

echo ✅ 打包完成
echo.

echo [步骤4/5] 验证打包结果...
echo.

if not exist "dist\红枫工具箱\红枫工具箱.exe" (
    echo ❌ exe文件不存在
    pause
    exit /b 1
)

if not exist "dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ❌ 浏览器文件未打包
    echo    这是致命问题!
    pause
    exit /b 1
)

echo ✅ 关键文件验证通过
echo.

echo [步骤5/5] 生成打包报告...
echo.
echo ========================================
echo 打包结果报告
echo ========================================
echo.
echo 📁 输出目录: dist\红枫工具箱\
echo.
echo 📄 主程序:
for %%A in ("dist\红枫工具箱\红枫工具箱.exe") do echo    红枫工具箱.exe - %%~zA 字节
echo.
echo 📁 依赖文件:
echo    _internal\ - 包含所有依赖库和浏览器
echo.
echo 🌐 浏览器:
for %%A in ("dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe") do echo    chrome.exe - %%~zA 字节
echo.
echo ========================================
echo ✅ 打包成功!
echo ========================================
echo.
echo 下一步:
echo 1. 测试运行: 双击 dist\红枫工具箱\红枫工具箱.exe
echo 2. 如果测试通过,将整个 "dist\红枫工具箱" 文件夹打包成zip
echo 3. 发送给用户使用
echo.
echo 重要提醒:
echo - 用户必须完整解压所有文件
echo - _internal文件夹和exe必须在同一目录
echo - 不要只发送exe文件
echo.
pause

