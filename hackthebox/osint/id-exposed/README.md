# Id exposed

> **We are looking for Sara Medson Cruz's last location, where she left a
> message. We need to find out what this message is! We only have her email:
> saramedsoncruz@gmail.com**

## Trial & error

Possible path:
- looking for all social accounts with username `saramedsoncruz`
- scaping info on the associated google account
- sending a canary token by email?

## Sending a canary token

Let's try and send a token of appreciation to the creator ;)
![canary-token][canary-token-url]


```
http://canarytokens.com/static/traffic/terms/7lu4i2en60q3oear2ujk30zp6/contact.php
```

## Moving on

Looking for tools to perform osint on google accounts. it quickly appears that
the user-id is key.

The first online tool, [epieos][epieos-url], finds the user-id right away:

> 117395327982835488254

This gives us access to the [user contributions][google-account-contributions]: the flag is hidden in a comment.

[canary-token-url]: http://canarytokens.com/static/traffic/terms/7lu4i2en60q3oear2ujk30zp6/contact.php
[epieos-url]: https://tools.epieos.com/email.php
[google-account-contributions]: https://www.google.com/maps/contrib/117395327982835488254
