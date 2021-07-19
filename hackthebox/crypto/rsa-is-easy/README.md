# RSAisEasy

> **I think this is safe... Right?**

> Author: **[ryaagard][author-profile-url]**

## RSAfe?

We're given:

- `c1`, the ciphertext of the first half of the flag
- `c2`, the ciphertext of the second half
- `n1`, the modulus used in the encryption of c1
- `F = n1 * E + n2`, where n2 is the modulus used for c2
- `e = 0x10001`, the public exponent for both encryptions

The exponent e is high enough to have:

![][equation_high-public-exponent]

So we can't directly compute the e-root of the ciphertexts!
(I'm developing reflexes with all those RSA challenges!)

But n1 and n2 share a common factor!

```python
n1 = p * q
n2 = q * z
```

So if we somehow get n2, we'll be able to factor both n1 and n2!

## Calculating n2

If by chance n1 is smaller than n2:

![][equation_n2]

It can be tested with:

![][equation_test-n2]

And it is the case, so we can calculate n2:

```python
n2 = F % n1
```

## Decrypting the ciphertexts

Since the prime decompositions of n1 and n2 share the factor q, it is their GCD.
In practice, it means that we can calculate p and z with the extended Euclid algorithm:

```python
q, x, y = extended_euclid_gcd(n1, n2)
p = n1 // q
z = n2 // q
```

(see the attached script for the Euclidean algorithm)

Then the private exponents can be computed by following the RSA algorithm:

```python
lambda1 = ((p -1 ) * (q - 1)) // extended_euclid_gcd(p - 1, q - 1)[0]
lambda2 = ((q -1 ) * (z - 1)) // extended_euclid_gcd(q - 1, z - 1)[0]

d1 = inverse(e, lambda1)
d2 = inverse(e, lambda2)
```

And finally the plaintext flags, through exponentiation:

```python
f1 = pow(c1, d1, n1)
f2 = pow(c2, d2, n2)
```

> HTB{1_m1ght_h4v3_m3ss3d_uP_jU$t_4_l1ttle_b1t?}

[author-profile-url]: https://app.hackthebox.eu/users/222411

[equation_high-public-exponent]: images/equations/high-public-exponent.png
[equation_n2]: images/equations/n2.png
[equation_test-n2]: images/equations/test-n2.png

