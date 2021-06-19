#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

# =================================================== rotate a single character

def _rotate(c, delta=13, origin='a', count=26):
    return chr(ord(origin) + ((ord(c) - ord(origin) + delta) % count))

def rotate(c, alpha=13, digits=0):
    if c.isalpha():
        if c.islower():
            return _rotate(c, alpha, 'a', 26)
        else:
            return _rotate(c, alpha, 'A', 26)
    elif c.isdigit():
        return _rotate(c, digits, '0', 10)
    else:
        return c

# ===================================================== rotate the input string

def caesar(s, alpha=13, digits=0):
    for c in s:
        yield rotate(c, alpha, digits)

def main():
    parser = argparse.ArgumentParser(description='Cipher the input with the Caesar substitution scheme.')
    parser.add_argument('data', metavar='data', type=str, help='the string to rotate')
    parser.add_argument('--alpha', metavar='alpha', type=int, default=13, help='rotation count on alpha characters')
    parser.add_argument('--digits', metavar='digits', type=int, default=0, help='rotation count on digit characters')

    args = parser.parse_args()

    print(''.join(caesar(args.data, args.alpha, args.digits)))

if __name__ == '__main__':
    main()
