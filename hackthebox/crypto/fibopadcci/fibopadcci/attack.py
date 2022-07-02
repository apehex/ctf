# -*- coding: utf-8 -*-

from fibopadcci import FIBOPADCCI, is_hex, mask, pad, to_bytes, xor

# ===================================================================== logging

LOGGING_FORMAT = '''Oracle {{
\tready:\t{}
\tdone:\t{}
\tnext:\t{}

\ta:\t{}
\tb:\t{}
\tc:\t{}

\ta_secret:\t{}
\ta_masked:\t{}
\tb_masked:\t{}
\tc_masked:\t{}

\tp_known:\t{}
\tfibopadcci:\t{}
\tdelta:\t{}

\tplaintext:\t{}
}}\n\n'''

# ======================================================= padding oracle attack

class Oracle:

    # ==================================================================== meta

    def __init__(self):
        self._plaintext_iv_secret = b'HTB{th3_s3crt_A}'
        self._plaintext_known_bytes = b''
        self.reset()

    def __str__(self):
        __a, __b, __c = self.alter_ciphertext()
        return LOGGING_FORMAT.format(
            self.is_ready(),
            self.is_done(),
            self.is_next_iv(self._plaintext_iv),
            self._plaintext_iv.hex(),
            self._ciphertext_iv.hex(),
            self._ciphertext.hex(),
            self._plaintext_iv_secret.hex(),
            __a.hex(),
            __b.hex(),
            __c.hex(),
            self._plaintext_known_bytes.hex(),
            self.calculate_fibopadcci(len(self._plaintext_known_bytes) + 1),
            self.calculate_next_delta(),
            self._plaintext_known_bytes)

    def reset(self):
        self._plaintext_iv = b''
        self._ciphertext_iv = b''
        self._ciphertext = b''

    # ====================================================================== IO

    @staticmethod
    def _check_single_cbc_parameter(parameter: bytes, count: int=0) -> bool:
        return (
            bool(parameter)
            and type(parameter) == bytes
            and len(parameter) % 16 == 0
            and (count == 0 or (len(parameter) // 16 == count)))

    @staticmethod
    def _check_cbc_parameters(parameters) -> bool:
        # plaintext iv, ciphertext iv, ciphertext
        # in this order
        return (
            bool(parameters)
            and len(parameters) == 3
            and Oracle._check_single_cbc_parameter(parameters[0], 1)
            and Oracle._check_single_cbc_parameter(parameters[1], 1)
            and Oracle._check_single_cbc_parameter(parameters[2], 0))

    def set_cbc_parameters(self, parameters):
        if self._check_cbc_parameters(parameters):
            self._plaintext_iv = to_bytes(parameters[0])
            self._ciphertext_iv = to_bytes(parameters[1])
            self._ciphertext = to_bytes(parameters[2])
        return parameters

    # ============================================= oracle attack: control flow

    def is_next_iv(self, iv: bytes) -> bool:
        l = len(self._plaintext_known_bytes)
        return (
            not self.is_done()
            and (l == 0 or iv[-l:] == self.calculate_next_iv()[-l:]))

    def is_done(self) -> bool:
        return (
            len(self._plaintext_known_bytes) >= 16
            and self._check_cbc_parameters((self._plaintext_iv, self._ciphertext_iv, self._ciphertext)))

    def is_ready(self) -> bool:
        """
        Check whether all cipher parameters are valid
        and the plaintext IV allows the decryption of the next byte.
        """
        return (
            self._check_single_cbc_parameter(self._plaintext_iv_secret, 1)
            and self._check_cbc_parameters((self._plaintext_iv, self._ciphertext_iv, self._ciphertext))
            and self.is_next_iv(self._plaintext_iv))

    # ================================================ oracle attack: iteration

    def calculate_fibopadcci(self, l: int) -> bytes:
        """
        Calculate the padding that will allow the decryption of the next
        unknown byte.

        That right padding is also padded on the left to output a block
        of length 16.

        Manipulating entities of block size simplifies the calculations.
        """
        return pad(FIBOPADCCI[:l], right=False, fill=b'i'*16, until=16)

    def calculate_next_delta(self) -> bytes:
        """
        Calculate the delta will allow the decryption of the next byte.
        """
        l = len(self._plaintext_known_bytes)
        if not self.is_done():
            return xor(
                self.calculate_fibopadcci(l + 1),
                pad(self._plaintext_known_bytes, right=False, fill=b'G'*16, until=16))
        else:
            return b''

    def calculate_next_iv(self) -> bytes:
        """
        Calculate the plaintext IV that will allow the decryption of the next
        unknown byte.

        Only the last bytes of that IV are fixed: the rest is filled with junk.
        (meaning: (b'.' * 16) ^ a_s)

        Manipulating entities of block size simplifies the calculations.
        """
        if not self.is_done():
            return xor(
                self._plaintext_iv_secret,
                self.calculate_next_delta())
        else:
            return b''

    def decrypt_next_byte(self) -> bytes:
        l = len(self._plaintext_known_bytes)
        if self.is_next_iv(self._plaintext_iv):
            __last_bytes = xor(
                self._plaintext_iv,
                xor(
                    self._plaintext_iv_secret,
                    self.calculate_fibopadcci(l + 1)))
            self._plaintext_known_bytes = __last_bytes[-l-1:]
        return self._plaintext_known_bytes


    def alter_ciphertext(self):
        __mask = xor(self._plaintext_iv_secret, self._plaintext_iv)
        return (
            mask(self._plaintext_iv, __mask),
            mask(self._ciphertext_iv, __mask),
            mask(self._ciphertext, __mask))

# ======================================================================== main

def main():
    pass

if __name__ == "__main__":
    main()
