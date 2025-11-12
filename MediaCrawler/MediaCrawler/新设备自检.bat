@echo off
chcp 65001 >nul
echo ========================================
echo   红枫工具箱 - 新设备自检工具 V2.1
echo   检查程序是否能在当前设备运行
echo ========================================
echo.

:: 设置颜色
color 0E

set ERROR_COUNT=0

:: 检查1: 操作系统
echo [1/8] 检查操作系统...
ver | find "Windows" >nul
if errorlevel 1 (
    echo ❌ 错误: 不支持的操作系统
    set /a ERROR_COUNT+=1
) else (
    ver
    echo ✅ 操作系统: Windows
)
echo.

:: 检查2: exe文件
echo [2/8] 检查主程序文件...
if exist "红枫工具箱.exe" (
    echo ✅ 找到: 红枫工具箱.exe
    for %%A in ("红枫工具箱.exe") do echo    大小: %%~zA 字节
) else (
    echo ❌ 错误: 未找到 红枫工具箱.exe
    set /a ERROR_COUNT+=1
)
echo.

:: 检查3: _internal文件夹
echo [3/8] 检查依赖文件夹...
if exist "_internal" (
    echo ✅ 找到: _internal 文件夹
    for /f %%A in ('dir /a /s /b "_internal" ^| find /c /v ""') do echo    文件数: %%A
) else (
    echo ❌ 错误: 未找到 _internal 文件夹
    echo    这是最常见的问题!
    echo    解决方法: 重新解压完整的压缩包
    set /a ERROR_COUNT+=1
)
echo.

:: 检查4: 浏览器驱动
echo [4/8] 检查浏览器驱动...
if exist "_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ✅ 找到: Chromium浏览器驱动
    for %%A in ("_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe") do echo    大小: %%~zA 字节
) else (
    echo ❌ 错误: 未找到浏览器驱动
    echo    路径: _internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe
    echo    这会导致采集功能无法使用!
    set /a ERROR_COUNT+=1
)
echo.

:: 检查5: 路径中的中文和空格
echo [5/8] 检查安装路径...
set CURRENT_PATH=%CD%
echo 当前路径: %CURRENT_PATH%

echo %CURRENT_PATH% | findstr /R /C:"[一-龥]" >nul
if not errorlevel 1 (
    echo ⚠️ 警告: 路径包含中文字符
    echo    建议: 解压到纯英文路径
    echo    例如: C:\RedMaple\
    set /a ERROR_COUNT+=1
) else (
    echo ✅ 路径不包含中文
)

echo %CURRENT_PATH% | findstr /C:" " >nul
if not errorlevel 1 (
    echo ⚠️ 警告: 路径包含空格
    echo    建议: 解压到无空格路径
    echo    例如: C:\RedMaple\
    set /a ERROR_COUNT+=1
) else (
    echo ✅ 路径不包含空格
)
echo.

:: 检查6: 磁盘空间
echo [6/8] 检查磁盘空间...
for /f "tokens=3" %%a in ('dir /-c ^| find "可用字节"') do set FREE_SPACE=%%a
echo 可用空间: %FREE_SPACE% 字节
if %FREE_SPACE% LSS 1073741824 (
    echo ⚠️ 警告: 磁盘空间不足 1GB
    echo    建议: 至少保留 2GB 可用空间
) else (
    echo ✅ 磁盘空间充足
)
echo.

:: 检查7: 杀毒软件
echo [7/8] 检查杀毒软件...
echo ⚠️ 注意: 某些杀毒软件可能会误报或拦截
echo.
echo 常见杀毒软件:
echo   - Windows Defender
echo   - 360安全卫士
echo   - 腾讯电脑管家
echo   - 火绒安全
echo.
echo 建议: 将程序添加到白名单或临时关闭杀毒软件
echo.

:: 检查8: 文件完整性
echo [8/8] 检查文件完整性...
set MISSING_FILES=0

if not exist "_internal\customtkinter" (
    echo ❌ 缺少: customtkinter 库
    set /a MISSING_FILES+=1
)

if not exist "_internal\playwright" (
    echo ❌ 缺少: playwright 库
    set /a MISSING_FILES+=1
)

if %MISSING_FILES% EQU 0 (
    echo ✅ 关键文件完整
) else (
    echo ❌ 错误: 缺少 %MISSING_FILES% 个关键文件
    echo    解决方法: 重新下载并完整解压
    set /a ERROR_COUNT+=1
)
echo.

:: 总结
echo ========================================
echo   自检结果
echo ========================================
echo.

if %ERROR_COUNT% EQU 0 (
    echo ✅ 所有检查通过!
    echo.
    echo 💡 下一步:
    echo    1. 双击 红枫工具箱.exe 启动程序
    echo    2. 如果启动失败,查看 crash_log.txt
    echo    3. 如果有问题,联系开发者
    echo.
    color 0A
) else (
    echo ❌ 发现 %ERROR_COUNT% 个问题!
    echo.
    echo 🔧 解决方法:
    echo    1. 重新下载完整的压缩包
    echo    2. 使用WinRAR或7-Zip完整解压
    echo    3. 解压到英文路径 ^(例如: C:\RedMaple\^)
    echo    4. 关闭杀毒软件后重试
    echo    5. 确保解压时没有跳过任何文件
    echo.
    color 0C
)

echo ========================================
echo.
pause

