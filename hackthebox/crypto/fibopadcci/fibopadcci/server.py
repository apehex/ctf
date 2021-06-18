# -*- coding: utf-8 -*-

import socketserver
from Crypto.Cipher import AES
import os

#from secret import flag, key
from fibopadcci import unhex, SuperSecureEncryption

# ===================================================================== targets

flag = b'whatiwouldntgivetoknowthispieceofinformation'
key  = b'16bytesofsupersecretkeyunpadded_'

# ==================================================================== greeting

WLC_MSG = """
-------------------------------------------------------------------------
|           Welcome to my Super Secure Encryption service!              |
|        We use AES along with custom padding for authentication        |
|         for extra security, so only admins should be able to          |
|          decrypt the flag with the key I have provided them!          |
|       Admins: Feel free to send me messages that you have             |
|       encrypted with my key, but make sure they are padded            |
|       correctly with my custom padding I showed you (fibopadcci)      |
|          Also, please use the a value I gave you last time,           |
|   if you need it, ask a fellow admin, I don't want some random        |
|               outsiders decrypting our secret flag.                   |
-------------------------------------------------------------------------
"""[1:]

MENU_MSG = """\n
-------------------------
| Menu                  |
-------------------------
|[0] Encrypt flag.      |
|[1] Send me a message! |
-------------------------
"""[1:]

# ===================================================================== service

def encryptFlag():
    encrypted, a, b = SuperSecureEncryption(key).encrypt(flag)
    return f'encrypted_flag: {encrypted.hex()}\na: {a}\nb: {b}'

def sendMessage(ct, a, b):
    if len(ct) % 16:
        return "Error: Ciphertext length must be a multiple of the block length (16)!"
    if len(a) != 16 or len(b) != 16:
        return "Error: a and b must have lengths of 16 bytes!"
    decrypted = SuperSecureEncryption(key).decrypt(ct, a, b)
    if decrypted != None:
        return "Message successfully sent!"
    else:
        return "Error: Message padding incorrect, not sent."

def handle(self):
    self.write(WLC_MSG)
    while True:
        self.write(MENU_MSG)
        option = self.query("Your option: ")
        if option == "0":
            self.write(encryptFlag())
        elif option == "1":
            try:
                ct = unhex(self.query("Enter your ciphertext in hex: "))
                b = unhex(self.query("Enter the B used during encryption in hex: "))
                a = b'HTB{th3_s3crt_A}' # My secret A! Only admins know it, and plus, other people won't be able to work out my key anyway!
                self.write(sendMessage(ct,a,b))
            except ValueError as e:
              self.write("Provided input is not hex!")
        else:
            self.write("Invalid input, please try again.")

# ====================================================================== server

class RequestHandler(socketserver.BaseRequestHandler):
    handle = handle

    def read(self, until='\n'):
        out = ''
        while not out.endswith(until):
            out += self.request.recv(1).decode()
        return out[:-len(until)]

    def query(self, string=''):
        self.write(string, newline=False)
        return self.read()

    def write(self, string, newline=True):
        self.request.sendall(str.encode(string))
        if newline:
            self.request.sendall(b'\n')

    def close(self):
        self.request.close()

class Server(socketserver.ForkingTCPServer):

    allow_reuse_address = True

    def handle_error(self, request, client_address):
        self.request.close()

# ======================================================================== main

def main():
    port = 1337
    server = Server(('0.0.0.0', port), RequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()