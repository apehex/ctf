import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

############################################################ the encrypted data

PASSWORD = 'z64&Rx27Z$B%73up'.encode()
IV = bytes.fromhex('9907bb679e1765dcbdb467c1c4b00d21')
KEY = hashlib.sha256(PASSWORD).digest()

with open('payloads/9tVI0', 'rb') as shellcode_file:
    RAW = shellcode_file.read()

##################################################################### utilities

def xor(m: bytes, k: bytes) -> bytes:
    return bytes([m[__i] ^ k[__i % len(k)] for __i in range(len(m))])

__cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
__decryptor = __cipher.decryptor()

####################################################################### decrypt

__shellcode_aes = __decryptor.update(RAW[16:]) + __decryptor.finalize()
__shellcode_xor = xor(m=RAW, k=PASSWORD)

######################################################################## output

with open('sources/shellcode.aes.bin', 'wb') as __out_file:
    __out_file.write(__shellcode_aes)

with open('sources/shellcode.xor.bin', 'wb') as __out_file:
    __out_file.write(__shellcode_xor)
