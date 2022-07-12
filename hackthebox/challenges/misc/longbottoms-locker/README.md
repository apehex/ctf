# Longbottom's locker

> **Break into Longbottom's vault and steal his secrets.**

## HMAC

The website a requesting a password: it has to be somehow encoded in the 

Looking at the source, the password is implicitely hardcoded inside a HMAC:

```javascript
var passphrase = document.getElementById('passwd').value,
    encryptedMsg = '4cce4470203e10b395ab1787a22553a5b2503d42a965da813676d929cc16f76cU2FsdGVkX19FvUyhqWoQKHXNLBL64g8acK4UQoP6XZQ/n4MRL3rgQj8TJ/3r8Awtxte2V9s+RLfQHJOHGwYtctqRa/H2BetmxjwGG+LYKUWC8Z6WBoYbecwtATCOuwewnp+VKBzsWLme+3BZyRgKEA==',
    encryptedHMAC = encryptedMsg.substring(0, 64),
    encryptedHTML = encryptedMsg.substring(64),
    decryptedHMAC = CryptoJS.HmacSHA256(encryptedHTML, CryptoJS.SHA256(passphrase).toString()).toString();

if (decryptedHMAC !== encryptedHMAC) {
    alert('Bad passphrase!');
    return;
}

var plainHTML = CryptoJS.AES.decrypt(encryptedHTML, passphrase).toString(CryptoJS.enc.Utf8);
```

The input field tells us that the password is at most 18 characters long.

There are pointers to Harry Potter's lore, which could be used to build a
dictionary and try a bruteforce attack.

Still this would be chancy at best, and I want to solve the challenge logically.

## Looking around

So I assume there must be clues hidden somewhere. The images files are
especially conspicuous.

### Fast and failed

`trid`, `exiftool`, `steg*` tools find nothing outstanding / hidden. Apparently
there's 5.1 KB of room for a payload.

Yet `strings -n8` outputs:

```
__MACOSX/UX
8f@[8f@[
__MACOSX/._donotshareUX
```

### Pickles?

In the end, `binwalk` finds compressed data:

```
(lp1
(lp2
(S' '
I163
tp3
aa(lp4
(S' '
I1
tp5
a(S'.'
I1
tp6
a(S'd'
I1
tp7
a(S'8'
I4
tp8
a(S'b'
I1
tp9
a(S'.'
I1
tp10
a(S' '
I12
tp11
a(S'd'
I1
tp12
```

I don't know this format, but there are a lot of recurrent / structured data.
Expressed in Perl regex, the patterns are:

- `I\d+`
- `lp\d+`
- `tp\d+`
- `S'[a-zA-Z0-9]+'`

These look like indexes and quoted strings. So I guess this is

After googling around, I realized that the data is a `pickle` dump: the `S'[a-zA-Z0-9]+'`
are indeed strings and `I\d+` are actually integers, `F` for floats etc.

## Decoding

The data can be loaded with:

```python
with open('donotshare', 'rb') as f:
    data = pickle.load(f, encoding='utf-8')
```

And that data is indeed a coherent python array; actually an arrays of arrays like:

```python
[(' ', 1), ('.', 1), ('d', 1), ('8', 4), ('b', 1), ('.', 1), (' ', 12), ('d', 1), ('8', 3), (' ', 7), ('8', 3), (' ', 2), ('.', 1), ('d', 1), ('8', 4), ('b', 1), ('.', 1), (' ', 22), ('d', 1), ('8', 4), (' ', 2), ('8', 3), ('b', 1), (' ', 4), ('8', 3), (' ', 8), ('8', 7), ('b', 1), ('.', 1), (' ', 3), ('.', 1), ('d', 1), ('8', 4), ('b', 1), ('.', 1), (' ', 2), ('8', 9), (' ', 2), ('8', 9), (' ', 2), ('8', 3), (' ', 5), ('8', 3), (' ', 15)]
```

My first reflex is to interpret each tuple as `(character, repetition)` and
concatenate all the 

```python
def decode(occurrences):
    return ''.join([c * n for c, n in occurrences])
decode(data[2])
'd88P  Y88b          d8888       888 d88P  Y88b                    d8P888  8888b   888        888   Y88b d88P  Y88b 888        888        888     888               '
```

So I'm now looking at python strings, that don't make much sense yet...

After printing the arrays one by one, I realized that the stacked lines actually
made an ASCII art graffiti!

This graff is the password of the locker, finally!
