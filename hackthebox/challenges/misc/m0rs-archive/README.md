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

Since the naming convention suggest there are close to a thousand iterations,
the process needs to be automated.

The key step is to convert an image to a password:

1. infer the password length from the image size
2. iterate on the digits of the password:
    1. get the pixel data for the ith digit
    2. translate the pixel data to morse
    3. decode the morse into a digit

### Extrating data from the image

The data for a digit of the password is a line of the image:

```python
def digit_data(image: Image.Image, index: int) -> List:
    __width = image.size[0]
    return list(image.getdata())[index*__width:(index+1)*__width]
```

### Decoding the data

The pixel data is encoded as RGB, a tuple of 3 integers. But the image has only
2 colors, one for the white / spacing and another for the 

So a pixel line can be translated to a binary string:

```python
def rgb_to_binary(data: List) -> str:
    # the second pixel is always black
    return ''.join([str(int(__d == data[1])) for __d in data])
```

Only the "1" have meaning for the encoding, the "0" are only spacing that
separate the Morse letters: the letters can be listed thanks to `str.split`.

Then, the number of successive "1" differentiate the morse symbols:

```python
MORSE = {
    '1': '.',
    '111': '-'}

def binary_to_morse(line: str) -> str:
    return ''.join(map(
        lambda x: MORSE.get(x, ''),
        line.split('0')))
```

And finally from Morse to alphanumeric:

```python
def morse_to_alpha(morse: str) -> str:
    return ALPHABET.get(morse, '')
```

### Iterating on the digits

The image has data on every odd line:

```python
for __i in range(1, image.size[1], 2):
    __data = digit_data(image, __i)
    __digit = morse_to_alpha(binary_to_morse(rgb_to_binary(__data)))
    __password += __digit
```

## Extracting a single archive

Thanks to the module `argparse`, we can use the script from the CLI:

```shell
PASSWORD=$(python decode.py "pwd.png")
rm pwd.png
unzip -P "$PASSWORD" -d . ./flag_*.zip 
```

## Automating the process

Prepare a working environment:

```shell
TMP=$(mktemp -d)
unzip -d "${TMP}" M0rsarchive.zip
```

And finally, iterate:

```shell
for i in {999..0}; do
    PASSWORD=$(python decode.py "${TMP}/pwd.png")
    unzip -P "${PASSWORD}" -d "${TMP}" "${TMP}/flag_"*.zip
    rm "${TMP}/pwd.png" "${TMP}/flag_"*.zip
    mv "${TMP}/flag/"* "${TMP}"
    rm -rf "${TMP}/flag/"
done
```

> `HTB{D0_y0u_L1k3_m0r53??}`

[author-profile]: https://app.hackthebox.com/users/22280
[morse-password]: images/morse-password.png
