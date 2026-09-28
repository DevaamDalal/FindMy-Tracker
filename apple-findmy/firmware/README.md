# ESP32 Find My Firmware

This directory handles flashing the Macless-Haystack compatible firmware to the ESP32.

## Prerequisites
1. You must have generated your keys using `generate_keys.py` in the parent directory.
2. You need the Base64 advertisement key printed by the script.

## Getting the Firmware
Download the latest OpenHaystack/Macless-Haystack firmware for the ESP32. You can usually find this in the [Macless-Haystack repository releases](https://github.com/dchristl/macless-haystack) or the original OpenHaystack project.

*(Note: Ensure you download the pre-compiled `.bin` file for the ESP32, e.g., `esp32_firmware.bin`.)*

## Embedding the Key
Depending on the specific firmware version, you may need to compile it yourself with the Base64 key embedded in a header file, or the firmware might provide a web interface/serial prompt to input the Base64 key after flashing. Check the specific release notes for the binary you downloaded.

## Flashing Instructions
1. Connect your ESP32 to your PC via USB. No extra wiring is needed; the ESP32 acts as a standard BLE beacon.
2. Run the provided PowerShell script to flash the firmware. Replace `COM3` with your actual COM port and provide the path to your downloaded firmware file:

```powershell
.\flash.ps1 -COMPort "COM3" -FirmwarePath "path\to\esp32_firmware.bin"
```

## How It Works
Once flashed and configured with your advertisement key, the ESP32 will continuously broadcast a BLE beacon acting as an Apple device (like an AirTag). Any passing Apple device (iPhone, iPad, etc.) will hear this beacon and automatically report its location (encrypted) to Apple's servers.
