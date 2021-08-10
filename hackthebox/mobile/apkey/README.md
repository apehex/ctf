> **This app contains some unique keys. Can you get one?**

> Author: **[bertolis][author-profile]**

## Browsing the sources

First, unpack:

```bash
apktool d -o sources base.apk
```

Nothing in the manifest, but the "META-INF" folder contains:

```
982095  4 -rw-r--r-- 1 root root  1531 Aug  9 20:36 JOHN.DSA
982094 84 -rw-r--r-- 1 root root 82115 Aug  9 20:36 JOHN.SF
982093 84 -rw-r--r-- 1 root root 81953 Aug  9 20:36 MANIFEST.MF
```

```bash
# Collecting data from file: sources/original/META-INF/JOHN.DSA
#  40.2% (.CAT) Microsoft Security Catalog (DER encoded) (2020/8)
#  39.8% (.DER) DER encoded X509 Certificate (2000/1)
#  19.9% (.P7S) PKCS #7 Signature (1001/2)
trid JOHN.DSA
```

[author-profile]: https://app.hackthebox.eu/users/27897
