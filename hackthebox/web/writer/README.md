> Author: **[TheCyberGeek][author-profile]**

## Initial discovery

### Services

```bash
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 98:20:b9:d0:52:1f:4e:10:3a:4a:93:7e:50:bc:b8:7d (RSA)
|   256 10:04:79:7a:29:74:db:28:f9:ff:af:68:df:f1:3f:34 (ECDSA)
|_  256 77:c4:86:9a:9f:33:4f:da:71:20:2c:e1:51:10:7e:8d (ED25519)
80/tcp  open  http        Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Story Bank | Writer.HTB
```

```bash
137/udp open          netbios-ns  Samba nmbd netbios-ns (workgroup: WORKGROUP)
138/udp open|filtered netbios-dgm
Service Info: Host: WRITER
```

### Web directories

```bash
/contact              (Status: 200) [Size: 4905]
/logout               (Status: 302) [Size: 208] [--> http://10.10.11.101/]
/about                (Status: 200) [Size: 3522]                          
/static               (Status: 301) [Size: 313] [--> http://10.10.11.101/static/]
/dashboard            (Status: 302) [Size: 208] [--> http://10.10.11.101/]       
/server-status        (Status: 403) [Size: 277]                                  
/administrative       (Status: 200) [Size: 1443] 
```

### SMB shares

```bash
# Doing NBT name scan for addresses from 10.10.11.101

# IP address       NetBIOS Name     Server    User             MAC address      
# ------------------------------------------------------------------------------
# 10.10.11.101     WRITER           <server>  WRITER           00:00:00:00:00:00
sudo nbtscan -r 10.10.11.101
```

```bash
# [*] 10.10.11.101:445      - SMB Detected (versions:2, 3) (preferred dialect:SMB 3.1.1) (compression capabilities:) (encryption capabilities:AES-128-CCM) (signatures:optional) (guid:{74697277-7265-0000-0000-000000000000}) (authentication domain:WRITER)
```

```bash
# 	Sharename       Type      Comment
# 	---------       ----      -------
# 	print$          Disk      Printer Drivers
# 	writer2_project Disk      
# 	IPC$            IPC       IPC Service (writer server (Samba, Ubuntu))
smbclient --no-pass -L //10.10.11.101
```

### Manual inspection

The website was made with WooCommerce.
Creation date: around `2021-05-17 21:57:04`.

Can browse `http://10.10.11.101/static/`.

The authors of the blog posts may have accounts:

```
Yolanda Wu
Nina Chyll
Catherine Hill
Evelyn Kill
Christina Marie
R.A
Shawn Forno
```

[author-profile]: https://app.hackthebox.eu/users/114053
