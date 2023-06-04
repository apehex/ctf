## Gate one

The first gate requires to call from a contract:

```solidity
require(msg.sender != tx.origin);
```

## Gate two

The second gate requires a specific amount of gas:

```solidity
require(gasleft() % 8191 == 0);
```

This could be worked out in debug mode on Remix for example, by logging the remaining gas at this point.
But this is tedious; instead it can be bruteforced:

```solidity
for (uint i=0; i<8191; i++) {
  try Gate(TARGET).enter{gas:81910+i}(key) {
    console.log(i);
    break;
  } catch {}
}
```

I implemented this loop in a second contract to make sure this extra logic wasn't consuming gas.
In the end it returns:

> `256`

## Gate three

Casting to a smaller uint removes the bytes on the right.

So the first check means that the bits 16 to 31 are zeroes:

```solidity
require(uint32(uint64(_gateKey)) == uint16(uint64(_gateKey)))
```

IE the key follows the template `0x????????0000????`.

Then the first half cannot be all zeroes:

```solidity
require(uint32(uint64(_gateKey)) != uint64(_gateKey))
```

And finally:

```solidity
require(uint32(uint64(_gateKey)) == uint16(uint160(tx.origin)))
```

Means that the first 2 bytes of the key are the same as the player's address:
in my case, `0xAAD026992b0065D4A9c7019B082cb748D042411F`.

So the key is now like `0x????????0000411F`, for example `0xFFFFFFFF0000411F`.

The key can also be computed at runtime with:

```solidity
uint64 key = uint64(1 << 62) + uint64(uint16(uint160(tx.origin)));
```
