# The Needle

> **As a part of our SDLC process, we've got our firmware ready for security
> testing. Can you help us by performing a security assessment?**

## Interpreting

`file` tells us:

`firmware.bin: Linux kernel ARM boot executable zImage (big-endian)`

Actually `firmware.bin` seems to be a Linux image, compressed with xz:

```
strings -n8 firmware.bin

System halted
Attempting division by 0!
stack-protector: Kernel stack is corrupted
Uncompressing Linux...
decompressor returned an error
done, booting the kernel.
XZ decompressor ran out of memory
Input is not in the XZ format (wrong magic bytes)
Input was encoded with settings that are not supported by this XZ decoder
XZ-compressed data is corrupt
Bug in the XZ decompressor
```

## Decompression

Binwalk is enough to identify and decompress all the files of the squashed-fs:

```
binwalk -e firmware.bin > firmware.bin.walk
```

Alternatively, the image can be extracted using a linux kernel script:

```
./extract-vmlinux.sh firmware.bin > vmlinux.img`
file vmlinux.img

vmlinux.img: ELF 32-bit MSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-musl-armeb.so.1, no section header
```

## Looking for the needle

Binwalk left us with a tidy squash-fs actually.

Mass greping the filesystem for credentials is impractical:

```
grep -ria 'password' .firmware.bin.extracted/squashfs-root/ | wc -l
132
```

There are many source & binary checking for credentials without actually storing
any valuable data.

Since `firmware.bin` is a full-featured linux it may have services that
establish remote connections.

The configuration may be interesting, especially for the network services.
There's only a couple of them, going through each of them in turn is feasible.

```
#!/bin/sh
sign=`cat /etc/config/sign`
TELNETD=`rgdb
TELNETD=`rgdb -g /sys/telnetd`
if [ "$TELNETD" = "true" ]; then
	echo "Start telnetd ..." > /dev/console
	if [ -f "/usr/sbin/login" ]; then
		lf=`rgbd -i -g /runtime/layout/lanif`
		telnetd -l "/usr/sbin/login" -u Device_Admin:$sign	-i $lf &
	else
		telnetd &
	fi
fi
```

We can now connect to the remote machine with `Device_Admin:qS6-X/n]u>fVfAt!`.

