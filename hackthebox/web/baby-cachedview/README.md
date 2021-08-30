> I made a service for people to cache their favourite websites, come and check it out!
> But don't try anything funny, after a recent incident we implemented military
> grade IP based restrictions to keep the hackers at bay...

> Authors: **[makelaris][author-profile-1] & [makelarisjr][author-profile-2]**

## Caching the flag

### SSRF

The client asks the server to retrieve a webpage for him; the target url is
sent in a serialized json object:

```javascript
fetch('/api/cache', {
    method: 'POST',
    body: JSON.stringify({
        'url': url.value
    }),
    headers: {
        'Content-Type': 'application/json'
    }
})
```

The SSRF is not a bug, but a feature.

The goal is the file `flag.png` at the root of the server WD.

### The filter

The flag can only be requested from the localhost:

```python
@web.route('/flag')
@is_from_localhost
def flag():
    return send_file('flag.png')
```

I should have read twice: I spent most of my time reaching for `/flag.png`
instead of `/flag`...

This makes the caching function the ideal candidate, since it originates from
the server.

But the caching operation checks whether the target is the localhost:

```python
def is_inner_ipaddress(ip):
    ip = ip2long(ip)
    return ip2long('127.0.0.0') >> 24 == ip >> 24 or \
            ip2long('10.0.0.0') >> 24 == ip >> 24 or \
            ip2long('172.16.0.0') >> 20 == ip >> 20 or \
            ip2long('192.168.0.0') >> 16 == ip >> 16 or \
            ip2long('0.0.0.0') >> 24 == ip >> 24

if is_inner_ipaddress(socket.gethostbyname(domain)):
    return flash('IP not allowed', 'danger')
```

This last test defeats most tricks from [Hacktricks][hacktricks-ssrf]. The domain is checked
after `socket.gethostbyname(domain)` has performed a DNS resolution, so:

- the sneaky formatings are processed before the test and the result is standardized:
  `https://{domain}@127.0.0.1` and the like fail because they return  `127.0.0.1` or `None`
- DNS redirections are followed prior to the test: `http://spoofed.burpcollaborator.net/flag`
  fails because the domain `spoofed.burpcollaborator.net` redirects to `127.0.0.1`
  which is the string tested
- all the numeric variation like `0` fail too because the test is an integer
  comparison, not a string comparison (also this happens after resolution)

## Bypassing the filter

### Bouncing

Still the filter is applied only once, on the submited url. The subsequent requests
made by the server are whitelisted.

So we can bounce on a redirection url, like a URL shortener:

```
https://tinyurl.com/tepk9b => http://localhost/flag
```

```
{"domain":"tinyurl.com","filename":"6e60563f6bc57bdd097962c230cb.png","level":"success","message":"Successfully cached tinyurl.com"}
```

### Paycache

Another solution would be to craft a webpage with this image tag:

```html
<img src="http://localhost/flag">
```

And serve it on a public page, through Ngrok for example:

![][paycache]

> HTB{reb1nd1ng_y0ur_dns_r3s0lv3r_0n3_qu3ry_4t_4_t1m3}

[author-profile-1]: https://app.hackthebox.eu/users/107
[author-profile-2]: https://app.hackthebox.eu/users/95
[hacktricks-ssrf]: https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery
[paycache]: images/paycache.png
