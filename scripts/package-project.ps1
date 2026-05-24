#Requires -Version 5.1
<#
.SYNOPSIS
  打包项目源码（不含 build、缓存、本机环境），便于拷贝到另一台电脑。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\package-project.ps1
  powershell -ExecutionPolicy Bypass -File .\scripts\package-project.ps1 -OutputDir D:\backup
#>
param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ProjectName = Split-Path -Leaf $ProjectRoot
$Timestamp = Get-Date -Format "yyyyMMdd-HHmm"
$ZipName = "${ProjectName}-src-${Timestamp}.zip"

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Split-Path -Parent $ProjectRoot
}

$ZipPath = Join-Path $OutputDir $ZipName
$StageDir = Join-Path $env:TEMP "esp32-c3-package-$Timestamp"
$StageProject = Join-Path $StageDir $ProjectName

Write-Host "=== 打包项目 ===" -ForegroundColor Cyan
Write-Host "源目录: $ProjectRoot"
Write-Host "输出:   $ZipPath"

if (Test-Path $StageDir) {
    Remove-Item -Recurse -Force $StageDir
}
New-Item -ItemType Directory -Force -Path $StageProject | Out-Null

$ExcludeDirs = @(
    'build', '.cache', '.git', 'dist', '.vscode\extensions'
)
$ExcludeFiles = @('*.zip')

robocopy $ProjectRoot $StageProject /E /NFL /NDL /NJH /NJS /nc /ns /np `
    /XD build .cache .git dist `
    | Out-Null

if ($LASTEXITCODE -ge 8) {
    throw "robocopy 失败，退出码 $LASTEXITCODE"
}

if (Test-Path $ZipPath) {
    Remove-Item -Force $ZipPath
}
Compress-Archive -Path $StageProject -DestinationPath $ZipPath -Force
Remove-Item -Recurse -Force $StageDir

$SizeMb = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
Write-Host ""
Write-Host "打包完成: $ZipPath ($SizeMb MB)" -ForegroundColor Green
Write-Host "Unzip and follow README section: New PC deployment guide (Cursor)."
