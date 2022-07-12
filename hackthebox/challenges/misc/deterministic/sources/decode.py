#!/usr/bin/env python

from itertools import cycle

######################################################################### parse

with open('deterministic.txt', 'r') as __f:
    FSM = {__l.strip().split(' ')[0]: __l.strip().split(' ')[1:] for __l in __f}

######################################################################## follow

def follow(fsm: list, start: str, end: str) -> list:
    __transition = fsm.get(start, None)
    if __transition and start != end:
        yield int(__transition[0])
        yield from follow(fsm, __transition[1], end)

def _follow(fsm: list, start: str, end: str) -> list:
    __current = start
    __out = []
    while __current and __current != end:
        __transition = fsm.get(__current, None)
        __current = __transition[1]
        __out.append(int(__transition[0]))
    return __out

ct = bytes(list(follow(FSM, start='69420', end='999')))

####################################################################### decrypt

def xor(a, b):
    return [x ^ y for x, y in zip(a, cycle(b))]

for i in range(256):
    print(i, '\t', bytes(xor(ct, bytes([i]))[:16]))

print(bytes(xor(ct, bytes([0x69]))))
