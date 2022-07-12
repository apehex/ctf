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
__qr_data = [[1 if __p == '_' else 0 for __p in __l] for __l in __lines]

# store as an image
__qr_image = Image.new('1', (51, 51))
__qr_image.putdata(list(chain(*__qr_data)))
__qr_image = __qr_image.resize((256,256))
__qr_image.save('qrcode.png')
