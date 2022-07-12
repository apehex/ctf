# Signals

> **Some amateur radio hackers captured a strange signal from space.**
> **A first analysis indicates similarities with signals transmitted by the ISS.**
> **Can you decode the signal and get the information?**

> Author: **[brigante][author-profile-link]**

## Listening to the audio

To the ear the signal sounds more or like strident Morse code. It actually
follows the same encoding as some ISS transmissions.

The ISS sends images to the earth over analog radio, line by line.

## Decoding the audio

On linux, there's a full featured package for sstv, Qsstv, but it doesn't
read its input from file.

To trick it to analyse our wav file, we'll redirect the audio output
from a common player to the input of Qsstv.

The process is detailed in an [article by m0nkc][qsstv-null-sink-article].

Using Pulseaudio:

```bash
pacmd load-module module-null-sink sink_name=sstv-sink
```

Then Qsstv can be set to record from the virtual sink from the Pulseaudio
control panel, or `pavucontrol`:

![][pulseaudio-record-from-null-sink]

(make sure qsstv is configured with Pulseaudio, and not Alsa, in the options panel)

The only thing left is to play the audio:

```bash
paplay -d sstv-sink ~/workspace/ctf/hackthebox/hardware/signals/Signal.wav
```

And we see the flag, coming at us from the moon:

![][qsstv-decoding-screenshot]

## Bonus: the slow scan TV

The image is transmitted line by line, pixel by pixel, in a radio signal.

The pixel levels are encoded with FM: 1500 Hz is for white and 2300 Hz for black,
with the intensity linearily scaling.

The 1200 Hz acts as a delimiter, like CRLF: the intervals of 5 ms at 1200 Hz


There are several flavors of this protocol

Robot : développé avec la gamme d’interfaces SSTV Robot (Californie)
Wraase : développé avec la gamme d’interfaces Wraase (Allemagne)
Martin : développé par l’Anglais Martin Emmerson G3OQD
Scottie : développé par l’Écossais Eddie Murphy GM3BSC
AVT : développé par Ben Blish-Williams AA7AS avec la gamme d’interfaces SSTV AVT (Montana)

[author-profile-link]: https://app.hackthebox.eu/users/19281
[pulseaudio-record-from-null-sink]: images/pulseaudio_record-from-the-sink.png
[qsstv-decoding-screenshot]: images/qsstv_decoding.png
[qsstv-null-sink-article]: https://www.chonky.net/hamradio/decoding-sstv-from-a-file-on-a-linux-system
