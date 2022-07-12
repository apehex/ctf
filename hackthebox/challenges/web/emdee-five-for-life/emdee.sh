#!/bin/bash

URL="http://178.62.61.23:30288/"

# post a single hash to the server
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

echo "qyJmp196QLTUb9qgUMLD" |
  send_hash |
  perl -ne 'm#([a-zA-Z0-9]{20})#gi && print $1' |
  md5sum - |
  cut -d' ' -f1 |
  send_hash
