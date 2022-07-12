#!/usr/bin/env python

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

#################################################################### parameters

CT_FLAG = 0x4845da3014a52429e914c3117b1c45a0a68d6454e83057af6fcadadae011814d0a
CT_KEY = 0x13822f9028b100e2b345a1ad989d9cdedbacc3c706c9454ec7d63abb15b58bef8ba545bb0a3b883f91bf12ca12437eb42e26eff38d0bf4f31cf1ca21c080f11877a7bb5fa8ea97170c932226eab4812c821d082030100030d84ebc63fd8767cde994e0bd1a1f905c27fb0d7adb55e3a1f101d8b5b997ba6b1c09a5e1cc65a9206906ef5e01f13d7beeebdf389610fb54676f76ec0afc51a304403d44bb3c739fd8276f0895c3587a710d15e43fc67284070519e6e0810caf86b134f02ec54018
E = 0x10001
N = 0x77d1e32bfe41fb07612bcb952e8b196d9c303941dd1947d4fb5e0fb80dea75382a1c8c951ce7394408edc801d3cd9bb4c5acd6eb0f61f512aea903b3ed440ebcf3c38d8c1baf3762f2e52517dc3b6b3273e60d2530eab551d6e55dd2349d89f96282c34039f9a6f6a80fac7e144586f3c9ee0b0bbd48fe6e5b79ab07b219585e30e42fcbe59723e562fe3c2d956de2b76e6404b654a04483060f8764a9f1cf7320709e97ae831d8cf3f04c7d9ff2c3ab0932358c9ccd518c49f4943440f4ebc7
P = 0xc6c36983462083ed3b98a4681b44a0a7cbd177d16b41a1ecc924ade2f5e9af0bfc3658e888624f4679240468b4e9a3cc592261e52e9ddee05742ccb1c20aa2d7

################################################################# factorization

phi = (P - 1) * pow(P, 2) # N = P ** 3 => phi(N) = (P-1) * (P ** 2)
d = pow(E, -1, phi)

############################################################ decrypting the key

key = pow(CT_KEY, d, N)

########################################################### decrypting the data

data = pad(bytes.fromhex(hex(CT_FLAG)[2:]),16)
cipher = AES.new(bytes.fromhex(hex(key)[2:]), AES.MODE_ECB)

print(cipher.decrypt(data))
