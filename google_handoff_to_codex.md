# Google Find My Tracker - Handoff to Codex

This document summarizes the state of the Google Find My Device Network (FMDN) tracker implementation. Apple Find My development continues separately.

## 1. Project State and Limitations
**Goal:** Register a custom ESP32 BLE tracker on Google's Find My Device Network using Leon Böttger's `GoogleFindMyTools`. 

**Current Blocker:** Google strictly requires the registering account to have an active End-to-End Encryption (E2EE) vault created by an Android device. 
- The user attempted registration with a secondary account (`devaamsvnit@gmail.com`) that did not have an active vault.
- Previous development implemented a "Fake Vault Key Bypass" in the Python tooling. 
- *Observed Result:* The Python script sent the `RegisterBleDeviceRequest` to Google. Google returned HTTP `200 OK` with an **empty gRPC payload** (`b''`), which previously crashed the gRPC parser. The script generated an Advertisement Key locally.
- *Observed Result:* When attempting to fetch locations via `NOVA_LIST_DEVICS_API_SCOPE`, the returned device list is completely empty (`[]`).
- *Assumption / Conclusion:* Google's backend silently drops `CreateBleDevice` requests if the `encryptedIdentityKey` does not trace back to a valid FMDN vault on the account.

## 2. Code Modifications (GoogleFindMyTools)

Since `GoogleFindMyTools` is an ignored submodule/nested repo, a `.patch` file of all modifications has been generated at the root of the workspace: `google_findmy_tools_modifications.patch`.

*Upstream Commit SHA:* `d46e9528578015b51d3b84dd91bf8f16e9ab850f`

### Summary of Changes in Python Tools:
1. **`SpotApi/GetEidInfoForE2eeDevices/get_owner_key.py`**
   - Modified to bypass the `_retrieve_owner_key` vault logic. If no vault exists, it checks for a local `fake_owner_key.json` and generates a random 32-byte hex key if missing. (This bypasses the local crash but does not bypass Google's server validation).
2. **`SpotApi/grpc_parser.py`**
   - Modified `extract_grpc_payload` to gracefully return `b''` if `len(grpc) == 0`. Google's `CreateBleDevice` API returns an empty `200 OK` response if the vault is invalid, which previously caused a `ValueError`.

## 3. ESP32 Firmware & Build Instructions

### Configuration
The `google-findmy/firmware` repository originally lacked Bluetooth defaults for the standard ESP32 target. We created `google-findmy/firmware/sdkconfig.defaults` with the following:
```ini
CONFIG_BT_ENABLED=y
CONFIG_BT_BLUEDROID_ENABLED=y
CONFIG_BT_BLE_ENABLED=y
```

### Build Command (Isolated Docker Build)
To bypass Windows WSL2 NTFS file-locking crashes during CMake builds, we mapped the volume but executed the build in an isolated `/tmp/` directory, then copied the binaries back out.
```powershell
docker run --rm -v "C:\Users\devaa\OneDrive\Documents\Antigraity\FindMy\google-findmy\firmware:/project" espressif/idf:latest bash -c "cp -r /project /tmp/firmware && cd /tmp/firmware && rm -rf build sdkconfig && idf.py set-target esp32 && idf.py build && mkdir -p /project/build_output && cp build/ESPFindMy.bin build/bootloader/bootloader.bin build/partition_table/partition-table.bin /project/build_output/"
```
*(This command succeeded completely. The `build_output` folder is intentionally ignored in `.gitignore`).*

### Flash Command
Flashing was performed successfully via Windows `esptool` with the following memory offsets:
```powershell
python -m esptool --chip esp32 -p COM4 -b 460800 --before default-reset --after hard-reset write-flash --flash-mode dio --flash-size 2MB --flash-freq 40m 0x1000 build_output\bootloader.bin 0x8000 build_output\partition-table.bin 0x10000 build_output\ESPFindMy.bin
```

## 4. Sanitized Logs

### 4.1 Registration Crash (Before `grpc_parser.py` Patch)
```text
Traceback (most recent call last):
  File "/app/GoogleFindMyTools/main.py", line 10, in <module>
    list_devices()
  File "/app/GoogleFindMyTools/SpotApi/CreateBleDevice/create_ble_device.py", line 83, in register_esp32
    spot_request("CreateBleDevice", bytes_data)
  File "/app/GoogleFindMyTools/SpotApi/grpc_parser.py", line 11, in extract_grpc_payload
    raise ValueError("Invalid GRPC payload")
ValueError: Invalid GRPC payload
```
*(The payload length was 0 bytes, HTTP status 200)*

### 4.2 Empty Device List Log (After Registration with Fake Key)
```text
The following trackers are available:

If you want to see locations of a tracker, type the number of the tracker and press 'Enter'.
Traceback (most recent call last):
  File "/app/GoogleFindMyTools/main.py", line 10, in <module>
    list_devices()
  File "/app/GoogleFindMyTools/NovaApi/ListDevices/nbe_list_devices.py", line 68, in list_devices
    selected_idx = int(selected_value) - 1
ValueError: invalid literal for int() with base 10: ''
```
*(The raw `parse_device_list_protobuf(result_hex)` returned `[]` with no `deviceMetadata` entries).*

## 5. Security & Sanitization
- All real Advertisement Keys have been stripped from the firmware (`main.c` line 30 replaced with `INSERT_YOUR_ADVERTISEMENT_KEY_HERE`).
- `advertisement_key.txt` was deleted.
- `.gitignore` was updated to ignore auth tokens, keys, and `build_output`.
