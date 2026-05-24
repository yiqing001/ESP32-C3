#Requires -Version 5.1
<#
  Pack APP serial_ota_tool to EXE (one-shot).
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\scripts\build-app-exe.ps1
#>
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
& powershell -ExecutionPolicy Bypass -File (Join-Path $ProjectRoot "APP\serial_ota_tool\build_exe.ps1")
exit $LASTEXITCODE
