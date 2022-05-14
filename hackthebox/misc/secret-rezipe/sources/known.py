#/usr/bin/env python

PT = '0A 69 77 69 6C 6C 66 69 6E 64 79 6F 75 69 77 69 6C 6C 65 78 70 6F 73 65 79 6F 75 0A'.split(' ')
OFFSET = 34
OPTION = '-x {offset} {byte}'.format

arguments = ' '.join([OPTION(offset=hex(__i+OFFSET)[2:], byte=PT[__i]) for __i in range(len(PT))])
