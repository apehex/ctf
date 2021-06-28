# -*- coding: utf-8 -*-

import socketserver
from Crypto.Cipher import AES
import os

# ========================================================= block manipulations

def chunk(l, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

# ===================================================================== padding

FIBOPADCCI = bytes([1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121, 98, 219, 61])

def pad(data: bytes, right: bool=True, fill: bytes=FIBOPADCCI, until: int=16) -> bytes:
    """
    Pad until the total length reaches a block size.
    """
    l = len(data) % until
    if right:
        return data + fill[:until-l]
    else:
        return fill[:until-l] + data

def checkpad(data: bytes) -> bytes:
    
    if len(data) % 16:
        return 0
    char = data[-1]

    try:
        start = FIBOPADCCI.index(char)
    except ValueError:
        return 0
    
    newfibopadcci = FIBOPADCCI[:start][::-1]

    for i in range(len(newfibopadcci)):
        char = data[-(i+2)]
        if char != newfibopadcci[i]:
            return 0
    return 1

# ==================================================================== encoding

def int_to_byte(n: int) -> bytes:
    __h = str(hex(n % 256))[2:]
    return bytes.fromhex("0" * (2-len(__h)) + __h)

def to_bytes(data) -> bytes:
    if type(data) == int:
        return int_to_byte(data)
    elif type(data) == bytes:
        return data
    elif type(data) == str and is_hex(data):
        return bytes.fromhex(data)
    return b''

def is_hex(data: str) -> bool:
    try:
        int(data, 16)
        return True
    except:
        return False

def unhex(data: str) -> bytes:
    return bytes.fromhex(data)

# ========================================================================= xor

def xor(a: bytes, b: bytes) -> bytes:
    return bytes([_a ^ _b for _a, _b in zip(a, b)])

def mask(message: bytes, pattern: bytes) -> bytes:
    q = len(message) // len(pattern)
    r = len(message) % len(pattern)
    return xor(message, (pattern * q) + pattern[:r])

# ========================================================================= aes

class SuperSecureEncryption: # This should be unbreakable!
    def __init__(self, key):
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, data):
        data = pad(data)
        
        a = os.urandom(16).replace(b'\x00', b'\xff') 
        b = os.urandom(16).replace(b'\x00', b'\xff')

        lb_plain = a
        lb_cipher = b
        output = b''

        for block in chunk(data, 16):
            enc = self.cipher.encrypt(xor(lb_cipher, block))
            enc = xor(enc, lb_plain)
            output += enc
            lb_plain = block
            lb_cipher = enc

        return output, a.hex(), b.hex()

    def decrypt(self, data, a, b):
        lb_plain = a
        lb_cipher = b
        output = b''

        for block in chunk(data, 16):
            dec = self.cipher.decrypt(xor(block, lb_plain))
            dec = xor(dec, lb_cipher)
            output += dec
            lb_plain = dec
            lb_cipher = block

        if checkpad(output):
            return output
        else:
            return None

# ============================================================ encryption tests

def main():
    KEY    = b'16bytesofsupersecretkeyunpadded_'
    A      = bytes.fromhex("dc3b5c7b9cf0aa2a02eab3a36e8f9e10")
    B      = bytes.fromhex("7a5395c3b1d5be7d22a470918895bb74")
    CT     = bytes.fromhex("c482b25753c1d815270e60f030d634b56f7785e064cc5ee83352fd5f34d9f067432b19deb92328b2a20ea59a72165f66")
    A_     = b'HTB{th3_s3crt_A}'
    AA_    = xor(A, A_)
    B_     = mask(B, AA_)
    CT_    = mask(CT, AA_)
    CIPHER = SuperSecureEncryption(KEY)

    print(f'ct:\t{CT.hex()}\nct_:\t{CT_.hex()}\na:\t{A.hex()}\na_:\t{A_.hex()}\nb:\t{B.hex()}\n')

# ======================================================================== main

if __name__ == "__main__":
    main()
