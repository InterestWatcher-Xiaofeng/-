@echo off
chcp 65001 >nul
title 红枫工具箱 - 一键打包发布 V2.1
echo.
echo ╔════════════════════════════════════════╗
echo ║  红枫工具箱 - 一键打包发布 V2.1        ║
echo ║  自动完成: 打包 → 测试 → 发布          ║
echo ╚════════════════════════════════════════╝
echo.

:: 设置颜色
color 0B

:: 询问用户是否继续
echo ⚠️ 此脚本将执行以下操作:
echo   1. 清理旧的打包文件
echo   2. 使用PyInstaller打包程序
echo   3. 验证打包结果
echo   4. 创建发布包
echo   5. 生成完整文档
echo.
echo 预计耗时: 5-10分钟
echo.
set /p CONFIRM=是否继续? (Y/N): 
if /i not "%CONFIRM%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)

echo.
echo ========================================
echo   开始打包流程...
echo ========================================
echo.

:: 步骤1: 打包程序
echo.
echo ┌────────────────────────────────────────┐
echo │  步骤 1/4: 打包程序                    │
echo └────────────────────────────────────────┘
echo.
call 打包exe-稳定版.bat
if errorlevel 1 (
    echo.
    echo ❌ 打包失败,流程终止
    pause
    exit /b 1
)

:: 步骤2: 测试程序
echo.
echo ┌────────────────────────────────────────┐
echo │  步骤 2/4: 测试程序                    │
echo └────────────────────────────────────────┘
echo.
echo 正在验证打包结果...
echo.

:: 检查exe
if not exist "dist\红枫工具箱\红枫工具箱.exe" (
    echo ❌ 错误: 未找到exe文件
    pause
    exit /b 1
)
echo ✅ exe文件存在

:: 检查浏览器驱动
if not exist "dist\红枫工具箱\_internal\playwright_browsers\chromium-1124\chrome-win\chrome.exe" (
    echo ❌ 错误: 浏览器驱动缺失
    pause
    exit /b 1
)
echo ✅ 浏览器驱动存在

:: 检查关键依赖
if not exist "dist\红枫工具箱\_internal\customtkinter" (
    echo ❌ 错误: customtkinter库缺失
    pause
    exit /b 1
)
echo ✅ customtkinter库存在

if not exist "dist\红枫工具箱\_internal\playwright" (
    echo ❌ 错误: playwright库缺失
    pause
    exit /b 1
)
echo ✅ playwright库存在

echo.
echo ✅ 所有验证通过!
echo.

:: 询问是否测试运行
set /p TEST_RUN=是否测试运行程序? (Y/N): 
if /i "%TEST_RUN%"=="Y" (
    echo.
    echo 启动程序进行测试...
    echo 请在程序中测试基本功能:
    echo   1. 程序能否正常启动
    echo   2. 界面是否正常显示
    echo   3. 登录功能是否正常
    echo   4. 采集功能是否正常
    echo.
    echo 测试完成后,关闭程序继续...
    echo.
    start "" "dist\红枫工具箱\红枫工具箱.exe"
    pause
)

:: 步骤3: 创建发布包
echo.
echo ┌────────────────────────────────────────┐
echo │  步骤 3/4: 创建发布包                  │
echo └────────────────────────────────────────┘
echo.
call 创建发布包.bat
if errorlevel 1 (
    echo.
    echo ❌ 创建发布包失败
    pause
    exit /b 1
)

:: 步骤4: 生成发布说明
echo.
echo ┌────────────────────────────────────────┐
echo │  步骤 4/4: 生成发布说明                │
echo └────────────────────────────────────────┘
echo.

set RELEASE_DIR=红枫工具箱-V2.1-发布版

:: 创建GitHub Release说明
(
echo # 红枫工具箱 V2.1 发布
echo.
echo ## 📝 版本信息
echo.
echo - **版本号**: V2.1
echo - **发布日期**: %date%
echo - **类型**: 重大UI/UX改进
echo.
echo ## ✨ 主要更新
echo.
echo ### 🎨 界面优化
echo - ✅ **移除浏览器预览** - 不再使用tkinterweb组件
echo - ✅ **新增实时日志显示** - 使用CTkTextbox实现
echo - ✅ **彩色分级日志** - INFO/SUCCESS/WARNING/ERROR/HEADER/PROGRESS
echo - ✅ **清空日志按钮** - 一键清空日志记录
echo.
echo ### 🚀 功能改进
echo - ✅ **实时采集进度** - 详细显示采集过程
echo - ✅ **错误日志保存** - 自动保存crash_log.txt
echo - ✅ **依赖检查** - 启动时检查关键依赖
echo.
echo ### 🐛 问题修复
echo - ✅ **浏览器卡死** - 移除浏览器预览,解决卡死问题
echo - ✅ **稳定性提升** - 不再依赖tkinterweb
echo.
echo ## 📦 下载说明
echo.
echo ### 文件说明
echo - `红枫工具箱-V2.1.zip` - 完整安装包
echo - 大小: 约300MB ^(包含浏览器驱动^)
echo.
echo ### 安装步骤
echo 1. 下载 `红枫工具箱-V2.1.zip`
echo 2. 完整解压所有文件到英文路径
echo 3. 运行 `新设备自检.bat` 检查环境
echo 4. 双击 `红枫工具箱.exe` 启动程序
echo.
echo ### ⚠️ 重要提示
echo - ✅ 必须完整解压所有文件
echo - ✅ 不要删除 `_internal` 文件夹
echo - ✅ 解压到英文路径^(无中文、无空格^)
echo - ✅ 关闭杀毒软件后再运行
echo.
echo ## 🎯 支持平台
echo - ✅ 抖音 - 关键词搜索、指定内容、创作者主页
echo - ✅ 小红书 - 关键词搜索、指定内容、创作者主页
echo - ⏳ B站 - 开发中
echo - ⏳ 知乎 - 开发中
echo.
echo ## 🐛 常见问题
echo.
echo ### Q: 双击exe没反应?
echo A: 
echo 1. 运行 `新设备自检.bat` 检查环境
echo 2. 查看 `crash_log.txt` 错误日志
echo 3. 关闭杀毒软件后重试
echo.
echo ### Q: 提示"浏览器文件缺失"?
echo A:
echo 1. 检查是否完整解压所有文件
echo 2. 检查 `_internal\playwright_browsers` 是否存在
echo 3. 重新下载完整压缩包
echo.
echo ### Q: 杀毒软件报毒?
echo A: 这是误报,PyInstaller打包的程序常被误报
echo - 添加到杀毒软件白名单
echo - 临时关闭杀毒软件
echo.
echo ## 📧 反馈与支持
echo - GitHub Issues: https://github.com/InterestWatcher-Xiaofeng/-/issues
echo - 问题反馈: 在GitHub提Issue
echo.
echo ## 📜 更新日志
echo.
echo 完整更新日志请查看 [更新日志.txt]
echo.
echo ---
echo.
echo **感谢使用红枫工具箱!** 🎉
) > "%RELEASE_DIR%\GitHub-Release说明.md"

echo ✅ GitHub Release说明已生成
echo.

:: 完成
echo.
echo ╔════════════════════════════════════════╗
echo ║  🎉 打包发布流程完成!                  ║
echo ╚════════════════════════════════════════╝
echo.
echo 📁 发布目录: %RELEASE_DIR%\
echo.
echo 📄 生成的文件:
echo   ✅ 红枫工具箱.exe - 主程序
echo   ✅ _internal\ - 依赖文件夹
echo   ✅ README.txt - 完整说明
echo   ✅ 快速开始.txt - 快速指南
echo   ✅ 更新日志.txt - 版本历史
echo   ✅ 使用说明.txt - 使用说明
echo   ✅ 新设备自检.bat - 环境检查
echo   ✅ GitHub-Release说明.md - GitHub发布说明
echo.
echo 💡 下一步操作:
echo.
echo   1️⃣ 压缩发布包
echo      - 使用7-Zip或WinRAR
echo      - 压缩为: 红枫工具箱-V2.1.zip
echo      - 压缩格式: ZIP ^(兼容性最好^)
echo.
echo   2️⃣ 上传到GitHub
echo      - 创建新的Release: v2.1
echo      - 上传: 红枫工具箱-V2.1.zip
echo      - 复制: GitHub-Release说明.md 的内容
echo.
echo   3️⃣ 测试分发
echo      - 在其他设备上下载测试
echo      - 确保完整解压后能正常运行
echo      - 收集用户反馈
echo.
echo ⚠️ 发布前检查清单:
echo   □ 在本机测试通过
echo   □ 在其他设备测试通过
echo   □ 所有功能正常
echo   □ 文档完整准确
echo   □ 版本号正确
echo.
pause

