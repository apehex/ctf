#!/usr/bin/env python

import base64
from Crypto.Cipher import AES

CIPHERTEXT = base64.b64decode("sjAbajc4sWMUn6CHJBSfQ39p2fNg2trMVQ/MmTB5mno=")
KEY = base64.b64decode("6F+WgzEp5QXodJV+iTli4Q==")
IV = base64.b64decode("DZ6YdaWJlZav26VmEEQ31A==")

cipher = AES.new(key=KEY, mode=AES.MODE_CBC, iv=IV)
flag = cipher.decrypt(CIPHERTEXT)

print(flag)
