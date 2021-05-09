# Nuclear sale

> **Plutonium Labs is a private laboratory experimenting with plutonium
> products. A huge sale is going to take place and our intelligence agency is
> interested in learning more about it. We have managed to intercept the traffic
> of their mail server. Can you find anything interesting?**

## Reading the mails

After opening `challenge.pcap` in wireshark, we see a selection of SMTP packets.
It is the full-transcript of a back-and-forth conversation between
"sales@plutonium.lab" and "management@plutonium.lab".

To improve readability, the textual content can be reconstructed by following
the TCP stream or exporting the IMF objects.

Both parties talk about a mysterious seller, keeping his identity masked.
However there are a few clues, in the order of the conversation:

```
We are very XORry but the management does not approve such a sale.

He is a high profile individual. His information is encrypted below:
6b65813f4fe991efe2042f79988a3b2f2559d358e55f2fa373e53b1965b5bb2b175cf039

Here is the ciphertext encrypted with our key.
fd034c32294bfa6ab44a28892e75c4f24d8e71b41cfb9a81a634b90e6238443a813a3d34

Encrypting again with our key...
de328f76159108f7653a5883decb8dec06b0fd9bc8d0dd7dade1f04836b8a07da20bfe70
```

## Making sense of the exchanges

So the encryption is explicitely a XOR scheme.

Let's call the hex hashes `h1`, `h2`, `h3` in order of appearance.

We can infer / guess that:
- h1 contains the secret, encrypted with a first key, `k1`
- h2 is either a key or data encrypted with another key, `k2`
- h3 is somehow made of h1 and h2

The simplest scheme would be:
- h1 = k1 ^ m1
- h2 = k2
- h3 = k1 ^ k2

So:
- h2 ^ h3 = k2 ^ k1 ^ k2 = k1
- and h2 ^ h3 ^ h1 = k1 ^ k1 ^ m1 = m1

And indeed this snippet prints the flag:

```python
m = h1 ^ h2 ^ h3

# now we interpret the hex as ASCII
print(bytes.fromhex(hex(m)[2:]))
```
