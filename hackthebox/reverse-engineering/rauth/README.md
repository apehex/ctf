# RAuth

> **My implementation of authentication mechanisms in C turned out to be failures.**
> **But my implementation in Rust is unbreakable. Can you retrieve my password?**

> Author: **[TheCyberGeek][author-profile-link]**

## Fast and failed

The binary has a size of 10M, static analysis will be a pain.

The binary asks for a password on execution and returns with "You entered a
wrong password!".

Potentially the test could be a string comparison against the decrypted password.
So we search for these strings in Ghidra: a direct "string search" fails.

Still we can see with `strings -n8 | grep -ia 'success'` that there's a match
somewhere. Looking for synonyms like in the list of symbols, I stumbled on
`unwrap_failed`.

The target string is actually a comment, and a portion of the code is encrypted:
it appears as junk in Ghidra, but binwalk reports data encrypted with blowfish-448.

The function "unwrap_failed" is referenced in the `rauth::main` (not the EP "main):
from the assembly POV it's very convoluted, so we'll try dynamic analysis.

## Locating the decryption calls

We'll have the binary decrypt itself and inspect it while running, thanks to `gdb`.

When the binary prompts for the password we can break manually with Ctrl+C.

The RIP is set on a comparison:

```
0x7ffff7f75762 <read+18>        cmp    rax, 0xfffffffffffff000
0x7ffff7f75768 <read+24>        ja     0x7ffff7f757c0 <read+112>
```

After stepping once and typing a random string, `info registers` shows:

```
rax            0x6                 0x6
```

I typed "hello\n": it is testing the input string length, 6 here.

This instruction is easy to spot in Ghidra's disassembled code, since it should
be a syscall to read / stdin:

```
0010653f ff 15 33        CALL       qword ptr [->std::io::stdio::Stdin::read_line]
         58 24 00
```

Browsing the disassembled code, the input is used to try and decrypt with the Salsa20:

```
salsa20::core::Core<R>::new(0x20,&stack0xfffffffffffffe38,&local_138,&local_108);
```

```
00106652 e8 a9 f2        CALL       salsa20::core::Core<R>::new
         ff ff
```

There are 3 calls to the `Salsa` library: the cipher object creation and 2
decryption calls. These are bound to show valuable information, so we'll look
for these calls during runtime.

These calls are located at offsets `0x00106652`, `0x00106759` and `0x001068eb`.
Or, relative to the offset `0x00106460` at the start of the main function:

- `rauth::main+498`
- `rauth::main+761`
- `rauth::main+1163`

Those offsets will be the targets of further debugging.

## Extracting the decryption parameters

Starting from the prompt, we step through the main function, skipping all nested
calls with `finish`.

Once on `rauth::main+498` we analyse the registers as strings with `x/s $rdx`:

```
$rdi = ""
$rsi = "ef39f4f20e76e33bd25f4db338e81b100"
$rdx = "d4c270a3"
```

Judging from the documentation:

- `ef39f4f20e76e33bd25f4db338e81b100` is the password
- `d4c270a3` is the nonce

Only thing left is the content to be decrypted. `rauth::main+761` tries to
decrypt with the user input:

```
0x55555540675e <rauth::main+766> test   al, al
0x555555406760 <rauth::main+768> jne    0x555555406a89 <_ZN5rauth4main17h7d7aed61ae7734f4E+1577>
```

And we find the encrypted content:

```
05055fb1a329a8d558d9f556a6cb31f324432a31c99dec72e33eb66f62ad1bf9
```

Bonus: `rauth::main+1163` decrypts a fake flag: "HTB{F4k3_f74g_4_t3s7ing}q\341\001".

## Decrypting the credentials

We can now reverse the Salsa20 encryption:

```python
cipher = Salsa20.new(key=b'ef39f4f20e76e33bd25f4db338e81b10', nonce=b'd4c270a3')
password = cipher.decrypt(binascii.unhexlify(b'05055fb1a329a8d558d9f556a6cb31f324432a31c99dec72e33eb66f62ad1bf9'))
```

> TheCrucialRustEngineering@2021;)

Finally, we use this password to connect to the remote instance with ncat:

> HTB{I_Kn0w_h0w_t0_5al54}

[author-profile-link]: https://app.hackthebox.eu/users/114053
