# -*- coding: utf-8 -*-

import re
import socket
from enum import auto, Flag
from select import select

from attack import Oracle

""" Python 'netcat like' module """

# ==============================

RESET  = 0
APPEND = 1
SPLIT  = 2

# ============================================================ server responses

SAMPLE = b'encrypted_flag: f74fb219b261a3ae0f6ea8e4b795f84ca478471aed5b44bfc4c04bc787ab7eed59419be0661ba6530136f38bc49d3aca\na: 4f82851a99f3f2f5cf712b222688cc7e\nb: dddee5182e9242a3a9c951a0b2473e75\n\n-------------------------\n| Menu                  |\n-------------------------\n|[0] Encrypt flag.      |\n|[1] Send me a message! |\n-------------------------\n\nYour option: '

OUTPUT_WLC_REGEX    = re.compile(r'welcome to my super secure', re.IGNORECASE)
OUTPUT_MENU_REGEX   = re.compile(r'menu', re.IGNORECASE)

OUTPUT_CT_REGEX     = re.compile(r'encrypted_flag:\s*([a-f0-9]+)\\n', re.IGNORECASE)
OUTPUT_A_REGEX      = re.compile(r'a:\s*([a-f0-9]{32})', re.IGNORECASE)
OUTPUT_B_REGEX      = re.compile(r'b:\s*([a-f0-9]{32})', re.IGNORECASE)

PROMPT_CHOICE_REGEX = re.compile(r'your option', re.IGNORECASE)
PROMPT_CT_REGEX     = re.compile(r'enter your ciphertext', re.IGNORECASE)
PROMPT_B_REGEX      = re.compile(r'enter the B used during encryption', re.IGNORECASE)

SUCCESS_REGEX       = re.compile(r'message successfully sent', re.IGNORECASE)
ERROR_LENGTH_REGEX  = re.compile(r'length', re.IGNORECASE)
ERROR_PADDING_REGEX = re.compile(r'padding incorrect', re.IGNORECASE)
ERROR_HEX_REGEX     = re.compile(r'provided input is not hex', re.IGNORECASE)
ERROR_CHOICE_REGEX  = re.compile(r'please try again', re.IGNORECASE)

class State(Flag):
    NONE                = 0

    OUTPUT_WLC          = auto()
    OUTPUT_MENU         = auto()
    
    OUTPUT_CT           = auto()
    OUTPUT_A            = auto()
    OUTPUT_B            = auto()

    PROMPT_CHOICE       = auto()
    PROMPT_CT           = auto()
    PROMPT_B            = auto()

    SUCCESS             = auto()
    ERROR_LENGTH        = auto()
    ERROR_PADDING       = auto()
    ERROR_HEX           = auto()
    ERROR_CHOICE        = auto()

def parse_socket_state(response: str) -> State:
    __state = State.NONE

    if OUTPUT_WLC_REGEX.search(response):
        __state |= State.OUTPUT_WLC

    if OUTPUT_MENU_REGEX.search(response):
        __state |= State.OUTPUT_MENU

    if OUTPUT_CT_REGEX.search(response):
        __state |= State.OUTPUT_CT

    if OUTPUT_A_REGEX.search(response):
        __state |= State.OUTPUT_A

    if OUTPUT_B_REGEX.search(response):
        __state |= State.OUTPUT_B

    if PROMPT_CHOICE_REGEX.search(response):
        __state |= State.PROMPT_CHOICE

    if PROMPT_CT_REGEX.search(response):
        __state |= State.PROMPT_CT

    if PROMPT_B_REGEX.search(response):
        __state |= State.PROMPT_B

    if SUCCESS_REGEX.search(response):
        __state |= State.SUCCESS

    if ERROR_LENGTH_REGEX.search(response):
        __state |= State.ERROR_LENGTH

    if ERROR_PADDING_REGEX.search(response):
        __state |= State.ERROR_PADDING

    if ERROR_HEX_REGEX.search(response):
        __state |= State.ERROR_HEX

    if ERROR_CHOICE_REGEX.search(response):
        __state |= State.ERROR_CHOICE

    return __state

# ======================================================================= react

def extract_hex_values(data: bytes):
    __a_match = OUTPUT_A_REGEX.search(str(data))
    __b_match = OUTPUT_B_REGEX.search(str(data))
    __ct_match = OUTPUT_CT_REGEX.search(str(data))

    if __ct_match and __a_match and __b_match:
        return (
            bytes.fromhex(__a_match.group(1)),
            bytes.fromhex(__b_match.group(1)),
            bytes.fromhex(__ct_match.group(1)))
    else:
        return ()

# ========================================================================= tcp

HOST = "127.0.0.1"
PORT = 1337
MAX_TRIES = 1024 # on average 256 tries are enough

class Netcat:

    def __init__(self, ip: str, port: int):

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(2)
        self._socket.connect((ip, port))
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 4)
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 8)
        self._io = [self._socket]

    def read(self, length: int=1024):

        """ Read 1024 bytes off the socket """

        return self._socket.recv(length)
 
    def write(self, data: bytes) -> int:

        """ Send data """

        return self._socket.send(data)
    
    def close(self) -> None:

        """ Terminate the TCP stream """

        return self._socket.close()

    def talk(self):
        __state = State.NONE
        __oracle = Oracle()

        __response = b''

        i = 0

        while (not (__state & State.SUCCESS)) and (i < 10):
            __infds, __outfds, __errfds = select(self._io, self._io, self._io, 4)

            if __infds:
                __response = self.read(1024)
                __state = parse_socket_state(str(__response))

            if __outfds:
                print(__state)
                if (
                        __state & State.ERROR_HEX
                        or __state & State.ERROR_CHOICE
                        or __state & State.ERROR_LENGTH
                        or __state & State.ERROR_PADDING):
                    __oracle.reset()
                    i += 1

                if __state & State.OUTPUT_CT and __state & State.OUTPUT_A and __state & State.OUTPUT_B:
                    __oracle.set_parameters(extract_hex_values(__response))

                if __state & State.PROMPT_CHOICE:
                    if __oracle.is_ready():
                        self.write(b'1\n')
                    else:
                        self.write(b'0\n')

                if __state & State.PROMPT_CT:
                    self.write(__oracle.alter_ciphertext()[1] + b'\n')

                if __state & State.PROMPT_B:
                    self.write(__oracle.alter_ciphertext()[2] + b'\n')

        return __oracle

#TODO log
#TODO remove temp bytes variables
#TODO reset state
