# Steps

> **We accessed the embedded device's asynchronous serial debugging interface**
> **while it was operational and captured some messages that were being**
> **transmitted over it. Can you decode them?**

## Interpreting the file

Running `file` or `exiftool` tells us the `.sal` is actually a `.zip`.

Extracting it leaves us with:
- digital-0.bin
- meta.json

The header of `digital-0.bin` is:
```
3c53 414c 4541 453e 0100 0000 6400 0000  <SALEAE>....d...
```

Saleae makes USB Logic Analyzers, according to their documentation we are facing
an analog dump.

Also the meta information labels 16 pixel channels

## Reading the data

Actually the `logic` software from Saleae can directly read the `.sal` file.

After trying multiple protocol analysers, interpreting the data stream with
the MIDI analyser display a message from HTB!

## Failed attempts

### Reading the dump data

Directly in Hex.

Using Saleae v2 scripts to extract data from the binary.

Looking at the strings gave no hint.

### Plotting the analog values

Extracting the numeric values from the binary:

```shell_session
sigrok-cli -I raw_analog -i digital-0.bin -O csv -o digital-0.csv
```

It can be displayed with python matplotlib, but looking at the chart gave no clue.

### Interpreting as an audio recording

```shell_session
sigrok-cli -I raw_analog -i digital-0.bin -O wav -o digital-0.wav
```
The output is a few ms long, there's no audible sound.
