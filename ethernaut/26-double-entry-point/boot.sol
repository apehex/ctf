// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IDetectionBot {
    function handleTransaction(address, bytes calldata) external;
}

interface IForta {
    function setDetectionBot(address) external;
    function notify(address, bytes calldata) external;
    function raiseAlert(address) external;
}

contract Boot is IDetectionBot {
    address public _vault;

    constructor (address vault) {
        _vault = vault;
    }

    function handleTransaction(address user, bytes calldata data) external {
        (,,address _origin) = abi.decode(data[4:], (address, uint256, address));
        if (_origin == _vault) {
            IForta(msg.sender).raiseAlert(user);
        }
    }
}
