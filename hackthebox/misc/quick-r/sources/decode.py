#!/usr/bin/env python

from itertools import chain
from PIL import Image

############################################################ color codes in hex

WHITE = '1b5b376d20201b5b306d'
BLACK = '1b5b34316d20201b5b306d'

######################################################################## decode
def decode(data: str) -> str:
	return data.replace(WHITE, '_').replace(BLACK, '#')

########################################################################### cli

# split the HEX stream into lines
# remove the tabulations at the start of each line
__lines = [decode(__l[2:]) for __l in input().split('0a')[:-1]]

# convert to binary
__data = [[1 if __p == '_' else 0 for __p in __l] for __l in __lines]
# print(list(chain(*__data)))

# store as an image
__qrcode = Image.new('1', (51, 51))
__qrcode.putdata(list(chain(*__data)))
__qrcode.save('qrcode.png')

# decode the qrcode

# perform the calculation

