from base64 import b64decode
from itertools import cycle

KEY = bytes.fromhex('4d65bdbad183f00203b1e80cf96fba549663dabeab12fab153a921b346975cdd')
DATA = b64decode('6LTFa96F2sGseGYEXiuG3Q==') # a response from the server

def encrypt(data):
    return bytes([x ^ y for (x, y) in zip(data, cycle(KEY))])
