> Some web developers wrote this fancy new app! It's really cool, isn't it?

> Author: **[lunatec][author-profile]**

## Browsing the package

The sources are rather barren:

```bash
d2j-dex2jar app-release.apk
jd-gui app-release-dex2jar.jar
```

Let's look for credentials and the like:

```bash
apktool d -o sources app-release.apk
grep -ria password sources
# nothing
grep -ria secret sources
# still nothing
grep -raoH SFR # SFR is HTB encoded in base64
# app-release.apk:SFR
# sources/assets/index.android.bundle:SFR
# sources/build/apk/lib/armeabi-v7a/libjsc.so:SFR
# sources/build/apk/lib/armeabi-v7a/libjsc.so:SFR
# sources/lib/armeabi-v7a/libjsc.so:SFR
# sources/lib/armeabi-v7a/libjsc.so:SFR
grep -a SFR sources/assets/index.android.bundle
# __d(function(g,r,i,a,m,e,d){Object.defineProperty(e,"__esModule",{value:!0}),e.myConfig=void 0;var t={importantData:"baNaNa".toLowerCase(),apiUrl:'https://www.hackthebox.eu/',debug:'SFRCezIzbTQxbl9jNDFtXzRuZF9kMG43XzB2MzIyMzRjN30='};e.myConfig=t},400,[]);
perl -ne 'm#debug:'"'"'([/=0-9A-Za-z]*?)'"'"'#g && print $1' \
    sources/assets/index.android.bundle | base64 -d
# HTB{23m41n_c41m_4nd_d0n7_0v32234c7}
```

[author-profile]: https://app.hackthebox.eu/users/192853
