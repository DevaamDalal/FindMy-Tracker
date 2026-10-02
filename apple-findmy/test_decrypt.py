import os
import json
import base64
import struct
import datetime
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import urllib.request

hashed_adv_key = "k4iK+dqBDT48rLZ0uWyKGmwPRzvA6FU9GG3+mx8BWfk="
priv_key_b64 = "U4ESsr9qcnINi9PowMrFykF+OKvWcFlkGs+w/A=="

payload = {"days": 7, "ids": [hashed_adv_key]}
req = urllib.request.Request("http://localhost:6176/", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    res = json.loads(response.read().decode())

reports = res.get('results', [])
priv_bytes = base64.b64decode(priv_key_b64)
priv_key = ec.derive_private_key(int.from_bytes(priv_bytes, "big"), ec.SECP224R1())

print(f"Found {len(reports)} reports")
for rep in reports:
    try:
        data = base64.b64decode(rep['payload'])
        if len(data) > 88: data = data[:4] + data[5:]
        timestamp = struct.unpack(">I", data[0:4])[0] + 978307200
        pub_key_bytes = data[5:62]
        ciphertext = data[62:72]
        auth_tag = data[72:88]
        
        pub_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), pub_key_bytes)
        shared_key = priv_key.exchange(ec.ECDH(), pub_key)
        
        digest = hashes.Hash(hashes.SHA256())
        digest.update(shared_key)
        digest.update(b"\x00\x00\x00\x01")
        digest.update(pub_key_bytes)
        derived_key = digest.finalize()
        
        aes_key = derived_key[:16]
        iv = derived_key[16:]
        
        aesgcm = AESGCM(aes_key)
        decrypted = aesgcm.decrypt(iv, ciphertext + auth_tag, None)
        
        lat = struct.unpack(">i", decrypted[0:4])[0] / 10000000.0
        lon = struct.unpack(">i", decrypted[4:8])[0] / 10000000.0
        acc = decrypted[8]
        
        time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print(f"Success! lat={lat}, lon={lon}, acc={acc}, time={time_str}")
    except Exception as e:
        print(f"Decryption error: {repr(e)}")
