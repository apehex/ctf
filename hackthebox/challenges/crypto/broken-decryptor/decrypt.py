#!/usr/bin/env python

import enum
import itertools
import re
import socket
import sys

from typing import List

# =================================================================== utilities

def xor(a, b):
    return bytes([_a ^ _b for _a, _b in zip(a, b)])

def unhex(msg):
    return bytes.fromhex(msg)

# =================================================================== wrangling

OUTPUT_CT_REGEX = re.compile(r'^([a-f0-9]+)(\\n|\n)', re.IGNORECASE)

def extract_ciphertext(data: bytes) -> bytes:
    """
    Extract a hex blob from a stream of ASCII bytes
    """
    __hex_ciphertext = ''
    __match = OUTPUT_CT_REGEX.search(data.decode('utf-8'))
    if __match:
        __hex_ciphertext = __match.group(1)
    return bytes.fromhex(__hex_ciphertext)

# ====================================================================== socket

class Netcat:

    def __init__(self, ip: str, port: int):
        """
        Initialize the socket and internal attributes.
        """
        self._data = b''

        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self._socket.settimeout(0.04)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 4)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 8)

        self.reset()

    def reset(self) -> None:
        """
        Resets the data buffer and server state.
        """
        self._socket.connect((self._ip, self._port))
        # self._socket.setblocking(0) # raises an exception of an operation doesn't immediately succeed

    def menu(self) -> None:
        """
        Return to the menu whatever the state of the connection.
        """
        try:
            self.write(b'\n') # return to the menu
            self.read() # flush the menu text
        except Exception:
            self.reset()
            self.write(b'\n') # return to the menu
            self.read() # flush the menu text

    def read(self, length: int=1024, overwrite=True) -> bytes:
        """
        Read 1024 bytes off the socket.
        """
        if overwrite:
            self._data = b''

        # get data until the socket buffer is empty
        try:
            self._data += self._socket.recv(length)
        except Exception:
            pass # timeout exception: no more data

        return self._data

    def write(self, data: bytes) -> int:
        """
        Send data.
        """
        return self._socket.send(data)

    def close(self) -> None:
        """
        Terminate the TCP stream
        """
        return self._socket.close()

    def request_flag_encryption(self) -> bytes:
        """
        Choose option 1 from the server interface.
        """
        if b'option: ' not in self._data:
            self.menu()
        self.write(b'1\n')
        return self.read()

    def request_plaintext_encryption(self, plaintext: bytes) -> bytes:
        """
        Choose option 2 from the server interface.
        """
        if b'option: ' not in self._data:
            self.menu()
        self.write(b'2\n')
        self.read()
        self.write(bytes(plaintext.hex(), 'utf-8') + b'\n')
        return self.read()

    def collect_ciphertexts(self, count: int, plaintext: bytes=b'') -> List[bytes]:
        """
        Request `count` ciphertexts from the server.
        Can either be the encrypted flag or the encryption of an input plaintext.
        The total number of ciphertexts should be enough for statistical analysis
        of the bytes.
        """
        __ciphertexts = []

        while len(__ciphertexts) < count:
            # ask for the encrypted flag / plaintext
            if plaintext:
                __buffer = nc.request_plaintext_encryption(plaintext)
            else:
                __buffer = nc.request_flag_encryption()

            # extract and store all the flag ciphertexts
            __ciphertext = extract_ciphertext(__buffer)
            if __ciphertext:
                __ciphertexts.append(__ciphertext)
                print(__ciphertext.hex(), end='\r')

        return __ciphertexts

# ================================================================== statistics

def find_missing_bytes(collection: List[int]) -> List[int]:
    """
    Because of the substitution, the null byte never appears in `otp`.

    So the bytes with no occurences in the collected ciphertexts correspond to
    otp_i = 0x00.
    """
    # occurences of all possibles bytes
    __o = [collection.count(__b) for __b in range(256)]

    # return the byte values with 0 occurences
    return [__b for __b, __c in enumerate(__o) if __c == 0]

def compute_candidate_ciphertexts(ciphertexts: List[bytes]) -> List[bytes]:
    """
    Computes all ciphertexts composed of bytes with no occurences in the input
    list.
    """
    __candidate_bytes = [
        find_missing_bytes([__c[__i] for __c in ciphertexts])
        for __i in range(len(ciphertexts[0]))]

    # return the cartesian product of all bytes
    return [bytes(__p) for __p in itertools.product(*__candidate_bytes)]

# ======================================================================== main

if __name__ == '__main__':
    randomized_ciphertexts = []
    nc = Netcat(ip='188.166.173.208', port=30370)

    # discard the menu output
    nc.menu()

    # fix the otp to the null byte => k_i + 0x00 + p_i
    print(f'\n[+] Request 4096 random encryptions of the flag...')
    randomized_ciphertexts = nc.collect_ciphertexts(count=4096)

    # compute the candidate ciphertexts that have the otp fixed to 0x00
    print(f'\n[+] Compute the candidate ciphertexts with null otp...')
    candidates_without_otp = compute_candidate_ciphertexts(randomized_ciphertexts)
    print(candidates_without_otp)

    # candidates_without_otp = [b'\xee\xaf\x10\xae\xc9\xc5\xc2\xe6\xc7\xb1\xa1H\xd1`\xd3']

    # flush the buffer
    nc.menu()

    # encrypting the candidate ciphertexts will remove the keystream:
    # k_i + k_i + 0x00 + otp_i + p_i = otp_i + p_i
    print(f'\n[+] Re-encrypt the candidate ciphertexts to cancel out the keystream...')
    candidates_without_keystream = []
    for __candidate in candidates_without_otp:
        print(f'[+] Request 4096 encryptions of {__candidate.hex()}...')
        randomized_ciphertexts = nc.collect_ciphertexts(count=4096, plaintext=__candidate)

        # then, we can apply the former trick to remove the new otp:
        # only the plaintext bytes p_i remain!!
        print(f'[+] Finally compute the candidate plaintexts...')
        candidates_without_keystream += compute_candidate_ciphertexts(randomized_ciphertexts)

    print(f'\n[+] All candidate plaintexts:')
    print(candidates_without_keystream)

    nc.close()
