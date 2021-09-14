> The decrypt function is broken and I lost my flag. Can you help me fix it?

> Author: **[r4j][author-profile]**

## AES CTR

AES CTR:

- generates a keystream:
  - here the IV & counter are constant throughout the session
- uses the same function for encryption & decryption
- here the keystream is the same for all encryptions (same IV & counter)
- 

## Deducing otp from stats

Because of the substitution, the frequency of bytes is not even:

the keystream k and the plaintext p are constants, only o changes between two
encryptions. All the variance is due to the otp

With 4096 = 16 * 256 requests, each byte should appear 16 times in average:
it is unlikely that a byte other than 0x00 will not appear. This allows to
single out the null byte.

Find the byte that never appears at each position

## Canceling the keystream

> HTB{1V_r3u$3#!}

[author-profile]: https://app.hackthebox.eu/users/13243
