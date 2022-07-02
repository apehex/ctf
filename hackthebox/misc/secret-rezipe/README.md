> We have launched a startup that produces soft drinks.
> We use special ingredients to make them very tasty,
> so we have a lot of protections on our files to prevent our competitors from
> copying our ideas.

> Author: **[7Rocky][author-profile]**

## Testing the webapp

### Local deloyment

I had to specify a DNS server in `/etc/docker/daemon.json`:

```json
{
    "dns": ["10.83.0.1", "8.8.8.8"]
}
```

### Modifying the rezipe

The website has 2 routes: one to the frontpage, the other to suggest (POST)
ingredients.

The suggested ingredients are combined with a secret and both written in a
single file. It has a name similar to `tmp/99f7993263916c504c9d7aa9424dd06a/ingredients.txt`.

With `HTB{fake_flag_for_testing}` as secret, submiting this plaintext:

```json
{
    "ingredients": "ME{some_suggestion}"
}
```

Fills the file "ingredients.txt" with:

```
Secret: HTB{fake_flag_for_testing}
ME{some_suggestion}
```

This file is then put in an encrypted zip file and sent back.

## The "known plaintext" attack

The first 8 bytes of the encrypted zip are always known, as well as the bytes following offset 34.

The offset depends on the flag length; it can be found by sending an empty list of ingredients:

```shell
curl -s -k -X $'POST' -o re.zip \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-binary $'ingredients=' \
    $'http://localhost:1337/ingredients'
unzip -l re.zip 
# Archive:  re.zip
#   Length      Date    Time    Name
# ---------  ---------- -----   ----
#        34  2022-06-30 12:02   tmp/dda1bdf4e45603261b02ed50853f275d/ingredients.txt
# ---------                     -------
#        34                     1 fil
```

The legacy zip encryption has a long standing vulnerability, the [known plaintext attack][kpa-wiki].

## Mixing known ingredients in

```python
print(cli_args(KNOWN['prefix']['plaintext'], KNOWN['prefix']['offset']))
# -x 0 53 -x 1 65 -x 2 63 -x 3 72 -x 4 65 -x 5 74 -x 6 3a -x 7 20
```

## Cracking

I didn't manage to make the offset option work. So we'll use the sparse attack and specify the known byte one by one:

```shell
bkcrack -C ~/downloads/encrypted.zip \
    -c tmp/41e3952c6920cd5735812e00f1fdcb09/ingredients.txt \
    -x 22 0A -x 23 69 -x 24 77 -x 25 69 -x 26 6C -x 27 6C -x 28 66 -x 29 69 -x 2a 6E -x 2b 64 -x 2c 79 -x 2d 6F -x 2e 75 -x 2f 69 -x 30 77 -x 31 69 -x 32 6C -x 33 6C -x 34 65 -x 35 78 -x 36 70 -x 37 6F -x 38 73 -x 39 65 -x 3a 79 -x 3b 6F -x 3c 75 -x 3d 0A
```

```shell
curl -s -k -X $'POST' -o re.zip \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-binary $'ingredients=<?xml version="1.0" ' \
    $'http://localhost:1337/ingredients'
bkcrack -C re.zip -c tmp/29f087644dc6ef1a0af59fac25740ecf/ingredients.txt -p suffix.txt -o 22 -x 0 53 -x 1 65 -x 2 63 -x 3 72 -x 4 65 -x 5 74 -x 6 3a -x 7 20
```

[author-profile]: https://app.hackthebox.com/users/532274
[kpa-wiki]: https://en.wikipedia.org/wiki/Known-plaintext_attack
[pkcrack]: https://github.com/keyunluo/pkcrack
