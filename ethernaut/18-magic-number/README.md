## EVM bytecode

The EVM executes contract operations defined in a low level programming language and encoded as bytecode.

Like assembly, this language has opcodes like `0X60` / `PUSH1`.

In Remix the compilation of the contract:

```solidity
contract A {
  fallback() external {}
}
```

Will result in the following bytecode:

```
6080604052348015600f57600080fd5b50604780601d6000396000f3fe6080604052348015600f57600080fd5b00fea26469706673582212209a1b046473621921ba8454b43594616500102874a38fbb85f06fc07bdf81231064736f6c63430008120033
```

Which is in terms of opcodes:

```
[1] PUSH1 0x80
[3] PUSH1 0x40
[4] MSTORE
[5] CALLVALUE
[6] DUP1
[7] ISZERO
[9] PUSH1 0x0f
[10] JUMPI
[12] PUSH1 0x00
[13] DUP1
[14] REVERT
[15] JUMPDEST
[16] POP
[18] PUSH1 0x47
[19] DUP1
[21] PUSH1 0x1d
[23] PUSH1 0x00
[24] CODECOPY
[26] PUSH1 0x00
[27] RETURN
[28] 'fe'(Unknown Opcode)
[30] PUSH1 0x80
[32] PUSH1 0x40
[33] MSTORE
[34] CALLVALUE
[35] DUP1
[36] ISZERO
[38] PUSH1 0x0f
[39] JUMPI
[41] PUSH1 0x00
[42] DUP1
[43] REVERT
[44] JUMPDEST
[45] STOP
[46] 'fe'(Unknown Opcode)
[47] LOG2
[53] PUSH5 0x6970667358
[54] '22'(Unknown Opcode)
[55] SLT
[56] SHA3
[57] SWAP11
[58] SHL
[59] DIV
[65] PUSH5 0x73621921ba
[66] DUP5
[67] SLOAD
[68] 'b4'(Unknown Opcode)
[69] CALLDATALOAD
[70] SWAP5
[73] PUSH2 0x6500
[74] LT
[75] '28'(Unknown Opcode)
[97] PUSH21 0xa38fbb85f06fc07bdf81231064736f6c6343000812
[98] STOP
[99] CALLER
```

Way above the 10 opcodes aim of the challenge...

## Code golfing the runtime bytecode

So, 42 is `0x2a` in hex, which is what we want to return.
It will be stored in a `uint` variable, whih is a 32 bytes memory slot.

This is easily done by following the [tutorial from e18r][evm-bytecode-programming]:

OPCODE | Explanation
-------|-------------
`602a` | Push the value `0x2a` / 42 on the stack
`6000` | Push the position 0 on the stack
`52`   | Store 42 in memory at position 0
`6020` | Push the length 32 (in byte count) on the stack
`6000` | Push the position 0 on the stack
`f3`   | Return the 1 byte located at memory position 0

In total, exactly 10 bytes:

> `602a60005260206000f3`

## Deployment bytecode

The previous code is the runtime section of a contract.

To deploy a contract, the EVM executes its constructor and stores the result on the blockchain.

So the goal is now to build a program that will return the previous bytecode.

It is very similar to the previous code:
store 10 bytes in memory after the constructor code and then return it.

OPCODE | Explanation
-------|-------------
`600a` | Push the length 10 on the stack
`600c` | Push the position 12 on the stack (first position after the constructor code)
`6000` | Push the destination 0 on the stack
`39`   | Copy the 10 bytes at position 12 to the destination 0
`600a` | Push the length 10 on the stack
`6000` | Push the position 0 on the stack
`f3`   | Return the 10 bytes located at memory position 0

Finally, the bytecode of the contract is the concatenation of the two sections:

```js
payload = '600a600c600039600a6000f3'+'602a60005260206000f3'
```

A transaction without destination is interpreted as a contract creation:

```js
txn = await web3.eth.sendTransaction({from: player, data: payload})
await contract.setSolver(txn.contractAddress)
```

[evm-bytecode-programming]: https://hackmd.io/@e18r/r1yM3rCCd
