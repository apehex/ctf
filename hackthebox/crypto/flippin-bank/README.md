# Flippin bank

> **The Bank of the World is under attack. Hackers found a way in and locked the
> admins out. However, the netcat authentication by the intruders is not
> perfectly secure. Could you help the admins log in?**

## Testing

The app asks for username & password and returns a `ciphertext`.

```
username: a
a's password: b
########################################################################
#                  Welcome to the Bank of the World                    #
#             All connections are monitored and recorded               #
#      Disconnect IMMEDIATELY if you are not an authorized user!       #
########################################################################
Leaked ciphertext: 0a853d3ecf5f64672d28162dd83637e910614da13e1a10226673edbeb5f89bef
enter ciphertext: 0a853d3ecf5f64672d28162dd83637e910614da13e1a10226673edbeb5f89bef
Please try again.
```

## Reading the sources

### Encryption scheme

Looking at `app.py`:

```
def encrypt_data(data):
	padded = pad(data.encode(),16,style='pkcs7')
	cipher = AES.new(key, AES.MODE_CBC,iv)
	enc = cipher.encrypt(padded)
	return enc.hex()

msg = 'logged_username=' + user +'&password=' + passwd
```

The `ciphertext` is the string `logged_username=a&passowrd=b` encrypted with AES CBC.

And the encryption is parametrized with:

```
key = get_random_bytes(16)
iv = get_random_bytes(16)
```

Replaying the request (username=a, password=b) request returns the same cipher:

```
0a853d3ecf5f64672d28162dd83637e910614da13e1a10226673edbeb5f89bef
```

So the IV & key remain the same between sessions.

### Credentials

The server looks for specific credentials in the ciphertext:

```
if b'admin&password=g0ld3n_b0y' in unpad(paddedParams,16,style='pkcs7'):
  return 1
```

The goal is to enter:

> `admin` and `g0ld3n_b0y`

But we cannot type it directly in plaintext.

## Modifying the ciphertext

### AES CBC decryption scheme

So we have to forge a ciphertext so that:
- the credentials typed differ from `admin & g0ld3n_b0y`
- after decryption it contains `admin&password=g0ld3n_b0y`

The ciphertext is in CBC mode, so decryption follows this algorithm:

```
plaintext(n) = cipher(n-1) XOR decrypt(cipher(n))
```
Which means that altering the cipher itself directly impacts the plaintext.

### Block selection

The plaintext string, cut in blocks of 16 bytes:

```
logged_username=
admin&password=g
0ld3n_boy
```

To modify the plaintext blocks 2 or 3,

Since tampering either the cipher blocks 2 or 3 would also scramble the
plaintext username or password, we can only modify the **first block**.

### Byte flipping

The XOR operation happens byte by byte, at a given index.

With any byte `b`, XOR has these interesting properties:

```
b XOR b = 0
0 XOR b = b
```

Let's say we want to change a "b" in the plaintext into an "a". In ASCII:
- "a" is code 0x61
- "b" is code 0x62

`c` being the cipher byte and `b` the corresponding decrypted byte in the
next block:

```
c ^ b = "b" = 0x62
(c ^ b) ^ (0x62 ^ 0x61)
  = 0x62 ^ 0x62 ^ 0x61
  = 0x61 = "a"

(c ^ b) ^ 0x61 ^ 0x62 = (c ^ 0x61 ^ 0x62) ^ b
```

So, changing cypher byte c for:

```
c' = c ^ 0x61 ^ 0x62 = c ^ 0x03
```

will flip the plaintext "b" to "a"!

### Actual modifications

1) bypass the server tests by entering `bdmin` and `g0ld3n_b0y`:

```
b0d9c88dd9d236a50d50e4559c6db67e7409f5111b846800b3b0ec6cf17dc8ef92044c64b65cbdb8ea960ce5fd5a774a
```

2) modify the first byte of cipher :

```
0xb0 ^ 0x03 = 0xb3
```

3) the resulting ciphertext is:

```
b3d9c88dd9d236a50d50e4559c6db67e7409f5111b846800b3b0ec6cf17dc8ef92044c64b65cbdb8ea960ce5fd5a774a
```

The server replies with the flag! :)
