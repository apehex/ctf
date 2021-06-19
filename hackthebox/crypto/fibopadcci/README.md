# Fibopadcci

> **While investigating the reported insider risk, we managed to retrieve the**
> **source code for a suspicious server. However, we still can't figure out how to**
> **decrypt the admin's message. Can you help us?**

## Interacting with the server

The server has 2 modes:

- mode 0 sends the flag
- mode 1 sends a message

Each time you request the encryption the result changes. Supposing that the flag
and key are constant, the change comes from the randomization of the IV a & b.

```
encrypted_flag: 47b756c88a143410ed2ba29e94689b89fcba3706f14b33fbbf65be59b78c4a5845fc5c2a1bbb66a21f0b3b23dbeed815
a: b1d755cd8fff461835974451f7528fd3
b: dcfefc222548071dc06db50c3b6e1e18
```

In return, the mode 1 allow to send a ciphertext with its IV. The server's
only only says whether the padding is correct after decryption.

## The scheme

AES is used in block mode:

- the block length is 16 bytes
- the data is padded:
  - until it reaches a length multiple of 16
  - the padding values are an excerpt from the Fibonacci sequence
- then it is chunked

More precisely, it is a variant of the CBC mode, with a propagation from one
block to the next.

With:

- ![p_i][symbol_p-i] the ith plaintext block (length 16 bytes)
- ![c_i][symbol_c-i] the ith encrypted block (length 16 bytes)
- ![AES][symbol_aes] the encryption function in ECB mode
- ![AES][symbol_aes-1] the inverse function, ie the decryption algorithm

![][equation_aes-cbc]

Because of the chaining, xorring each cipher block with a constant &alpha;
impacts all the plaintext with the same constant:

![][equation_plaintext-tweaking]

This can be easily demonstrated by a mathematical induction, thanks to the
former equation set.

And it means that we can modify the plaintext without knowing the key!

## The padding oracle

There is little chance that the random cipher text will produce a full
Fibonacci sequence after decryption. The only plausible possibility is a
single padding byte, `OxO1`. So:

![][equation_decrypt-last-byte]

Finally! This gives us the last byte of the last block.
In my case: `b`

The server tries to decrypt with a fixed value for a:

```
HTB{th3_s3crt_A}
0x4854427b7468335f73336372745f417d
```

## The implementation

Easier said than done though!


[equation_aes-cbc]: maths/equation_aes-cbc.png
[equation_decrypt-last-byte]: maths/equation_decrypt-last-byte.png
[equation_invert-secret-iv]: maths/equation_invert-secret-iv.png
[equation_plaintext-tweaking]: maths/equation_plaintext-tweaking.png
[symbol_aes]: maths/symbol_aes.png
[symbol_aes-1]: maths/symbol_aes-1.png
[symbol_c-i]: maths/symbol_c-i.png
[symbol_p-i]: maths/symbol_p-i.png