# -*- coding: utf-8 -*-

from fibopadcci import is_hex, mask, xor

# ================================================================ bruteforcing

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+'

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
# ===================================================================== logging

LOGGING_FORMAT = '''Oracle {{
\tready:\t{}
\ta:\t{}
\tb:\t{}
\tc:\t{}
\ta_s:\t{}
\ta_m:\t{}
\tb_m:\t{}
\tc_m:\t{}
}}\n\n'''

# ======================================================= padding oracle attack

class Oracle:

    def __init__(self):
        self._plaintext_iv_secret = b'HTB{th3_s3crt_A}'
        self.reset()

    def __str__(self):
        __a, __b, __c = self.alter_ciphertext()
        return LOGGING_FORMAT.format(
            self.is_ready(),
            self._plaintext_iv.hex(),
            self._ciphertext_iv.hex(),
            self._ciphertext.hex(),
            self._plaintext_iv_secret.hex(),
            __a.hex(),
            __b.hex(),
            __c.hex())

    def reset(self):
        self._plaintext_iv = b''
        self._ciphertext_iv = b''
        self._ciphertext = b''

    def _check_cipher_parameter(self, parameter: bytes, count: int=0) -> bool:
        return (
            bool(parameter)
            and type(parameter) == bytes
            and len(parameter) % 16 == 0
            and (count == 0 or (len(parameter) // 16 == count)))

    def is_ready(self) -> bool:
        return (
            self._check_cipher_parameter(self._plaintext_iv_secret, 1)
            and self._check_cipher_parameter(self._plaintext_iv, 1)
            and self._check_cipher_parameter(self._ciphertext_iv, 1)
            and self._check_cipher_parameter(self._ciphertext, 0))

    def set_plaintext_iv(self, data) -> bytes:
        if data:
            if type(data) == bytes:
                self._plaintext_iv = data
            elif type(data) == str and is_hex(data):
                self._plaintext_iv = bytes.fromhex(data)
        return self._plaintext_iv

    def set_ciphertext_iv(self, data) -> bytes:
        if data:
            if type(data) == bytes:
                self._ciphertext_iv = data
            elif type(data) == str and is_hex(data):
                self._ciphertext_iv = bytes.fromhex(data)
        return self._ciphertext_iv

    def set_ciphertext(self, data) -> bytes:
        if data:
            if type(data) == bytes:
                self._ciphertext = data
            elif type(data) == str and is_hex(data):
                self._ciphertext = bytes.fromhex(data)
        return self._ciphertext

    def set_parameters(self, parameters):
        if parameters and len(parameters) == 3:
            self.set_plaintext_iv(parameters[0])
            self.set_ciphertext_iv(parameters[1])
            self.set_ciphertext(parameters[2])
        return parameters

    def alter_ciphertext(self):
        __mask = xor(self._plaintext_iv_secret, self._plaintext_iv)
        return (
            mask(self._plaintext_iv, __mask),
            mask(self._ciphertext_iv, __mask),
            mask(self._ciphertext, __mask))

    def decrypt(self):
        __mask = xor(self._plaintext_iv_secret, self._plaintext_iv)
        __plaintext_masked = bytes.fromhex('00000000000000000000000000000001')
        __plaintext = xor(__mask, __plaintext_masked)
        return __plaintext

# ======================================================================== main

def main():
    pass

if __name__ == "__main__":
    main()
