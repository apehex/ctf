> oh... god... what have you done...

> Author: **[willwam845][author-profile]**

## MistakE(s)?

This is a RSA challenge with:

- p, q, n known
- both `q-1` and `p-1` have little prime factors

## Decrypting the RSA part

The GCD of `p - 1` and `e` is 2:

`f1 ^ (x*e) = f1 ^ 2 * f1 ^ y(p-1) = f1 ^ 2`

and apply the square root algorithm

> `HTB{why_d1d_y0u_m3ss_3v3ryth1ng_up_1ts_n0t_th4t_h4rd`

## Decrypting the DH part

1) it is feasible to solve the DLP in GF(p) and GF(q) separately:
  - with the `discrete_log` function in Sagemath
  - it is still rather computation intensive
  - it doesn't take advantage of the particularities of p & q: `p-1` & `q-1`
    both have a smooth prime factorization
2) solve in GF(p) and GF(q) and use the decompositions with the Pohlig-Hellman
  algorithm

Pohlig-Hellman + Chinese remainders

> `_ju5t_us3_pr0p3r_p4r4m3t3rs_f0r_4ny_crypt0syst3m...}`

[author-profile]: https://app.hackthebox.eu/users/219091
