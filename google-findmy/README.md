# Google Find My Device - ESP32 Tracker

This directory contains the necessary scripts and documentation to set up an ESP32 as a tracker on the Google Find My Device network. This setup relies on the excellent [GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools) project by Leon Böttger.

## Overview

The Google Find My Device network allows you to track offline devices by broadcasting a unique Bluetooth Low Energy (BLE) advertisement. Nearby Android devices pick up this advertisement and anonymously report the location back to Google's servers. By running a custom firmware on the ESP32 and registering it with your Google account, you can turn the ESP32 into a tracker.

## Prerequisites

Before starting, ensure you have the following:

1.  **ESP32 Development Board:** Any standard ESP32 board with Bluetooth support.
2.  **Visual Studio Code (VS Code):** Used for editing and building the firmware.
3.  **ESP-IDF Extension for VS Code:** Required for compiling the firmware.
4.  **Python 3.x:** Required to run the registration and location scripts.
5.  **Git:** Required to clone the GoogleFindMyTools repository.
6.  **Google Chrome:** Required by the Python registration script (uses selenium/undetected_chromedriver).
7.  **Google Account:** Must be an account currently in use on a real, active Android device.

## Step-by-Step Setup Instructions

1.  **Run the Setup Script:**
    Open PowerShell, navigate to this directory, and run the setup script to install dependencies and clone the required repository:
    ```powershell
    .\setup.ps1
    ```

2.  **Register the Tracker:**
    Run the registration script. This will open a Chrome browser window where you must log in to your Google Account.
    ```powershell
    .\register_tracker.ps1
    ```
    *Important:* Save the generated "Advertisement Key" output from this step. You will need it for the firmware.

3.  **Configure and Flash Firmware:**
    *   Follow the instructions in `firmware/README.md` to configure the ESP32 firmware.
    *   You will need to insert your Advertisement Key into the firmware source code.
    *   Build and flash the firmware to your ESP32.

4.  **Locate the Tracker:**
    Once the ESP32 is running and broadcasting, you can locate it using the location script:
    ```powershell
    .\locate_tracker.ps1
    ```

## Known Limitations

*   **Key Rotation / Re-registration:** Due to how the unofficial API interacts with Google's servers, the tracker registration typically expires every 3-4 days. You must re-run the registration script (or use `auto_reregister.ps1`) and update the firmware key (or have a dynamic key loading mechanism) to keep it trackable.
*   **No Official App Support:** The tracker will *not* show up in the official "Find My Device" app on your phone. You can only view its location using the Python script provided in this toolkit.
*   **Location Only:** Only location tracking is supported. Features like "Play Sound" or "Mark as Lost" are not available.
*   **Account Requirements:** The Google account used must be active on a real Android device; otherwise, the Find My Device network features may not work properly.

## Troubleshooting

*   **Chrome Driver Errors:** If the registration script fails to open Chrome, ensure you have the latest version of Google Chrome installed and that it's accessible in your system path.
*   **No Location Found:** If the locate script returns no location, ensure the ESP32 is powered on, has been near other Android devices, and that the advertisement key in the firmware exactly matches the one registered. Remember that it can take time for reports to propagate.
*   **ESP-IDF Build Issues:** Ensure you have correctly configured the ESP-IDF extension in VS Code. Clean the build folder and rebuild.

## Upstream Repository

This project utilizes tools from:
[https://github.com/leonboe1/GoogleFindMyTools](https://github.com/leonboe1/GoogleFindMyTools)
