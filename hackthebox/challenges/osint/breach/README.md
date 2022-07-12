> You managed to pull some interesting files off one of Super Secure Startup's
> anonymous FTP servers. Via some OSINT work(a torrent or online Password breach
> site) you have also procured a recent data breach dump.
> Can you unlock the file and retrieve the key?

> Author: **[greenwolf][author-profile]**

## Bruteforcing

Apart from the locked document, we're given a user dataset and a job description.

Let's try the obvious and bruteforce the document with the given credentials.

First, we create the wordlist:

```bash
perl -ne 'm#"(.*)"#g && print $1."\n"' public-data-breach.txt > wordlist
```

Then extract the hash from the Office document:

```bash
python2.7 office2hashcat.py challenge/key.docx > key.hash
```

And run hashcat:

```bash
hashcat -m 9600 -a 0 -r best64.rule key.hash wordlist
```

```
Session..........: hashcat
Status...........: Running
Hash.Name........: MS Office 2013
Hash.Target......: $office$*2013*100000*256*16*864066dedfdf18dde04bf2c...b83ade
Time.Started.....: Wed Aug 25 22:08:30 2021 (1 min, 24 secs)
Time.Estimated...: Wed Aug 25 22:18:31 2021 (8 mins, 37 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (wordlist)
Guess.Mod........: Rules (best64.rule)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:     2566 H/s (8.22ms) @ Accel:2 Loops:128 Thr:1024 Vec:1
Recovered........: 0/1 (0.00%) Digests
Progress.........: 212992/1540000 (13.83%)
Rejected.........: 0/212992 (0.00%)
Restore.Point....: 0/20000 (0.00%)
Restore.Sub.#1...: Salt:0 Amplifier:13-14 Iteration:25344-25472
Candidate.Engine.: Device Generator
Candidates.#1....: bzonlyone9 -> dazaabc1239
Hardware.Mon.#1..: Temp: 80c Fan: 63% Util:100% Core:1290MHz Mem:3004MHz Bus:16
```

Fails.

## OSINT

While the bruteforce attempt is running, let's do some actual

The document must have been locked by an employee: let's look them up.

"Super Secure Startup" brings up a few Twitter accounts on Google.
Bianca Phelps is a HR employee and appears in the breach data:

```
17620,Bianka,Phelps,b.phelps@supersecurestartup.com,Female,126.204.123.232,"Love!July2018"
```

So we can find all the employees:

```bash
# 267,Johanna,Boyce,j.boyce@supersecurestartup.com,Female,225.10.71.76,"t434839865"
# 5502,Ishaaq,Boone,i.boone@supersecurestartup.com,Female,9.69.124.206,"shibby0"
# 9673,Lidia,Kaur,l.kaur@supersecurestartup.com,Female,81.107.254.205,"dama-051288."
# 13686,Kalvin,Tyler,k.tyler@supersecurestartup.com,Male,119.245.151.100,"mybebosyt"
# 17620,Bianka,Phelps,b.phelps@supersecurestartup.com,Female,126.204.123.232,"Love!July2018"
# 19955,Pedro,Smith,p.smith@supersecurestartup.com,Male,62.130.245.163,"shloffle"
grep -ia 'supersecurestartup' public-data-breach.txt
```

The key is sure to hidden here, since the document comes from the startup. But
all these passwords failed already, even with the alteration rules from hashcat.

All the employees created their accounts in march 2019, and the password of Bianka
is a date. So may-be this is a strong hint to try "Love!March2019":

> SFRCe1A0c3N3MHJkX0JyM2FjaDNzX0M0bl9CM19BX1RyM2FzdXIzX1Ryb3YzXzBmX0luZjBybWF0aTBufQ==

You know what to do!

[author-profile]: https://app.hackthebox.eu/users/110957
