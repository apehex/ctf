#!/usr/bin/env python3

from sage.arith.misc import crt # Chinese Remainder Theorem
from sage.groups.generic import bsgs, discrete_log # baby steps giant steps
from sage.rings.finite_rings.integer_mod import square_root_mod_prime
from typing import List

# ================================================================== parameters
N = 0xbe30ccaf896c16f53515e298df25df9158d0a95295c119f0444398b94fae26c0b4cf3a43b120cf0fb657069e0621eb1d2dd832eef3065e80ddbc35854dd4585cc41fd6a5b36339c0d9fcc066272be6818be6a624f75482bbb9c408010ac8c27b20397d870bfcb14e6318097b1601f99e391c9b68c5c586f8da561ff8507be9212713b910b748370ce692c11afa09b74ce80c5f5dd72046415aeed85e1ecedca14abe17ed19ab97729b859120699d9f80dd13f8483773df15b938b8399702a6e846b8728a70f1940d4c6e5835a06a89925eb1ec91a796f270e2d9be1a2c4bee5517109c161f04333d9c0d4034fbbd2dcf69fe734b759a89937f4d8ea0ee6b8385aae14a2cce361
P = 0x16498bf7cc48a7465416e0f9ec8034f4030991e73aff9524ef74cc574228e36e6e1944c7686f69f0d1186a69b7aa77d7e954edc8a6932f006786f4648ecc8d4f4d3f6c03d9a1ee9fe61b28b6dd2791a63be581b8811a8ac90a387241ea68b7d36b4a274f64c7a721ad55cfcef23cd14c72542f576e4b507c11c4fa198e80021d484691b
Q = N // P
E = 0x69420
G = 0x69420

# ================================================================= ciphertexts
CT1 = 0xa82b37d57b6476fa98f6ee7c278d934bd96c49aa1c5399552d25211230d76cb16ade049572bf631e3849903638d41c884957b9592d0aa072b2bdc3105fe0e3253284f85286ec613966f9cde77ae06e2053dc2254e44ca673b4c76879eff84e5fc32af976c1bfafe147a277d72aad674db749ed8f34d2ebe8189cf12afc9baa17764e4b
CT2 = 0x65d57a564b8a8667a956705442063392b9b975b8ef869a6dbed04d6e585351f559fe6f5d96823f60b7306740fe2cf5aa81e4a12736d4f0a4826cbc8b4312643af19c75432b4ab222837031851f312df5d707b39bdf2d272f25c1947f3e2943f3592cb0519fee8f4b458021b6b8ee4eabeeae5127d412df4f6a88f66d7cc34c6bb77e0a1440737d0e167f9489f0c7fbfd7f6a5870b4b2865d29b91f6c2b375951e85b1b9f03887d4d3c4a6218111a95021ed1d554c57269e7830c3e7b8e17d13e1fb75ee9f305833d0cb6bfab738572cdbbc8b33b878ad25f78d47d7f449a6c348f5f9f1df3e09f924534a3669b4e69bd0411d154ec756b210691e2efc4a55aa664d938a868f4d

# ================================================== Chinese remainders theorem

# crt in sagemath
def chinese_remainders(congruences, moduli):
    assert len(congruences) == len(moduli)

    _k = len(moduli)
    _product = prod(moduli)
    _basis = [_product // moduli[i] for i in range(_k)]
    _inverses = [pow(_basis[i], -1, moduli[i]) for i in range(_k)]

    r = sum([congruences[i] * _basis[i] * _inverses[i] for i in range(_k)])
    return r % _product

# ==================================================== Pohlig-Hellman algorithm

def _phi(p: int, q: int) -> List[int]:
    _p_factors = {_f[0]: _f[1] for _f in list(factor(p - 1))}
    _q_factors = {_f[0]: _f[1] for _f in list(factor(q - 1))}
    _all_factors = set(_p_factors.keys()).union(set(_q_factors.keys()))
    return {_f: _p_factors.get(_f, 0) + _q_factors.get(_f, 0) for _f in _all_factors}

def _pohlig_hellman_prime_order(g: int, h: int, n: int, p: int, e: int) -> int:
    """
    `g` generates a cyclic group of order p^e.
    """
    _hi = h
    _di = 0
    _xi = 0
    _gamma = pow(g, p ** (e - 1), n)

    for i in range(e):
        _hi = pow(
            (pow(g, -_xi, n) * h) % n,
            p ** (e - 1 - i),
            n)
        _di = bsgs(_gamma, _hi, bounds=(0, p), operation='*')
        _xi = _xi + _di * (p ** i)

    return _xi

def pohlig_hellman(h, g, p, q):
    _order = (p - 1) * (q - 1)
    _factors = _phi(p, q)
    _congruences = {}
    for _pi, _ei in _factors.items():
        _ni = _order // (_pi ** _ei)
        _gi = pow(g, _ni, p * q)
        _hi = pow(h, _ni, p * q)
        _xi = _pohlig_hellman_prime_order(g=_gi, h=_hi, n=p*q, p=_pi, e=_ei)
        _congruences[_pi ** _ei] = _xi

    return _congruences # x_i for each p_i ** e_i

# ========================================================================= rsa
_, x, y = xgcd(E, P - 1) # 2
ct1_2 = pow(CT1, x, P) # CT1^2
pt1 = int(square_root_mod_prime(ct1_2, P))

# ================================================================ dh: method 1
group_p = GF(P)
group_q = GF(Q)

xp = discrete_log(group_p(CT2), group_p(G))
xq = discrete_log(group_q(CT2), group_q(G))

pt2 = crt([xp, xq], [P-1, Q-1])

# pt2_i = pohlig_hellman(CT2, G, P, Q)
# pt2 = int(crt(
#     list(pt2_i.values()), # x_i
#     list(pt2_i.keys()))) # p_i ^ e_i

# ==================================================================== decoding
flag1 = bytes.fromhex(hex(P-pt1)[2:-138])
flag2 = bytes.fromhex(hex(pt2)[2:-400])
