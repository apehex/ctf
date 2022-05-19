#!/usr/bin/env python

from flask_unsign import session

KEY = 'secret123'
COOKIE = {"logged_in":True,"username":"blue"}

__jwt = session.sign(
    value=COOKIE,
    secret=KEY,
    legacy=False)

print(__jwt)
