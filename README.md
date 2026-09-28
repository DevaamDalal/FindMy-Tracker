# FindMy Tracker — Dual-Network ESP32 Tracker

DIY tracker that works with both Apple Find My and Google Find My Device networks using ESP32 microcontrollers.

## Architecture

```text
       +-------------------+
       |    FindMy Tracker |
       +--------+----------+
                |
       +--------+--------+
       |                 |
+------v------+   +------v-------+
| Apple Track |   | Google Track |
| (ESP32)     |   | (ESP32)      |
+------+------+   +------+-------+
       |                 |
+------v------+   +------v-------+
|  Apple      |   |  Google      |
|  Find My    |   |  Find My     |
|  Network    |   |  Device      |
+-------------+   +--------------+
```

## Directory Structure

- `apple-findmy/` - Code and resources for the Apple Find My network.
- `google-findmy/` - Code and resources for the Google Find My Device network.
- `setup_all.ps1` - Master setup script.
- `requirements.txt` - Python dependencies.

## Quick Start

1. Ensure you have the hardware and software prerequisites installed.
2. Run `./setup_all.ps1` from PowerShell to prepare your environment.
3. For the Apple track, see [apple-findmy/README.md](apple-findmy/README.md).
4. For the Google track, see [google-findmy/README.md](google-findmy/README.md).

## Hardware Requirements

- 2x ESP32 Development Boards (e.g., ESP32-WROOM-32)
- Micro-USB or USB-C cables (depending on your boards) for programming and power

## Software Requirements

- Python 3.8+
- Docker & Docker Compose
- Git
- VS Code (with recommended extensions)
- ESP-IDF (installed via extensions/scripts)

## Sub-Projects

- [Apple Find My Tracker](apple-findmy/README.md)
- [Google Find My Device Tracker](google-findmy/README.md)

## Legal Disclaimer

This project is for educational and experimental purposes only. It is not affiliated with, endorsed by, or sponsored by Apple Inc. or Google LLC. Use of their respective networks must comply with their terms of service. Do not use this for malicious tracking or any illegal activities.
