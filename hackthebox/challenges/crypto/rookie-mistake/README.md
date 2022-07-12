> oh... god... what have you done...

> Author: **[willwam845][author-profile]**

## The mistakes

This is a RSA challenge with:

- p, q, n, e, and the ciphertexts known
- both `q-1` and `p-1` have little prime factors

```python
def genprime():
    p = 2
    while p.bit_length() < 1020:
        p *= getPrime(30)
    while True:
        x = getPrime(16)
        if isprime((p * x) + 1):
            return (p * x) + 1
            break
```

In other words `p-1` and `q-1` will be easy to factor.

## Decrypting the RSA part

The problem is:

```python
ct1 = pow(flag1,e,p)
```

With e, p and ct1 known.

"By design", the GCD of `p - 1` and `e` is 2:

```python
gcd, x, y = xgcd(e, p - 1)
```

So the extended Euclidean algorithm allows to calculate x & y such that:

![][square-flag]

From there, we can just use the [square root utility of Sagemath][sagemath-sqrt]
and decode the result:

```python
_, x, y = xgcd(E, P - 1) # 2
ct1_2 = pow(CT1, x, P) # CT1^2
pt1 = int(square_root_mod_prime(ct1_2, P))
flag1 = bytes.fromhex(hex(P-pt1)[2:-138])
```

> `HTB{why_d1d_y0u_m3ss_3v3ryth1ng_up_1ts_n0t_th4t_h4rd`

## Decrypting the DH part

The second problem is:

```python
ct2 = pow(g, flag2, n)
```

With g, n and ct2 known. This is known as a "discrete logarithm problem" or [DLP][wikipedia-dlp-article].

Since we know the prime factors p and q of n, the DLP can be solved separately
in GF(p) and GF(q). The Chinese remainder theorem will then provide x.

What's more p and q are smooth numbers, so the [Pohlig-Hellman algorithm][wikipedia-smooth-number] is
a computable alternative to process the DLP. It has a [built-in implementation in Sagemath][sagemath-discrete-log]:

```python
xp = discrete_log(group_p(CT2), group_p(G))
xq = discrete_log(group_q(CT2), group_q(G))
pt2 = crt([xp, xq], [P-1, Q-1])
flag2 = bytes.fromhex(hex(pt2)[2:-400])
```

> `_ju5t_us3_pr0p3r_p4r4m3t3rs_f0r_4ny_crypt0syst3m...}`

[author-profile]: https://app.hackthebox.eu/users/219091
[sagemath-discrete-log]: https://doc.sagemath.org/html/en/reference/groups/sage/groups/generic.html#sage.groups.generic.discrete_log
[sagemath-sqrt]: https://doc.sagemath.org/html/en/reference/finite_rings/sage/rings/finite_rings/integer_mod.html#sage.rings.finite_rings.integer_mod.square_root_mod_prime
[wikipedia-dlp-article]: https://en.wikipedia.org/wiki/Discrete_logarithm#Algorithms
[wikipedia-smooth-number]: https://en.wikipedia.org/wiki/Smooth_number#Powersmooth_numbers

[square-flag]: images/equations/square-flag.png
