# Eternal loop

> **Can you find a way out of this loop?**

## What loop?

the file from HTB is an archive... containing another archive:

```bash
unzip -l 37366.zip

Archive:  37366.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
   460340  2018-05-23 10:02   5900.zip
---------                     -------
   460340                     1 file
```

Aaaaand it's also encrypted:

```bash
unzip 37366.zip

Archive:  37366.zip
[37366.zip] 5900.zip password:
```

First thing that comes to mind works: the filename is also the password.

## Iterating

The first step is to automatically retrieve the password:

```bash
unzip -l 5900.zip | sed -n 4p | perl -ne 'm/([0-9]+).zip/g && print $1'
```

Then extract the archive, get the name of the extracted file and iterate:

```bash
while file "$archive" | grep -qia compression; do
  echo "+ $archive"
  archive=$(unzip -P "$password" "$archive" | perl -ne 'm/inflating:\s+(.+zip)/g && print $1')
  password=$(unzip -l "$archive" | sed -n 4p | perl -ne 'm/([0-9]+).zip/g && print $1')
done
```

## Finally!

The script finally reaches an archive it cannot decompress.

It contains a single file, "DoNotTouch", whose password cannot be guessed with
our former method.

Let's try and crack it:

```bash
fcrackzip -v -u -D -p rockyou.txt 6969.zip
```

The final file is a sqlite database:

```bash
file DoNotTouch
DoNotTouch: SQLite 3.x database, last written using SQLite version 3021000

sqlite3 DoNotTouch
>.tables
albums          employees       invoices        playlists
artists         genres          media_types     tracks
customers       invoice_items   playlist_tra
```

Hopefully enumerating the "employees" tables is enough to find the flag!
