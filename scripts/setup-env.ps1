#Requires -Version 5.1
<#
.SYNOPSIS
  在新 Windows 电脑上安装 ESP-IDF v5.3.2（EIM）及 esp32c3 工具链。

.DESCRIPTION
  与 README「新电脑部署指南」配套。需联网。安装完成后在 Cursor 中选择 ESP-IDF 版本并打开本项目。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\setup-env.ps1
#>
param(
    [string]$IdfVersion = "v5.3.2",
    [string]$IdfBasePath = "$env:USERPROFILE\.espressif",
    [string]$EimJsonPath = "C:\Espressif\tools\eim_idf.json"
)

$ErrorActionPreference = "Stop"

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

Write-Host "=== ESP32-C3 项目：环境安装脚本 ===" -ForegroundColor Cyan
Write-Host "ESP-IDF: $IdfVersion | 目标: esp32c3"
Write-Host ""

if (-not (Test-Command git)) {
    Write-Host "[1/4] 安装 Git ..." -ForegroundColor Yellow
    winget install Git.Git --accept-package-agreements --accept-source-agreements
} else {
    Write-Host "[1/4] Git 已安装: $(git --version)"
}

if (-not (Test-Command eim)) {
    Write-Host "[2/4] 安装 EIM CLI ..." -ForegroundColor Yellow
    winget install Espressif.EIM-CLI --accept-package-agreements --accept-source-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path", "User")
} else {
    Write-Host "[2/4] EIM 已安装: $(eim --version)"
}

Write-Host "[3/4] 安装 ESP-IDF $IdfVersion（约 15-30 分钟，视网络而定）..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path (Split-Path $EimJsonPath) | Out-Null
$ConfigFile = Join-Path (Split-Path $PSScriptRoot -Parent) "eim_config.toml"
if (Test-Path $ConfigFile) {
    eim install -c $ConfigFile -p $IdfBasePath --esp-idf-json-path $EimJsonPath -n true
} else {
    eim install -i $IdfVersion -p $IdfBasePath -t esp32c3 --esp-idf-json-path $EimJsonPath
}

Write-Host "[4/4] 列出已安装版本 ..." -ForegroundColor Yellow
eim list

Write-Host ""
Write-Host "=== 环境安装完成 ===" -ForegroundColor Green
Write-Host "下一步（在 Cursor 中）："
Write-Host "  1. 安装扩展: espressif.esp-idf-extension"
Write-Host "  2. Ctrl+Shift+P -> ESP-IDF: Select Current ESP-IDF Version -> 选择 $IdfVersion"
Write-Host "  3. 打开本项目文件夹，Ctrl+Shift+P -> ESP-IDF: Set Target -> esp32c3"
Write-Host "  4. 修改 .vscode/settings.json 中的 idf.portWin 为实际 COM 口"
Write-Host "  5. Ctrl+Alt+B 编译，Ctrl+Alt+F 烧录"
