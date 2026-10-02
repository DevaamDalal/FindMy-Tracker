param (
    [string]$COMPort = "COM3"
)

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

if (-Not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

Write-Host "Erasing flash on $COMPort..." -ForegroundColor Cyan
python -m esptool --port $COMPort erase_flash

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to erase flash. Check your COM port and connections."
    exit 1
}

Write-Host "Flashing firmware and key to $COMPort..." -ForegroundColor Cyan
python -m esptool --port $COMPort --baud 460800 write_flash -z `
    0x1000 bootloader.bin `
    0x8000 partitions.bin `
    0x10000 firmware.bin `
    0x110000 keyfile.bin

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nFlash successful!" -ForegroundColor Green
    Write-Host "Your ESP32 is now broadcasting your specific key as an Apple Find My device."
} else {
    Write-Error "Flashing failed."
}
