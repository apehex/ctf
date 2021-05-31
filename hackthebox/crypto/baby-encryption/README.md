# Baby encryption

> **You are after an organised crime group which is responsible for the illegal
> weapon market in your country. As a secret agent, you have infiltrated the
> group enough to be included in meetings with clients. During the last
> negotiation, you found one of the confidential messages for the customer. It
> contains crucial information about the delivery. Do you think you can decrypt
> it?**

## The encryption

Each byte is mapped to a new value with the following arithmetic operation:

```python
ct.append((123 * char + 18) % 256)
```

Trivia: this multiplicative group of integers modulo 256 contains 256 distinct
elements.

```python
enc = [((123 * n) + 18) % 256 for n in range(256)]
len(set(enc))
256
```

`{123 * n % 256}` is a group with an inverse element:

```python
```

## Decryption

To decrypt the message, we can either:

1) use a mapping
2) mathematically invert the arithmetic operation

Since 179 is the inverse of 123 modulo 256:

```python
def decrypt(b: int):
  return ((b - 18) * 179) % 256
```

This will do:

```python
print(bytes([decrypt(b) for b in CT]))
```
