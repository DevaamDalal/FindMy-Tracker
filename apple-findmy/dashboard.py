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
        <div>
            <a href="/timeline" style="color: white; text-decoration: none; margin-right: 20px; font-size: 14px; border: 1px solid white; padding: 4px 10px; border-radius: 4px;">View Timeline</a>
            <div class="info" id="status" style="display:inline-block;"><span class="pulse"></span>Scanning for reports...</div>
        </div>
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
                    var name = latest.name ? latest.name : "Tracker";
                    marker.bindPopup("<b>ESP32 AirTag (" + name + ")</b><br>Last seen: " + latest.time + "<br>Accuracy: " + latest.acc + "m").openPopup();
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

TIMELINE_HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>FindMy Tracker Timeline</title>
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
        <h1>📍 FindMy Tracker - Timeline</h1>
        <div>
            <a href="/" style="color: white; text-decoration: none; margin-right: 20px; font-size: 14px; border: 1px solid white; padding: 4px 10px; border-radius: 4px;">Back to Live Map</a>
            <div class="info" id="status" style="display:inline-block;"><span class="pulse"></span>Loading history...</div>
        </div>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
        var mapLayerGroup = L.layerGroup().addTo(map);
        
        function updateTimeline() {
            fetch('/data')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('status').innerHTML = '❌ Error: ' + data.error;
                        return;
                    }
                    if (data.length === 0) {
                        document.getElementById('status').innerHTML = '<span class="pulse" style="background:#ff9500;box-shadow:0 0 8px #ff9500;"></span>No history available yet.';
                        return;
                    }
                    
                    mapLayerGroup.clearLayers();
                    
                    // Group data by tracker name
                    const trackers = {};
                    data.forEach(loc => {
                        let n = loc.name ? loc.name : "Tracker";
                        if (!trackers[n]) trackers[n] = [];
                        trackers[n].push(loc);
                    });
                    
                    let bounds = L.latLngBounds();
                    
                    // Render each tracker
                    Object.keys(trackers).forEach((name, tIndex) => {
                        let locs = trackers[name];
                        locs.sort((a, b) => a.ts - b.ts); // oldest to newest
                        
                        let latlngs = locs.map(loc => [loc.lat, loc.lon]);
                        let pathColor = ['blue', 'red', 'green', 'purple', 'orange'][tIndex % 5];
                        
                        // Draw Polyline
                        L.polyline(latlngs, {color: pathColor, weight: 3, opacity: 0.7}).addTo(mapLayerGroup);
                        
                        // Draw Points
                        locs.forEach((loc, index) => {
                            let isLatest = (index === locs.length - 1);
                            let popupText = `<b>${name}</b><br>Seen: ${loc.time}<br>Accuracy: ${loc.acc}m`;
                            bounds.extend([loc.lat, loc.lon]);
                            
                            if (isLatest) {
                                L.marker([loc.lat, loc.lon]).bindPopup(popupText + " <b>(Current)</b>").addTo(mapLayerGroup);
                                L.circle([loc.lat, loc.lon], {radius: loc.acc, color: pathColor, fillColor: pathColor, fillOpacity: 0.1}).addTo(mapLayerGroup);
                            } else {
                                L.circleMarker([loc.lat, loc.lon], {radius: 5, color: pathColor, fillColor: 'white', fillOpacity: 1, weight: 2})
                                 .bindPopup(popupText).addTo(mapLayerGroup);
                            }
                        });
                    });
                    
                    map.fitBounds(bounds, {padding: [50, 50]});
                    document.getElementById('status').innerHTML = '<span class="pulse"></span>Timeline updated.';
                })
                .catch(e => {
                    document.getElementById('status').innerHTML = '❌ Connection lost...';
                });
        }
        updateTimeline();
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
        elif self.path == '/timeline':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(TIMELINE_HTML_PAGE.encode('utf-8'))
        elif self.path == '/data':
            try:
                keys = []
                for filename in os.listdir('keys'):
                    if filename.endswith('.keys'):
                        with open(os.path.join('keys', filename), 'r') as f:
                            hashed_adv_key = None
                            priv_key_b64 = None
                            for line in f:
                                if line.startswith('Hashed adv key:'):
                                    hashed_adv_key = line.split(':', 1)[1].strip()
                                elif line.startswith('Private key:'):
                                    priv_key_b64 = line.split(':', 1)[1].strip()
                            if hashed_adv_key and priv_key_b64:
                                keys.append({'hash': hashed_adv_key, 'priv': priv_key_b64, 'name': filename.split('.')[0]})
                
                decrypted_list = []
                for key_data in keys:
                    payload = {"days": 7, "ids": [key_data['hash']]}
                    try:
                        req = urllib.request.Request("http://localhost:6176/", data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                        with urllib.request.urlopen(req) as response:
                            res = json.loads(response.read().decode())
                        reports = res.get('results', [])
                    except Exception as e:
                        print(f"Fetch error for {key_data['name']}: {e}")
                        reports = []
                    
                    priv_bytes = base64.b64decode(key_data['priv'])
                    priv_key = ec.derive_private_key(int.from_bytes(priv_bytes, "big"), ec.SECP224R1())
                
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
                            decrypted_list.append({"lat": lat, "lon": lon, "acc": acc, "time": time_str, "ts": timestamp, "name": key_data['name']})
                        except Exception as e:
                            with open("error.log", "a") as errf: errf.write(f"Decryption error: {e}\n")
                
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
