@echo off
chcp 65001 >nul
echo ========================================
echo   红枫工具箱 - 创建发布包 V2.1
echo   打包完整的可分发版本
echo ========================================
echo.

:: 设置颜色
color 0B

:: 检查dist目录
echo [1/5] 检查打包文件...
if not exist "dist\红枫工具箱\红枫工具箱.exe" (
    echo ❌ 错误: 未找到打包后的exe文件
    echo 请先运行: 打包exe-稳定版.bat
    pause
    exit /b 1
)
echo ✅ 找到打包文件
echo.

:: 创建发布目录
echo [2/5] 创建发布目录...
set RELEASE_DIR=红枫工具箱-V2.1-发布版
if exist "%RELEASE_DIR%" (
    echo 删除旧的发布目录...
    rmdir /s /q "%RELEASE_DIR%"
)
mkdir "%RELEASE_DIR%"
echo ✅ 发布目录已创建: %RELEASE_DIR%
echo.

:: 复制程序文件
echo [3/5] 复制程序文件...
echo 复制 dist\红枫工具箱\ 到 %RELEASE_DIR%\
xcopy "dist\红枫工具箱" "%RELEASE_DIR%\" /E /I /H /Y >nul
if errorlevel 1 (
    echo ❌ 复制失败
    pause
    exit /b 1
)
echo ✅ 程序文件已复制
echo.

:: 创建完整的使用文档
echo [4/5] 创建使用文档...

:: README.txt
(
echo ========================================
echo   红枫工具箱 V2.1
echo   社交媒体数据采集工具
echo ========================================
echo.
echo 📝 版本信息:
echo   版本号: V2.1
echo   发布日期: %date%
echo   更新内容: 移除浏览器预览,新增实时日志显示
echo.
echo 🎯 支持平台:
echo   ✅ 抖音 - 关键词搜索、指定内容、创作者主页
echo   ✅ 小红书 - 关键词搜索、指定内容、创作者主页
echo   ⏳ B站 - 开发中
echo   ⏳ 知乎 - 开发中
echo.
echo 📦 采集内容:
echo   ✅ 视频/笔记基本信息
echo   ✅ 评论数据
echo   ✅ 创作者信息
echo   ✅ 导出为CSV格式
echo.
echo 🚀 快速开始:
echo   1. 完整解压所有文件到英文路径
echo   2. 运行 新设备自检.bat 检查环境
echo   3. 双击 红枫工具箱.exe 启动程序
echo   4. 首次使用需要登录平台账号
echo   5. 选择平台和采集模式
echo   6. 输入关键词或链接
echo   7. 点击"开始采集"
echo.
echo ⚠️ 重要提示:
echo   1. 必须完整解压所有文件
echo   2. 不要删除 _internal 文件夹
echo   3. 解压到英文路径^(无中文、无空格^)
echo   4. 关闭杀毒软件后再运行
echo   5. 首次运行会进行环境检查
echo.
echo 🐛 常见问题:
echo.
echo   Q: 双击exe没反应?
echo   A: 1. 运行 新设备自检.bat 检查环境
echo      2. 查看 crash_log.txt 错误日志
echo      3. 关闭杀毒软件后重试
echo.
echo   Q: 提示"浏览器文件缺失"?
echo   A: 1. 检查是否完整解压所有文件
echo      2. 检查 _internal\playwright_browsers 是否存在
echo      3. 重新下载完整压缩包
echo.
echo   Q: 采集失败?
echo   A: 1. 检查网络连接
echo      2. 重新登录平台账号
echo      3. 检查关键词或链接是否正确
echo.
echo   Q: 杀毒软件报毒?
echo   A: 这是误报,PyInstaller打包的程序常被误报
echo      解决方法:
echo      1. 添加到杀毒软件白名单
echo      2. 临时关闭杀毒软件
echo      3. 使用Windows Defender^(误报率较低^)
echo.
echo 📧 联系方式:
echo   GitHub: https://github.com/InterestWatcher-Xiaofeng/-
echo   问题反馈: 在GitHub提Issue
echo.
echo ========================================
) > "%RELEASE_DIR%\README.txt"

:: 快速开始.txt
(
echo ========================================
echo   红枫工具箱 - 快速开始指南
echo ========================================
echo.
echo 🎯 第一步: 环境检查
echo   1. 运行 新设备自检.bat
echo   2. 确保所有检查通过
echo   3. 如果有错误,按提示解决
echo.
echo 🎯 第二步: 启动程序
echo   1. 双击 红枫工具箱.exe
echo   2. 等待程序启动^(首次启动较慢^)
echo   3. 看到主界面表示启动成功
echo.
echo 🎯 第三步: 登录账号
echo   1. 选择要采集的平台^(抖音/小红书^)
echo   2. 点击"登录"按钮
echo   3. 在弹出的浏览器中登录账号
echo   4. 登录成功后关闭浏览器
echo   5. 登录信息会自动保存
echo.
echo 🎯 第四步: 开始采集
echo.
echo   方式1: 关键词搜索
echo   1. 选择"关键词搜索"模式
echo   2. 输入关键词^(每行一个^)
echo   3. 设置采集数量
echo   4. 点击"开始采集"
echo.
echo   方式2: 指定内容
echo   1. 选择"指定内容"模式
echo   2. 输入视频/笔记链接^(每行一个^)
echo   3. 点击"开始采集"
echo.
echo   方式3: 创作者主页
echo   1. 选择"创作者主页"模式
echo   2. 输入创作者主页链接
echo   3. 设置采集数量
echo   4. 点击"开始采集"
echo.
echo 🎯 第五步: 查看结果
echo   1. 采集完成后,数据保存在 data 文件夹
echo   2. 文件格式: CSV^(可用Excel打开^)
echo   3. 文件命名: 时间戳_数量_类型.csv
echo.
echo ========================================
) > "%RELEASE_DIR%\快速开始.txt"

:: 更新日志.txt
(
echo ========================================
echo   红枫工具箱 - 更新日志
echo ========================================
echo.
echo V2.1 ^(2025-11-12^) ⭐ 当前版本
echo   [重大更新] 移除浏览器预览,改为实时日志显示
echo   [新增] 彩色分级日志显示
echo   [新增] 清空日志按钮
echo   [优化] 采集进度实时显示
echo   [优化] 界面稳定性提升
echo   [修复] 浏览器预览卡死问题
echo.
echo V2.0.3 ^(2025-11-12^)
echo   [修复] JavaScript语法兼容性问题
echo   [修复] 新设备浏览器驱动问题
echo   [优化] 禁用stealth.min.js
echo   [优化] 添加首次搜索验证提示
echo.
echo V2.0.2 ^(2025-11-11^)
echo   [修复] 新设备EXE运行问题
echo   [优化] 浏览器驱动路径管理
echo.
echo V2.0.1 ^(2025-11-10^)
echo   [修复] 浏览器页面关闭问题
echo   [修复] 进度显示卡死问题
echo   [优化] 登录流程
echo.
echo V2.0.0 ^(2025-11-08^)
echo   [新增] 小红书RPA采集功能
echo   [新增] 批量关键词采集
echo   [新增] 创作者主页采集
echo   [优化] GUI界面美化
echo.
echo V1.0.0 ^(2025-11-03^)
echo   [发布] 首个正式版本
echo   [支持] 抖音关键词搜索
echo   [支持] 评论数据采集
echo   [支持] CSV导出
echo.
echo ========================================
) > "%RELEASE_DIR%\更新日志.txt"

:: 复制自检脚本
copy "新设备自检.bat" "%RELEASE_DIR%\" >nul

echo ✅ 使用文档已创建
echo.

:: 计算总大小
echo [5/5] 计算发布包大小...
for /f "tokens=3" %%a in ('dir "%RELEASE_DIR%" /s /-c ^| find "个文件"') do set TOTAL_SIZE=%%a
set /a SIZE_MB=%TOTAL_SIZE% / 1048576
echo 📦 发布包大小: %SIZE_MB% MB
echo.

:: 完成
echo ========================================
echo   🎉 发布包创建完成!
echo ========================================
echo.
echo 📁 发布目录: %RELEASE_DIR%\
echo 📦 总大小: %SIZE_MB% MB
echo.
echo 📄 包含文件:
echo   ✅ 红枫工具箱.exe - 主程序
echo   ✅ _internal\ - 依赖文件夹
echo   ✅ README.txt - 完整说明
echo   ✅ 快速开始.txt - 快速指南
echo   ✅ 更新日志.txt - 版本历史
echo   ✅ 使用说明.txt - 使用说明
echo   ✅ 新设备自检.bat - 环境检查
echo.
echo 💡 下一步:
echo   1. 测试: 在其他设备上测试运行
echo   2. 压缩: 将 %RELEASE_DIR% 压缩为zip
echo   3. 分发: 上传到GitHub Releases或网盘
echo.
echo ⚠️ 分发提示:
echo   - 建议使用7-Zip或WinRAR压缩
echo   - 压缩格式: ZIP ^(兼容性最好^)
echo   - 文件名: 红枫工具箱-V2.1.zip
echo   - 提醒用户完整解压所有文件
echo.
pause

