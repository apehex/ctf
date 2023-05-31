## Data layout

The layout of the contract's storage is:

```js
// '0x0000000000000000000000000000000000000000000000000000000000000001'
await web3.eth.getStorageAt(contract.address, 0, (err,res)=>{console.log(res)});
// '0x0000000000000000000000000000000000000000000000000000000064772e20'
await web3.eth.getStorageAt(contract.address, 1, (err,res)=>{console.log(res)});
// '0x000000000000000000000000000000000000000000000000000000002e20ff0a'
await web3.eth.getStorageAt(contract.address, 2, (err,res)=>{console.log(res)});
// '0x81a718b13684a6fa11aa9cb4209dd5f8fb95b619c4acf76f134933898b31c48b'
await web3.eth.getStorageAt(contract.address, 3, (err,res)=>{console.log(res)});
// '0x4381e74154631230ba80eb3a08dd7581b3bf0177ec3c17e755bb6e759698e76a'
await web3.eth.getStorageAt(contract.address, 4, (err,res)=>{console.log(res)});
// '0xa5bfe0c0128fbb1c6f4a29625277dc9357b3a3f85c564e39664f598f8b13ec3f'
await web3.eth.getStorageAt(contract.address, 5, (err,res)=>{console.log(res)});
```

Each slot has a length of 32 bytes, with:

- slot 0 contains a single bool:
  - `bool public locked`
  - encoded as `0x0000000000000000000000000000000000000000000000000000000000000001` or `true`
- slot 1 contains a single uint:
  - `uint256 public ID`
  - encoded as `0x0000000000000000000000000000000000000000000000000000000064772e20` or `1685532192`
- slot 2 is the concatenation of:
  - `uint8 private flattening`, equals to `0x0a` or `10`
  - `uint8 private denomination`, equals to `0xff` or `255`
  - `uint16 private awkwardness`, equals to `0x2e20` or `11808`
  - encoded from the right as `0x000000000000000000000000000000000000000000000000000000002e20ff0a`
- slot 3 is `data[0]`:
  - `0x81a718b13684a6fa11aa9cb4209dd5f8fb95b619c4acf76f134933898b31c48b`
- slot 4 is `data[1]`:
  - `0x4381e74154631230ba80eb3a08dd7581b3bf0177ec3c17e755bb6e759698e76a`
- slot 5 is `data[2]`:
  - `0xa5bfe0c0128fbb1c6f4a29625277dc9357b3a3f85c564e39664f598f8b13ec3f`

## Extracting the key

Then `data[2]` is cast to `bytes16`:
this operation keeps the 16 most significant bytes, IE the bytes on the left.

So the key is made of the bytes `0xa5bfe0c0128fbb1c6f4a29625277dc93` from `0xa5bfe0c0128fbb1c6f4a29625277dc9357b3a3f85c564e39664f598f8b13ec3f`.

```js
// true
await contract.locked()
// submit the key
await contract.unlock('0xa5bfe0c0128fbb1c6f4a29625277dc93')
// false
await contract.locked()
```
