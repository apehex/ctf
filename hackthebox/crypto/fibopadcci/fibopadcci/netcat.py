# -*- coding: utf-8 -*-

import re
import socket
from enum import auto, Flag
from select import select

from attack import Oracle

""" Python 'netcat like' module """

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

class ServerResponse(Flag):
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

def parse_server_response(data: str) -> ServerResponse:
    __response = ServerResponse.NONE

    if OUTPUT_WLC_REGEX.search(data):
        __response |= ServerResponse.OUTPUT_WLC

    if OUTPUT_MENU_REGEX.search(data):
        __response |= ServerResponse.OUTPUT_MENU

    if OUTPUT_CT_REGEX.search(data):
        __response |= ServerResponse.OUTPUT_CT

    if OUTPUT_A_REGEX.search(data):
        __response |= ServerResponse.OUTPUT_A

    if OUTPUT_B_REGEX.search(data):
        __response |= ServerResponse.OUTPUT_B

    if PROMPT_CHOICE_REGEX.search(data):
        __response |= ServerResponse.PROMPT_CHOICE

    if PROMPT_CT_REGEX.search(data):
        __response |= ServerResponse.PROMPT_CT

    if PROMPT_B_REGEX.search(data):
        __response |= ServerResponse.PROMPT_B

    if SUCCESS_REGEX.search(data):
        __response |= ServerResponse.SUCCESS

    if ERROR_LENGTH_REGEX.search(data):
        __response |= ServerResponse.ERROR_LENGTH

    if ERROR_PADDING_REGEX.search(data):
        __response |= ServerResponse.ERROR_PADDING

    if ERROR_HEX_REGEX.search(data):
        __response |= ServerResponse.ERROR_HEX

    if ERROR_CHOICE_REGEX.search(data):
        __response |= ServerResponse.ERROR_CHOICE

    return __response

# ======================================================================= react

class ClientResponse(Flag):
    NONE          = 0

    RESET         = auto()
    RETURN        = auto()

    EXTRACT_DATA  = auto()

    CHOOSE_OPTION = auto()

    OUTPUT_CT     = auto()
    OUTPUT_B      = auto()

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

def reply(server):
    __client = ClientResponse.NONE

    if (
            (server & ServerResponse.ERROR_HEX)
            or (server & ServerResponse.ERROR_CHOICE)
            or (server & ServerResponse.ERROR_LENGTH)
            or (server & ServerResponse.ERROR_PADDING)):
        __client = ClientResponse.RESET

    if (server & ServerResponse.SUCCESS):
        __client = ClientResponse.RETURN

    if (server & ServerResponse.OUTPUT_CT) and (server & ServerResponse.OUTPUT_A) and (server & ServerResponse.OUTPUT_B):
        __client = ClientResponse.EXTRACT_DATA

    if (server & ServerResponse.PROMPT_CHOICE):
        __client = ClientResponse.CHOOSE_OPTION

    if (server & ServerResponse.PROMPT_CT):
        __client = ClientResponse.OUTPUT_CT

    if (server & ServerResponse.PROMPT_B):
        __client = ClientResponse.OUTPUT_B

    return __client

# ===================================================================== logging

LOGGING_FORMAT = '''================================================
infds:\t{}
outfds:\t{}
server:\t{}
client:\t{}
input:\t{}
\n\n'''

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
        __server = ServerResponse.NONE
        __client = ClientResponse.NONE
        __oracle = Oracle()

        __data = b''

        i = 0

        while (not (__server & ServerResponse.SUCCESS)) and (i < 10):
            __infds, __outfds, __errfds = select(self._io, self._io, self._io, 4)

            print(LOGGING_FORMAT.format(
                str(__infds),
                str(__outfds),
                __server,
                __client,
                __data))

            if __infds:
                __data = self.read(1024)
                __server = parse_server_response(str(__data))
                __client = reply(__server)

            if __outfds:
                if __client & ClientResponse.RESET:
                    __oracle.reset()
                    i += 1

                if __client & ClientResponse.EXTRACT_DATA:
                    __oracle.set_parameters(extract_hex_values(__data))

                if __client & ClientResponse.CHOOSE_OPTION:
                    if __oracle.is_ready():
                        self.write(b'1\n')
                    else:
                        self.write(b'0\n')

                if __client & ClientResponse.OUTPUT_CT:
                    self.write(__oracle.alter_ciphertext()[2] + b'\n')

                if __client & ClientResponse.OUTPUT_B:
                    self.write(__oracle.alter_ciphertext()[1] + b'\n')

        return __oracle

#TODO log
#TODO reset state: actually the response str
