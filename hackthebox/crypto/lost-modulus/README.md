> I encrypted a secret message with RSA but I lost the modulus.
> Can you help me recover it?

> Author: **[r4j][author-profile]**

## The custom RSA

Actually the algorithm looks legit.

The only problem I could find is:

```python
self.e = 3
```

`p` and `q` are huge numbers, so is the unknown modulus:

```python
self.p = getPrime(512)
self.q = getPrime(512)
```

So when performing the encryption, there's a good chance that:

![][equation_low-exponent]

In this case, the encrypted flag is the square root of the ciphertext:

![][equation_flag-cubic-root]

## Calculation

Actually there's a bottleneck: since the numbers are huge, the standard math
calculation of the cubic root will return a rounded number.

Instead of performing a root calculation, we can directly search for a number
whose cube is the target.

With a dichotomic search:

```python
def nth_root(x, n):
    # Start with some reasonable bounds around the nth root.
    upper_bound = 1
    while upper_bound ** n <= x:
        upper_bound *= 2
    lower_bound = upper_bound // 2
    # Keep searching for a better result as long as the bounds make sense.
    while lower_bound < upper_bound:
        mid = (lower_bound + upper_bound) // 2
        mid_nth = mid ** n
        if lower_bound < mid and mid_nth < x:
            lower_bound = mid
        elif upper_bound > mid and mid_nth > x:
            upper_bound = mid
        else:
            # Found perfect nth root.
            return mid
    return mid + 1
```

(this doesn't work for negative numbers, but whatever)

All that remains is encoding the result:

```python
bytes.fromhex(hex(nth_root(ct, 3))[2:])
```

> `HTB{n3v3r_us3_sm4ll_3xp0n3n7s_f0r_rs4}`

[author-profile]: https://app.hackthebox.eu/users/13243
[equation_flag-cubic-root]: images/flag-cubic-root.png
[equation_low-exponent]: images/low-exponent.png
