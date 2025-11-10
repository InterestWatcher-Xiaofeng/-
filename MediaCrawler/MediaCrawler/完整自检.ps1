# 红枫工具箱 - 完整自检脚本（包含代码验证）
param(
    [string]$TestPath = "C:\Users\Yu feng\Desktop\红枫工具箱-最终测试版"
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "红枫工具箱 - 完整自检（包含代码验证）" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$distPath = "dist\红枫工具箱"
$passCount = 0
$failCount = 0

function Check-Item {
    param([string]$Name, [bool]$Pass, [string]$Details = "")
    if ($Pass) {
        Write-Host "  [OK] $Name" -ForegroundColor Green
        if ($Details) { Write-Host "       $Details" -ForegroundColor Gray }
        $script:passCount++
    } else {
        Write-Host "  [FAIL] $Name" -ForegroundColor Red
        if ($Details) { Write-Host "         $Details" -ForegroundColor Yellow }
        $script:failCount++
    }
}

# ============================================================================
# 第1阶段：打包文件检查
# ============================================================================
Write-Host "第1阶段：打包文件检查" -ForegroundColor Yellow
Write-Host ""

# 检查exe
$exeExists = Test-Path "$distPath\红枫工具箱.exe"
if ($exeExists) {
    $exeInfo = Get-Item "$distPath\红枫工具箱.exe"
    $exeSize = [math]::Round($exeInfo.Length/1MB, 2)
    $exeTime = $exeInfo.LastWriteTime
    Check-Item "主程序exe" $true "大小: $exeSize MB, 时间: $exeTime"
} else {
    Check-Item "主程序exe" $false "文件不存在"
}

# 检查_internal
$internalExists = Test-Path "$distPath\_internal"
if ($internalExists) {
    $fileCount = (Get-ChildItem "$distPath\_internal" -Recurse -File).Count
    $totalSize = [math]::Round((Get-ChildItem "$distPath\_internal" -Recurse -File | Measure-Object -Property Length -Sum).Sum/1MB, 2)
    Check-Item "_internal文件夹" $true "$fileCount 个文件, $totalSize MB"
} else {
    Check-Item "_internal文件夹" $false
}

# 检查gui_app模块
Write-Host ""
Write-Host "  🔍 检查gui_app模块是否被打包..." -ForegroundColor Cyan
$guiAppFiles = Get-ChildItem "$distPath\_internal" -Filter "*gui_app*" -Recurse -File
if ($guiAppFiles.Count -gt 0) {
    Check-Item "gui_app模块" $true "找到 $($guiAppFiles.Count) 个相关文件"
    foreach ($file in $guiAppFiles) {
        Write-Host "       - $($file.Name) ($([math]::Round($file.Length/1KB, 2)) KB)" -ForegroundColor Gray
    }
} else {
    Check-Item "gui_app模块" $false "未找到gui_app相关文件！"
}

Write-Host ""

# ============================================================================
# 第2阶段：浏览器驱动检查
# ============================================================================
Write-Host "第2阶段：Playwright浏览器驱动" -ForegroundColor Yellow
Write-Host ""

# 同时兼容两种路径：dist\playwright_browsers 与 dist\_internal\playwright_browsers
$browsersBase1 = "$distPath\_internal\playwright_browsers"
$browsersBase2 = "$distPath\playwright_browsers"
if (Test-Path $browsersBase1) { $browsersBase = $browsersBase1 }
elseif (Test-Path $browsersBase2) { $browsersBase = $browsersBase2 }
else { $browsersBase = $null }

if ($browsersBase) {
    $browsersPath = "$browsersBase\chromium-1124"
    Check-Item "chromium-1124文件夹" (Test-Path $browsersPath) "位置: $browsersPath"

    $chromeExe = "$browsersPath\chrome-win\chrome.exe"
    if (Test-Path $chromeExe) {
        $chromeSize = [math]::Round((Get-Item $chromeExe).Length/1MB, 2)
        Check-Item "chrome.exe" $true "$chromeSize MB"
    } else {
        Check-Item "chrome.exe" $false
    }

    $exeFiles = @("chrome.exe", "chrome_proxy.exe", "chrome_pwa_launcher.exe", "elevation_service.exe", "notification_helper.exe")
    $allExist = $true
    foreach ($exe in $exeFiles) {
        if (-not (Test-Path "$browsersPath\chrome-win\$exe")) { $allExist = $false }
    }
    Check-Item "5个关键exe文件" $allExist

    $hasMarkers = (Test-Path "$browsersPath\DEPENDENCIES_VALIDATED") -and (Test-Path "$browsersPath\INSTALLATION_COMPLETE")
    Check-Item "Playwright标记文件" $hasMarkers

    if (Test-Path $browsersPath) {
        $browserFileCount = (Get-ChildItem $browsersPath -Recurse -File).Count
        $browserSize = [math]::Round((Get-ChildItem $browsersPath -Recurse -File | Measure-Object -Property Length -Sum).Sum/1MB, 2)
        Check-Item "浏览器驱动统计" $true "$browserFileCount 个文件, $browserSize MB"
    }
} else {
    Check-Item "playwright_browsers 目录" $false "未在 _internal 或 根目录 找到"
}

Write-Host ""

# ============================================================================
# 第3阶段：配置文件检查
# ============================================================================
Write-Host "第3阶段：配置文件" -ForegroundColor Yellow
Write-Host ""

Check-Item "config文件夹" (Test-Path "$distPath\_internal\config")
Check-Item "libs文件夹" (Test-Path "$distPath\_internal\libs")
Check-Item "icon.ico" (Test-Path "$distPath\_internal\icon.ico")

Write-Host ""

# ============================================================================
# 第4阶段：Python库检查
# ============================================================================
Write-Host "第4阶段：Python运行时" -ForegroundColor Yellow
Write-Host ""

Check-Item "playwright库" (Test-Path "$distPath\_internal\playwright")
Check-Item "customtkinter库" (Test-Path "$distPath\_internal\customtkinter")

Write-Host ""

# ============================================================================
# 第5阶段：模拟新设备测试
# ============================================================================
Write-Host "第5阶段：模拟新设备环境" -ForegroundColor Yellow
Write-Host ""

Write-Host "  正在复制到测试位置: $TestPath" -ForegroundColor Cyan
if (Test-Path $TestPath) {
    Remove-Item $TestPath -Recurse -Force
}
Copy-Item $distPath $TestPath -Recurse

Check-Item "复制到新位置" (Test-Path $TestPath)

$testBrowsersBase1 = Join-Path $TestPath 'playwright_browsers'
$testBrowsersBase2 = Join-Path $TestPath '_internal\playwright_browsers'
if (Test-Path $testBrowsersBase2) { $testBrowsersBase = $testBrowsersBase2 }
elseif (Test-Path $testBrowsersBase1) { $testBrowsersBase = $testBrowsersBase1 }
else { $testBrowsersBase = $null }
$testBrowserPath = if ($testBrowsersBase) { Join-Path $testBrowsersBase 'chromium-1124\chrome-win\chrome.exe' } else { '' }
Check-Item "新位置浏览器存在" (Test-Path $testBrowserPath)

# 检查gui_app模块
$testGuiAppFiles = Get-ChildItem "$TestPath\_internal" -Filter "*gui_app*" -Recurse -File -ErrorAction SilentlyContinue
if ($testGuiAppFiles.Count -gt 0) {
    Check-Item "新位置gui_app模块" $true "找到 $($testGuiAppFiles.Count) 个文件"
} else {
    Check-Item "新位置gui_app模块" $false "未找到gui_app模块！"
}

Write-Host ""

# ============================================================================
# 第6阶段：启动测试
# ============================================================================
Write-Host "第6阶段：程序启动测试" -ForegroundColor Yellow
Write-Host ""

Write-Host "  正在启动程序（5秒后自动关闭）..." -ForegroundColor Cyan
$proc = Start-Process "$TestPath\红枫工具箱.exe" -WorkingDirectory $TestPath -PassThru
Start-Sleep -Seconds 5

if ($proc -and -not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force
    Check-Item "程序启动" $true "成功启动并运行"
} else {
    Check-Item "程序启动" $false "程序启动失败或崩溃"
}

Write-Host ""

# ============================================================================
# 汇总报告
# ============================================================================
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "检查报告汇总" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "通过: $passCount" -ForegroundColor Green
Write-Host "失败: $failCount" -ForegroundColor Red
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "🎉 所有检查项通过！" -ForegroundColor Green
    Write-Host ""
    Write-Host "下一步：手动功能测试" -ForegroundColor Yellow
    Write-Host "1. 启动程序: $TestPath\红枫工具箱.exe" -ForegroundColor White
    Write-Host "2. 点击'登录管理' -> '登录抖音'" -ForegroundColor White
    Write-Host "3. 检查浏览器是否正常打开" -ForegroundColor White
    Write-Host "4. 检查是否有错误提示" -ForegroundColor White
    Write-Host ""
    Write-Host "是否立即启动测试？(Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        Write-Host "正在启动程序..." -ForegroundColor Green
        Start-Process "$TestPath\红枫工具箱.exe" -WorkingDirectory $TestPath
        Write-Host "程序已启动，请按照上述步骤测试" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  发现 $failCount 个问题，需要修复！" -ForegroundColor Red
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan

