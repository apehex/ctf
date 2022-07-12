> They released this new mystery box thing to modify messages or something,
> but i'm sure my signing server will be fine.

> Author: **[willwam845][author-profile]**

## The chosen message attach

The server uses RSA, with both public and private keys unknown.

We can request the signature of any message apart from `M`: upon receiving the
signature of M, the server responds with the flag.

So we want to forge the signature of M from the signature of other numbers. In particular:

![][equation-signature-breakdown]

Since M is prime itself, we cannot use its prime factorization.

Instead we can choose an arbitraty message m<sub>1</sub> and compute:

![][equation-signature-forging]

## Calculating the modulus

To calculate the inverse of our chosen message, we'll need the modulus.

Hopefully it can be obtained from the signature of -1:

![][equation-modulus-calculation]

## Forging a signature

So, with N and m<sub>1</sub> = 3, we compute m<sub>2</sub>:

```python
m2 = M * pow(3, -1, N)
```

Then we ask the server for the signatures of m<sub>1</sub> and m<sub>2</sub>.

We can finally submit the signature of M: it is the product of the two former
signatures.

> HTB{3mpl0y33s_mu5t_h45h_4ll_m3554g3s_b3f0r3_l00k1ng_4t_th3m_t0_pr3v3nt_bl1ndn3ss}

[author-profile]: https://app.hackthebox.eu/users/219091

[equation-modulus-calculation]: images/modulus-calculation.png
[equation-signature-breakdown]: images/signature-breakdown.png
[equation-signature-forging]: images/signature-forging.png
