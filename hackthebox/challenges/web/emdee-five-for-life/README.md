# Emdee five for life

> **Can you encrypt fast enough?**

## The challenge

The page displays a random string, a single input form and is titled "MD5
encrypt this string".

Manually submiting the form with the hash gives: "Too slow!".

It looks like the challenge is to submit the hash as soon as the page arrives.

## Hashing

With burpsuite, we capture the request and save it as curl command:

```bash
send_hash() {
  read hash
  echo $(curl -s -k --compressed -X $'POST' \
    -H $'Content-Length: 25' \
    -H $'Content-Type: application/x-www-form-urlencoded' \
    -H $'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
    -H $'Accept-Encoding: gzip, deflate' \
    -H $'Connection: close' \
    -b $'PHPSESSID=cgt1c1290th6lnb2uars7idl04' \
    --data-binary "hash=$hash" \
    "$URL")
  return 0
}
```

Matching the string is easy enough:

```bash
perl -ne 'm#([a-zA-Z0-9]{20})#'
```

And chain the requests:

```bash
echo "qyJmp196QLTUb9qgUMLD" |
  send_hash |
  perl -ne 'm#([a-zA-Z0-9]{20})#gi && print $1' |
  md5sum - |
  cut -d' ' -f1 |
  send_hash
```

That's it!