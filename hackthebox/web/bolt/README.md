> Author: **[d4rkpayl0ad][author-profile]**

## Discovery

### Port scanning

```bash
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     nginx 1.18.0 (Ubuntu)
443/tcp open  ssl/http nginx 1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=passbolt.bolt.htb/organizationName=Internet Widgits Pty Ltd/stateOrProvinceName=Some-State/countryName=AU
| Not valid before: 2021-02-24T19:11:23
|_Not valid after:  2022-02-24T19:11:23
823/tcp   filtered unknown
2972/tcp  filtered pmsm-webrctl
3032/tcp  filtered redwood-chat
6340/tcp  filtered unknown
6773/tcp  filtered unknown
8102/tcp  filtered kz-migr
17147/tcp filtered unknown
24096/tcp filtered unknown
26590/tcp filtered unknown
27224/tcp filtered unknown
30519/tcp filtered unknown
32710/tcp filtered unknown
33774/tcp filtered unknown
47686/tcp filtered unknown
55595/tcp filtered unknown
57182/tcp filtered unknown
57574/tcp filtered unknown
62571/tcp filtered unknown
63959/tcp filtered unknown
```

```bash
gobuster dir -u http://bolt.htb -w /usr/share/wordlists/discovery/raft-large-directories-lowercase.txt
# /contact              (Status: 200) [Size: 26293]
# /logout               (Status: 302) [Size: 209] [--> http://10.10.11.114/]
# /register             (Status: 200) [Size: 11038]
# /download             (Status: 200) [Size: 18570]
# /login                (Status: 200) [Size: 9287]
# /services             (Status: 200) [Size: 22443]
# /profile              (Status: 500) [Size: 290]
# /index                (Status: 308) [Size: 247] [--> http://10.10.11.114/]
# /pricing              (Status: 200) [Size: 31731]
# /sign-up              (Status: 200) [Size: 11038]
# /sign-in              (Status: 200) [Size: 9287]
# /check-email          (Status: 200) [Size: 7331]
gobuster dir -u http://demo.bolt.htb -w /usr/share/wordlists/discovery/raft-medium-directories-lowercase.txt
# /logout               (Status: 302) [Size: 219] [--> http://demo.bolt.htb/login]
# /register             (Status: 200) [Size: 11066]
# /login                (Status: 200) [Size: 9710]
```

```bash
gobuster vhost --domain bolt.htb --append-domain -w /usr/share/wordlists/discovery/subdomains-top1million-20000.txt -u http://10.10.11.114
# Found: mail.bolt.htb (Status: 200) [Size: 4943]
# Found: demo.bolt.htb (Status: 302) [Size: 219]
```

### Browsing the webserver

The website is mostly empty / not responding, apart from the pages `/login`
and `/download`.

The default / random credentials don't work on the login page and it's not
possible to register a new account.

On the download page there's a docker image.

## Break-in

The Docker image hosts a web app that may have shared credentials.

The app files are scattered between the Docker image layers. The goal is to
find the database credentials and data.

So we extract all the layers and look for the Flask sources:

```bash
find image/ -type f -name '*.py' | grep -iav site-packages | grep -iav 'usr/lib'
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/forms.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/home/routes.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/util.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/__init__.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/forms.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/routes.py
# image/41093412e0da959c80875bb0db640c1302d5bcdffec759a3a5670950272789ad/app/base/models.py
# image/3049862d975f250783ddb4ea0e9cb359578da4a06bf84f05a7ea69ad8d508dab/app/base/.wh.routes.py
# image/3049862d975f250783ddb4ea0e9cb359578da4a06bf84f05a7ea69ad8d508dab/app/base/.wh.forms.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/config.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/gunicorn-cfg.py
# image/745959c3a65c3899f9e1a5319ee5500f199e0cadf8d487b92e2f297441f8c5cf/run.py
# image/2265c5097f0b290a53b7556fd5d721ffad8a4921bfc2a6e378c04859185d27fa/app/base/forms.py
# image/2265c5097f0b290a53b7556fd5d721ffad8a4921bfc2a6e378c04859185d27fa/app/base/routes.py
```

And the Flask config holds:


```python
# PostgreSQL database
SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
    config( 'DB_ENGINE'   , default='postgresql'    ),
    config( 'DB_USERNAME' , default='appseed'       ),
    config( 'DB_PASS'     , default='pass'          ),
    config( 'DB_HOST'     , default='localhost'     ),
    config( 'DB_PORT'     , default=5432            ),
    config( 'DB_NAME'     , default='appseed-flask' )
)
```

Next hunt for the data store files:

```bash
find image/ -type f -name 'db.sqlite3'
# image/a4ea7da8de7bfbf327b56b0cb794aed9a8487d31e588b75029f6b527af2976f2/db.sqlite3
```

And this DB has some admin credentials in the User table:

```bash
sqlite3 image/a4ea7da8de7bfbf327b56b0cb794aed9a8487d31e588b75029f6b527af2976f2/db.sqlite3 'select * from User' 
# 1|admin|admin@bolt.htb|$1$sm1RceCh$rSd3PygnS/6jlFDfF2J5q.||
```

This is a MD5 hash:

```bash
hashcat -m 2600 -a 0 admin.hash /usr/share/wordlists/passwords/rockyou-50.txt
```

> admin:deadbolt

This allows to connect to the dashboard AdminLTE.

## Lateral movement



```python
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]
        code      = request.form['invite_code']
        if code != 'XNSS-HSJW-3NGU-8XTJ':
```

## Moving

Registering / accessing `passbolt.bolt.htb` requires the input email to be
tagged with an invite code:

![][require-invitation]

[author-profile]: https://app.hackthebox.eu/users/168546

[require-invitation]: 
