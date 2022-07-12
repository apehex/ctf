#/usr/bin/env python

############################################################### known plaintext

KNOWN = {
    'prefix': {
        'offset': 0, # Secret: 
        'plaintext': 'Secret: HTB{'.encode('utf-8').hex(':').upper().split(':')},
    'suffix': {
        'offset': 34, # ________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
        'plaintext': '\n<?xml version="1.0" '.encode('utf-8').hex(':').upper().split(':')}}

##################################################################### formating

_format = '-x {offset} {byte}'.format

def cli_args(plaintext, offset):
    return ' '.join([
        _format(
            offset=__i+offset,      # the offset is a decimal number
            byte=plaintext[__i])    # contrary to the data
        for __i in range(len(plaintext))])

######################################################################## output

print(cli_args(KNOWN['prefix']['plaintext'], KNOWN['prefix']['offset']))
