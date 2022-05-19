#!/usr/bin/env python

import os
import socketserver
import subprocess
import sys

def ep():
    return 0

args = {'k1': ep, 'k2': 'v2'}

fs = '{k1.__globals__[os]}'

print(fs.format(**args))
