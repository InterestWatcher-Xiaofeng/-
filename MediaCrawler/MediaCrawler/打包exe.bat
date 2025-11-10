@echo off
chcp 65001 >nul
echo ========================================
echo 红枫工具箱 - EXE打包脚本 V1.2.5
echo ========================================
echo.

echo [1/6] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "红枫工具箱-发布版" rmdir /s /q "红枫工具箱-发布版"
echo ✓ 清理完成
echo.

echo [2/6] 检查依赖...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ✗ 未安装 PyInstaller
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)
echo ✓ 依赖检查完成
echo.

echo [3/6] 开始打包...
pyinstaller MediaCrawler-GUI.spec --clean
if errorlevel 1 (
    echo ✗ 打包失败！
    pause
    exit /b 1
)
echo ✓ 打包完成
echo.

echo [4/6] 创建发布目录结构...
mkdir "红枫工具箱-发布版" 2>nul
mkdir "红枫工具箱-发布版\红枫工具箱" 2>nul
echo ✓ 目录创建完成
echo.

echo [5/6] 复制文件到发布目录...
REM 复制exe及其依赖文件
xcopy /E /I /Y "dist\红枫工具箱\*" "红枫工具箱-发布版\红枫工具箱\" >nul
REM 创建启动批处理文件
echo @echo off > "红枫工具箱-发布版\红枫工具箱\启动红枫工具箱.bat"
echo chcp 65001 ^>nul >> "红枫工具箱-发布版\红枫工具箱\启动红枫工具箱.bat"
echo start "" "红枫工具箱.exe" >> "红枫工具箱-发布版\红枫工具箱\启动红枫工具箱.bat"
REM 复制使用说明
if exist "GUI使用说明.md" copy /y "GUI使用说明.md" "红枫工具箱-发布版\红枫工具箱\使用说明.md" >nul
REM 创建README
echo 🎉 欢迎使用红枫工具箱 - 数据采集版 > "红枫工具箱-发布版\README.txt"
echo. >> "红枫工具箱-发布版\README.txt"
echo 📂 请进入"红枫工具箱"文件夹 >> "红枫工具箱-发布版\README.txt"
echo 🚀 双击"红枫工具箱.exe"或"启动红枫工具箱.bat"即可运行 >> "红枫工具箱-发布版\README.txt"
echo. >> "红枫工具箱-发布版\README.txt"
echo 📖 详细使用说明请查看"使用说明.md" >> "红枫工具箱-发布版\README.txt"
echo. >> "红枫工具箱-发布版\README.txt"
echo ⚠️ 首次运行需要安装Playwright浏览器（约300MB） >> "红枫工具箱-发布版\README.txt"
echo    软件会自动提示安装，请按照提示操作 >> "红枫工具箱-发布版\README.txt"
echo ✓ 文件复制完成
echo.

echo [6/6] 清理临时文件...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
echo ✓ 清理完成
echo.

echo ========================================
echo 🎉 打包成功！
echo ========================================
echo.
echo 📦 发布包位置: 红枫工具箱-发布版\
echo 📂 用户看到的文件夹: 红枫工具箱\
echo 🚀 启动文件: 红枫工具箱.exe
echo 📖 使用说明: 使用说明.md
echo.
echo 💡 提示:
echo    1. 用户打开"红枫工具箱-发布版"文件夹
echo    2. 进入"红枫工具箱"子文件夹
echo    3. 双击"红枫工具箱.exe"即可运行
echo.
echo 📦 可以将"红枫工具箱-发布版"文件夹打包成zip分发
echo.

pause

