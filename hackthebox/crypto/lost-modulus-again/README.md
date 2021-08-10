> **I lost my modulus again, can you help me one more time?**

> Author: **[0verflowme][author-profile]**

## Calculating the modulus

While browsing the known attacks on the RSA for the "Quick Maffs" challenge,
I came across the Coppersmith methods and its "short padding" variant.

So for once, we'll skip the makeshift attempts!

The attack requires the modulus, hopefully it can be computed from the
known messages:

![][equation-modulus]

In Sage:

```python
G, x, y = xgcd(M3 ** 3 - C3, M4 ** 3 - C4)
```

The equation above only guarantes that N divides this GCD, but the coefficient
`k1` and `k2` could have a common factor.

To check, 

```python
# 2046.7055097450218
# 2045.7397272640376
# 2041.174820714303
# 2046.8654262375285
# 2047.0934372332526
print(f'{math.log2(C1)}\n{math.log2(C2)}\n{math.log2(C3)}\n{math.log2(C4)}\n{math.log2(G)}')
```

There's less than a factor of 2 between G and C4: G is actually the modulus N.

## Calculating the padding delta

Since the padding and public exponent are both small

The challenge matches the requirements for the Coppersmith attack:

![][equation-coppersmith-requirements]

Where the message M is the target flag.

With:

![][equation-coppersmith-definitions]

The difference in padding is a root of the resultant in X of P1 and P2:

![][equation-coppersmith-solution]

This calculation is straightforward in Sage:

```python
def coppersmith_short_pad_attack(c1: int, c2: int, n:int, e: int=3, eps: float=0.04):
    R1.<x, y> = PolynomialRing(Zmod(n))
    R2.<y> = PolynomialRing(Zmod(n))

    g1 = (x ^ e - c1).change_ring(R2)
    g2 = ((x + y) ^ e - c2).change_ring(R2)
 
    # Changes the base ring to Z_N[y] and finds resultant of g1 and g2 in x
    res = g1.resultant(g2, variable=x)

    # the resultant is a function of y only
    roots = res.univariate_polynomial().change_ring(Zmod(n)).small_roots(epsilon=eps)

    return roots[0]
```

This gives us the difference in padding between M1 and M2: the relation 

## The Franklin-Reiter related message attack

Replacing Y with the padding delta, M1 is a common root of P1 and P2. So `X - M1`
is a factor in the polynomial GCD of P1 and P2.

Using Sage (MVP!):

```python
def composite_gcd(g1,g2):
    return g1.monic() if g2 == 0 else composite_gcd(g2, g1 % g2)

def franklin_reiter_attack(c1, c2, n, D, e=3):
    R.<x> = PolynomialRing(Zmod(n))
    g1, g2 = [x ^ e - c1, (x + D) ^ e - c2]
    return -composite_gcd(g1,g2).coefficients()[0]
```

So:

```python
# the root is found modulo N: since it's negative it appears as a large number 
delta = coppersmith_short_pad_attack(C1, C2, n, E) - n
message = franklin_reiter_attack(C1, C2, n, delta, E)
```

```python
b'HTB{Fr4nk1ln_r3t1t3r_sh0rt_p4d_4tt4ck!4nyw4ys_n3v3r_us3_sm0l_3xp_f0r_rs4!1s_th1s_Msg_g01ng_l4rg3r?_0h_y3s_cuz_1_h4v3_t0_Pr3v3nt_Cub3_r00t_4tt4ck}\xf5V\x87\x06EC\xd8\xa8\xcaS\xc7?\xb3\xfcN\xce'
```

[author-profile]: https://app.hackthebox.eu/users/109128

[equation-coppersmith-definitions]: images/equations/coppersmith-definitions.png
[equation-coppersmith-requirements]: images/equations/coppersmith-requirements.png
[equation-coppersmith-solution]: images/equations/coppersmith-solution.png
[equation-modulus]: images/equations/modulus.png
