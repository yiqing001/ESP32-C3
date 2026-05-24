#Requires -Version 5.1
<#
.SYNOPSIS
  启动本地 HTTP 服务，打开 OTA 网页控制台（局域网设备发现与烧录）

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\ota-console.ps1
#>
$ConsoleDir = Join-Path (Split-Path $PSScriptRoot -Parent) "tools\ota_console"
$Port = 8080

Write-Host "OTA 控制台: http://127.0.0.1:$Port/" -ForegroundColor Cyan
Write-Host "请确保 PC 与 ESP32 在同一 WiFi 网段" -ForegroundColor Yellow
Set-Location $ConsoleDir
python -m http.server $Port
