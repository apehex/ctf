# Fibopadcci

> **While investigating the reported insider risk, we managed to retrieve the**
> **source code for a suspicious server. However, we still can't figure out how to**
> **decrypt the admin's message. Can you help us?**

## Interacting with the server

The server has 2 modes:
- mode 0 sends the flag
- mode 1 sends a message

Each time you request the encryption the result changes. Supposing that the flag
is constant, the key is somehow randomized.

```
encrypted_flag: 47b756c88a143410ed2ba29e94689b89fcba3706f14b33fbbf65be59b78c4a5845fc5c2a1bbb66a21f0b3b23dbeed815
a: b1d755cd8fff461835974451f7528fd3
b: dcfefc222548071dc06db50c3b6e1e18
```

## The scheme

AES is used in block mode:
- the block length is 16 bytes
- the data is padded, to reach a length multiple of 16
- then it is chunked

## Sending a message

The server tries to decrypt with a fixed value for a:

```
HTB{th3_s3crt_A}
0x4854427b7468335f73336372745f417d
```

The first step of the decryption is xorring with a:

```
ECB-1(x) = b ^ AES-1 (a ^ x)
```

`a` is updated after each decrypted block, so the input value is actually used
once, on the first block.

Noting `a` the original IV, `a_` the fixed IV:

```
b_ = b ^ a ^ a_
&rarr; b_ ^ a_ = b ^ a
```

So replacing the first block with `b_ = b ^ a ^ a_` will force the decryption
using the original `a`.