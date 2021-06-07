#!/usr/env/python

import base64

from Crypto.PublicKey import RSA as rsa

with open('key1.pem') as __f:
  K1 = rsa.import_key(__f.read())

with open('key2.pem') as __f:
  K2 = rsa.import_key(__f.read())

with open('message1') as __f:
  M1 = __f.read()

with open('message2') as __f:
  M2 = __f.read()

def extended_euclid_gcd(a, b):
    """
    Returns a list `result` of size 3 where:
    Referring to the equation ax + by = gcd(a, b)
        result[0] is gcd(a, b)
        result[1] is x
        result[2] is y
    """
    s = 0; old_s = 1
    t = 1; old_t = 0
    r = b; old_r = a

    while r != 0:
        quotient = old_r//r # In Python, // operator performs integer or floored division
        # This is a pythonic way to swap numbers
        # See the same part in C++ implementation below to know more
        old_r, r = r, old_r - quotient*r
        old_s, s = s, old_s - quotient*s
        old_t, t = t, old_t - quotient*t
    return [old_r, old_s, old_t]

_, x, y = extended_euclid_gcd(K1.e, K2.e)

m1 = int(base64.b64decode(M1).hex(), 16)
m2 = int(base64.b64decode(M2).hex(), 16)

m = pow(m1, x, K1.n) * pow(m2, y, K1.n)
m = m % K1.n

print(bytes.fromhex(hex(m)[2:]))
