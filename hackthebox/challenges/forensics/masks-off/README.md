> This year's Valentine's Day was special. Cupid's arrow hit me right in the head
> instead of the heart. I broke up with my "security engineer" partner because I
> found out I was being spied all these years. I knew my partner was into malware
> develpment but never expected this skill to be used against me. My partner is a
> cyber security engineer by day and a vigilante hacker by night but I am a
> forensics analyst all day.

> Author: **[thewildspirit][author-profile]**

## Parsing the capture file

According to Wireshark, all the packets form 3 TCP streams:

- 2 file transfers
- and a suspicious back and forth conversation without a known structure

Exporting the files in Wireshark gives:

```shell
ls -lah payloads/
# 1842920  12K -rw-r--r-- 1 gully gully  12K May 13 18:56 %2f
# 1842919  56K -rw-r--r-- 1 gully gully  55K May 13 18:55 ic2kp
file payloads/*
# payloads/%2f:   data
# payloads/ic2kp: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=2d426a616202b1c6516d38a89bd9af1e133f29f1, for GNU/Linux 3.2.0, stripped
cat 'payloads/%2f' | head -n 2
cat 'payloads/%2f' | head -n 2
# --------------------------32f1c18193d8e1f7
# Content-Disposition: form-data; name="data"; filename="b12gb.zip"
```

The second file was actually a POST upload to `192.168.1.11:8000`.

Let's extract the file itself:

```shell
sed -n 4,39p payloads/%2f > payloads/b12gb.zip
unzip -l payloads/b12gb.zip
# Archive:  payloads/b12gb.zip
# warning [payloads/b12gb.zip]:  2 extra bytes at beginning or within zipfile
#   (attempting to process anyway)
#   Length      Date    Time    Name
# ---------  ---------- -----   ----
#    229376  2022-02-04 15:27   cert9.db
#    294912  2022-02-04 14:55   key4.db
#        50  2022-02-04 14:51   times.json
#      1882  2022-02-04 15:27   logins.json
# ---------                     -------
#    526220                     4 files
dd bs=2 skip=1 if=payloads/b12gb.zip of=b12gb.zip
```

The second stream / conversation looks encrypted. May-be these files are the
keys for the exchange.

Since the conversation started after the upload of the ELF file, and the
structure / protocole is unknown, it may be the product of this executable.

## Reversing the ELF file

VIRUSTOTAL identifies the executable as a "Rekoobe backdoor":

![][virustotal-ic2kp]

[author-profile]: https://app.hackthebox.com/users/70891
[virustotal-ic2kp]: images/virustotal-ic2kp.png
