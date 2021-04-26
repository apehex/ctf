# Cat

> **Easy leaks**

## Content

Using `file cat.ab` we learn that it is an Android backup.

## Extraction

```bash
( printf "\x1f\x8b\x08\x00\x00\x00\x00\x00" ; tail -c +25 cat.ab ) |
  tar xfvz -
```

This outputs both applications and user data.

## Exploration

Browsing user data, we find some data leak on a photo:

> HTB{ThisBackupIsUnprotected}
