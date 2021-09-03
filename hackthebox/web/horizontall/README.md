> Author: **[wail99][author-profile]**

## Discovery

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Did not follow redirect to http://horizontall.htb
|_http-server-header: nginx/1.14.0 (Ubuntu)
```

```javascript
r.a.get("http://api-prod.horizontall.htb/reviews").then((function(s) {
```

```
HTTP/1.1 404 Not Found
Server: nginx/1.14.0 (Ubuntu)
Date: Fri, 03 Sep 2021 09:12:31 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 60
Connection: close
Vary: Origin
Content-Security-Policy: img-src 'self' http:; block-all-mixed-content
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Allow: HEAD, GET
X-Powered-By: Strapi <strapi.io>

{"statusCode":404,"error":"Not Found","message":"Not Found"}
```

`admin/src/containers/InputModalStepperProvider/index.js` has a `/proxy?url=`
functionality which could be abused to route to internal IPs and access private
IPs available to the server.

`http://api-prod.horizontall.htb/users` is forbidden.

```
/admin                (Status: 200) [Size: 854]
/Admin                (Status: 200) [Size: 854]
/users                (Status: 403) [Size: 60] 
/reviews              (Status: 200) [Size: 507]
/ADMIN                (Status: 200) [Size: 854]
/Users                (Status: 403) [Size: 60] 
/Reviews              (Status: 200) [Size: 507]
```

> admin:admin

```json
{
    "jwt":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywiaXNBZG1pbiI6dHJ1ZSwiaWF0IjoxNjMwNjcxMTE0LCJleHAiOjE2MzMyNjMxMTR9.VjOpD6TxXsOXyZ_HQGaEi6P_lZuwh7T_fIsm4bc4XX8",
    "user":{
        "username":"admin",
        "id":3,
        "email":"admin@horizontall.htb",
        "blocked":null,
        "isAdmin":true
    }
}
```

## Footfhold

Strapi is riddled with CVEs

## Strapi to developer

Just follow the trail:

```bash
grep -ria password . | tee pw.tmp
# ./config/environments/development/database.json:        "password": "#J!:F9Zt2u"
cat config/environments/development/database.json
# {
#   "defaultConnection": "default",
#   "connections": {
#     "default": {
#       "connector": "strapi-hook-bookshelf",
#       "settings": {
#         "client": "mysql",
#         "database": "strapi",
#         "host": "127.0.0.1",
#         "port": 3306,
#         "username": "developer",
#         "password": "#J!:F9Zt2u"
#       },
#       "options": {}
#     }
#   }
# }
mysql -h'127.0.0.1' -D'strapi' -u'developer' -p'#J!:F9Zt2u' -e'show tables;'
mysql -h'127.0.0.1' -D'strapi' -u'developer' -p'#J!:F9Zt2u' -e'select * from strapi_administrator;'
# +----+----------+-----------------------+--------------------------------------------------------------+--------------------+---------+
# | id | username | email                 | password                                                     | resetPasswordToken | blocked |
# +----+----------+-----------------------+--------------------------------------------------------------+--------------------+---------+
# |  3 | admin    | admin@horizontall.htb | $2a$10$svfqkU62mjQ5UwYlf2uFKO0ueTYJ61WJ5qS/.EbdLWsXVAXoMPcX6 | NULL               |    NULL |
# +----+----------+-----------------------+--------------------------------------------------------------+--------------------+---------+
```

[author-profile]: https://app.hackthebox.eu/users/4005
