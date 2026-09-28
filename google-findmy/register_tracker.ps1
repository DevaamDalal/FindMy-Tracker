<#
.SYNOPSIS
Registers the ESP32 tracker with the Google Find My network.

.DESCRIPTION
Navigates to the GoogleFindMyTools directory and executes the main registration script.
Provides guidance on the login process and saving the advertisement key.
#>

$ErrorActionPreference = "Stop"
$toolsDir = "GoogleFindMyTools"

if (-not (Test-Path $toolsDir)) {
    Write-Error "GoogleFindMyTools directory not found. Please run setup.ps1 first."
    exit 1
}

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "       Google Find My Tracker Registration        " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will open a Google Chrome browser window."
Write-Host "You MUST log in with a Google account that is currently"
Write-Host "active on a real Android device."
Write-Host ""
Write-Host "After successful login, the script will generate an"
Write-Host "'Advertisement Key'. You must copy this key!"
Write-Host ""
Write-Host "Press any key to launch the registration script..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Push-Location $toolsDir
try {
    Write-Host "Launching Python script..." -ForegroundColor Yellow
    python main.py
    
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Warning "Python script exited with code $exitCode."
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "                Registration Complete             " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "If successful, you should see an Advertisement Key above."
Write-Host "Copy this key. You will need to paste it into the"
Write-Host "ESP32 firmware source code (main.c) before building."
Write-Host "Check firmware/README.md for more details."
