# misDirection

> **During an assessment of a unix system the HTB team found a suspicious
> directory. They looked at everything within but couldn't find any files with
> malicious intent.**

## Interpretation

Let's look at the content of this directory:

```
.secret
|-- 0
|   `-- 6
|-- 1
|   |-- 22
|   `-- 30
|-- 2
|   `-- 34
|-- 3
|-- 4
|-- 5
|   `-- 16
|-- 6
|-- 7
|-- 8
|-- 9
|   `-- 36
|-- A
|-- B
|   `-- 23
|-- C
|   `-- 4
|-- D
|   `-- 26
|-- E
|   `-- 14
|-- F
|   |-- 19
|   |-- 2
|   `-- 27
|-- G
|-- H
|-- I
|-- J
|   `-- 8
|-- K
|-- L
|-- M
|-- N
|   |-- 11
|   |-- 25
|   |-- 31
|   `-- 33
|-- O
|-- P
|-- Q
|-- R
|   |-- 3
|   `-- 7
|-- S
|   `-- 1
|-- T
|-- U
|   `-- 9
|-- V
|   `-- 35
|-- W
|-- X
|   |-- 17
|   |-- 21
|   `-- 29
|-- Y
|-- Z
|-- a
|-- b
|-- c
|-- d
|   `-- 13
|-- e
|   `-- 5
|-- f
|-- g
|-- h
|-- i
|-- j
|   |-- 10
|   `-- 12
|-- k
|-- l
|-- m
|-- n
|-- o
|-- p
|   `-- 32
|-- q
|-- r
|-- s
|   `-- 24
|-- t
|-- u
|   |-- 20
|   `-- 28
|-- v
|-- w
|-- x
|   `-- 15
|-- y
`-- z
    `-- 18
```

All the files are empty.

The meaning seems to be in the naming of files and directories:
- the directories are named `[a-zA-Z0-9]`, like an alphabet
- the parent / child relation of the directories and files

Also, all the numbers between 1 and 36 appear exactly once:

```
find .secret/ -type f | xargs -I '{}' basename {} | sort -n
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
```

So the numbers can be interpreted as indexes: each filename could indicate the
position(s) where the corresponding ASCII character appears.

## Reconstructing the string

The end result is therefore a string of length 36:

```
____________________________________
```

Applying the rule to the first 2 directories:

```
|-- 0
|   `-- 6
|-- 1
|   |-- 22
|   `-- 30
```

gives us:

```
_____0_______________1_______1______
```

And, after processing all the files:

```
SFRCe0RJUjNjdEx5XzFuX1BsNDFuX1NpN2V9
```

## Making sense of it

The final string is not formated as a flag yet.

Either:
1) the interpretation was wrong
2) there are further steps

### Looking for more

The string contains `[G-Z]` so it cannot be directly interpreted as hex.

My only idea came from this: `36 = 10 + 26` :O

So could actually be a remapping to the alphabet `[0-9a-z]` or `[0-9A-Z]`.

Similar to a rot13 encryption:

```
SFRCe0RJUjNjdEx5XzFuX1BsNDFuX1NpN2V9
||||||||||||||||||||||||||||||||||||
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

But there was nothing more to encrypt / decrypt with this scheme...
Plus it is ambiguous since we have to choose arbitrarily whether to map to
numbers first and choose between upper and lower case.

### Kiss!

After searching for a while I just decided to run base64, and it worked!
