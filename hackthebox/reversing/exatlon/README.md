> **Can you find the password?**

> Author: **[OctopusTR][author-profile]**

## Fast and failed

The binary displays a banner and then asks for a password on a loop:

```
███████╗██╗  ██╗ █████╗ ████████╗██╗      ██████╗ ███╗   ██╗       ██╗   ██╗ ██╗
██╔════╝╚██╗██╔╝██╔══██╗╚══██╔══╝██║     ██╔═══██╗████╗  ██║       ██║   ██║███║
█████╗   ╚███╔╝ ███████║   ██║   ██║     ██║   ██║██╔██╗ ██║       ██║   ██║╚██║
██╔══╝   ██╔██╗ ██╔══██║   ██║   ██║     ██║   ██║██║╚██╗██║       ╚██╗ ██╔╝ ██║
███████╗██╔╝ ██╗██║  ██║   ██║   ███████╗╚██████╔╝██║ ╚████║███████╗╚████╔╝  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═══╝   ╚═╝


[+] Enter Exatlon Password  :
``` 

Nothing outstanding / clear from `exiftool`, `trid`, `strings`.

`ltrace` / `strace` don't show any obvious password comparisons.

Browsing with Ghidra and looking for the syscalls, I couldn't find the
read / write (0x0 / 0x1) calls. The binary is most likely packed / obfuscated.

## Unpacking

The packer is actually advertized in the `strings`:

```
$Info: This file is packed with the UPX executable packer http://upx.sf.net$
```

Unpacking is straightforward:

```bash
upx -d -k -o exatlon_v1.unpacked exatlon_v1
```

## Static analysis

Hopefully we can analyse the new binary with `ghidra`!

The `main` function displays `"[+] Looks Good ^_^ \n\n\n"`  after a string comparison.
This is definitely the password check.

The user input is first processed by the mysterious `exatlon` and then compared with:

```
"1152 1344 1056 1968 1728 816 1648 784 1584 816 1728 1520 1840 1664 784 1632 1856 1520 1728 816 1632 1856 1520 784 1760 1840 1824 816 1584 1856 784 1776 1760 528 528 2000 "
```

The exatlon function is a little convoluted, we'll try and analyse it in the
debugger, starting from the comparison at offset `main+267` (0x404d37-0x404c2c).

## Dynamic analysis

To learn more about the `exalton` algorithm we can fuzz it.

After typing "HTBHTB" in the prompt, we can see in gdb:

```
$rdi   : 0x00007fffffffdf00  →  0x00007fffffffdf10  →  "1152 1344 1056 1152 1344 1056 "
```

It gives many informations away:

- there are 6 numbers, most likely one for each letter in "HTBHTB"
- the first 3 numbers match the start of the target string: we've found the -encrypted- flag
- the "exatlon" algorithm processes its input string character by character

## Reversing Exatlon

There are several paths:

1) feeding the whole ASCII alphabet to the binary to learn the character mapping
2) understanding and reversing the actual logic of "exatlon"

I opted for the first option! :D

First, generate the alphabet of printable ASCII characters:

```python
# '!"#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~'
re.sub(r'(\\x..|\\.|b\'|\'| )', '', str(bytes(range(0,256))))
```

Feed it to exaltlon, in gdb:

```bash
b *(main+267)
run
!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}~
x/s *($rdi)
```

In return, exatlon spits:

```
"528 544 560 576 592 608 624 640 656 672 688 704 720 736 752 768 784 800 816 832 848 864 880 896 912 928 944 960 976 992 1008 1024 1040 1056 1072 1088 1104 1120 1136 1152 1168 1184 1200 1216 1232 1248 1264 1280 1296 1312 1328 1344 1360 1376 1392 1408 1424 1440 1456 1488 1504 1520 1552 1568 1584 1600 1616 1632 1648 1664 1680 1696 1712 1728 1744 1760 1776 1792 1808 1824 1840 1856 1872 1888 1904 1920 1936 1952 1968 1984 2000 2016 "
```

This is actually working! 2000 is `{`, and it is found at the last position
of the target string, ie the closing bracket of `HTB{...}`.

Finally, apply the mapping to our target:

```python
ALPHABET_CLEAR = '''!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}~'''
ALPHABET_ENCRYPTED = "528 544 560 576 592 608...".split(" ")
ALPHABET_MAPPING = {ALPHABET_ENCRYPTED[_i]: ALPHABET_CLEAR[_i] for _i in range(len(ALPHABET_CLEAR))}

PASSWORD_ENCRYPTED = "1152 1344 1056 1968...".split(" ")

print("".join([ALPHABET_MAPPING[_c] for _c in PASSWORD_ENCRYPTED]))
```

> HTB{l3g1c3l_sh1ft_l3ft_1nsr3ct1on!!}

## Bonus: malware packing

In retrospect it was "obvious" the binary was packed.

First, the wrapper binary does not link to the standard libraries at all:

![][meta-comparison_packed-unpacked]

Then it opens a file (syscall 2 in Ghidra), for no appearant reason.
According to Wikipedia this file is a cache for UPX:

```
UPX supports two mechanisms for decompression: an in-place technique and extraction to temporary file.
```

Also UPX compresses its input, which increases the entropy:

```bash
# Entropy = 7.903744 bits per byte.
# Optimum compression would reduce the size
# of this 709524 byte file by 1 percent.
ent exatlon_v1

# Entropy = 6.299165 bits per byte.
# Optimum compression would reduce the size
# of this 2202568 byte file by 21 percent
ent exatlon_v1.unpacked 
```

The key takeaway is that the original binary cannot be compressed: it is
already compressed / packed.

This challenge made me discover `radare2` (yup I'm n00b):

```bash
rahash2 -a entropy ./exatlon_v1
```

[author-profile]: https://app.hackthebox.eu/users/158119
[meta-comparison_packed-unpacked]: images/meta-comparison_packed-unpacked.png
