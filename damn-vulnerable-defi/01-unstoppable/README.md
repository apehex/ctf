> There’s a tokenized vault with a million DVT tokens deposited.
> It’s offering flash loans for free, until the grace period ends.

> To pass the challenge, make the vault stop offering flash loans.

> You start with 10 DVT tokens in balance.

## Finding the quirk

The `UnstoppableVault` has a cryptic check in `totalAssets`:

```solidity
if eq(sload(0), 2)
```

This checks the first storage slot against `2`.

Since the vault inherits from `IERC3156FlashLender, ReentrancyGuard, Owned, ERC4626`, the first storage slot comes from `ReentrancyGuard`:

```solidity
abstract contract ReentrancyGuard {                                              
    uint256 private locked = 1;                                                  
                                                                                 
    modifier nonReentrant() virtual {                                            
        require(locked == 1, "REENTRANCY");                                      
                                                                                 
        locked = 2;                                                              
                                                                                 
        _;                                                                       
                                                                                 
        locked = 1;                                                              
    }                                                                            
}
```

IE, the view checks whether the contract is locked.

This and the "unstoppable" name made me think of re-entrancy / infinite loop DOS.
But there's actually a more subtle issue:

```solidity
if (convertToShares(totalSupply) != balanceBefore) revert InvalidBalance();
```

The shares are roughly computed on `deposit` and `withdraw` operations on the vault.
It doesn't account for direct transfers of the underlying token.

These direct transfers wouldn't give shares and are a lost for anyone making them.
Still they are possible and will actually break the protocol!

```js
await token.connect(player).transfer(vault.address, 1);
```
