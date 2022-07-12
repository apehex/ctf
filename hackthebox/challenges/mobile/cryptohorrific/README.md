> Secure coding is the keystone of the application security!

> Author: **[bsecure][author-profile]**

## Browsing the package

Apart from the app binary, the project folder is mostly empty. There's one file
that stands out though:

```bash
# Collecting data from file: hackthebox.app/challenge.plist
# 100.0% (.) Mac OS X Binary-format PList (8000/1)
trid challenge.plist
```

It contains base64 encoded data, with a "flag" mention.

```
00000000: 6270 6c69 7374 3030 a101 d302 0304 0506  bplist00........
00000010: 0754 666c 6167 5269 6455 7469 746c 655f  .TflagRidUtitle_
00000020: 1058 5471 2b43 577a 5153 3077 597a 7332  .XTq+CWzQS0wYzs2
00000030: 724a 2b47 4e72 504c 5036 7165 6b44 6277  rJ+GNrPLP6qekDbw
00000040: 7a65 3666 4965 5252 7742 4b32 5758 484f  ze6fIeRRwBK2WXHO
00000050: 6862 6137 5752 324f 474e 5546 4b6f 4176  hba7WR2OGNUFKoAv
00000060: 7957 376e 6a54 434d 6c51 7a6c 7749 5264  yW7njTCMlQzlwIRd
00000070: 4a76 6150 3269 5951 3d3d 5331 3233 5f10  JvaP2iYQ==S123_.
00000080: 1048 6163 6b54 6865 426f 7849 7343 6f6f  .HackTheBoxIsCoo
00000090: 6c08 0a11 1619 1f7a 7e00 0000 0000 0001  l......z~.......
000000a0: 0100 0000 0000 0000 0800 0000 0000 0000  ................
000000b0: 0000 0000 0000 0000 91                   .........
```

Since the challenge is about encryption, it's safe to assume the goal is to
decrypt this data.

## Looking for the key

The decryption logic is most likely in the binary: let's look at it in Ghidra.

Searching for "key" and "secret" in the strings, I found "SecretManager:key:iv:data:".
It is referenced by this chunk of code:

```c
IVar10 = SecretManager:key:iv:data:(
	IVar10,
	(SEL)"SecretManager:key:iv:data:",
	1,
	"!A%D*G-KaPdSgVkY",
	"QfTjWnZq4t7w!z%C",
	IVar9);
```

Which performs a decryption with:

- AES most likely
- the key `!A%D*G-KaPdSgVkY`
- the IV `QfTjWnZq4t7w!z%C`
- and the data located in IVar9

Following the trail, IVar9 has been filled with data from a plist file:

```c
uVar5 = __stubs::_objc_msgSend(&_OBJC_CLASS_$_NSBundle,"mainBundle");
uVar5 = __stubs::_objc_retainAutoreleasedReturnValue(uVar5);
uVar6 = __stubs::_objc_msgSend(uVar5,"pathForResource:ofType:",&cf_challenge,&cf_plist);
uVar6 = __stubs::_objc_retainAutoreleasedReturnValue(uVar6);
uVar4 = __stubs::_objc_msgSend(uVar4,"initWithContentsOfFile:",uVar6);
uVar7 = __stubs::_objc_msgSend(uVar4,"objectAtIndex:",0);
uVar7 = __stubs::_objc_retainAutoreleasedReturnValue(uVar7);
uVar8 = __stubs::_objc_msgSend(uVar7,"objectForKey:",&cf_flag);
uVar8 = __stubs::_objc_retainAutoreleasedReturnValue(uVar8);
IVar9 = __stubs::_objc_msgSend(uVar3,"initWithBase64EncodedString:options:",uVar8,0);
```

The former assumption looks valid.

## Decrypting the flag

```python
CIPHERTEXT = base64.b64decode("Tq+CWzQS0wYzs2rJ+GNrPLP6qekDbwze6fIeRRwBK2WXHOhba7WR2OGNUFKoAvyW7njTCMlQzlwIRdJvaP2iYQ==")
KEY = bytes("!A%D*G-KaPdSgVkY", "utf-8")
IV = bytes("QfTjWnZq4t7w!z%C", "utf-8")

cipher = AES.new(key=KEY, mode=AES.MODE_ECB)
flag = cipher.decrypt(CIPHERTEXT)
```

At first I included the "X" at the start of the base64 encoded string, but this
resulted in a padding error. Since the "==" at the end is legit padding, it had
to be the start that was messed up.

> HTB{%SoC00l_H4ckTh3b0xbyBs3cur31stCh4ll3ng3!!Cr4zY%}

[author-profile]: https://app.hackthebox.eu/users/25695
