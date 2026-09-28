<#
.SYNOPSIS
Automates the re-registration of the ESP32 tracker.

.DESCRIPTION
Due to limitations in the unofficial API, registration keys expire every 3-4 days.
This script is designed to be run as a scheduled task to automatically renew
the registration.

NOTE: This script assumes you have configured the Python tool to authenticate
without manual browser interaction (e.g., using saved cookies/session data),
otherwise it will halt waiting for user input.

.EXAMPLE
To set up as a Windows Scheduled Task running every 3 days:
schtasks /create /tn "GoogleFindMyReReg" /tr "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\path\to\auto_reregister.ps1" /sc daily /mo 3
#>

$toolsDir = "GoogleFindMyTools"
$logFile = "reregistration.log"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Set-Location $scriptDir

function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $message"
    Add-Content -Path $logFile -Value $logEntry
    Write-Host $logEntry
}

if (-not (Test-Path $toolsDir)) {
    Write-Log "ERROR: GoogleFindMyTools directory not found."
    exit 1
}

Write-Log "Starting automated re-registration..."

Push-Location $toolsDir
try {
    # Run the registration script. 
    # IMPORTANT: The underlying Python script must be configured to run headless 
    # and reuse authentication for this to work completely unattended.
    $output = python main.py 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Re-registration successful."
        # If you have a mechanism to automatically push the new key to the ESP32
        # (e.g., via a local web server or MQTT), you would extract the key from $output
        # and trigger that update here.
    } else {
        Write-Log "ERROR: Re-registration failed. Exit code: $LASTEXITCODE"
        Write-Log "Output: $output"
    }
} catch {
    Write-Log "ERROR: Exception occurred during re-registration: $_"
} finally {
    Pop-Location
}
Write-Log "Automated re-registration process finished."
