> The decrypt function is broken and I lost my flag. Can you help me fix it?

> Author: **[r4j][author-profile]**

## The broken decryptor

### Broken algorithm

The server uses [AES CTR][wikipedia-article]:

![][ctr-flow-chart]

- each block is encrypted / decrypted **independently**
- it is initialized with a private key and an IV
- it generates a stream of cipher blocks
- uses the same function for encryption & decryption

And in this particular case, the IV is a global / constant throughout the session:

```python
key = os.urandom(0x10).replace(b'\x00', b'\xff')
iv = os.urandom(0x10).replace(b'\x00', b'\xff')
```

So the counter is also the same on each encrytion and the keystream too!

### Broken conversions

So the security is broken, but that's not all:

```python
def decrypt(data):
    ctr = Counter.new(128, initial_value=int(iv.hex(), 16))
    crypto = AES.new(key, AES.MODE_CTR, counter=ctr)
    return crypto.decrypt(data.encode())
```

`data.encode()` passes a `str` to the decrypt function which expects `bytes`:

```
1) Get flag
2) Encrypt Message
3) Decrypt Message
Your option: 3
Enter ciphertext: dba3ab0550c6ad06a13e7a17ac13939c
An error occured
```

But this doesn't matter since the encryption and decryption functions are
the same in AES CTR.

### Custom encryption

Let's look at the encryption more closely.

In theory for each plaintext block b<sub>i</sub>:

![][standard-ctr-encryption]

Here, there's a little customization:

![][custom-ctr-encryption]

Where o<sub>i</sub> is a random block, independent of the encryption this time.

## Canceling the random bytes

### With statistics

But there's yet another implementation issue:

```python
otp = os.urandom(len(data)).replace(b'\x00', b'\xff')
```

> The byte `0x00` never appears in the random stream `otp` (o in the latest equation).

Then, for all bytes j of any block i:

![][all-the-byte-values-except-one]

When iterating through the random bytes, all the values are taken in the encrypted bytes.
All except one, the value resulting from a null random byte:

![][canceling-the-randomness]

So, if we request the flag encryption enough times, the only values which will
not appear in the set of ciphertexts will correspond to the above formula.

### In practice

More precisely, enough will be 4096 = 256 * 16. With each value repeated 16 times
on average, it is unlikely that a byte other than 0x00 will not appear. This allows to
single out the null byte.

The server is relentlessly queried by a python script, thanks to the socket module.

Then the following function finds the missing byte in a set of integers:

```python
def find_missing_bytes(collection: List[int]) -> List[int]:
    """
    Because of the substitution, the null byte never appears in `otp`.

    So the bytes with no occurences in the collected ciphertexts correspond to
    otp_i = 0x00.
    """
    # occurences of all possibles bytes
    __o = [collection.count(__b) for __b in range(256)]

    # return the byte values with 0 occurences
    return [__b for __b, __c in enumerate(__o) if __c == 0]
```

And then iterate over all the positions in all the blocks:

```python
def compute_candidate_ciphertexts(ciphertexts: List[bytes]) -> List[bytes]:
    """
    Computes all ciphertexts composed of bytes with no occurences in the input
    list.
    """
    __candidate_bytes = [
        find_missing_bytes([__c[__i] for __c in ciphertexts]) 
        for __i in range(len(ciphertexts[0]))]

    # return the cartesian product of all bytes
    return [bytes(__p) for __p in itertools.product(*__candidate_bytes)]
```

### Canceling the keystream

At this stage, we have computed ![][without-the-random-bytes].

Re-encrypting this ciphertext will result in:

![][canceling-the-keystream]

And finally, we can apply the former trick to remove the randomness.

> HTB{1V_r3u$3#!}

[author-profile]: https://app.hackthebox.eu/users/13243
[wikipedia-article]: https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)

[all-the-byte-values-except-one]: images/equations/all-the-byte-values-except-one.png
[canceling-the-keystream]: images/equations/canceling-the-keystream.png
[canceling-the-randomness]: images/equations/canceling-the-randomness.png
[ctr-flow-chart]: images/ctr-flow-chart.svg
[custom-ctr-encryption]: images/equations/custom-ctr-encryption.png
[standard-ctr-encryption]: images/equations/standard-ctr-encryption.png
[without-the-random-bytes]: images/equations/without-the-random-bytes.png
