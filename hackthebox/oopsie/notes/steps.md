# Steps

## Enumeration

> Apache & ssh services

## Exploration

Proxy http://10.10.10.28 or look at the source in dev tools.

There's an anchor with url `'/cdn-cgi/login/script.js`.
Actually `http://10.10.10.28/cdn-cgi/login/index.php` is a login page.

We try the credentials harvested from the previous ctf (Archetype):
```
Guest / Admin / Administrator
M3g4c0rp_123 / MEGACORP_4dm1n!!"
```

## Fuzz Admin Page

> GET parameters can be guessed (sequential)

We bruteforce the accound id with fuff:
```bash
ffuf -c -v -z -mc 200 -request-proto http -mr "<td>\d+</td>" -w ids.forged -request accounts-id.txt
```
> 86575 ; super admin ; superadmin@megacorp.com

## Upload a Reverse Shell

First find where the uploads land

```console
$ dirsearch -u http://10.10.10.28 -e php
```

> yeah... /uploads/

## Upload a file

1) Open `http://10.10.10.28/cdn-cgi/login/admin.php?content=uploads` with super admin credentials (cookie)
2) Select webshell file and submit the upload, as admin
3) Find the corresponding request in burp proxy
4) Repeat the request, changing the cookie to super admin once again
5) Go to `http://10.10.10.28/uploads/webshell.php`

## Exploit

> we have a shell!

Browsing around we see "robert" in /home and /var/www/html shows us:
- sqli is possible with the id parameters on the admin.php page
- the credentials to connect to the db...

> robert M3g4C0rpUs3r!

## Move Around

Checking the `/etc/ssh/sshd_config`, login with password is allowed, so we try
the db credentials...

> bingo, ssh session with robert's credentials

Looking for more....
