# MarketDump

> **We have got informed that a hacker managed to get into our internal network**
> **after pivoiting through the web platform that runs in public internet. He**
> **managed to bypass our small product stocks logging platform and then he got our**
> **costumer database file. We believe that only one of our costumers was targeted.**
> **Can you find out who the customer was?**

## The dump

### Protocol breakdown

- ARP:
  - 16 ARP packets
- DATA:
  - 61 packets
  - reverse shell over TCP
- DNS:
  - 6 packets over UDP & 5 over TCP
  - domains: acid
- HTTP:
  - 36 packets
  - pages / requests:
    - / => 
    - /sdk => 
    - /about =>
    - **/costumers.sql => most of the traffic volume**
- ICMP:
  - 14 packets
- IPP:
  - 1 malformed packed
- TCP:
  - 2828 packets in total
  - 2000 packets or more
- MySQL:
  - 2 packets
  - standard greeting
- NTP:
  - 4 packets
- PGSQL:
  - 2 packets
  - error
- SSH:
  - 1 packet
- TELNET:
  - 46 packets
  - login attempts
  - dashboard with stock reports
  - exploit

### Endpoints

- 10.0.2.3 is the client server
- 10.0.2.15 is the attacker
- 129.70.132.36 is an NTP time server

## The attack scenario

- the attacker connected on the ethernet network
- SYN scan of roughly a 1000 ports (1010 RST packets)
- login attempts via TELNET
- exploit the TELNET dashboard callback: `Type exit to exit the program: nc.traditional -lvp 9999 -e /bin/bash`
- launch a reverse shell to the port 9999
- copy the customers database over /tmp
- start a python server on port 9998, from the /tmp directory
- GET the data over HTTP
- rm the database from the server

## The stolen data

Scrolling down, we notice one record doesn't follow the format:

```
American Express,378467610293297
American Express,NVCijF7n6peM7a7yLYPZrPgHmWUHi97LCAzXxSEUraKme
American Express,341025508735219
```

Here I thought "this is clearly base64", and it turns out it's base58!

Turns out base58 is designed for readability, and removes:
- ambiguous characters like O, 0, I and l
- special characters altogether
