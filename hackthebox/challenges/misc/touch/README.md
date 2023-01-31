> Push me, and then just touch me, till I can get my, Satisfaction!

> Author: **[ly4k][author-profile]**

## Touching base

The service listening looks like a reverse shell:

```shell
nc 206.189.115.160 30001
# bash: cannot set terminal process group (1): Inappropriate ioctl for device
# bash: no job control in this shell
# ctf@misctouchmp-413156-6db9f7664d-ntjpp:/$ ps auxf
```

The challenge is to elevate the user privileges through the binary file `touch`:

```shell
cat /etc/passwd | grep -v nologin
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# ctf:x:1000:1000::/home/ctf:/bin/bash
sudo -l
# bash: sudo: command not found
ss -pantu
# bash: ss: command not found
ls -lah /home/ctf
# -rw-r--r-- 1 ctf  ctf   220 Apr 18  2019 .bash_logout
# -rw-r--r-- 1 ctf  ctf  3.5K Apr 18  2019 .bashrc
# -rw-r--r-- 1 ctf  ctf   807 Apr 18  2019 .profile
# lrwxrwxrwx 1 root root   14 Aug  2 14:50 touch -> /usr/bin/touch
```

## Failed attempts

Unfortunately, touch is [not in GTFOBins][gtfobins]!

### Touching the flag

Trying to access any path under root does not return any error:

```shell
touch /root/flag.txt
touch /root/doesnotexist
```

And the shell displays errors:

```shell
touch -t dfgjdfgj /root/flag.txt
# touch: invalid date format 'dfgjdfgj'
```

This allows to find the actual path of the flag:

```shell
touch -r /root/flag me
# touch: failed to get attributes of '/root/flag': No such file or directory
touch -r /root/flag.txt me
```

### Modifying the link

It would be great to point the symbolic link to another binary while keeping its privileges:

```shell
ln -sf /bin/bash ./touch
ls -lah
# lrwxrwxrwx 1 ctf  ctf     9 Aug 15 09:19 touch -> /bin/bash
```

The owner / privileges are updated too!

Another possibility would be to modify the actual content of the symlink block on disk.
Idk how to do that, I only found how to create a new link and overwrite the old one.

### Playing with arguments

The substitution of nested commands is performed with the `ctf` user permission:

```shell
touch `whoami`
ls -lah
# -rw-r--r-- 1 root root    0 Aug 15 19:22 ctf
```

So this doesn't work:

```shell
touch `cat /root/flag.txt`
```

The last command doesn't error out, so the path is valid.

### Creating a significant file

```shell
ln -s /root/flag.txt /tmp/test
ls -lah /tmp
# lrwxrwxrwx 1 ctf  ctf    14 Aug 15 19:51 test -> /root/flag.txt
```

[author-profile]: https://app.hackthebox.com/users/75443
[gtfobins]: https://gtfobins.github.io/#touch
