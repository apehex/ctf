#!/usr/bin/env python

import base64
from Crypto.Cipher import AES
cipher = AES.new(bytes("kV9qhuzZkvvrgW6F", "utf-8"), AES.MODE_ECB)
flag = cipher.decrypt(base64.b64decode("1UlBm2kHtZuVrSE6qY6HxWkwHyeaX92DabnRFlEGyLWod2bkwAxcoc85S94kFpV1"))

print(flag)
