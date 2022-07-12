#!/usr/bin/env python3

BYTES = "585921c0 00000170 5664ddfa 00000012 00000000 00000026 00000002 00000001 5664e96c 585921c0 58592340 7b425448 5f796877 5f643164 34735f31 745f3376 665f3368 5f67346c 745f6e30 355f3368 6b633474 007d213f"

def decode(word: str) -> str:
    # start at 2 to ignore the "0x"
    return "".join([chr(int(word[i:i+2], 16)) for i in range(0, 8, 2)][::-1])

print("".join([decode(w) for w in BYTES.split(" ")]))
