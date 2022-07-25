> In a post-apocalyptic world,
> you are an aspiring botanist who has dedicated his life to the study of plants and their genetic manipulation,
> and is an expert on their embryonic stage.
> On your journey around the world,
> hoping to find a way to artificially create plants that can withstand Earth's cruel environment,
> you have come across a new species in a seemingly inhospitable area.
> You know it's time for you to unlock the secrets of nature.
> Will 5 plants be enough?

> Author: **[aris][author-profile]**

## The plant seeds

The challenge is an mutant child of RSA, except the algorithm isn't actually used to encrypt.

We're just given random seeds of RSA, called `rns`:

```python
rns = [rng.next() for _ in range(5)]
```

Where:

```python
def next(self):
    self.s = (self.s * self.p + self.q) % self.r
    return self.s
```

`p`, `q` and `r` are the secret prime factors of N:

```python
self.n = self.p * self.q * self.r
```

## Isolating the parameters

The sequence of seeds s<sub>i</sub> is a mix between an arithmetic and a geometric progression:

![][sequence-of-seeds]

This sequence can be transformed into a pure geometric progression with:

![][geometric-progression]

This last serie is simpler, it involves two unknowns instead of 3.

```python
delta_i = [(SEEDS[i+1] - SEEDS[i]) for i in range(len(SEEDS) - 1)]
```

## Calculating the secret modulus

Since the modulus `r` is unknown we can't invert a member of the sequence to find `p`, yet.

To find this modulus, we can compute two different numbers which are congruent modulo `r`.
For example:

![][multiple-of-secret-modulus]

This difference is a multiple of `r`!
Since the secret modulus divides the public modulus `N` too:

```python
a = delta_i[0] * delta_i[-1]
b = delta_i[1] * delta_i[2]

r = math.gcd(N, a - b)
```

## Factoring the public modulus

We can now compute the inverse of the geometric progression to find its factor `p`:

```python
p = delta_i[1] * pow(delta_i[0], -1, r) % r
q = pq // p 
```

The results can be checked easily:

```python
print('N % p: {}\nN % q: {}\nN % r: {}'.format(N % p, N % q, N % r))
# N % p: 0
# N % q: 0
# N % r: 0
```

## Calculating the secret exponent

Just like the private key in the RSA cryptosystem, the exponent `d` is the inverse of `e` modulo `phi`:

```python
phi = (p - 1) * (q - 1) * (r - 1)
d = pow(E, -1, phi)
```

## Decrypting

The secret exponent d is not actually used for RSA encryption but as the key to an AES cipher:

```python
key = sha256(bytes.fromhex(hex(d)[2:])).digest()
cipher = AES.new(key, AES.MODE_ECB)
flag = cipher.decrypt(CT)
```

> `HTB{0op5_my_$33d$_f311_0ff_5h3_gr0und_4nd_br0ugh5_y0u_4_fl4g!#@$%}`

[author-profile]: https://app.hackthebox.com/users/37925
[geometric-progression]: images/geometric-progression.png
[multiple-of-secret-modulus]: images/multiple-of-secret-modulus.png
[sequence-of-seeds]: images/sequence-of-seeds.png
