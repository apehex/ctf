> There is a locked door in front of us that can only be opened with the secret passphrase.
> There are no keys anywhere in the room, only this .txt.
> There is also a writing on the wall..
> "State 0: 69420, State N: 999, flag ends at state N, key length: one"..
> Can you figure it out and open the door?

> Author: **[w3th4nds][author-profile]**

## Interpreting the data

The file is a list of tuples `in label out`, like `100 H 110`.

There are a several mentions of "states": 

```
 The states are correct
```

This is most likely a [finite-state machine][finite-state-machine], and the file lists all its transitions.

Also the states mentioned in the description are the starting -"origin O"- and and exit states -"end N"-.

Counting the links shows that this automaton is very particular:

```shell
sort -u deterministic.txt | wc -l
# 408
cut -d ' ' -f 1 deterministic.txt | sort -u | wc -l
# 406
```

It is mostly a straight line / string, with the nodes `4` and `121` forming junctions:

```shell
sort -u deterministic.txt | cut -d ' ' -f 1 | uniq -c
# 2 121
# 2 4
```

## Parsing

```shell
sort -u deterministic.txt > transitions.txt
python  decode.py
```

Actually the script fails with the sorted data, because of an infinite loop.

On the original data, the script takes the other choice at the junction and finishes.

The format is consistent, so it can be parsed eyes closed:

```python
with open('deterministic.txt', 'r') as __f:
    FSM = {__l.strip().split(' ')[0]: __l.strip().split(' ')[1:] for __l in __f}
```

## Following the lead

Just follow the edges until the end node:

```python
def follow(fsm: list, start: str, end: str) -> list:
    __transition = fsm.get(start, None)
    if __transition and start != end:
        yield int(__transition[0])
        yield from follow(fsm, __transition[1], end)
```

It gives us a ciphertext (on the original data, not sorted):

```python
ct = bytes(list(follow(FSM, start='69420', end='999')))
# b'0\x06\x1cI\x04\x08\x07\x08\x0e\x0c\rI\x1d\x06I\x19\x08\x1a\x1aI\x1d\x01\x1b\x06\x1c\x0e\x01I\x08\x05\x05I\x1d\x01\x0cI\n\x06\x1b\x1b\x0c\n\x1dI\x1a\x1d\x08\x1d\x0c\x1aI\x06\x0fI\x1d\x01\x0cI\x08\x1c\x1d\x06\x04\x08\x1d\x08I\x08\x07\rI\x1b\x0c\x08\n\x01I\x1d\x01\x0cI\x0f\x00\x07\x08\x05I\x1a\x1d\x08\x1d\x0cGI$\x08\x07\x10I\x19\x0c\x06\x19\x05\x0cI\x1d\x1b\x00\x0c\rI\x1d\x06I\r\x06I\x1d\x01\x00\x1aI\x0b\x10I\x01\x08\x07\rI\x08\x07\rI\x0f\x08\x00\x05\x0c\rGGI&\x07\x05\x10I\x1d\x01\x0cI\x1b\x0c\x08\x05I\x06\x07\x0c\x1aI\x04\x08\x07\x08\x0e\x0c\rI\x1d\x06I\x1b\x0c\x08\n\x01I\x1d\x01\x0cI\x0f\x00\x07\x08\x05I\x1a\x1d\x08\x1d\x0cGI0\x06\x1cI\x08\x05\x1a\x06I\x0f\x06\x1c\x07\rI\x1d\x01\x0cI\x1a\x0c\n\x1b\x0c\x1dI\x02\x0c\x10I\x1d\x06I\r\x0c\n\x1b\x10\x19\x1dI\x1d\x01\x0cI\x04\x0c\x1a\x1a\x08\x0e\x0cGI0\x06\x1cI\x08\x1b\x0cI\x1d\x1b\x1c\x05\x10I\x1e\x06\x1b\x1d\x01\x10HHI0\x06\x1cI\x1a\x01\x06\x1c\x05\rI\x0b\x0cI\x1b\x0c\x1e\x08\x1b\r\x0c\rI\x1e\x00\x1d\x01I\x1d\x01\x00\x1aI\x0e\x00\x0f\x1dHI=\x01\x0cI\x19\x08\x1a\x1a\x19\x01\x1b\x08\x1a\x0cI\x1d\x06I\x1c\x07\x05\x06\n\x02I\x1d\x01\x0cI\r\x06\x06\x1bI\x00\x1aSI!=+\x12]\x1c\x1dY$]\x1d]6]\x1bZ6/\x1c<\x1c'6]\x07-6'Y\x1d6-X\x0f/X\n<\x05\x1dHH\x14'
```
## Decrypting

As mentionned in the description, the key is a single byte. We can just test every byte value:

```python
def xor(a, b):
    return [x ^ y for x, y in zip(a, cycle(b))]

for i in range(256):
    print(i, '\t', bytes(xor(ct, bytes([i]))[:16]))
# 104      b'Xnt!l`o`fde!un!q'
# 105      b'You managed to p'
# 106      b'Zlv#nbmbdfg#wl#s'
# 107      b'[mw"oclcegf"vm"r'
```

The key is `105` or the byte `0x69`.

```python
print(bytes(xor(ct, bytes([0x69]))))
# b'You managed to pass through all the correct states of the automata and reach the final state. Many people tried to do this by hand and failed.. Only the real ones managed to reach the final state. You also found the secret key to decrypt the message. You are truly worthy!! You should be rewarded with this gift! The passphrase to unlock the door is: HTB{4ut0M4t4_4r3_FuUuN_4nD_N0t_D1fF1cUlt!!}'
```

> `HTB{4ut0M4t4_4r3_FuUuN_4nD_N0t_D1fF1cUlt!!}`

[author-profile]: https://app.hackthebox.com/users/70668
[finite-state-machine]: https://en.wikipedia.org/wiki/Finite-state_machine
