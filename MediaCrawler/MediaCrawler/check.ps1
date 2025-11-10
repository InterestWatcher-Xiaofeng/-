# 红枫工具箱 - 全面自检脚本
Write-Host "================================================================================"
Write-Host "红枫工具箱 - 全面自检" -ForegroundColor Cyan
Write-Host "================================================================================"
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

# 第1部分：基础文件
Write-Host "第1部分：基础文件检查" -ForegroundColor Yellow
$exeExists = Test-Path "$distPath\红枫工具箱.exe"
if ($exeExists) {
    $exeSize = [math]::Round((Get-Item "$distPath\红枫工具箱.exe").Length/1MB, 2)
    Check-Item "主程序exe" $true "大小: $exeSize MB"
} else {
    Check-Item "主程序exe" $false
}

$internalExists = Test-Path "$distPath\_internal"
if ($internalExists) {
    $fileCount = (Get-ChildItem "$distPath\_internal" -Recurse -File).Count
    $totalSize = [math]::Round((Get-ChildItem "$distPath\_internal" -Recurse -File | Measure-Object -Property Length -Sum).Sum/1MB, 2)
    Check-Item "_internal文件夹" $true "$fileCount 个文件, $totalSize MB"
} else {
    Check-Item "_internal文件夹" $false
}
Write-Host ""

# 第2部分：浏览器驱动
Write-Host "第2部分：Playwright浏览器驱动" -ForegroundColor Yellow
$browsersPath = "$distPath\_internal\playwright_browsers\chromium-1124"
Check-Item "chromium-1124文件夹" (Test-Path $browsersPath)

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
Write-Host ""

# 第3部分：配置文件
Write-Host "第3部分：配置文件" -ForegroundColor Yellow
Check-Item "config文件夹" (Test-Path "$distPath\_internal\config")
Check-Item "libs文件夹" (Test-Path "$distPath\_internal\libs")
Check-Item "icon.ico" (Test-Path "$distPath\_internal\icon.ico")
Write-Host ""

# 第4部分：Python库
Write-Host "第4部分：Python运行时" -ForegroundColor Yellow
Check-Item "playwright库" (Test-Path "$distPath\_internal\playwright")
Check-Item "customtkinter库" (Test-Path "$distPath\_internal\customtkinter")
Write-Host ""

# 第5部分：总体统计
Write-Host "第5部分：总体统计" -ForegroundColor Yellow
if (Test-Path $distPath) {
    $allFiles = Get-ChildItem $distPath -Recurse -File
    $totalFiles = $allFiles.Count
    $totalSize = [math]::Round(($allFiles | Measure-Object -Property Length -Sum).Sum/1MB, 2)
    $totalFolders = (Get-ChildItem $distPath -Recurse -Directory).Count
    Check-Item "文件夹结构" $true "$totalFiles 个文件, $totalFolders 个文件夹, $totalSize MB"
}
Write-Host ""

# 汇总
Write-Host "================================================================================"
Write-Host "检查报告汇总" -ForegroundColor Cyan
Write-Host "================================================================================"
Write-Host "通过: $passCount" -ForegroundColor Green
Write-Host "失败: $failCount" -ForegroundColor Red
Write-Host ""
if ($failCount -eq 0) {
    Write-Host "所有检查项通过！软件可以发布！" -ForegroundColor Green
} else {
    Write-Host "发现 $failCount 个问题，需要修复！" -ForegroundColor Red
}
Write-Host "================================================================================"
