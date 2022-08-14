> We have received reports from CloudCompany that resources are involved in malicious activity similar to attempting unauthorized access to remote hosts on the Internet.
> We have since shut down the server and locked the SA.
> While we were trying to investigate what the entry point was,
> we discovered a phishing email from CloudCompany's IT department.
> You've since notified the vendor, and they've provided the source code of the email signing server for a security assessment.
> We've identified an outdated RSA verification code implementation, which we believe could be the cause of why the threat actors were able to impersonate the vendor.
> Can you replicate the attack and notify them of any possible misuse?

> Author: **[WizardAlfredo][author-profile]**

## The goal

The server displays a mail and a pubblic key, most likely linked to the sender.

```
From: IT Department <it@cloudcompany.com>
```

It then asks for a HEX signature.
According to the given code, the signature is meant to certify the sender:

```python
user, data = parseEmail()
signature = rsa.sign(user)
rsa.verify(user, signature)
```

To get the flag, we want the server to validate the HEX signature we provide, while keeping it different from the one from the legitimate support company.

```python
if not rsa.verify(user, forged_signature):
    sendMessage(s, "Invalid signature")
if different(rsa, signature, forged_signature):
    sendMessage(s, FLAG)
```

## BB'06 signing process

The signing procedure is broken; first it is using SHA-1:

```python
hash_value = sha1(message).digest()
```

And most importantly, it checks only part of the signature:

```python
r = re.compile(b'\x00\x01\xff+?\x00(.{15})(.{20})', re.DOTALL)
m = r.match(clearsig)
```

Indeed, the question mark in the regex stands for "non-greedy":
it returns the shortest match, which may not span the entire signature.

So a clear signature with minimal padding would satisfy the algorithm too:

```
00 01 FF 00 ASN1 HASH .. .. ..
```

Where the dots can be any HEX value.

This is one variant of "[Bleichenbacher's RSA signature forgery][article-bb06]" or "BB'06".

## Forging a signature

### Format of the decrypted signature

The verification phase is performed on the cube of the encrypted signature, because the public exponent is `3`.

After exponantiation, the byte stream `00 01 FF 00 ASN1 HASH` has a length of 39:
it is less than a fifth of the 256 bytes of a valid signature (same length as N).

The stream `00 01 FF 00 ASN1 HASH` is padded with `FF` on the right:

```python
def forge_clear_signature(message: bytes, length: int=len(N), prefix: bytes=ASN1) -> bytes:
    __cleartext = b'\x00\x01\xff\x00' + prefix + sha1(message).digest()
    return pad(__cleartext, length)
```

### Cubic root

The hexadecimal value of the clear signaure is interpreted as "[big endian][wiki-endianness]":
this means that the 39 known bytes are the most significant.

```python
clearsig = decrypted.to_bytes(keylength, "big")
```

And all the numbers close to cubic root of the clear signature will share their most significant bytes.

Unfortunately the floating point root cannot be computed directly:

```python
clear_signature = forge_clear_signature(USER, len(N), ASN1)
int(clear_signature.hex(), 16) ** (1/3.)
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
# OverflowError: int too large to convert to float
```

Instead, we can use a dichotomic search:

```python
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
```

This is thanks to the implementation of the integer in Python, which allows arbitrary precision.

### Actual computation

The public information on the target user are enough:

```shell
openssl rsa -inform PEM -text -noout -pubin -in sources/pubkey.pem 
# RSA Public-Key: (2047 bit)
# Modulus:
#     48:94:1f:ad:31:c2:9c:0d:6c:2a:cb:7d:da:0c:f6:
#     8a:74:74:69:9d:5c:d8:dc:13:bb:fd:86:20:fa:14:
#     3e:5f:28:5c:58:92:a7:1a:40:bf:b2:40:8f:f5:51:
#     5e:4d:b3:d1:5b:27:a2:5a:d2:d3:bf:36:82:01:7c:
#     a0:86:8a:2a:92:31:b0:e8:87:3e:e2:64:6c:b4:2f:
#     bd:44:fa:5a:d5:a7:f0:de:46:06:74:5b:57:63:8e:
#     95:25:9a:cc:6a:fd:0e:d2:e5:82:ae:37:d4:0d:7f:
#     76:6a:c2:1f:46:d5:59:88:09:dc:b6:2a:f6:a4:5f:
#     7e:8e:25:d2:76:18:c8:b0:01:e5:5b:21:f0:96:b5:
#     7b:da:ae:4a:fe:98:b3:ef:4d:e2:66:cb:67:8a:42:
#     8d:60:11:df:04:c2:fe:47:38:2b:71:ea:40:5d:a9:
#     c5:e9:35:ee:80:ae:0f:45:5c:3b:2c:aa:a5:aa:0d:
#     35:01:d8:3e:3b:b7:4d:3d:1b:fa:49:53:f3:43:7a:
#     39:66:20:18:1e:1f:58:c2:94:20:d9:3e:55:d0:8f:
#     84:8d:cb:3b:23:79:40:72:7e:7b:70:3e:1d:79:74:
#     5e:bf:e3:bf:c2:f9:50:10:e9:d3:20:c6:e6:38:61:
#     57:19:56:29:a2:7c:8e:59:b3:bd:dc:08:57:9f:62:
#     11
# Exponent: 3 (0x3)
```

The target user is in the header of the mail:

```python
USER = b'IT Department <it@cloudcompany.com>'
```

And the "ASN1" prefix is in the code:

```python
ASN1 = b'\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14'
```

Then, we forge the final signature and take its cube root:

```python
clear_signature = forge_clear_signature(USER, len(N), ASN1)
encrypted_signature = forge_encrypted_signature(clear_signature)
```

As a verification, we can check whether the hash is present in the cube / decrypted value:

```python
sha1(USER).digest().hex() in hex(int(encrypted_signature.hex(), 16) ** 3)
# True
```

Actually, the cube of the forged signature shares 86 bytes (172 HEX digits) with the target:

```python
len(clear_signature)
# 256
len(bytes.fromhex(hex(int(clear_signature.hex(), 16) - (int(encrypted_signature.hex(), 16) ** 3))[2:]))
# 170
```

Finally, the hexadecimal representation of the root can be sent:

```python
hex(fake)
# '0x32c38623fcb6700fc258dc1f410bcb948104032a0eed89dd539c569252004be5da95b737088c6262495f1d97bd9fefc9853a1c142e930232a6255aa6f1955382adc8ecf22cf0bf1f4db5de6670339ab44b49c59ad0'
```

The server responds favorably:

> `HTB{4_8131ch3n84ch32_254_vu1n}`

[author-profile]: https://app.hackthebox.com/users/201215
[article-bb06]: https://words.filippo.io/bleichenbacher-06-signature-forgery-in-python-rsa/
[wiki-endianness]: https://en.wikipedia.org/wiki/Endianness
[wiki-sha1]: https://en.wikipedia.org/wiki/SHA-1