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
curl -s -k -X $'POST' -o ingredients.zip \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-binary $'ingredients=' \
    $'http://localhost:1337/ingredients'
unzip -l ingredients.zip 
# Archive:  ingredients.zip
#   Length      Date    Time    Name
# ---------  ---------- -----   ----
#        34  2022-06-30 12:02   tmp/dda1bdf4e45603261b02ed50853f275d/ingredients.txt
# ---------                     -------
#        34                     1 fil
```

The legacy zip encryption has a long standing vulnerability, the [known plaintext attack][kpa-wiki].

## Spoiling the bin soup

This attack requires 12 bytes of known plaintext.

In theory they can be given at any position in the cipherfile. In practice, with `bkcrack`, the attack only worked for me when supplying the starting bytes of the encrypted file.

The following attempts all failed.

### Random tries

None of these worked:

```shell
# hex offset
bkcrack -C ingredients.zip -c tmp/29f087644dc6ef1a0af59fac25740ecf/ingredients.txt -p suffix.txt -o 22
# decimal offset
bkcrack -C ingredients.zip -c tmp/29f087644dc6ef1a0af59fac25740ecf/ingredients.txt -p suffix.txt -o 34
# diverse payloads, in particular the one in the repo's tutorial, or lorem ipsum, whatever! mb the diversity in the character set helps ??
echo -e -n '\n<?xml version="1.0" encoding="UTF-8"?>' > suffix.txt && bkcrack -C ingredients.zip -c tmp/29f087644dc6ef1a0af59fac25740ecf/ingredients.txt -p suffix.txt -o 22
# with / without a plaintext archive
bkcrack -C ingredients.zip -c tmp/badc04fc9daa98cac1cc404439de9a91/ingredients.txt -P ingredients.plain.zip -p ingredients.txt -o 22
# mirroring the names of the encrypted archive, in the plaintext archive
bkcrack -C ingredients.zip -c tmp/da1b304ee12577727b4e78dc0586c1cf/ingredients.txt -P tmp/da1b304ee12577727b4e78dc0586c1cf/ingredients.zip -p tmp/da1b304ee12577727b4e78dc0586c1cf/ingredients.txt -o 22
```

Of course I requested the archive with the known ingredients matching the plantext arguments; it differs from one line to the other on these examples. 

### Using the "sparse" technique / option

I tried a lot of variation of these:

```shell
# suffix in a file and the prefix specified byte by byte
bkcrack -C ingredients.zip -c tmp/29f087644dc6ef1a0af59fac25740ecf/ingredients.txt -p suffix.txt -o 22 -x 0 53 -x 1 65 -x 2 63 -x 3 72 -x 4 65 -x 5 74 -x 6 3a -x 7 20
# only the suffix, byte by byte
bkcrack -C ~/downloads/encrypted.zip -c tmp/41e3952c6920cd5735812e00f1fdcb09/ingredients.txt \
    -x 22 0A -x 23 69 -x 24 77 -x 25 69 -x 26 6C -x 27 6C -x 28 66 -x 29 69 -x 2a 6E -x 2b 64 -x 2c 79 -x 2d 6F -x 2e 75 -x 2f 69 -x 30 77 -x 31 69 -x 32 6C -x 33 6C -x 34 65 -x 35 78 -x 36 70 -x 37 6F -x 38 73 -x 39 65 -x 3a 79 -x 3b 6F -x 3c 75 -x 3d 0A
# same with the prefix too
bkcrack -C ~/downloads/encrypted.zip -c tmp/41e3952c6920cd5735812e00f1fdcb09/ingredients.txt -p prefix.txt \
    -x 22 0A -x 23 69 -x 24 77 -x 25 69 -x 26 6C -x 27 6C -x 28 66 -x 29 69 -x 2a 6E -x 2b 64 -x 2c 79 -x 2d 6F -x 2e 75 -x 2f 69 -x 30 77 -x 31 69 -x 32 6C -x 33 6C -x 34 65 -x 35 78 -x 36 70 -x 37 6F -x 38 73 -x 39 65 -x 3a 79 -x 3b 6F -x 3c 75 -x 3d 0A
```

Actually I discovered -after cracking ofc- that even though the help says:

```shell
bkcrack -h
# -x, --extra <offset> <data> Additional plaintext in hexadecimal starting
#     at the given offset (may be negative)
```

Only the data is expected to be in hexadecimal: the offset is a decimal number.

So I should have computed the offset / data of the payload with:

```python
KNOWN = {
    'prefix': {
        'offset': 0, # Secret: 
        'plaintext': 'Secret: HTB{'.encode('utf-8').hex(':').upper().split(':')},
    'suffix': {
        'offset': 34, # ________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        'plaintext': '\n<?xml version="1.0" '.encode('utf-8').hex(':').upper().split(':')}}

##################################################################### formating

_format = '-x {offset} {byte}'.format

def cli_args(plaintext, offset):
    return ' '.join([
        _format(
            offset=__i+offset,
            byte=plaintext[__i])
        for __i in range(len(plaintext))])

######################################################################## output

print(cli_args(KNOWN['prefix']['plaintext'], KNOWN['prefix']['offset']))
# -x 0 53 -x 1 65 -x 2 63 -x 3 72 -x 4 65 -x 5 74 -x 6 3a -x 7 20
```

### Using the CRC

The most significant byte of the CRC is right before the ciphertext; it can be specified with:

```shell
bkcrack -L ingredients.zip 
# Index Encryption Compression CRC32    Uncompressed  Packed size Name
# ----- ---------- ----------- -------- ------------ ------------ ----------------
#     0 ZipCrypto  Store       b9be1b86           64           76 tmp/80757f0c9028c5c657f574e502afe908/ingredients.txt
echo -e -n '\xb9Secret: HTB{' > prefix.txt
bkcrack -C ingredients.zip -c tmp/80757f0c9028c5c657f574e502afe908/ingredients.txt -p prefix.txt -o -1
```

This failed too.

## Cracking the "ZipCrypto" cipher

I didn't manage to make the offset option work. In the end the 12 bytes at the start of the file are enough, no need to add "public" ingredients:

```shell
curl -s -k -X $'POST' -o ingredients.zip \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-binary $'ingredients=' \
    $'http://localhost:1337/ingredients'
```

```shell
bkcrack -L ingredients.zip
# Index Encryption Compression CRC32    Uncompressed  Packed size Name
# ----- ---------- ----------- -------- ------------ ------------ ----------------
#     0 ZipCrypto  Store       49ba4df2           43           55 tmp/3c57e5e939abae3901ddd793321cfd06/ingredients.txt
echo -e -n 'Secret: HTB{' > prefix.txt
bkcrack -C ingredients.zip -c tmp/80757f0c9028c5c657f574e502afe908/ingredients.txt -p prefix.txt
# [18:00:48] Z reduction using 4 bytes of known plaintext
# 100.0 % (4 / 4)
# [18:00:48] Attack on 1375733 Z values at index 7
# Keys: a9f7ada8 fa26752d 57051fa0
# 44.7 % (615028 / 1375733)
# [18:22:51] Keys
# a9f7ada8 fa26752d 57051fa0
```

And now we know this is equivalent to:

```shell
# -x 11 7B and not -x 0B 7B
bkcrack -C ingredients.zip --cipher-index 0 -x 0 53 -x 1 65 -x 2 63 -x 3 72 -x 4 65 -x 5 74 -x 6 3A -x 7 20 -x 8 48 -x 9 54 -x 10 42 -x 11 7B
```

Finally the archive can be decrypted:

```shell
bkcrack -C ingredients.zip -c tmp/3c57e5e939abae3901ddd793321cfd06/ingredients.txt -k a9f7ada8 fa26752d 57051fa0 -d ingredients.txt
cat ingredients.txt
# Secret: HTB{C0mpr3sSi0n_1s_n0t_3NcryPti0n}
```

> `HTB{C0mpr3sSi0n_1s_n0t_3NcryPti0n}`

Also it is highly possible that some of my earlier tries would have worked with the correct decimal offset as argument: `34` for the test env and `43` for the VM deployed on HTB.

[author-profile]: https://app.hackthebox.com/users/532274
[kpa-wiki]: https://en.wikipedia.org/wiki/Known-plaintext_attack
[pkcrack]: https://github.com/keyunluo/pkcrack
