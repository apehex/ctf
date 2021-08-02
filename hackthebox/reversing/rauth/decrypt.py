#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import binascii
from Crypto.Cipher import Salsa20

cipher = Salsa20.new(key=b'ef39f4f20e76e33bd25f4db338e81b10', nonce=b'd4c270a3')
password = cipher.decrypt(binascii.unhexlify(b'05055fb1a329a8d558d9f556a6cb31f324432a31c99dec72e33eb66f62ad1bf9'))
print (password)
