#!/usr/bin/env python

from argparse import ArgumentParser
from PIL import Image
from typing import List

######################################################################### morse

ALPHABET = {
    '.----': '1',
    '..---': '2',
    '...--': '3',
    '....-': '4',
    '.....': '5',
    '-....': '6',
    '--...': '7',
    '---..': '8',
    '----.': '9',
    '-----': '0',
    '.-': 'A',
    '-...': 'B',
    '-.-.': 'C',
    '-..': 'D',
    '.': 'E',
    '..-.': 'F',
    '--.': 'G',
    '....': 'H',
    '..': 'I',
    '.---': 'J',
    '-.-': 'K',
    '.-..': 'L',
    '--': 'M',
    '-.': 'N',
    '---': 'O',
    '.--.': 'P',
    '--.-': 'Q',
    '.-.': 'R',
    '...': 'S',
    '-': 'T',
    '..-': 'U',
    '...-': 'V',
    '.--': 'W',
    '-..-': 'X',
    '-.--': 'Y',
    '--..': 'Z',
    '--..--': ',',
    '.-.-.-': '.',
    '..--..': '?',
    '-..-.': '/',
    '-....-': '-',
    '-.--.': '(',
    '-.--.-': ')'}

MORSE = {
    '1': '.',
    '111': '-'}

##################################################################### wrangling

def digit_data(image: Image.Image, index: int) -> List:
    __width = image.size[0]
    return list(image.getdata())[index*__width:(index+1)*__width]

###################################################################### decoding

def rgb_to_binary(data: List) -> str:
    # the second pixel is always black
    return ''.join([str(int(__d == data[1])) for __d in data])

def binary_to_morse(line: str) -> str:
    return ''.join(map(lambda x: MORSE.get(x, ''), line.split('0')))

def morse_to_alpha(morse: str) -> str:
    return ALPHABET.get(morse, '').lower()

########################################################################### cli

def main(image):
    __password = ''

    for __i in range(1, image.size[1], 2):
        __data = digit_data(image, __i)
        __digit = morse_to_alpha(binary_to_morse(rgb_to_binary(__data)))
        __password += __digit

    return __password

if __name__ == '__main__':
    __parser = ArgumentParser(description='Translate an image to a text password')
    __parser.add_argument('path', metavar='path', type=str, help='the path to an image file, containing the encoded password')

    __args = __parser.parse_args()
    with Image.open(__args.path) as __image:
        print(main(__image))
