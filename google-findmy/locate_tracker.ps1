<#
.SYNOPSIS
Retrieves the location of the registered ESP32 tracker.

.DESCRIPTION
Runs the Python script to fetch the latest location data from the Google Find My network.
Supports a loop flag to check location periodically.

.PARAMETER Loop
Switch to continuously poll for location updates every 60 seconds.
#>

param (
    [switch]$Loop
)

$ErrorActionPreference = "Stop"
$toolsDir = "GoogleFindMyTools"
$pollIntervalSeconds = 60

if (-not (Test-Path $toolsDir)) {
    Write-Error "GoogleFindMyTools directory not found. Please run setup.ps1 first."
    exit 1
}

Push-Location $toolsDir
try {
    if ($Loop) {
        Write-Host "Starting location tracking loop. Press Ctrl+C to stop." -ForegroundColor Cyan
        while ($true) {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Fetching location..." -ForegroundColor Yellow
            python request_reports.py
            
            Write-Host "Waiting $pollIntervalSeconds seconds before next check..." -ForegroundColor DarkGray
            Start-Sleep -Seconds $pollIntervalSeconds
        }
    } else {
        Write-Host "Fetching tracker location..." -ForegroundColor Cyan
        python request_reports.py
    }
} finally {
    Pop-Location
}
