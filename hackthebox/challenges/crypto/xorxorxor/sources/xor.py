#!/usr/bin/python3

ENCRYPTED = bytes.fromhex('134af6e1297bc4a96f6a87fe046684e8047084ee046d84c5282dd7ef292dc9')
PREFIX = b'HTB{'

def encrypt(key: bytes, data: bytes) -> bytes:
  return bytes([
    data[i] ^ key[i % len(key)]
    for i in range(len(data))])

if __name__ == "__main__":
  key = encrypt(PREFIX, ENCRYPTED[:4])
  flag = encrypt(key, ENCRYPTED)
  print(flag)
