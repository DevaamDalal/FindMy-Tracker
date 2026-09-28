# Visual Guide: Flashing ESP32 Firmware in VS Code

This guide walks you through using the ESP-IDF Extension in Visual Studio Code to build and flash your tracker firmware.

## 1. Extension Setup

Ensure you have the official extension installed.

```text
+-------------------------------------------------------------+
| VS Code - Extensions (Ctrl+Shift+X)                         |
+-------------------------------------------------------------+
| Search: esp-idf                                             |
|                                                             |
| [ ] Espressif IDF                                           |
|     Official extension for ESP-IDF                          |
|     [ Install ]                                             |
+-------------------------------------------------------------+
```
*After installation, press `F1`, type `ESP-IDF: Configure extension`, and follow the setup wizard to install the framework.*

## 2. The ESP-IDF Bottom Toolbar

Once configured and the `firmware` folder is open, look at the bottom blue status bar in VS Code. You will use these buttons from left to right.

```text
[1] Port  [2] Target  [3] Config  [4] Clean  [5] Build  [6] Flash  [7] Monitor  [8] Build, Flash & Monitor
 🔌 COM3   ⚙️ esp32   🔧 defconfig  🗑️       ⚙️       ⚡       📺          🔥 
```

## 3. Step-by-Step Execution

### Step A: Select COM Port
Click the **🔌 Port** icon [1]. A dropdown will appear at the top. Select the COM port corresponding to your connected ESP32.

### Step B: Set Target Device
Click the **⚙️ Target** icon [2]. A dropdown will appear. Select your exact ESP32 model (e.g., `esp32`, `esp32c3`, `esp32s3`).

### Step C: Build, Flash, and Monitor (The Easy Way)
Click the **🔥 Build, Flash & Monitor** icon [8]. This single button will:
1. Compile your C code.
2. Upload the compiled binary to the ESP32 over the selected COM port.
3. Open a terminal to show the serial output from the device.

### Step D: Verify Operation
In the terminal that opens, look for output indicating successful initialization of the BLE stack and the start of broadcasting.

```text
+-------------------------------------------------------------+
| TERMINAL                                                    |
+-------------------------------------------------------------+
| I (321) BTDM_INIT: BT controller compile version [...]      |
| I (355) system_api: Base MAC address is not set             |
| I (360) phy_init: phy_version 4670,719f9f6,Feb 18 2021      |
| I (410) FINDMY: Starting Google Find My Advertisement...    |
| I (415) FINDMY: Broadcasting Key: 12 34 56...               |
+-------------------------------------------------------------+
```

If you see output similar to the above, your tracker is running!

## Troubleshooting

*   **Port not showing up:** Ensure your USB cable supports data transfer, not just charging. You may also need to install CP210x or CH340 drivers depending on your board.
*   **Failed to connect (Timeout):** Some ESP32 boards require you to hold down the "BOOT" button while connecting/flashing. Press and hold it when the terminal says `Connecting...`.
