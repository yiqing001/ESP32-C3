#Requires -Version 5.1
param(
    [switch]$SkipPip,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root

function Write-BuildMsg($msg, $color) {
    if (-not $Quiet) {
        if ($color) { Write-Host $msg -ForegroundColor $color }
        else { Write-Host $msg }
    }
}

$venvPython = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-BuildMsg "Creating venv..."
    python -m venv .venv
    $SkipPip = $false
}

if (-not $SkipPip) {
    & $venvPython -m pip install -q -r requirements.txt
    & $venvPython -m pip install -q pyinstaller
}

$distExe = Join-Path $Root "dist\ESP32-C3-Serial-OTA.exe"
if (Test-Path $distExe) { Remove-Item -Force $distExe }

Write-BuildMsg "Building EXE (about 1-2 min)..."
& $venvPython -m PyInstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name "ESP32-C3-Serial-OTA" `
    --hidden-import serial.tools.list_ports `
    --collect-submodules serial `
    --hidden-import PyQt5.sip `
    --collect-submodules PyQt5 `
    main.py

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-BuildMsg "[$stamp] OK: $distExe" Green
