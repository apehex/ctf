The contract overrides `transfer` from its parent:

```solidity
function transfer(address _to, uint256 _value) override public lockTokens returns(bool) {
  super.transfer(_to, _value);
}
```

This new function prevents the user from withdrawing his tokens before 10 years:

```solidity
modifier lockTokens() {
  if (msg.sender == player) {
    require(block.timestamp > timeLock);
    _;
  } else {
   _;
  }
}
```

Still the contract inherits from `ERC20`, which has another similar method, `transferFrom`.

This requires an extra step to approve the transfer, but works the same:

```js
await contract.approve(player, '1000000000000000000000000')
await contract.transferFrom(player, '0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', '1000000000000000000000000')
await contract.balanceOf(player) // 0
```
