#Requires -Version 5.1
<#
.SYNOPSIS
  在已安装 EIM/ESP-IDF 的终端中编译本项目（自动加载激活脚本）。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
  powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1 -Port COM5 -Flash
#>
param(
    [string]$Port = "",
    [switch]$Flash,
    [switch]$Monitor
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$ActivationScripts = Get-ChildItem "C:\Espressif\tools\Microsoft.*.PowerShell_profile.ps1" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending
if (-not $ActivationScripts) {
    Write-Error "未找到 C:\Espressif\tools\Microsoft.*.PowerShell_profile.ps1，请先运行 scripts\setup-env.ps1"
}
. $ActivationScripts[0].FullName
Set-Location $ProjectRoot

idf.py build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($Flash) {
    if ([string]::IsNullOrWhiteSpace($Port)) {
        idf.py flash
    } else {
        idf.py -p $Port flash
    }
}
if ($Monitor) {
    if ([string]::IsNullOrWhiteSpace($Port)) {
        idf.py monitor
    } else {
        idf.py -p $Port monitor
    }
}
