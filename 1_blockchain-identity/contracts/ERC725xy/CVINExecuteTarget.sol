// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINExecuteTarget
 * @dev Minimal target contract used ONLY by the CVINVehicleERC725XY test suite to
 *      prove that ERC-725X `execute` performs a REAL low-level call with an
 *      observable side effect (state mutation + msg.sender == the account), not a
 *      stub. Not part of any standard being benchmarked.
 */
contract CVINExecuteTarget {
    uint256 public value;
    address public lastCaller;

    event ValueSet(address indexed caller, uint256 value);

    function setValue(uint256 newValue) external {
        value = newValue;
        lastCaller = msg.sender;
        emit ValueSet(msg.sender, newValue);
    }

    function willRevert() external pure {
        revert("CVINExecuteTarget: forced revert");
    }
}
