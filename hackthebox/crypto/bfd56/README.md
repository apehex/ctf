> At least Delastelle didn't have to worry about bit flipping.
> p.s.The flag format is HTB{ALL_IN_UPPERCASE}.

> Author: **[arcayn][author-profile]**

## The Encryption Scheme

First decrypt, then unmask.

The IV and formula for unmasking are given.

The alphabet is missing "J".

The code is messy, with input arguments reassigned:

```python
def strmask(msg,mask):
    mask = (mask * ((len(msg)//len(mask)) + 1))
    return "".join([ALPHABET[(ALPHABET.index(i) + ALPHABET.index(j)) % 25] for i,j in zip(msg, mask)])
```

Indice of the last occurence of each character in the key, in base 5.

Unknowns:

- block length: divides 320 => 2, 4, 8, 16, 32, 64, 160
- key
- 

The key must contain all the characters in the alphabet (or at least the
message to encrypt):
length >= 25

`encrypt_block` replaces the characters from the plaintext with characters from the key:

```python
ret += characters[str(res[i]) + str(res[i+1])]
```

It can only return one of the the first 50 characters of the key.
If there are repetitions in the key, the result will be skewed towards those
repeated characters.

To be a valid index `res[i+1]` must be a rest modulo 5

So it safe to say the key is actually 25 characters long: `4 * 5 + 4 = 24` is
the maximum index.

The encryption is a character mapping 

Mask = translation in the alphabet space
Encrypt = 

1. decrypt a ciphertext with a known key
2. somehow get away without the key

[author-profile]: https://app.hackthebox.com/users/331561
