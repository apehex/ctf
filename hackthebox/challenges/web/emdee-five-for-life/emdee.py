#!/usr/bin/env python
import requests
import hashlib
import re

URL="http://178.62.61.23:30288/"

# session
s = requests.session()

# load the page
page = s.get(URL)

# the challenge
challenge = re.search("[a-zA-Z0-9]{20}", page.text)[0]

# hash
emdee = hashlib.md5(challenge.encode('utf-8')).hexdigest()

print(f'challenge: {challenge}\nmd5 hash : {emdee}')

result = s.post(url = URL, data = {'hash': emdee})

print(result.text)
