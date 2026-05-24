#Requires -Version 5.1
<#
  使用本机 ESP-IDF v5.5 + V55_tools 编译（与 Cursor 扩展当前环境一致）。
  解决「IDF 5.5 + C:\Espressif 旧工具链」混用导致的 CMake 报错。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1
  powershell -ExecutionPolicy Bypass -File .\scripts\build-v55.ps1 -Port COM6 -Flash
#>
param(
    [string]$Port = "",
    [switch]$Flash,
    [switch]$FullClean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$IdfPath = "E:\Study\Software\esp\v5.5\esp-idf"
$ToolsPath = "E:\Study\Software\esp\V55_tools"
$Python = "$ToolsPath\python_env\idf5.5_py3.11_env\Scripts\python.exe"

if (-not (Test-Path $IdfPath)) {
    Write-Error "未找到 ESP-IDF: $IdfPath"
}
if (-not (Test-Path $Python)) {
    Write-Error "未找到 Python 环境: $Python"
}

$env:IDF_PATH = $IdfPath
$env:IDF_TOOLS_PATH = $ToolsPath
$env:IDF_PYTHON_ENV_PATH = "$ToolsPath\python_env\idf5.5_py3.11_env"

$exportLines = & $Python "$IdfPath\tools\idf_tools.py" export --format key-value
foreach ($line in $exportLines) {
    if ($line -match '^PATH=(.+)$') {
        $env:PATH = $Matches[1]
    } elseif ($line -match '^([^=]+)=(.*)$') {
        Set-Item -Path "env:$($Matches[1])" -Value $Matches[2]
    }
}

Set-Location $ProjectRoot
$IdfPy = "$IdfPath\tools\idf.py"

if ($FullClean -and (Test-Path build)) {
    Remove-Item -Recurse -Force build
}

& $Python $IdfPy build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "OK: build\esp32-c3-lcd.bin" -ForegroundColor Green

if ($Flash) {
    if ($Port) {
        & $Python $IdfPy -p $Port flash
    } else {
        & $Python $IdfPy flash
    }
}
