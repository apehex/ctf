import socketserver
from Crypto.Cipher import AES
import os

# ========================================================================= FIB

fib = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 121, 98, 219, 61]

# ========================================================================= AES

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

        for block in chunks(data, 16):
    
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
        for block in chunks(data, 16):
            dec = self.cipher.decrypt(xor(block, lb_plain))
            dec = xor(dec, lb_cipher)
            output += dec
            lb_plain = dec
            lb_cipher = block
        return output
        # if checkpad(output):
        #     return output
        # else:
        #     return None

# ============================================================== tcp connection

HOST = "127.0.0.1"
PORT = "1337"

def check_response():
    pass

# ================================================================ bruteforcing

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+{}'

def bruteforce():
    for a0 in ALPHABET:
        for a1 in ALPHABET:
            for a2 in ALPHABET:
                for a3 in ALPHABET:
                    for a4 in ALPHABET:
                        for a5 in ALPHABET:
                            for a6 in ALPHABET:
                                for a7 in ALPHABET:
                                    for a8 in ALPHABET:
                                        for a9 in ALPHABET:
                                            for a10 in ALPHABET:
                                                yield bytes(
                                                    f'HTB{{{a0}{a1}{a2}{a3}{a4}{a5}{a6}{a7}{a8}{a9}{a10}}}',
                                                    'utf-8')

# =================================================================== utilities

def chunks(l, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def int_to_byte(n: int) -> str:
    __h = str(hex(n % 255))[2:]
    return bytes.fromhex("0" * (2-len(__h)) + __h)

def xor(a: bytes, b: bytes) -> bytes:
    return bytes([_a ^ _b for _a, _b in zip(a, b)])

def pad(data: bytes) -> bytes: #Custom padding, should be fine!
    c = 0
    while len(data) % 16:
        data += int_to_byte(fib[c])
        c += 1
    return data

def checkpad(data: bytes) -> bytes:
    
    if len(data) % 16:
        return 0
    char = data[-1]

    try:
        start = fib.index(char)
    except ValueError:
        return 0
    
    newfib = fib[:start][::-1]

    for i in range(len(newfib)):
        char = data[-(i+2)]
        if char != newfib[i]:
            return 0
    return 1

# =============================================================== change the IV

def mask(
        message: bytes,
        pattern: bytes) -> bytes:
    if len(message) % len(pattern):
        return None
    else:
        __mask = pattern * (len(message) // len(pattern))
        return xor(message, __mask)

# ============================================================ encryption tests

KEY    = b'16bytesofsupersecretkeyunpadded_'
A      = bytes.fromhex("98a8ea331fa71a7fdf2824d9ff70460e")
B      = bytes.fromhex("0afb737c2a61819637c95a3bd96dad87")
CT     = bytes.fromhex("6caa603e2e74aa50270411cec6d5cb027f75a5b68fecc1403542392c7421617d9e644968c6f43691909e7146422455f4")
A_     = b'HTB{th3_s3crt_A}'
AA_    = xor(A, A_)
B_     = mask(B, AA_)
CT_    = mask(CT, AA_)
CIPHER = SuperSecureEncryption(KEY)

# ======================================================================== main

print(f'ct:\t{CT.hex()}\nct_:\t{CT_.hex()}\na:\t{A.hex()}\na_:\t{A_.hex()}\nb:\t{B.hex()}\n')
