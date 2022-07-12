> Let's see if you're a QuickR soldier as you pretend to be

> Author: **[hfz][author-profile]**

## The challenge

QuickR refers to "quick response code", a 2D barcode. Here, it is sent over as
ASCII art:

![][ascii-qrcode]

This QR code translates to:

```
60.38225375139366 x 413.08018551883515 / 233.93430618643774 =
```

## Extracting the data

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
xxd -p -c 65536 qrcode.txt | python sources/decode.py
```

In `decode.py`, this string is then split on the newline code `0a` and stripped
of the tab codes `09`, at the start of each line:

```python
__lines = [decode(__l[2:]) for __l in input().split('0a')[:-1]]
```

Here the `decode` function translates the HEX values for the color codes into
straightforward ASCII characters:

```python
WHITE = '1b5b376d20201b5b306d'
BLACK = '1b5b34316d20201b5b306d'

def decode(data: str) -> str:
    return data.replace(WHITE, '_').replace(BLACK, '#')
```

And finally, these ASCII characters are replaced with "0" and "1":

```python
__qr_data = [[1 if __p == '_' else 0 for __p in __l] for __l in __lines]
```

I didn't replace HEX directly with binary because conflicts may arise between
HEX "0" and binary "0" when replacing.

### Translating the QR code

The array of binary data is not directly exploitable, the standard for QR codes
is actually a little involved...

So the data is first exported in an image:

```python
__qr_image = Image.new('1', (51, 51))
__qr_image.putdata(list(chain(*__qr_data)))
__qr_image = __qr_image.resize((256,256)) # to improve recognition
__qr_image.save('qrcode.png')
```

And then read by a specialized tool:

```shell
zbarimg -q qrcode.png
```

## Evaluating the challenge

In the end, the QR codes contain simple arithmetic operations like:

```
60.38225375139366 x 413.08018551883515 / 233.93430618643774 =
```

It can be processed with the dreaded `eval`:

```python
# get rid of the "=" sign at the end and "QR-Code:"
print(eval(input().replace('x', '*')[8:].split("=")[0]), end="")
```

Without sanitization ofc, what could go wrong with a simple QR code??

The whole process is then:

```shell
sed -n '14,64p' buffer.txt |
    xxd -p -c 65536 |
    python sources/decode.py && zbarimg -q qrcode.png |
        python -c 'print(eval(input().replace("x", "*")[8:].split("=")[0]), end="")' |
        xclip -selection primary
```

Anyway it's done:

> ``HTB{@lriGh7_1_tH1nK_y0u`r3_QuickR_s0ldi3r}``

[author-profile]: https://app.hackthebox.com/users/19832
[ascii-qrcode]: images/qrcode.png
