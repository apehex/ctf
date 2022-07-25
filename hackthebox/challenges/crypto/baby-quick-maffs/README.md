> Wikipedia says "the Rabin cryptosystem has been mathematically proven to be computationally secure against a chosen-plaintext attack as long as the attacker cannot efficiently factor integers",
> so I created my own cool implementation.

> Author: **[coletree][author-profile]**

## The encryption algorithm

The [Rabin cryptosystem][wiki-rabin] is similar to the RSA.
The public key `N = p * q` is known and the ciphertexts are squares:

```python
ciphers = [pow(c, 2, N) for c in parts]
```

Except the message is cut into parts prior to encryption:

```python
def partition_message(m, N):
    m1 = randint(1, N)
    parts = []
    remainder = 0
    while sum(parts) < m:
        if sum(parts) + m1 < m:
            parts.append(m1)
        else:
            remainder = m - sum(parts)
            parts.append(m1 + remainder)
    return (parts, remainder)
```

With:

![][definitions]

The message and ciphertext are both cut into parts:

![][parts]

Here the list of cipher has 3 elements: m<sub>1</sub><sup>2</sup> twice and (m<sub>1</sub>+r)<sup>2</sup> once.

## Decrypting

### Prime factorization

I launched a prime factorization in the background and it didn't succeed by the time I finished the challenge.

### Arithmetics

Since we know the actual remainder (which is not necessary for decryption and a blunder):

![][congruences]

Where the inverse of the remainder is well defined and equal to:

```python
print(pow(2 * R, -1, N))
# 2832960204350032590905037630577263909797762518029153959658033411415011365712127582827812725900278882583376533417417586364969574210566983289539351371237140
```

These congruences are easy to compute:

```python
m1 = pow(2 * R, -1, N) * (CT[2] - CT[0] - R**2) % N
print(bytes.fromhex(hex(2 * m1 + R)[2:]))
```

> `HTB{d0nt_ev4_r3l4ted_m3ss4ge_att4cks_th3y_ar3_@_d3a1_b7eak3r!!!}`

[author-profile]: https://app.hackthebox.com/users/473080
[congruences]: images/congruences.png
[definitions]: images/definitions.png
[parts]: images/parts.png
[wiki-rabin]: https://en.wikipedia.org/wiki/Rabin_cryptosystem
