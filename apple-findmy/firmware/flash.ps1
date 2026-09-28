param (
    [string]$COMPort = "COM3",
    [string]$FirmwarePath
)

if (-Not (Get-Command "esptool.py" -ErrorAction SilentlyContinue)) {
    Write-Error "esptool.py is not installed or not in PATH. Run setup.ps1 first."
    exit 1
}

if (-Not (Test-Path $FirmwarePath)) {
    Write-Error "Firmware file not found at: $FirmwarePath"
    exit 1
}

Write-Host "Erasing flash on $COMPort..." -ForegroundColor Cyan
esptool.py --port $COMPort erase_flash

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to erase flash. Check your COM port and connections."
    exit 1
}

Write-Host "Flashing firmware from $FirmwarePath to $COMPort..." -ForegroundColor Cyan
# ESP32 usually flashes app binaries at 0x10000. Adjust if your specific firmware requires bootloader/partitions.
esptool.py --port $COMPort --baud 460800 write_flash -z 0x10000 $FirmwarePath

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nFlash successful!" -ForegroundColor Green
    Write-Host "Your ESP32 is now broadcasting as an Apple Find My device."
} else {
    Write-Error "Flashing failed."
}
