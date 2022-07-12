#!/bin/bash

USERNAME="$@"

curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"variables\": {\"username\": \"'"${USERNAME}"$'\"}, \"query\": \"query($username: String!){\\n tasks(username: $username){\\n Assignedto\\n username\\n text\\n taskstatus\\n type\\n}\\n}\"}' \
    $'http://internal-api.graph.htb/graphql' |
    perl -ne $'m#"Assignedto":"([a-fA-F0-9]+)"# && print $1."\n"'
