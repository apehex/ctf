> To be accepted into the upper class of the Berford Empire, you had to attend the annual Cha-Cha Ball at the High Court.
> Little did you know that among the many aristocrats invited, you would find a burned enemy spy.
> Your goal quickly became to capture him, which you succeeded in doing after putting something in his drink.
> Many hours passed in your agency's interrogation room, and you eventually learned important information about the enemy agency's secret communications.
> Can you use what you learned to decrypt the rest of the messages?

> Author: **[Machina][author-profile]**

## Stream ciphers

At first, [Chacha20 looks quite intimidating][wiki-salsa20].

However, the cipher's complexity doesn't matter here:
In this scenario, Chacha20 does not directly encrypt the message but produces an independent byte stream.
And then this stream is used in a single XOR against the message.

```python
def xor(a, b):
    return bytes([__a ^ __b for __a, __b in zip(a, b)])
```

This is known as a stream cipher.

Anyway, since the key and the IV are the same for the encryption of the message and the flag, the cipher stream is the same.
XORing the encrypted message with the clear message will isolate the stream:

```python
xor(MESSAGE_CLEAR, MESSAGE_ENCRYPTED)
```

So that it can be canceled in the encryption of the flag:

```python
xor(xor(MESSAGE_CLEAR, MESSAGE_ENCRYPTED), FLAG_ENCRYPTED)
```

> `HTB{und3r57AnD1n9_57R3aM_C1PH3R5_15_51mPl3_a5_7Ha7}`

[author-profile]: https://app.hackthebox.com/users/131103
[wiki-salsa20]: https://en.wikipedia.org/wiki/Salsa20
