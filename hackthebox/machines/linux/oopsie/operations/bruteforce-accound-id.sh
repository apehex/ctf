#!bin/bash

# display only ok (200) responses
ffuf -request requests/accounts-id.txt \
  -mc 200 -mr "<td>\d+</td>" -c -v -w ids.forged
