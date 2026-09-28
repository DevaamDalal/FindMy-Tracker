import os
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption, PublicFormat

# Constants
KEYS_DIR = "keys"
DEVICE_NAME = "ESP32_FindMy_Tracker"

def main():
    print("Generating Apple Find My Keys...")
    
    # Ensure keys directory exists
    os.makedirs(KEYS_DIR, exist_ok=True)
    
    # 1. Generate a P-224 private key
    # Apple's Find My network relies on ECDSA P-224 keypairs.
    private_key = ec.generate_private_key(ec.SECP224R1())
    
    # 2. Derive the public key (Advertisement key)
    public_key = private_key.public_key()
    
    # Save the private key in PEM format (required by Haystack)
    priv_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )
    
    priv_key_path = os.path.join(KEYS_DIR, "private_key.pem")
    with open(priv_key_path, "wb") as f:
        f.write(priv_pem)
    
    print(f"Private key saved to {priv_key_path}")

    # Extract the raw bytes of the public key (uncompressed format)
    # The first byte is 0x04 (indicating uncompressed), followed by X and Y coordinates (28 bytes each)
    pub_bytes = public_key.public_bytes(
        encoding=Encoding.X962,
        format=PublicFormat.UncompressedPoint
    )
    
    # The advertisement key is just the X coordinate (bytes 1-28)
    adv_key_bytes = pub_bytes[1:29]
    
    # Encode as Base64 for easy copying/pasting into firmware or configs
    adv_key_b64 = base64.b64encode(adv_key_bytes).decode('utf-8')
    
    # Save a generic devices.json for Macless-Haystack dashboard
    # You might need to update this structure depending on the specific Macless-Haystack version,
    # but typically it just maps a label to the key.
    devices_data = {
        adv_key_b64: {
            "name": DEVICE_NAME,
            "private_key": priv_pem.decode('utf-8')
        }
    }
    
    devices_path = os.path.join(KEYS_DIR, "devices.json")
    with open(devices_path, "w") as f:
        json.dump(devices_data, f, indent=4)
        
    print(f"Device registry saved to {devices_path}")
    
    print("\n" + "="*50)
    print("SUCCESS: Keys Generated!")
    print("="*50)
    print("Your Base64 Advertisement Key (for ESP32 Firmware):")
    print(f"\n    {adv_key_b64}\n")
    print("Keep your private_key.pem safe. It is required to decrypt locations.")

if __name__ == "__main__":
    main()
