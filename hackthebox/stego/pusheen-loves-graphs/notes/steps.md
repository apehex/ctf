# Pusheen Loves Graphs

> **Pusheen just loves graphs, Graphs and IDA. Did you know cats are weirdly controlling about their reverse engineering tools? Pusheen just won't use anything except IDA.**

## Installing IDA

This is the actual hard part...

### qwingraph

IDA Free is in Archlinux AUR package repo, but IDA requires an extra lib to
display graphs:

> qwingraph

It is **NOT** distributed with the default installation...

After several attempts, I fell back to the Windows installer... Only to find it
didn't include qwingraph either!

We have several options:
- downloading a ready made binary from [x64dbg][x64dbg-qwingraph-release] (Windows)
- compiling the source code from [Hex-Rays][hex-rays-download-src] (Windows / Linux)
- building from source using a helper script from [WqyJh][wqyjh-github-build]
- merging AUR packages for [IDA Pro][aur-ida-pro] and [IDA Free][aur-ida-free]?

### Microsoft Visual C++ redistributable 2010 x86

Thinking it would go in one quick step, I opted for Windows binaries...

The release from `x64dbg` is linked to Qt4 and the corresponding DLLs are in the bundle.

**BUT** qwingraph depends on `msvcr100.dll` and `msvcp100.dll`, which are part
of Microsoft Visual C++ redistributable **2010**.
MSVCR 2010 is no longer maintained, much less available for download...

The `wayback machine` gives us an installer for MSVCR 2010 but the target DLLs
are only in the x64 package, and qwingraph requires **32 bit** DLLs.

This was too much for me, I ignored my paranoia and went to the first shady
looking result from google for `msvcr100.dll` and `msvcp100.dll`.

In the end, the directory for IDA Free in `Program Files` should contain:

```
msvcp100.dll
msvcr100.dll
QtCore4.dll
QtGui4.dll
qwingraph.exe
```

and scraps of my soul.

## Viewing the graph

Once the setup is complete, the challenge falls into place: opening the binary,
IDA warns:

> The graph is too big (more than 1000 nodes)

After tweaking the settings from 1000 max nodes to 20000, the graph overview
outlines the text:

> fUn_w17h_CFGz

Wrapping it in `HTB{}` does the job!

> I'll remember this and stick to Ghidra!

[aur-ida-free]: https://aur.archlinux.org/packages/ida-free/
[aur-ida-pro]: https://aur.archlinux.org/packages/ida-pro/
[hex-rays-download-src]: https://www.hex-rays.com/products/ida/support/download/
[wqyjh-github-build]: https://github.com/WqyJh/qwingraph_qt5
[x64dbg-qwingraph-release]: https://github.com/x64dbg/testplugin/releases
