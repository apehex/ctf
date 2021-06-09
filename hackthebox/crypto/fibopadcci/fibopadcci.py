import argparse

from Crypto.Cipher import AES

# ============================================================== tcp connection

HOST = 127.0.0.1
PORT = 1337

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

def int_to_byte(n: int) -> str:
    __h = str(hex(n % 255))[2:]
    return bytes.fromhex("0" * (2-len(__h)) + __h)

def xor(a: bytes, b: bytes) -> bytes:
    return bytes([_a ^ _b for _a, _b in zip(a, b)])

def pad(data): #Custom padding, should be fine!
    c = 0
    while len(data) % 16:
        data += int_to_byte(fib[c])
        c += 1
    return data

# =============================================================== change the IV

def change_plain_iv(
        ct: bytes,
        old: bytes,
        sub: bytes) -> bytes:
    if len(ct) % 16:
        return None
    else:
        return xor(xor(ct[:16], old), sub) + ct[16:]

# ask for the encrypted flag
def main():
    ct = bytes.fromhex("434d6b77c1b4396326d008b2dab8415b")
    a = bytes.fromhex("a8934508402a306729d2a82d32dea41b")
    b = bytes.fromhex("b6ba9921ac82c44b5ee20b52345e1076")

    flags = bruteforce()

    while True:
        pass

if __name__ == '__main__':
    main()
