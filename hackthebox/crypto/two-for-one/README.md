# Two for one

> **Alice sent two times the same message to Bob**.

## PEM encryption

Both keys and messages are base64 encoded, following PEM standards.

According to the PEM standard (RFC [1421][rfc-1421], [1422][rfc-1422a], [1423][rfc-1423] & [1424][rfc-1424]), the algorithm for asymetrical
encryption is RSA.

The 2 public keys are almost identical:

```bash
diff key1 key2
8c8
< lwIDAQAB
---
> lwIDBTy3
```

Actually the difference is only in the exponent `e`, the modulus `n` is the
same for both public keys.

```python
from Crypto.PublicKey import RSA as rsa
with open('key1.pem') as __f:
  K1 = rsa.import_key(__f.read())
print("n = ", K1.n, "\n\n", "e = ", K1.e)
```

> n = 25080356853331150673712092961488349508728123694382279186941974911344272809718201683391687288116618021523872262260746884803456249468108932413753368793568123710905490623939699616018064364038794824072468125668702688048418916712950393799664781694224559810656290997284081084848717062228887604668548576609649709572412523306016494962925450783098637867249337121156908328927249731928363360657779226929980928871118145919627109584218577535657544952661333527174942990937484743860494188129607347202336812042045820577108243818426559386634634103676467773122325120858908782192357380855678371737765634819794619802582481594876770433687

> e1 = 65537 (Fermat number F4)

> e2 = 343223

## Math

So Alice has encrypted the same message twice, with 2 different RSA keys:

```
m1 = m ^ e1 (mod n)
m1 ^ d1 = m (mod n)

m2 = m ^ e2 (mod n)
m2 ^ d2 = m (mod n)
```
Since e1 and e2 are coprime, Bézout:

```
e1 * x + e2 * y = 1
```

then:

```
m = m ^ (e1 * x + e2 * y)
m = (m ^ (e1 * x)) * (m ^ (e2 * y))
m = ((m ^ e1) ^ x) * ((m ^ e2) ^ y)
m = (m1 ^ x) * (m2 ^ y) (mod n)
```

Either x or y is bound to be negative. Supposing y is negative:

```
m2 ^ y = (m2 ^ -1) ^ |y| (mod n)
```

Where `m2 ^ -1` is the multiplicative inverse of m2 modulo n.

## The actual decryption

The numbers are modulo n, which is very large: 2048 bits.

```python
K1.n.bit_length()
```

This usually spells implementation issues...

> Fortunately Python 3+ handles arbitrarily large numbers transparently, with the basic `int` type <3

So we can directly read the messages as integers:

```python
import base64
with open('message1') as __f:
  M1 = __f.read()
  m1 = int(base64.b64decode(M1).hex(), 16)
```

Then, the extended Euclidean algorithm (not covered here) gives us `x` & `y`
such that:

```python
x * K1.e + y * K2.e
```

> 1

And, operating modulo `n` for efficiency:

```python
m = pow(m1, x, K1.n) * pow(m2, y ,K1.n)
m = m % K1.n
print(bytes.fromhex(hex(m)[2:]))
```

[rfc-1421]: http://www.ietf.org/rfc/rfc1421.txt
[rfc-1422]: http://www.ietf.org/rfc/rfc1422.txt
[rfc-1423]: http://www.ietf.org/rfc/rfc1423.txt
[rfc-1424]: http://www.ietf.org/rfc/rfc1424.txt
