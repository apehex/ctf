#!/bin/bash

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
