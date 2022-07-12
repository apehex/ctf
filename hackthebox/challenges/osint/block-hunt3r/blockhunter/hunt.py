# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

# =================================================================== constants

# a manual search on Etherscan gave an approximate block range:
# block #3134000 dates back to 2020-07-29
# block #3151400 dates back to 2020-08-02
FIRST = 3150846

# =================================================================== wrangling

def filename(block_id, transaction_id):
    _q = block_id // 1000
    _parent = f'{_q * 1000}-{(_q + 1) * 1000}'
    return f'transactions/{_parent}/{block_id}.{transaction_id}.json'

def export(transaction):
    _out = {}
    _out['blockHash'] = transaction['blockHash'].hex()
    _out['blockNumber'] = transaction['blockNumber']
    _out['from'] = transaction['from']
    _out['gas'] = transaction['gas']
    _out['gasPrice'] = transaction['gasPrice']
    _out['hash'] = transaction['hash'].hex()
    _out['input'] = transaction['input']
    _out['nonce'] = transaction['nonce']
    _out['r'] = transaction['r'].hex()
    _out['s'] = transaction['s'].hex()
    _out['to'] = transaction['to']
    _out['type'] = transaction['type']
    _out['v'] = transaction['v']
    _out['value'] = transaction['value']

    return _out

# =========================================================== connect to Infura

with open('_infura.json', 'r') as _f:
    infura = json.load(_f)

w3 = Web3(Web3.HTTPProvider(f'https://goerli.infura.io/v3/{infura["project"]}'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# ======================================================= filter blocks by date

after = datetime.fromisoformat('2020-07-30 00:00:00').timestamp()
before = datetime.fromisoformat('2020-08-02 00:00:00').timestamp()
timestamp = datetime.now().timestamp()
number = FIRST

while timestamp >= after:
    # ================================================================ progress
    print(f'{FIRST - number} blocks #{number}...', end='\r')

    # ==================================================== query the blockchain
    block = w3.eth.get_block(number)
    timestamp = block["timestamp"]

    if timestamp <= before:
        for _tid in block["transactions"]:
            _t = w3.eth.get_transaction(_tid.hex())

            # ========================================================== export
            with open(filename(number, _tid.hex()), "w") as _f:
                json.dump(export(_t), _f, indent=4)

    # ==================================================================== next
    number -= 1
