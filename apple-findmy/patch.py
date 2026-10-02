import os
text = open('pypush_gsa_icloud_patched.py', 'r').read()
text = text.replace('com.apple.dt.Xcode/3594.4.19', 'com.apple.akd/1.0')
text = text.replace('\
User-Agent\: \Xcode\', '\User-Agent\: \akd\')
open('pypush_gsa_icloud_patched.py', 'w').write(text)
