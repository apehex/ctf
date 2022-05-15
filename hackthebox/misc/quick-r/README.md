> Let's see if you're a QuickR soldier as you pretend to be

> Author: **[hfz][author-profile]**

## Extracting the data

QuickR refers to "quick response code", a 2D barcode. Here, it is sent over as
ASCII art:

![][ascii-qrcode]

The QR code can be acquired with:

```shell
nc 134.209.22.191 30344 | tee buffer.txt
```

And the text surrounding it is filtered with:

```shell
sed -n '14,64p' buffer.txt > qrcode.txt
```

## Decoding the data

I didn't find a simple way to interpret a QR code as data matrix.

So we'll export the data as an image to then read it with a specialized tool.

### From color codes to pixel RGB

The Shell color codes are easier to match and replace in HEX. The whole data
chunk can be read as a single HEX string:

```shell
xxd -p -c 65536 qrcode.txt | python decode.py
```

This string is then split on the newline code `0a` and stripped of the tab
codes `09`, at the start of each line:

```python

```

[author-profile]: https://app.hackthebox.com/users/19832
[ascii-qrcode]: images/qrcode.png
