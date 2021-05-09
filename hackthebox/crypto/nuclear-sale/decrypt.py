#!/usr/bin/python

# the encrypted hashes
h1 = 0x6b65813f4fe991efe2042f79988a3b2f2559d358e55f2fa373e53b1965b5bb2b175cf039
h2 = 0xfd034c32294bfa6ab44a28892e75c4f24d8e71b41cfb9a81a634b90e6238443a813a3d34
h3 = 0xde328f76159108f7653a5883decb8dec06b0fd9bc8d0dd7dade1f04836b8a07da20bfe70

# assumptions:
# h1 = k1 ^ m1
# h2 = k2
# h3 = k1 ^ k2
# so h2 ^ h3 = k2 ^ k1 ^ k2 = k1
# and h2 ^ h3 ^ h1 = k1 ^ k1 ^ m1 = m1
m = h1 ^ h2 ^ h3

# now we interpret the hex as ASCII
print(bytes.fromhex(hex(m)[2:]))
