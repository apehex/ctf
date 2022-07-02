#/usr/bin/env python

############################################################### known plaintext

KNOWN = {
    'prefix': {
        'offset': 0, # Secret: 
        'plaintext': 'Secret: '.encode('utf-8').hex(':').split(':')},
    'suffix': {
        'offset': 34, # ________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        'plaintext': '\n<?xml version="1.0" '.encode('utf-8').hex(':').upper().split(':')}}

###############################################################

_format = '-x {offset} {byte}'.format

def cli_args(plaintext, offset):
    return ' '.join([
        _format(
            offset=hex(__i+offset)[2:],
            byte=plaintext[__i])
        for __i in range(len(plaintext))])

###################

print(cli_args(KNOWN['suffix']['plaintext'], KNOWN['suffix']['offset']))
