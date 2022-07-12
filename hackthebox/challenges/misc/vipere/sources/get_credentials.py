# leaked properties of "get_credentials"
ARGCOUNT = 1
POSONLYARGCOUNT = 0
KWONLYARGCOUNT = 0
NLOCALS = 10
STACKSIZE = 6
FLAGS = 67
BYTECODE = b'd\x01}\x01d\x02}\x02d\x03d\x00d\x00d\x04\x85\x03\x19\x00}\x03d\x05d\x00d\x00d\x04\x85\x03\x19\x00}\x04d\x06}\x05d\x07}\x06d\x08}\x07t\x00|\x01\x83\x01|\x03\x17\x00t\x00d\t\x83\x01\x17\x00|\x04\x17\x00|\x07\x17\x00|\x02\xa0\x01d\nd\x0b\xa1\x02\x17\x00|\x06d\x00d\x00d\x04\x85\x03\x19\x00\x17\x00d\x0c\x17\x00t\x00|\x05\x83\x01d\r\x14\x00\x17\x00t\x00d\x0e\x83\x01\x17\x00}\x01d\x0fd\x10d\x11d\x12\x9c\x03}\x08|\x08D\x00]\x14}\t|\x01\xa0\x01|\t|\x08|\t\x19\x00\xa1\x02}\x01q\x8e|\x01S\x00'
CONSTS = (None, 72, 'apts_c', 'BT', -1, 'orc', 109, 'ocoh', 'iss', 123, 'p', 'n', '_h', 4, 125, '0', '1', '4', ('o', 'l', 'a'))
NAMES = ('chr', 'replace')
VARNAMES = ('self', 'f', 'a', 'blue', 'c', 'm', 'h', 'i', 'd', 'x')
FILENAME = '/home/ctf/database.py'
NAME = 'get_credentials'
FIRSTLINENO = 22
LNOTAB = b'\x00\x01\x04\x01\x04\x01\x0e\x01\x0e\x01\x04\x01\x04\x01\x04\x01N\x01\x0c\x01\x08\x01\x12\x01'
CELLVARS = ()
FREEVARS = ()

# builder
function_type = type(lambda: None)
code_type = type((lambda: None).__code__)

code_obj = code_type(ARGCOUNT, POSONLYARGCOUNT, KWONLYARGCOUNT, NLOCALS, STACKSIZE, FLAGS, BYTECODE, CONSTS, NAMES, VARNAMES, FILENAME, NAME, FIRSTLINENO, LNOTAB, cellvars=CELLVARS, freevars=FREEVARS)
function_obj = function_type(code_obj, {'__builtins__': __builtins__}, None, None, None)

# class
class SecureDatabase():

    def __init__(self):
        pass

SecureDatabase.get_credentials = function_obj

print(SecureDatabase().get_credentials())
