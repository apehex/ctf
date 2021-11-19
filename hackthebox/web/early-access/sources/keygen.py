#!/usr/bin/env python3
import itertools
import random
import requests
import sys
import string
from re import match
from typing import Iterator

# ==================================================================== generate

def calc_cs(key: str) -> int:
    return sum(key[:23].encode()) - 135 # 3 * 45, remove 3 times the value of '-'

def calc_g1_rest(v: int, i: int=0) -> int:
    return (v << i + 1) % 256 ^ v

def gen_g1() -> Iterator[str]:
    __r = [221, 81, 145]
    __c = [[calc_g1_rest(v, i) for v in range(256)].index(__r[i]) for i in range(3)]
    for __d in itertools.combinations(set(string.digits) - set(__c), 2):
        __g1 = ''.join([chr(c) for c in __c]) + __d[0] + __d[1]
        __g4 = gen_g4(__g1)
        if bool(match(r"^[A-Z0-9]{5}$", __g4)):
            yield ''.join([chr(c) for c in __c]) + __d[0] + __d[1]

def gen_g2() -> Iterator[str]:
    for __g in itertools.product(string.ascii_uppercase + string.digits, repeat=5):
        if sum(''.join(__g[::2]).encode()) == sum(''.join(__g[1::2]).encode()):
            yield ''.join(__g)

def gen_g3(magic: int=346) -> Iterator[str]:
    for __c3 in string.digits:
        for __c1 in string.ascii_uppercase:
            __v2 = magic - sum(b'XP') - ord(__c3) - ord(__c1)
            if (__v2 in list(bytes(string.ascii_uppercase, 'utf-8'))):
                yield 'XP' + __c1 + chr(__v2) + __c3

def gen_g4(g1: str) -> str:
    return ''.join([chr(ord(c) ^ i) for c, i in zip(g1, [12, 4, 20, 117, 0])])

def gen_key(magic: int) -> Iterator[str]:
    __i1 = gen_g1()
    __i2 = gen_g2()
    __i3 = gen_g3(magic)
    for __g1 in __i1:
        for __g2 in __i2:
            for __g3 in __i3:
                __g4 = gen_g4(__g1)
                __k = f'{__g1}-{__g2}-{__g3}-{__g4}-'
                __k += str(calc_cs(__k))
                yield __k

# ====================================================================== verify

def g1_valid(g1: str) -> bool:
    r = [(ord(v)<<i+1)%256^ord(v) for i, v in enumerate(g1[0:3])]
    if r != [221, 81, 145]:
        return False
    for v in g1[3:]:
        try:
            int(v)
        except:
            return False
    return len(set(g1)) == len(g1)

def g2_valid(g2: str) -> bool:
    p1 = g2[::2]
    p2 = g2[1::2]
    return sum(bytearray(p1.encode())) == sum(bytearray(p2.encode()))

def g3_valid(g3: str, magic: int=346) -> bool:
    if g3[0:2] == 'XP':
        return sum(bytearray(g3.encode())) == magic
    else:
        return False

def g4_valid(g1: str, g4: str) -> bool:
    return [ord(i)^ord(g) for g, i in zip(g1, g4)] == [12, 4, 20, 117, 0]

def cs_valid(key) -> bool:
    cs = int(key.split('-')[-1])
    return gen_cs(key) == cs

# ===================================================== bruteforce magic number

def send_request(payload: str, xrsf: str, session: str, token: str) -> str:
    r = requests.post(
        'https://earlyaccess.htb/key/verify',
        data = {'_token': token, 'key': payload},
        cookies = {'XSRF-TOKEN': xrsf, 'earlyaccess_session': session},
        verify = False)
    return r.text

def bruteforce_gamekey(xrsf: str, session: str, token: str) -> str:
    for magic in range(346, 406):
        __k = gen_key(magic).__next__()
        __r = send_request(
            payload=__k,
            xrsf=xrsf,
            session=session,
            token=token)
        if 'invalid' in __r.lower() or 'expired' in __r.lower():
            print(f'magic: {magic}\tkey: {__k}\tvalid: no...', end='\r')
        else:
            print(f'magic: {magic}\tkey: {__k}\tvalid: yes!!!', end='\r')
            return __k

if __name__ == '__main__':
    xrsf = 'eyJpdiI6IlRKRXB2UlE0R3BDdzFVMnBLUDYrVFE9PSIsInZhbHVlIjoiclhhTDVXM2lQWmF2RHBCRmpuaG41YUs3aXd2RlhoOUY4MzE1V2pZaUZTcENnOEovWE1PNzlRWE1LSWdzU3UrYytmRmtSSTBXSDIrWEtHbkhLQU9YUTVubDlveGVUUGQ3b1RYQmNOMm5JYjdva25zRlBjR3dMWVRia3M3Uk85SCsiLCJtYWMiOiIyMWU0OGI0YjljMzEwMDg3MzQyMTMxNDlmNGU3OGIxZGJjZjk1MTFlMmZhOWNlNjliYTA0NjJjYzU2NWNiY2RlIn0%3D'
    session = 'eyJpdiI6IlRURUVwSHB2TzBSZ3gzSmJadUVRNXc9PSIsInZhbHVlIjoiWlJhVjNrWWVpOEVzbndHYy9sNVJ1M1hUVkdMWmlVQStPTVlVcS93SHJIV3hrYmp6b2ViZnBtTUhkSW5vbEJEZmg0b1N6WnZ0M00zcUlzczJCcjVCbzlRUndCN1Y1d0hoK0xkbWJJUm0zaWxTcWY3N1h2SXpKWlM3Z1VicEd5ZmwiLCJtYWMiOiI2MjFhM2RhNjIwZGJkMTIwNGYxNzM0NmUyYmRjMjA5MDZiMDMyMGE0MmQ4MTQ1NTNmN2QwZGViYTJjN2VkY2I5In0%3D'
    token = 'KOEvuoUFe2Caml1zZkTHV9UoiXcXFyJlwmiY9lzS'
    requests.packages.urllib3.disable_warnings()
    key = bruteforce_gamekey(xrsf=xrsf, session=session, token=token)
