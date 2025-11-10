@echo off
chcp 65001 >nul
echo ========================================
echo 红枫工具箱 - 打包结果验证工具
echo ========================================
echo.

echo [1/5] 检查打包目录是否存在...
if exist "dist\红枫工具箱" (
    echo ✅ 打包目录存在
) else (
    echo ❌ 打包目录不存在
    echo    请先运行打包命令: pyinstaller MediaCrawler-GUI.spec
    pause
    exit /b 1
)
echo.

echo [2/5] 检查exe文件...
if exist "dist\红枫工具箱\红枫工具箱.exe" (
    echo ✅ exe文件存在
    for %%A in ("dist\红枫工具箱\红枫工具箱.exe") do echo    大小: %%~zA 字节
) else (
    echo ❌ exe文件不存在
    pause
    exit /b 1
)
echo.

echo [3/5] 检查_internal目录...
if exist "dist\红枫工具箱\_internal" (
    echo ✅ _internal目录存在
) else (
    echo ❌ _internal目录不存在
    pause
    exit /b 1
)
echo.

echo [4/5] 检查浏览器目录...
if exist "dist\红枫工具箱\_internal\playwright_browsers" (
    echo ✅ 浏览器目录存在
) else (
    echo ❌ 浏览器目录不存在
    echo    这是致命问题! 软件将无法在新设备上运行
    pause
    exit /b 1
)
echo.

echo [5/5] 检查chrome.exe...
if exist "dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ✅ chrome.exe存在
    for %%A in ("dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe") do echo    大小: %%~zA 字节
) else (
    echo ❌ chrome.exe不存在
    echo    这是致命问题! 软件将无法在新设备上运行
    pause
    exit /b 1
)
echo.

echo ========================================
echo ✅ 所有检查通过!
echo ========================================
echo.
echo 打包结果可以在新设备上运行
echo.
echo 发布步骤:
echo 1. 将整个 "dist\红枫工具箱" 文件夹打包成zip
echo 2. 发送给用户
echo 3. 用户解压后直接运行 红枫工具箱.exe
echo.
echo 注意事项:
echo - 必须完整解压所有文件
echo - 不要只复制exe文件
echo - _internal文件夹必须和exe在同一目录
echo.
pause

