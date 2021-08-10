> **Why does maths have to be so hard? Because some dudes with "degrees"**
> **decided there have to be 4529837459872034759 different equations and**
> **347293475923709458 different fields instead of just pure numbers.**

> Author: **[0verflowme][author-profile]**

## Fast and failed

Three messages are encrypted with a common RSA:

- each ciphertext `c_i` known
- the sum of all the plaintext messages is given as `hint`
- only the modulus `N` is known
- `p`, `q` and `e` are unknown random numbers of 1024 bits

### Analysing the hint?

First, the maximum length of each plaintext is:

```python
# 28.8290424388799
math.log(hint, 256)
```

> each plaintext has a maximum of 29 characters

Going further, the base 256 representation of the hint is:

```python
# ['c', '4', 't', '|', '\x1a', 'Ö', '"', '"', 'Ú', 'Ã', '×', '\x08', 'H', 'ß', 'Ä', '\\', '3', '7', '\t', '&', '\x08', 'J', '7', '\x00', '\n', '\x03', 'ë', '3', '\x1d']
HINT = [chr(i) for i in representation(hint, 256)]
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

In our case, we have 3 messages:

![][equation-quick-maffs]

Where `H` is the hint: 2674558878275613295915981392537201653631411909654166620884912623530781.

The Groebner base of the 4 polynomials

[author-profile]: https://app.hackthebox.eu/users/109128
[coppersmith-paper]: https://link.springer.com/content/pdf/10.1007/3-540-68339-9_1.pdf

[equation-quick-maffs]: images/equations/quick-maffs.png
[equation-related-messages]: images/equations/related-messages.png
[symbol-polynomial-relation]: images/symbols/polynomial-relation.png
