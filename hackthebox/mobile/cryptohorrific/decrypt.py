#!/usr/bin/env python

import base64
from Crypto.Cipher import AES

CIPHERTEXT = base64.b64decode("Tq+CWzQS0wYzs2rJ+GNrPLP6qekDbwze6fIeRRwBK2WXHOhba7WR2OGNUFKoAvyW7njTCMlQzlwIRdJvaP2iYQ==")
KEY = bytes("!A%D*G-KaPdSgVkY", "utf-8")
IV = bytes("QfTjWnZq4t7w!z%C", "utf-8")

cipher = AES.new(key=KEY, mode=AES.MODE_ECB)
flag = cipher.decrypt(CIPHERTEXT)

print(flag)
