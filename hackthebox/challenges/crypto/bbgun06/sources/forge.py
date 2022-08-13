from hashlib import sha1

######################################################################## knowns

USER = b'IT Department <it@cloudcompany.com>'
E = 3
N = bytes.fromhex('48941fad31c29c0d6c2acb7dda0cf68a7474699d5cd8dc13bbfd8620fa143e5f285c5892a71a40bfb2408ff5515e4db3d15b27a25ad2d3bf3682017ca0868a2a9231b0e8873ee2646cb42fbd44fa5ad5a7f0de4606745b57638e95259acc6afd0ed2e582ae37d40d7f766ac21f46d5598809dcb62af6a45f7e8e25d27618c8b001e55b21f096b57bdaae4afe98b3ef4de266cb678a428d6011df04c2fe47382b71ea405da9c5e935ee80ae0f455c3b2caaa5aa0d3501d83e3bb74d3d1bfa4953f3437a396620181e1f58c29420d93e55d08f848dcb3b237940727e7b703e1d79745ebfe3bfc2f95010e9d320c6e6386157195629a27c8e59b3bddc08579f6211')
ASN1 = b'\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14'
SIGNATURE = bytes.fromhex('0ac16e59fe8a01cebfb481cf80589bb3f21e100b360f06fd9d3a73de431942e695bd6ba18598fe317d5be5183f1aa0399c99d7075a61a91da07dcd4d86644f408b003888d484beeb58daeae2b42679ba152e827c886c6de5aa0cf267ef33fdbd88a0038824f8427ae21d5252ad9cf19b426c982c9ad9e9d45d0637e5a1f413377f4523a36ab01a054e6016fb9f158dc4cbfdddf3a84f65bc833d694c6a9306429f5bd6c4cac0b2a4df0bcf5ab207b6b7ab7480a9967f9c371db6c7dbf3212382059e589b483fd43c8b28da82213ce62f3cd5ee2e4fcf979c39bd7778982bb6dcd74d0c27bbbe4930cbab92e7adda46ec5a2c895a793b671d511e667dd41d1f98')

########################################################### forging a signature

def nth_root(x, n):
    # Start with some reasonable bounds around the nth root.
    upper_bound = 1
    while upper_bound ** n <= x:
        upper_bound *= 2
    lower_bound = upper_bound // 2
    # Keep searching for a better result as long as the bounds make sense.
    while lower_bound < upper_bound:
        mid = (lower_bound + upper_bound) // 2
        mid_nth = mid ** n
        if lower_bound < mid and mid_nth < x:
            lower_bound = mid
        elif upper_bound > mid and mid_nth > x:
            upper_bound = mid
        else:
            # Found perfect nth root.
            return mid
    return mid + 1

def pad(message: bytes, length: int) -> bytes:
    return message + max(0, length - len(message)) * b'\xff'

def forge(message: bytes, length: bytes=len(N), prefix: bytes=ASN1) -> int:
    __cleartext = b'\x00\x01\xff\x00' + prefix + sha1(message).digest()
    __encoded = int(pad(__cleartext, length).hex(), 16)
    return nth_root(__encoded, 3)
