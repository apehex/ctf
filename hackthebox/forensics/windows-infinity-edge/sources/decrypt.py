#!/usr/bin/env python

from argparse import ArgumentParser
from base64 import b64decode
from Crypto.Cipher import AES
from itertools import cycle

#################################################################### PARAMETERS

BS = 16
KEY = bytes.fromhex('4d65bdbad183f00203b1e80cf96fba549663dabeab12fab153a921b346975cdd')
IV = bytes([105, 110, 102, 105, 110, 105, 116, 121, 95, 101, 100, 103, 101, 104, 116, 98])

####################################################################### GENERIC

unpad = lambda s: s[:-s[-1]]

########################################################################### XOR

def decrypt_xor(data):
    return bytes([x ^ y for (x, y) in zip(data, cycle(KEY))])

########################################################################### AES

def decrypt_aes(data):
    __cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad(__cipher.decrypt(data))

########################################################################### CLI

def main():
    parser = ArgumentParser(description='Decrypt message to/from a SharPyShell')
    parser.add_argument('--input', metavar='input', type=str, help='a file containing the encrypted data')
    parser.add_argument('--output', metavar='output', type=str, help='the destination file for the decrypted data')
    parser.add_argument('--line', metavar='output', type=int, default=0, help='the target line in the input file')

    args = parser.parse_args()

    with open(args.input, 'r') as __if:
        with open(args.output, 'wb') as __of:
            for __i, __l in enumerate(__if):
                if __i == args.line:
                    __of.write(decrypt_aes(b64decode(__l.strip())))

if __name__ == '__main__':
    main()
