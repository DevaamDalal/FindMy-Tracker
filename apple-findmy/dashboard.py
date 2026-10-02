import os
import json
import base64
import struct
import datetime
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.x963kdf import X963KDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import webbrowser
import threading

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>FindMy Tracker Dashboard</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; display: flex; flex-direction: column; height: 100vh; }
        #header { background: #1a1a1a; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0,0,0,0.5); z-index: 1000; position: relative;}
        #map { flex: 1; z-index: 1;}
        h1 { margin: 0; font-size: 22px; font-weight: 500;}
        .info { font-size: 14px; background: #333; padding: 6px 12px; border-radius: 20px;}
        .pulse { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #4cd964; margin-right: 6px; box-shadow: 0 0 8px #4cd964;}
    </style>
</head>
<body>
    <div id="header">
        <h1>📡 FindMy Tracker</h1>
        <div class="info" id="status"><span class="pulse"></span>Scanning for reports...</div>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        var marker = null;
        var circle = null;
        
        function updateMap() {
            fetch('/data')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('status').innerHTML = '❌ Error: ' + data.error;
                        return;
                    }
                    if (data.length === 0) {
                        document.getElementById('status').innerHTML = '<span class="pulse" style="background:#ff9500;box-shadow:0 0 8px #ff9500;"></span>No locations yet. Waiting for iPhone ping...';
                        return;
                    }
                    var latest = data[0];
                    if (!marker) {
                        marker = L.marker([latest.lat, latest.lon]).addTo(map);
                        circle = L.circle([latest.lat, latest.lon], {radius: latest.acc, color: '#007aff', fillColor: '#007aff', fillOpacity: 0.2}).addTo(map);
                        map.setView([latest.lat, latest.lon], 16);
                    } else {
                        marker.setLatLng([latest.lat, latest.lon]);
                        circle.setLatLng([latest.lat, latest.lon]);
                        circle.setRadius(latest.acc);
                    }
                    marker.bindPopup("<b>ESP32 AirTag</b><br>Last seen: " + latest.time + "<br>Accuracy: " + latest.acc + "m").openPopup();
                    document.getElementById('status').innerHTML = '<span class="pulse"></span>Last updated: ' + latest.time;
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = '❌ Connection lost...';
                });
        }
        updateMap();
        setInterval(updateMap, 30000); // Check every 30 seconds
    </script>
</body>
</html>
"""

class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/data':
            try:
                hashed_adv_key = None
                priv_key_b64 = None
                with open('keys/SC11KR.keys', 'r') as f:
                    for line in f:
                        if line.startswith('Hashed adv key:'):
                            hashed_adv_key = line.split(':', 1)[1].strip()
                        elif line.startswith('Private key:'):
                            priv_key_b64 = line.split(':', 1)[1].strip()
                
                payload = {"days": 1, "ids": [hashed_adv_key]}
                req = urllib.request.Request("http://localhost:6176/", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req) as response:
                    res = json.loads(response.read().decode())
                
                reports = res.get('results', [])
                decrypted_list = []
                
                priv_bytes = base64.b64decode(priv_key_b64)
                priv_key = ec.derive_private_key(int.from_bytes(priv_bytes, "big"), ec.SECP224R1())
                
                for rep in reports:
                    try:
                        data = base64.b64decode(rep['payload'])
                        timestamp = struct.unpack(">I", data[0:4])[0] + 978307200
                        pub_key_bytes = data[5:62]
                        hint = data[62:66]
                        auth_tag = data[66:82]
                        ciphertext = data[82:]
                        
                        pub_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP224R1(), pub_key_bytes)
                        shared_key = priv_key.exchange(ec.ECDH(), pub_key)
                        
                        kdf = X963KDF(algorithm=hashes.SHA256(), length=32, sharedinfo=b"\x00\x00\x00\x01" + pub_key_bytes)
                        derived_key = kdf.derive(shared_key)
                        
                        aes_key = derived_key[:16]
                        iv = derived_key[16:]
                        
                        aesgcm = AESGCM(aes_key)
                        decrypted = aesgcm.decrypt(iv, ciphertext + auth_tag, None)
                        
                        lat = struct.unpack(">i", decrypted[0:4])[0] / 10000000.0
                        lon = struct.unpack(">i", decrypted[4:8])[0] / 10000000.0
                        acc = decrypted[8]
                        
                        time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        decrypted_list.append({"lat": lat, "lon": lon, "acc": acc, "time": time_str, "ts": timestamp})
                    except Exception as e:
                        pass
                
                decrypted_list.sort(key=lambda x: x['ts'], reverse=True)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(decrypted_list).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass # Suppress logging to keep console clean

if __name__ == '__main__':
    server = HTTPServer(('localhost', 6177), TrackerHandler)
    print("="*50)
    print("MAP DASHBOARD RUNNING!")
    print("Open your browser to: http://localhost:6177")
    print("="*50)
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open('http://localhost:6177')
    threading.Thread(target=open_browser).start()
    server.serve_forever()
