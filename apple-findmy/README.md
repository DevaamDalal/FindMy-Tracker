# Apple Find My (Macless-Haystack) Tracker

This directory contains the setup for the Apple Find My tracking component of the dual-network ESP32 tracker. We use the [Macless-Haystack](https://github.com/dchristl/macless-haystack) project to achieve this without requiring a Mac.

## Overview
The ESP32 broadcasts a custom BLE beacon containing an advertisement key (derived from a generated ECDSA P-224 keypair). Apple devices nearby pick up this beacon and report its location (encrypted) to Apple's Find My network. You can then retrieve and decrypt these location reports using the Macless-Haystack server and your private key.

## Prerequisites
- **Python 3.x**
- **Docker** and **Docker Compose**
- **esptool** (installed automatically via setup script)
- **A throwaway Apple ID** (requires SMS 2FA - do not use your main Apple ID)
- An **ESP32** development board

## Step-by-Step Setup

1. **Run the Setup Script**
   Run the PowerShell setup script to check dependencies and install required Python packages:
   ```powershell
   .\setup.ps1
   ```

2. **Generate Keys**
   Generate the ECDSA P-224 keypair for your tracker:
   ```powershell
   python generate_keys.py
   ```
   *Make note of the Base64 advertisement key printed to the console. You will need this for the firmware.*

3. **Start the Servers**
   Start the Anisette server and Macless-Haystack endpoint using Docker Compose:
   ```powershell
   docker-compose up -d
   ```
   *The haystack server will be accessible at http://localhost:6176. You'll need to log in with your throwaway Apple ID.*

4. **Flash the ESP32**
   Follow the instructions in `firmware/README.md` to download the firmware, embed your advertisement key, and flash it to the ESP32 using `firmware/flash.ps1`.

## Troubleshooting
- **Docker Containers Won't Start:** Ensure ports 6969 and 6176 are not in use by other applications.
- **Can't Login to Apple ID:** Verify your Anisette server is running properly and that you're using a fresh, dedicated Apple ID.
- **No Locations Showing:** It can take several hours for Apple devices to pick up and report the beacon. Ensure the ESP32 is powered and the BLE beacon is broadcasting.
