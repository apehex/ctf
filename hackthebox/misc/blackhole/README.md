# Blackhole

> **A strange file has been discovered in Stephen Hawking's computer. Can you**
> **discover what it is?**

## Fast & failed

Nothing suspicious with `exiftool`, `stegoveritas` and `strings -n8`.

Applying gimp filters -edge detect, contrast, sharpen and the like- doesn't help either.

Zooming? Nope, nothing hidden in the actual content.

## Steganography

Yet `steghide extract -sf hawking.jpg` asks for a password.
All I had left was guessing:

```
blackhole
tragic
life
funny
hawking
```

Finally!! It works, but it's very unsatisfying...

## Encoding

The extracted data looks like base64:

```
UldaeFluUnhlaUJKZFhoNGRXMTVJRlJ0YVhkMWVuTWd....
```

After decoding twice:

```
GSA{M3udQ_k3S_sG3_a4rSzQc5_F3s_X0t_c0vM}
```

This is clearly a rotation, with a delta of one character.
Surprisingly there's no ready made tool for this, so here's mine:

```python
# =================================================== rotate a single character

def _rotate(c, delta=13, origin='a', count=26):
    return chr(ord(origin) + ((ord(c) - ord(origin) + delta) % count))

def rotate(c, alpha=13, digits=0):
    if c.isalpha():
        if c.islower():
            return _rotate(c, alpha, 'a', 26)
        else:
            return _rotate(c, alpha, 'A', 26)
    elif c.isdigit():
        return _rotate(c, digits, '0', 10)
    else:
        return c

# ===================================================== rotate the input string

def caesar(s, alpha=13, digits=0):
    for c in s:
        yield rotate(c, alpha, digits)
```
