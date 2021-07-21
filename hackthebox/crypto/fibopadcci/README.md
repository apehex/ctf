# Fibopadcci

> **While investigating the reported insider risk, we managed to retrieve the**
> **source code for a suspicious server. However, we still can't figure out how to**
> **decrypt the admin's message. Can you help us?**

## Interacting with the server

The server has 2 modes:

```
-------------------------
| Menu                  |
-------------------------
|[0] Encrypt flag.      |
|[1] Send me a message! |
-------------------------
```

Mode 0 returns:

```
encrypted_flag: 47b756c88a143410ed2ba29e94689b89fcba3706f14b33fbbf65be59b78c4a5845fc5c2a1bbb66a21f0b3b23dbeed815
a: b1d755cd8fff461835974451f7528fd3
b: dcfefc222548071dc06db50c3b6e1e18
```

Each time you request an encrypted flag the result changes. Supposing that the flag
and key are constant, the change comes from the randomization of the IV a & b.

In return, the mode 1 allows to send a ciphertext with its IV. The server
only says whether the padding is correct after decryption.

## The scheme

### AES CBC

AES is used in block mode:

- the block length is 16 bytes
- the data is padded until it reaches a length multiple of 16
- then the data is chunked in blocks

More precisely, it is a variant of the CBC mode, with a propagation from one
block to the next.


### Particularities

Reading the server side code gives us the exact algorithm: 

![][equation_cbc]

The encryption scheme has a few particularities:

- each plaintext block is xorred twice:
  - once with the previous plaintext block
  - once with the previous encrypted block
- the padding is an excerpt from the Fibonacci sequence
- the decryption is made with an unrelated IV

I found that being rigorous with notations helps a lot with confusion.
The details of my notations are at the [end of the document](#annex-notations).

The special padding will be called "fibopadcci" and noted ![P_i][constant_fibopadcci-i], for
i bytes of padding:

![][constant_fibopadcci-5]


### Properties

Because of the chaining, xorring each cipher block with a constant &delta;
impacts all the plaintext with the same constant:

![][equation_cbc-linearity]

This can be easily demonstrated by a mathematical induction, thanks to the
former equation set.

And it means that we can modify the decrypted plaintext without knowing the key!

## The padding oracle

### Padding incorrect

Suppose we want to alter the cipher and send it to the server.

Selecting the mode 0, we receive:

- a plaintext IV ![a][variable_plaintext-iv]
- a ciphertext IV ![b][variable_ciphertext-iv]
- the flag ![c][equation_c-definition]:
  - padded with bytes from the Fibonacci sequence
  - encrypted with an unknown key ![K_s][constant_key]

And we send:

- a new ciphertext IV ![b+&delta;][equation_b-xor-delta]
- and a new ciphertext ![c+&delta;][equation_c-xor-delta]

The server then performs the decryption:

![][equation_fixed-plaintext-iv]

And it fails with "padding incorrect". For two reasons:

- ![c+&delta;][equation_c-xor-delta] is mostly random, there is no reason
  for it to end with the right padding
- the server actually performs the decryption with an unrelated plaintext IV, ![A_s][constant_plaintext-iv]

Both problems can be solved with a ~~bit~~ lot of coding.

### Adjusting to the fixed IV

The server performs the decryption with a fixed value for a, ![A_s][constant_plaintext-iv]:

```python
a = b'HTB{th3_s3crt_A}' # My secret A! Only admins know it, and plus, other people won't be able to work out my key anyway!
print(a.hex())
'4854427b7468335f73336372745f417d'
```

This limits the alteration vector to a single value:

![][equation_calculating-delta]

This way the server actually decrypts the altered ciphertext to:

![][equation_cbc-1-linearity]

### Success!

Still there is no guarantee that ![F_s+&delta;][equation_altered-plaintext] ends with a fibopadcci.

The server randomizes ![a][variable_plaintext-iv] and ![b][variable_ciphertext-iv] each time
we request the mode 0.

This makes the result of the decryption random as well: with enough tries, the
last few bytes of the decrypted vector will be valid fibopadcci.

On average, "enough" a probability of `(1 / 256^i)` for i matching bytes
of fibopadcci:

- `1 / 256` for 1 bytes
- `1 / 65536` for 2 bytes
- etc

When the server responds with "message successfully sent", realistically only the last byte matches.

And the fibopadcci of length 1 byte is:

![][constant_fibopadcci-1]

### Decryption of the last byte

Knowing ![P_1][constant_fibopadcci-1] is final result of the decryption, we can
infer the last byte:

![][equation_decrypt-last-byte-flag]

Finally! This gives us the last byte of the last block.

Yup, we knew this all along... Which is actually very good news, since I was
wondering the whole time if my ramblings made any sense.

Also, since that last byte is not padding:

> the flag is -at least- 16 bytes longs

### Iteration

That's when the attack cranks up!

## The implementation

I felt clever until I hit the socket implementation ^^

## Annex: notations

### Syntax

- the first numeric subscript index is the block index: ![F_s,n][constant_flag-block-n]
- the second numeric subscript index is the bytes index, in the block: ![F_s,n,i][constant_flag-block-n-byte-i]

### Naming

#### Constants

The constants are written in uppercase:

- the secret plaintext **flag** is ![F_s][constant_flag]
- the secret plaintext IV is ![A_s][constant_plaintext-iv]
- the secret key is ![K_s][constant_key]
- the number of blocks in the flag is ![N][constant_flag-length]
- the special padding:
  - is called "fibopadcci"
  - ![P_i][constant_fibopadcci-i] denotes a padding of i bytes
  - no distinction is made between:
    - a full block length random vector ending with i padding bytes
    - and a vector of only i padding bytes

#### Variables

In contrast, all the variables are written in lowercase:

- any plaintext IV is either ![a][variable_plaintext-iv] or ![p_0][variable_plaintext-0]
- any ciphertext IV is either ![b][variable_ciphertext-iv] or ![c_0][variable_ciphertext-0]
- any plaintext is ![p][variable_plaintext]
- any ciphertext is ![c][variable_ciphertext]
- any block index is ![n][variable_block-index]: ![F_s,n][constant_flag-block-n]
- any byte index is ![i][variable_byte-index]: ![F_s,n,i][constant_flag-block-n-byte-i]
- any block mask is ![&delta;][variable_block-mask] ; it can either represent:
  - a single block mask
  - or a mask of multiple blocks, with the same pattern repeated on each
  - depending on the size of the vector it is xorred with 
- any ignored / random byte in hexadecimal format is `..`

#### Functions

The functions are written in uppercase:

- the XOR operation is ![XOR][function_xor]
- the XOR inverse operation is also XOR ![XOR][function_xor]
- the AES encryption function is ![E][function_aes]
- the AES decryption function is ![E-1][function_aes-1]
- the overall CBC encryption scheme is ![C][function_cbc]
- the overall CBC decryption scheme is ![C-1][function_cbc-1]

[constant_fibopadcci-1]: maths/constants/fibopadcci-1.png
[constant_fibopadcci-5]: maths/constants/fibopadcci-5.png
[constant_fibopadcci-i]: maths/constants/fibopadcci-i.png
[constant_flag]: maths/constants/flag.png
[constant_flag-block-n]: maths/constants/flag-block-n.png
[constant_flag-block-n-byte-i]: maths/constants/flag-block-n-byte-i.png
[constant_flag-length]: maths/constants/flag-length.png
[constant_key]: maths/constants/key.png
[constant_plaintext-iv]: maths/constants/plaintext-iv.png

[equation_b-xor-delta]: maths/equations/b-xor-delta.png
[equation_c-xor-delta]: maths/equations/c-xor-delta.png
[equation_c-definition]: maths/equations/c-definition.png
[equation_cbc]: maths/equations/cbc.png
[equation_cbc-1-linearity]: maths/equations/cbc-1-linearity.png
[equation_cbc-linearity]: maths/equations/cbc-linearity.png
[equation_altered-plaintext]: maths/equations/altered-plaintext.png
[equation_calculating-delta]: maths/equations/calculating-delta.png
[equation_decrypt-last-byte-flag]: maths/equations/decrypt-last-byte-flag.png
[equation_decrypt-last-4-bytes-flag]: maths/equations/decrypt-last-4-bytes-flag.png
[equation_fixed-plaintext-iv]: maths/equations/fixed-plaintext-iv.png

[function_aes]: maths/functions/aes.png
[function_aes-1]: maths/functions/aes-1.png
[function_cbc]: maths/functions/cbc.png
[function_cbc-1]: maths/functions/cbc-1.png
[function_xor]: maths/functions/xor.png

[variable_block-index]: maths/variables/block-index.png
[variable_block-mask]: maths/variables/block-mask.png
[variable_byte-index]: maths/variables/byte-index.png
[variable_ciphertext-iv]: maths/variables/ciphertext-iv.png
[variable_ciphertext-0]: maths/variables/ciphertext-0.png
[variable_ciphertext]: maths/variables/ciphertext.png
[variable_plaintext-iv]: maths/variables/plaintext-iv.png
[variable_plaintext-0]: maths/variables/plaintext-0.png
[variable_plaintext]: maths/variables/plaintext.png
