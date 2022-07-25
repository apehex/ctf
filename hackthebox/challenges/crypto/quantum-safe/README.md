> I heard Shor's algorithm can do all sorts of nasty things to RSA,
> so I've decided to be super modern and protect my flag with cool new maffs!

> Author: **[Ir0nstone][author-profile]**

## The cryptosystem

The encryption mechanism is regular linear algebra.
It encode each character of a string into an integer vector:

![][encryption]

The public key is the 3x3 matrix in the middle and the numbers labeled u<sub>i</sub> are unknowns.

And the target is the value `c`, the ASCII code for each character.

## Quantum-Sage

The public key matrix is of rank 3, so it can be inverted:

```python
print(M.rank())
# 3
print(M.inverse())
# [3874/2099 4751/2099 2780/6297]
# [2567/2099 3166/2099  605/2099]
# [-208/2099 -241/2099 -107/6297]
```

So for two vectors of index i and 0 respectively:

![][decryption]

We don't need to guess / infer any of the unknowns to decrypt the message!
This equation directly yields the difference c<sub>i</sub> minus c<sub>0</sub>.

In Sage / Python:

```python
inv = M.inverse()
deltas = [(vector(__c) - vector(CT[0])) * inv for __c in CT]
```

Knowing that the first character is a `H`, the sequence of deltas can be decoded as actual letters:

```python
flag = ''.join([chr(ord('H') + __d[0]) for __d in deltas])
```

> `HTB{r3duc1nG_tH3_l4tTicE_l1kE_n0b0dY's_pr0bl3M}`

[author-profile]: https://app.hackthebox.com/users/249013
[decryption]: images/decryption.png
[encryption]: images/encryption.png
