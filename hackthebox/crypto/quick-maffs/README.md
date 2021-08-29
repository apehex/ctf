> Why does maths have to be so hard? Because some dudes with "degrees"
> decided there have to be 4529837459872034759 different equations and
> 347293475923709458 different fields instead of just pure numbers.

> Author: **[0verflowme][author-profile]**

## Fast and failed

Three messages are encrypted with a common RSA:

- each ciphertext c<sub>i</sub> is known
- the sum of all the plaintext messages is given as "hint"
- the modulus N is known
- but p, q and e are unknown, random and prime numbers

### Analysing the hint?

First, the maximum length of each plaintext is:

```python
# 28.8290424388799
math.log(hint, 256)
```

> each plaintext has a maximum of 29 characters

Going further, the base 256 representation of the hint is:

```python
# b'c4t|\x1a\xd6""\xda\xc3\xd7\x08H\xdf\xc4\\37\t&\x08J7\x00\n\x03\xeb3\x1d'
long_to_bytes(hint)
```

Most likely, one string is several characters longer than the others: the first
few characters of the base 256 representation come from a single string.

> one of the plaintexts starts with `c4t`.

Each character in this representation is the sum of three plaintext characters,
plus a carry of 0, 1 or 2 (in ordinal form).

A dictionnary could be used to make educated guesses on the length of the strings
and the characters. As a last resort.

### Interpreting the description?

The challenge description is also quite wordy:

- "degrees" could point toward exponent(iation) and the cyclic attack:
  - it works by powering through consecutive exponents of the ciphers
  - but it didn't succeed during all the time spent on this challenge
- "pure numbers" could be a reference to "perfect numbers":
  - in particular the hint could be equal to the some of its factors
  - still the hint is an odd number, and all known perfect numbers are even
- the numbers 4529837459872034759 and 4529837459872034759 could be:
  - prime factors? nope
  - the order of a cipher? nada
  - a private key? lol, sure

## The Franklin-Reiter related message attack

So I reached my wits end, time for some googling. This challenge is a very
specific case of the attacks presented by D. Coppersmith, M. Franklin,
J. Patarin and M. Reiter in a [paper of 1996][coppersmith-paper].

The paper is interested in the case where k messages are related by a polynomial
and satisfy the equations:

![][equation-related-messages]

In our case, the 3 messages are the solutions of:

![][equation-quick-maffs]

Where `H` is the "hint", ie the sum of all the messages.

So the following polynomials share a common root:

![][equation-common-root]

And:

![][equation-polynomial-resultant]

Both P<sub>1</sub> and S<sub>1</sub> have M<sub>1</sub> as root:

![][equation-common-factor]

So the GCD will have M<sub>1</sub>, the first message, as its lowest coefficient.

## Computing the GCD

In Sage:

```python
# when X=M1 both P2 and S2 have M2 as root
p2 = (y^e - CTS[1]).change_ring(X)
s2 = ((H - x - y)^e - CTS[2]).change_ring(X)

# their resultant is null, so M1 is a root of S1
s1 = p2.resultant(s2, variable=y)

# Y-M1 | GCD(R1, S1)
g = r1.gcd(s1)
```

## Bruteforcing the public exponent

Still the public exponent e remains unknown: the processing cannot be done yet.

Since e is supposedly low, it should be feasible to iterate until the GCD
is different from 1.

But the previous calculation is clumsy and it takes forever... Actually, Sage
has a built-in algorithm for reducing polynomials that is optimized:
the Gr&ouml;bner basis computation, as the paper points out.

```python
def basis_attack(e: int, n: int, w: int, c1: int, c2: int, c3: int):
    XYZ.<x,y,z> = PolynomialRing(Zmod(n))

    p0 = x + y + z - w
    p1 = x^e - c1
    p2 = y^e - c2
    p3 = z^e - c3

    i = ideal(p0, p1, p2, p3)

    return i.groebner_basis()
```

According to the previous section, when the value of e is wrong, the R<sub>i</sub> and S<sub>i</sub>
are coprime (they have no common factor). Hence the P<sub>i</sub> are coprime
and the basis of the ideal has only 1 as generator.

So we can check the length of the basis to know whether e has its original value:

```python
for e in Primes():
    b = basis_attack(e, N, H, CTS[0], CTS[1], CTS[2])

    # progress
    print(f'{e}:\t{b}', end='\r')

    if len(b) > 1:
        break
```

## Decoding the messages

Finally, the integer encoding of the messages is found in the constant coefficient
of each vector of the basis:

```python
m1 = N - b[0].coefficients()[1]
```

And interpreted as ASCII:

```python
print(bytes.fromhex(hex(m1)[2:]))
```

> HTB{5h0u1d_1t_b3_und3r_RSA_c4t3g0ry_0r_und3r_m4ths_c4t3g0ry?,1dk!but_gb_is_c00l}

[author-profile]: https://app.hackthebox.eu/users/109128
[coppersmith-paper]: https://link.springer.com/content/pdf/10.1007/3-540-68339-9_1.pdf

[equation-common-factor]: images/equations/common-factor.png
[equation-common-root]: images/equations/common-root.png
[equation-polynomial-resultant]: images/equations/polynomial-resultant.png
[equation-quick-maffs]: images/equations/quick-maffs.png
[equation-related-messages]: images/equations/related-messages.png
[symbol-polynomial-relation]: images/symbols/polynomial-relation.png
