# USB Ripper

> **There is a sysadmin, who has been dumping all the USB events on his Linux**
> **host all the year... Recently, some bad guys managed to steal some data from**
> **his machine when they broke into the office. Can you help him to put a tail on**
> **the intruders? Note: once you find it, "crack" it.**

## Browsing & Interpretation

### Device properties

```
cat syslog | perl -ne 'm/Product:\s+(.+)$/g && print $1."\n"' > products
cat syslog | perl -ne 'm/Manufacturer:\s+(.+)$/g && print $1."\n"' > manufacturers
cat syslog | perl -ne 'm/SerialNumber:\s+(.+)$/g && print $1."\n"' > serial-numbers
```

Do all connect devices appear in auth.json?

`syslog` contains 100000 device connections, and each of the files `products`,
`manufacturers` and `serial-numbers` contain 100000 lines.

So we expect all the ids from these 3 files to have a match in `auth.json`.

```
grep -Ff auth.json products | wc -l
grep -Ff auth.json manufacturers | wc -l
grep -Ff auth.json serial-numbers | wc -l
```

> However serial-numbers has 99999 matches out of 100000.

### Calculating the time span

Assuming the robbers stole a large volume of data, their usb drive must have
stayed plugged-in for a few minutes at least.

Browsing the logs, we see that devices typically stay connected for a few
seconds only.

```
cat syslog | grep -B 1 -ia 'disconnect' > disconnections
```

To calculate the timespans, we extract connection & disconnection datetimes and
format each line as a time calculation, like `1636451817 - 1636451843`.

```
cat disconnections |
  perl -pe 's/^(.+) kali kernel.*$/$1/g' | # extract the datetime
  xargs -I {} date -d {} +%s | # convert the datetimes to timestamps
  perl -pe 's/1619827200/--/g' | # retrieve the separators from the time convertions
  perl -pe 's/(\d+)\n/$1-/g' > timespan-calculations # format: connection - disconnection
```

Then we process the arithmetic and sort:

```
echo '#/bin/bash' > process-timespans.sh
cat timespan-calculations |
  perl -pe 's/(\d+)-(\d+)---/expr $1 - $2/g' >> process-timespans.sh
bash process-timespans.sh |
  awk '{print NR, " ", $0}' |
  sort -n -k 2 > devices-by-time-of-connection
```

Well. There's nothing stands out. (apart from my inefficient scripts...)

All the devices have been connected 60s at most.
Yeah quantity & quality right? They stole the right bits and knew exactly where
to find them, such efficiency!

## Finding the foreign device

Anyway we're back to the first idea: finding unauthorized devices.

```
#!/bin/bash

while read serial; do
  if ! grep -qia "$serial" auth.json; then echo "$serial"; fi
done
```

> 71DF5A33EFFDEA5B1882C9FBDC1240C6

`hash-identifier 71DF5A33EFFDEA5B1882C9FBDC1240C6` tells us it's most likely an
MD5 hash. So we google it:

```
w3m google.com/search?q=71DF5A33EFFDEA5B1882C9FBDC1240C6
```

> HTB{mychemicalromance}
