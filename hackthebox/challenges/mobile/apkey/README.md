> This app contains some unique keys. Can you get one?

> Author: **[bertolis][author-profile]**

## Browsing the package

### Resources

First, unpack the resources and manifest:

```bash
apktool d -o src APKey.apk
```

Nothing in the manifest, but the "META-INF" folder contains:

```bash
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

It looks like a wink to the cracking tool "John the ripper", but I found no use
for this file.

Grepping for keys, flags, ciphers etc fails too.

### Java code

So we go ahead and extract the Java source code:

```bash
jadx-gui APKey.apk &
```

The MainActivity of the app is located in `com/example.apkey`.

The app asks for a username:

```java
`if (MainActivity.this.f928c.getText().toString().equals("admin")) {`
```

And a password, which it processes into an MD5 hash:

```java
MessageDigest instance = MessageDigest.getInstance("MD5");
instance.update(obj.getBytes());
```

If the digest matches the hardcoded result, it proceeds with the following:

```java
if (str.equals("a2a3d412e92d896134d9c9126d756f")) {
    Context applicationContext = MainActivity.this.getApplicationContext();
    MainActivity mainActivity2 = MainActivity.this;
    b bVar2 = mainActivity2.e;
    g gVar = mainActivity2.f;
    makeText = Toast.makeText(applicationContext, b.a(g.a()), 1);
    makeText.show();
}
```

## Decoding

The goal is to run the instruction `Toast.makeText(applicationContext, b.a(g.a()), 1)`.

There several ways to do this:

- change the password check and recompile the app with known credentials
- reverse engineer & execute the target code

Actually the target code is straightforward:

```java
public class b {
    public static String a(String str) {
        char charAt = h.a().charAt(0);
        char charAt2 = a.a().charAt(8);
        char charAt3 = e.a().charAt(5);
        char charAt4 = i.a().charAt(4);
        char charAt5 = h.a().charAt(1);
        char charAt6 = h.a().charAt(4);
        char charAt7 = h.a().charAt(3);
        char charAt8 = h.a().charAt(3);
        char charAt9 = h.a().charAt(0);
        char charAt10 = a.a().charAt(8);
        char charAt11 = a.a().charAt(8);
        char charAt12 = i.a().charAt(0);
        char charAt13 = c.a().charAt(3);
        char charAt14 = f.a().charAt(3);
        char charAt15 = f.a().charAt(0);
        char charAt16 = c.a().charAt(0);
        SecretKeySpec secretKeySpec = new SecretKeySpec((String.valueOf(charAt) + String.valueOf(charAt2) + String.valueOf(charAt3) + String.valueOf(charAt4) + String.valueOf(charAt5).toLowerCase() + String.valueOf(charAt6) + String.valueOf(charAt7).toLowerCase() + String.valueOf(charAt8) + String.valueOf(charAt9) + String.valueOf(charAt10).toLowerCase() + String.valueOf(charAt11).toLowerCase() + String.valueOf(charAt12) + String.valueOf(charAt13).toLowerCase() + String.valueOf(charAt14) + String.valueOf(charAt15) + String.valueOf(charAt16)).getBytes(), g.b());
        Cipher instance = Cipher.getInstance(g.b());
        instance.init(2, secretKeySpec);
        return new String(instance.doFinal(Base64.decode(str, 0)), "utf-8");
    }
}
```

It gathers characters from all over the app to form the key and algorithm needed by:

```java
SecretKeySpec(byte[] key, String algorithm)
```

So I went for the second option before I knew it and gathered all the parts
in a single class. Each part is similar to this one:


```java
import java.util.ArrayList;

public class h {
  public static String a() {
    ArrayList<String> arrayList = new ArrayList();
    arrayList.add("8GGfdt");
    arrayList.add("7654rF");
    arrayList.add("09Hy24");
    arrayList.add("56Gth6");
    arrayList.add("hdgKj8");
    arrayList.add("kdIdu8");
    arrayList.add("kHtZuV");
    arrayList.add("jHurf6");
    arrayList.add("5tgfYt");
    arrayList.add("kd9Iuy");
    return arrayList.get(6);
  }
}
```

Running our custom `b.a` returns the key, algorithm and base64 encoded ciphertext:

```bash
# kV9qhuzZkvvrgW6F
# AES
# 1UlBm2kHtZuVrSE6qY6HxWkwHyeaX92DabnRFlEGyLWod2bkwAxcoc85S94kFpV1
javac Decode.java
java Decode
```

Finally, we can decrypt using Python:

```python
import base64
from Crypto.Cipher import AES
cipher = AES.new(bytes("kV9qhuzZkvvrgW6F", "utf-8"), AES.MODE_ECB)
cipher.decrypt(base64.b64decode("1UlBm2kHtZuVrSE6qY6HxWkwHyeaX92DabnRFlEGyLWod2bkwAxcoc85S94kFpV1"))
```

> b'HTB{m0r3_0bfusc4t1on_w0uld_n0t_hurt}\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c\x0c'

[author-profile]: https://app.hackthebox.eu/users/27897
