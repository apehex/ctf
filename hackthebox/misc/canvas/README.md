# Canvas

> **We want to update our website but we are unable to because the developer who
> coded this left today. Can you take a look?**

## The sources

The website is made of a simple login form, with all the logic in the file `js/login.js`.

The file is obfuscated:
- the variable names are mangled
- the strings are scrambled too

## Deobfuscation

The strings are simply ASCII hex, which is automatically translated by this tool:

```bash
uglifyjs js/login.js > login.pretty.js
```

The file is still messy, with logging and cookie handling. We're looking for
code related to authentication, like:

```javascript
function validate() {
    var _0x4d1a17 = _0x20fe,
        _0x32b344 = document["getElementById"]("username")["value"],
        _0x5997a2 = document[_0x4d1a17("0xd")]("password")[_0x4d1a17("0x0")];
    if (_0x32b344 == _0x4d1a17("0x12") && _0x5997a2 == _0x4d1a17("0x12")) return alert(_0x4d1a17("0x9")), window["location"] = "dashboard.html", ![];
    else {
        attempt--, alert(_0x4d1a17("0x2") + attempt + _0x4d1a17("0x15"));
        if (attempt == 0) return document[_0x4d1a17("0xd")](_0x4d1a17("0xb"))["disabled"] = !![], document[_0x4d1a17("0xd")]("password")[_0x4d1a17("0x10")] = !![], document[_0x4d1a17("0xd")]("submit")[_0x4d1a17("0x10")] = !![], ![]
    }
}
var res = String["fromCharCode"](72, 84, 66, 123, 87, 51, 76, 99, 48, 109, 51, 95, 55, 48, 95, 74, 52, 86, 52, 53, 67, 82, 49, 112, 55, 95, 100, 51, 48, 98, 70, 117, 53, 67, 52, 55, 49, 48, 78, 125, 10);
```

The last bit looks like ASCII chars again, and running it the Chrome dev console gives us the flag.