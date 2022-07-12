# Impossible Password

> **Are you able to cheat me and get the flag?**

## Reverse

The program asks for 2 subsequent inputs and compares them to some strings.

Loading the binary into Ghidra, we see that the first input is compared to the
hardcoded string "SuperSeKretKey".

But it doesn't matter since we can bypass both comparison and directly look at
the final function call, when both tests succeed:

```c
void FUN_00400978(byte *param_1) {
  int local_14;
  byte *local_10;

  local_14 = 0;
  local_10 = param_1;
  while ((*local_10 != 9 && (local_14 < 0x14))) {
    putchar((int)(char)(*local_10 ^ 9));
    local_10 = local_10 + 1;
    local_14 = local_14 + 1;
  }
  putchar(10);
  return;
}
```

## Interpret

Using the common naming conventions:

```c
void output(char *input) {
  int i;
  char *c;

  i = 0;
  c = input;
  while ((*c != 9 && (i < 20))) {
    putchar((int)(char)(*c ^ 9));
    c = c + 1;
    i = i + 1;
  }
  putchar(10);
  return;
}
```

> `c = c + 1;`

This increments the **memory address** referenced by c: the function browses the 20
adresses following the input pointer. Looking at the decompiled sources we see:

```c
local_48 = 0x41;
local_47 = 0x5d;
local_46 = 0x4b;
local_45 = 0x72;
local_44 = 0x3d;
local_43 = 0x39;
local_42 = 0x6b;
local_41 = 0x30;
local_40 = 0x3d;
local_3f = 0x30;
local_3e = 0x6f;
local_3d = 0x30;
local_3c = 0x3b;
local_3b = 0x6b;
local_3a = 0x31;
local_39 = 0x3f;
local_38 = 0x6b;
local_37 = 0x38;
local_36 = 0x31;
local_35 = 0x74;
```

## Output

Each hex value is xored with 0x09 and the result is interpreted as an ASCII
code:

`putchar((int)(char)(*c ^ 9));`

We reproduce this functionality with a custom snipet:

```c
#include <stdio.h>

char flag[] = "\x41\x5d\x4b\x72\x3d\x39\x6b\x30\x3d\x30\x6f\x30\x3b\x6b\x31\x3f\x6b\x38\x31\x74";

void output() {
  for (int i = 0 ; i < 20 ; i++) {
    putchar((int)(char)(flag[i] ^ 9));
  }
  putchar(10);
  return;
}

int main(int argc, char *argv) {
  output();
}
```

And get:

> HTB{40b949f92b86b18}
