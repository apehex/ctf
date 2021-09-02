#!/usr/bin/env python3

BYTES = "f7f88883 00000000 f7eb7862 ffffde80 00000000 3131785c 3131785c 38302520 25207838 78383025 30252078 20783830 38302520 25207838 78383025 30252078"

def decode(word: str) -> str:
    # start at 2 to ignore the "0x"
    return "".join([chr(int(word[i:i+2], 16)) for i in range(0, 8, 2)][::-1])

print("".join([decode(w) for w in BYTES.split(" ")]))
