> I have made a password verification app. If I can remember the password,
> the app will tell me it is correct. See if you can guess my password.

> Authors: **[heartpoll][author-profile-1]** & **[bertolis][author-profile-2]**

## Browsing the sources

After unpacking with:

```bash
jadx-gui com.companyname.seethesharpflag-x86.apk &
```

The manifest points to the main activity:

```xml
<activity android:name="crc644cebad5a72cca3b1.MainActivity">
```

And this activity references functions from the `SeeTheSharpFlag` DLL:

```java
static {
    Runtime.register("SeeTheSharpFlag.Droid.MainActivity, SeeTheSharpFlag.Android", MainActivity.class, __md_methods);
}

public MainActivity() {
    if (getClass() == MainActivity.class) {
        TypeManager.Activate("SeeTheSharpFlag.Droid.MainActivity, SeeTheSharpFlag.Android", "", this, new Object[0]);
    }
}

public MainActivity(int i) {
    super(i);
    if (getClass() == MainActivity.class) {
        TypeManager.Activate("SeeTheSharpFlag.Droid.MainActivity, SeeTheSharpFlag.Android", "System.Int32, mscorlib", this, new Object[]{Integer.valueOf(i)});
    }
}
```

These are most likely to be in charge of the password checking.

## Reversing the dlls

First, let's extract the DLLs from the package:

```bash
unzip unzip com.companyname.seethesharpflag-x86.apk "assemblies/SeeTheSharpFlag*" -d truc
```

After trying `dotPeek` and `ILSpy` without success, I noticed `XALZ` at the start
of the hex dumps of both DLLs: they are Xamarin DLLs.

The first result in Google is actually about "decompressing Xamazin DLLs", and
Github delivers "xamazin-decompress":

```bash
python xamarin-decompress.py truc/assemblies/SeeTheSharpFlag.Android.dll
```

The resulting DLL can be opened in ILSpy. Most of the classes are empty, only
this function stands out:

```csharp
private void Button_Clicked(object sender, EventArgs e)
{
    byte[] buffer = Convert.FromBase64String("sjAbajc4sWMUn6CHJBSfQ39p2fNg2trMVQ/MmTB5mno=");
    byte[] rgbKey = Convert.FromBase64String("6F+WgzEp5QXodJV+iTli4Q==");
    byte[] rgbIV = Convert.FromBase64String("DZ6YdaWJlZav26VmEEQ31A==");
    using AesManaged aesManaged = new AesManaged();
    using ICryptoTransform transform = aesManaged.CreateDecryptor(rgbKey, rgbIV);
    using MemoryStream stream = new MemoryStream(buffer);
    using CryptoStream stream2 = new CryptoStream(stream, transform, CryptoStreamMode.Read);
    using StreamReader streamReader = new StreamReader(stream2);
    if (streamReader.ReadToEnd() == ((InputView)SecretInput).get_Text())
    {
        SecretOutput.set_Text("Congratz! You found the secret message");
    }
    else
    {
        SecretOutput.set_Text("Sorry. Not correct password");
    }
}
```

Well, looks like this is a wrap!

## Decrypting the ciphertext

Since there's an IV AES is used in CBC mode. It can be easily decrypted in Python:

```python
CIPHERTEXT = base64.b64decode("sjAbajc4sWMUn6CHJBSfQ39p2fNg2trMVQ/MmTB5mno=")
KEY = base64.b64decode("6F+WgzEp5QXodJV+iTli4Q==")
IV = base64.b64decode("DZ6YdaWJlZav26VmEEQ31A==")

cipher = AES.new(key=KEY, mode=AES.MODE_CBC, iv=IV)
flag = cipher.decrypt(CIPHERTEXT)
```

> b'HTB{MyPasswordIsVerySecure}\x05\x05\x05\x05\x05'

[author-profile-1]: https://app.hackthebox.eu/users/74804
[author-profile-2]: https://app.hackthebox.eu/users/27897
