> Just unzip the archive ... several times ...

> Author: **[swani][author-profile]**

## The loop

Each archive contains yet another archive, like russian dolls:

```shell
unzip -l archives/1.zip 
# Archive:  archives/1.zip
#   Length      Date    Time    Name
# ---------  ---------- -----   ----
#    624814  2018-10-03 20:02   flag_999.zip
#        95  2018-10-03 20:02   pwd.png
# ---------                     -------
#    624909                     2 file
```

The password for the next archive is encoded as morse in "pwd.png":

![][morse-password]

## Translating the image to text

## Extracting a single archive

## Automating the process

[author-profile]: https://app.hackthebox.com/users/22280
[morse-password]: images/morse-password.png
