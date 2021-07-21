# Mission pinpossible

> **Our field agent cannot access the enemy base due to the password-protected**
> **internal gates, but observed that the password seemed to be partially**
> **displayed as it was typed into the security keypad. Thanks to an audacious**
> **mission, we were able to implant an embedded device into the wiring for the**
> **keypad's monitor, and intercepted some data. Your mission is to recover the**
> **password from the collected data.**

> Author: **[diogt][diogt-profile-url]**

## Interpreting the dump

The files "\*.logicdata" are logs from the first version of the Logic software
from Saleae. They actually can't be opened from the v2.

From the connection names in the image, we can infer that the recording follows
the [I2C protocol][i2c-wikipedia].

The software has an I2C analysis built-in, it can directly export the data stream!

## Expanding the analog signal

The Logic analyser outputs the byte stream in a csv file:

```csv
Time [s],Packet ID,Address,Data,Read/Write,ACK/NAK
0.448499000000000,0,0x4E,0x08,Write,ACK
0.448728500000000,1,0x4E,0x0C,Write,ACK
0.448958500000000,2,0x4E,0x08,Write,ACK
0.449248000000000,3,0x4E,0x18,Write,ACK
0.449478000000000,4,0x4E,0x1C,Write,ACK
0.449707500000000,5,0x4E,0x18,Write,ACK
```

All the bytes in the stream have been acknowledged (ACK): they were all
actually processed, we don't need to discard anything.

## Decoding the byte stream

Now, we need to decode the values exchanged with the LCD; they are specific to
the setup:

- the monitored IO pins are SDA and SCL
- the LCD is a QAPASS 1602
- there's a chip, the PCF8574T, which performs 8-bit remote I/O expansion

The PCF8574T chip performs the same computation as the I2C analyser:
it transforms an analog signal over time into a stream of numeric bytes.

So the former csv data is the byte stream received by the GPIO pins of the
QAPASS LCD, as output by the PCF8574T.

Let's reformat the data to handle it in Python:

```bash
tail -n8424 lcd-io-data.csv |
    cut -d',' -f4 |
    perl -pe 's#\n#,#g' |
    perl -pe 's#^(.*)$#\[$1\]#g' >> decode.py
```

Looking around for datasheets, I didn't find any reliable / understandable information.

It's easier to read code! [Matthias Hertel][mathertel-profile-url] has already turned all these
awful docs into [a great library][liquid-crystal-repo-url].

In this library the write operation is implemented by several lower level functions:

> write &rarr; \_send &rarr; \_sendNibble &rarr; \_write2Wire

The data is send in pairs: first the upper nibble, then the lower.

The PCF_RS flag is set on the upper, and both PCF_RS & PCF_EN on the lower.

And finally, in each byte packet sent:

- the upper half is the data nibble
- the lower half is the flag nibble, which should have RS | EN

So the process is:

- filter the packets with both RS and EN flags set
- extract the data from the packets
- reconstruct the byte with upper and lower nibbles

```python
nibbles = []
for packet in PACKETS:
    if (packet & PCF_RS) and (packet & PCF_EN):
        nibbles.append(packet)

paired_nibbles = [nibbles[i:i + 2] for i in range(0, len(nibbles), 2)]
lcd_lines = ""
for upper_nibble,lower_nibble in paired_nibbles:
    val = (upper_nibble & 0xF0) | (lower_nibble >> 4)
    lcd_lines += chr(val)
```

Since the controller refreshes the whole line after each input, one character
typed corresponds to a string like "Enter Password**********************************@".
Only the last character of these strings are of interest:

```python
PROMPT_REGEX = r'Enter Password\**'
''.join(re.split(PROMPT_REGEX, lcd_lines)).replace(' ', '')
```

> HTB{84d_d3519n_c4n_134d_70_134k5!d@}

[diogt-profile-url]: https://app.hackthebox.eu/users/1358
[i2c-wikipedia]: https://fr.wikipedia.org/wiki/I2C
[liquid-crystal-repo-url]: https://github.com/mathertel/LiquidCrystal_PCF8574/blob/master/src/LiquidCrystal_PCF8574.cpp
[mathertel-profile-url]: https://github.com/mathertel
