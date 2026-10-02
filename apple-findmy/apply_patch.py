import os

with open('pypush_gsa_icloud_patched.py', 'r') as f:
    text = f.read()

text = text.replace('com.apple.dt.Xcode/3594.4.19', 'com.apple.akd/1.0')
text = text.replace('"User-Agent": "Xcode"', '"User-Agent": "akd"')
text = text.replace('"X-Xcode-Version": "11.2 (11B41)",', '')

with open('pypush_gsa_icloud_patched.py', 'w') as f:
    f.write(text)
