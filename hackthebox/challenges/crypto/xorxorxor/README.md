> Who needs AES when you have XOR?

> Author: **[r4j][author-profile]**

## The challenge

There's a hex string in the "output.txt" file:

```
134af6e1297bc4a96f6a87fe046684e8047084ee046d84c5282dd7ef292dc9
```

`hash-identifier` doesn't recognize the format.
But it is labeled "flag", clearing all ambiguity.

## The encryption scheme

`challenge.py` shows that the flag is plaintext ASCII xored with a random key of length 4 bytes.

As usual, the flag must have the format "HTB{...}", ie the first 4 bytes of the plaintext are known.

XOR being its own inverse:

```
key ^ prefix = 0x134af6e1
key = 0x134af6e1 ^ prefix
```

where:
- prefix is the binary encoding of the known string "HTB{"
- 0x134af6e1 are the first 4 bytes of the encrypted flag

## Decypting

The process is simple:
1) deduce the encryption key thanks to "HTB{"
2) decrypt the whole flag with the key

We can reuse the code to decrypt the key and then the ciphertext...
After removing the excessive "class" code.

> `HTB{rep34t3d_x0r_n0t_s0_s3cur3}`

[author-profile]: https://app.hackthebox.com/users/13243
