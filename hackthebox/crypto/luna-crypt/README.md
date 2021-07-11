# LunaCrypt

> **Our astronaut gained access to a key satellite and intercepted an encrypted**
> **message. The forensics team also recovered a file that looks like a custom**
> **encryption protocol. We're sure that these two elements are linked.**
> **Please can you help us reveal the contents of the secret message?**

> Author: **[Xh4H][xh4h-profile-link]**

## Fun with flags!

The algorithm encrypts ascii strings, character by character by randomly
selecting a sequence of bitwise manipulations.

The sequence of operations is given by a numeric flag, one per encrypted character.

It is written in the output message along its corresponding character:

```python
output = [f"{str(ord(v))} {str(ord(FLAGS[i]))}" for i, v in enumerate(CHARS)]
```

## Loading the output

Since there's only one message, I wrote it into a hardcoded constant:

```python
CIPHERTEXT = "43 72 198 195 192 135 153 225 52 205 121 193 32 58 154 243 63 84 35 233 114 18 21 64 192 205 220 235 184 211 158 24 196 113 15 141 196 28 118 78 2 105 20 215 65 68 164 223 63 86".split()
CHARS = [int(_s) for _s in MESSAGE[::2]]
```

> the flags are shifted by a small constant!

That eluded me until the end, the author left a few traps for the impatients :)

```python
def AppendFlag(flag):
    FLAGS.append(strchr(flag > 0 and flag - len(str(flag)) or flag))
```

In most case the inverse is simply:

```python
def invert_flag(flag):
	return flag + len(str(flag))
```

The former doesn't work on 8, 9, 97, 98 and 99 because these number have a
different length after being shifted. Luckily none of these appear in the
ciphertext, so we can be lazy with reason!

```python
FLAGS = [invert_flag(int(_s)) for _s in MESSAGE[1::2]]
```

So we have the complete knowledge of all the operations performed to encrypt
the input message.

## Reversing the bitwise operations

To decrypt the message, we'll invert the successive bitwise operations one
after another.

The script can perform 4 different operations on the characters:

- `FL_NEGATE`:
  - bitwise negation
  - the negation is its own inverse
- `FL_XORBY6B`:
  - bitwise xor with `0x6b`
  - xor is its own inverse too
- `FL_XORBY3E`
 - bitwise xor with `0x3e`
 - xor with `Ox3e` again to invert
- `FL_SWAPBYTES`:
  - splits the byte in 2 parts:
    - the 4 left bits, `THIS_LSB`
    - the 4 right bits, `THIS_MSB`
  - swaps their positions: left part on the right and 
  - xor each part 
  - to invert:
    - xor with `0xBD`

So the only function missing is the inverse of the swap operation:

```python
def invert_swap(char):
    _byte = bitxor(ValidateChar(char), 0xBD)
    _left = bitext(_byte, 0, 4)
    _right = bitext(_byte, 4, 4)

    return strchr(bitbor(bitlst(_left, 4), _right))
```

Also, the operations are all symmetric, so the order doesn't matter.

## Decrypting the message

We can now decrypt a single character, knowing the corresponding flag:

```python
def decrypt_single_char(char, flag):
    _byte = ValidateChar(char)

    if CheckFlag(flag, FL_XORBY3E):
        _byte = XorBy3E(_byte)
    if CheckFlag(flag, FL_XORBY6B):
        _byte = XorBy6B(_byte)
    if CheckFlag(flag, FL_NEGATE):
        _byte = NegateChar(_byte)
    if CheckFlag(flag, FL_SWAPBYTES):
        _byte = invert_swap(_byte)

    return _byte
```

> Python 3 now has a standard library to deal with flags, `[Flag][python3-flag-link]`

And then we iterate:

```python
def decrypt(chars, flags):
    return ''.join([decrypt_single_char(_c, _f) for _c, _f in zip(chars, flags)])
```

For a second, I thought I messed up again since the first character is a space
instead of the expected "H"!

A great challenge, thanks to [Xh4H][xh4h-profile-link]!

> HTB{Lun4_Lu4_L4t1n_M00n}

[python3-flag-link]: https://docs.python.org/3/library/enum.html#flag
[xh4h-profile-link]: https://www.hackthebox.eu/profile/21439
