> The Bank of the World is under attack. Hackers found a way in and locked the
> admins out. However, the netcat authentication by the intruders is not
> perfectly secure. Could you help the admins log in?

> Author: **[P3t4][author-profile]**

## Interacting with the server

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

### The loggin process

The server asks for credentials:

```python
send_msg(s, 'username: ')
user = s.recv(4096).decode().strip()

send_msg(s, user +"'s password: " )
passwd = s.recv(4096).decode().strip()
```

Upon connection he leaks the ciphertext of the string:

```python
msg = 'logged_username=' + user +'&password=' + passwd
```

And then asks for a cipher. If the input cipher matches `b'admin&password=g0ld3n_b0y'` it returns the flag:

```python
if check:
    send_msg(s, 'Logged in successfully!\nYour flag is: '+ FLAG)
    s.close()
```

But we can't directly login with `admin` / `g0ld3n_b0y`, so the server does not immediately leak the target cipher.

### The encryption scheme

Looking further at `app.py`:

```python
def encrypt_data(data):
    padded = pad(data.encode(),16,style='pkcs7')
    cipher = AES.new(key, AES.MODE_CBC,iv)
    enc = cipher.encrypt(padded)
    return enc.hex()

msg = 'logged_username=' + user +'&password=' + passwd
```

The `ciphertext` is the string `logged_username=a&password=b` encrypted with AES CBC.

And the encryption is parametrized with:

```python
key = get_random_bytes(16)
iv = get_random_bytes(16)
```

Replaying the request (username=a, password=b) request returns the same cipher:

```
0a853d3ecf5f64672d28162dd83637e910614da13e1a10226673edbeb5f89bef
```

So the IV & key remain the same between sessions.

## Modifying the ciphertext

### AES CBC decryption scheme

So we have to forge a ciphertext so that:
- the credentials typed differ from `admin & g0ld3n_b0y`
- after decryption it contains `admin&password=g0ld3n_b0y`

The ciphertext is in CBC mode, so decryption follows this algorithm:

```
plaintext(n) = cipher(n-1) XOR decrypt(cipher(n))
```

Where `n` is a bloc index, of length 16 here. It is distinct from the byte index, inside a bloc.

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

`c` being the cipher byte and `b` the corresponding decrypted byte in the next block:

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

### Block selection

The algorithm operates on the following blocs of 16 bytes:

```
logged_username=
admin&password=g
0ld3n_boy
```

The last bloc is actually padded to have a length 16 too.

So if we modify the first bytes of the first bloc, "l", it will impact the decryption of the first byte of the second bloc: "a".

### Actual modifications

1) bypass the server tests by entering `bdmin` and `g0ld3n_b0y`; the server responds with:

```
b0d9c88dd9d236a50d50e4559c6db67e7409f5111b846800b3b0ec6cf17dc8ef92044c64b65cbdb8ea960ce5fd5a774a
```

2) modify the first byte of cipher :

```
0xab ^ 0x03 = 0xa8
```

3) the resulting ciphertext is:

```
a86e50a3d9b4a3a5c5e8d2f49e67d938cbca83bcc39e818633b7dd5e9ea0a56038823707697c58e281b198ead01a5652
```

The server replies with the flag! :)

> `HTB{b1t_fl1pp1ng_1s_c00l}`

[author-profile]: https://app.hackthebox.com/users/23
