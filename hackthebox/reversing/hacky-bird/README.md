> **Even Mr. Miyagi cannot seem to beat this game. Flap your wings and show him the way!**

> Author: **[st4ckh0und][author-profile]**

## Playing hacky bird

The game is a clone of flappy bird, except especially clunky / hard:

![][screenshot]

I never got past the 4th pipe, and the flag is supposedly unlocked on high scores!

So let's cheat!

## Static analysis

Browsing through the imports / exports in Ghidra, a few symbols stand out:

- IsDebuggerPresent:
  - there may be anti-debugging features
  - returns 0 when the thread is not attached to a debugger
  - 1 reference
- DrawTextW & SetTextColor:
  - after the start screen the only text displayed is the score
  - this could leak the address of the score
  - 2 references each, in the same function
- IntersectRect:
  - to check for collisions with the pipes
  - returns 0 when the rectangles don't intersect
  - 2 references
- WriteFile:
  - the highscore could be written on disk?
  - however there's no mention on the menu screen, it's a gamble
  - 6 references

The easiest to interpret / spot are the pipe collisions: IntersectRect is the
only function in the import list that can perform collisions and there are only
2 calls. One for each pipe?

Also, right after the collision checks is an intersting condition:

```c
if (999 < *(int *)(param_1 + 0x94)) {
```

Most likely this is checking the score, `param_1 + 0x94`, which is incremented
a couple lines ahead:

```c
*(int *)(param_1 + 0x94) = *(int *)(param_1 + 0x94) + 1;
```

Indeed we saw that the score increases one by one, when playing the game.

## Disabling collisions

Using the previous analysis, it should be easy to break on collision checks in
the debugger. And from there, the hope is to find the location of the score.

So in `x32dbg`:

```
setBPX IntersectRect
```

Running hacking bird drops us in "user32.IntersectRect". Next, we get back to
the calling function by pressing "run to user code".

The comparison jumps when there's a collision:

```
004030E4 | 0F85 CD000000            | jne hackybird.4031B7                    |
```

```
004030FE | 0F85 B3000000            | jne hackybird.4031B7                    |
```

So nopping these we'll turn the pipe collisions off!

Pretty fun, but the flag still doesn't show up!
This is coherent with the former disassembly analysis: the goal is to exceed 999.

## Changing the score

A few lines below the call to IntersecRect, the target appears:

```
0040312D | FF86 94000000            | inc dword ptr ds:[esi+94]               |
```

Breaking on this instruction, ESI is at `00C25B90`: then the score is supposed
to be at:

```python
# '0xc25c24'
hex(0xc25b90 + 0x94)
```

Then we follow ESI in the memory dump and modify 0x00C25C24: I chose not to
worry with endianness and write 0xFFFFFFFF.

The game breaks:

![][crash]

## Proper cheating

This is most likely due to an anti-debugging mechanism. At some point the binary
calls `IsDebuggerPresent`.

The options are now:

- trying `Cheat Engine`, a stealthy debugger specifically made for evading game defenses
- turning the anti-debugging features off
- patching the exe, by nopping the collisions and drastically increasing the score updates

The first option is most similar to the previous debugging so it should be fast,
unlike the other routes. I heard about it from the days of Dota in W3 and nerver
actually used it, I'm hyped.

Also, I looked it up in Google, because it's time I wrap this up...

In Cheat Engine, we can attach to a running HackyBird and find the previous
instructions with "search assembly".

I tried:

- nopping the collision checks
- lowering the win requirement to any / 7 pipe clears

But these break the game.

My guess is that we should leave the assembly intact and only modify memory.
So I set a breakpoint on the comparison and traced the memory address: when
it hits I just enter `E8 07` (1000) at `ESI + 0x94`:

> HTB{game_h3kk1n_is_funsies!}

[author-profile]: https://app.hackthebox.eu/users/84315
[crash]: images/crash.png
[screenshot]: images/flappy-101.png
