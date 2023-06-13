// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract Taken is ERC20 {
  address public _dex;

  constructor(address dex, string memory name, string memory symbol, uint supply) ERC20(name, symbol) {
    _dex = dex;
    _mint(msg.sender, supply);
    _mint(dex, supply);
  }

  function approve(address owner, address spender, uint256 amount) public {
    super._approve(owner, spender, amount);
  }
}
