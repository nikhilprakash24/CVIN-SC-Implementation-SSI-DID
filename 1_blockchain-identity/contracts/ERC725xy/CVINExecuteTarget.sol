// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINExecuteTarget
 * @author CVIN research project
 * @notice Test/demo call target for ERC-725X `execute` (records value and caller).
 * @dev Minimal target contract used ONLY by the CVINVehicleERC725XY test suite to
 *      prove that ERC-725X `execute` performs a REAL low-level call with an
 *      observable side effect (state mutation + msg.sender == the account), not a
 *      stub. Not part of any standard being benchmarked.
 *      Also used by benchmarks/scenarios/crud.js and the sandbox erc-725xy adapter
 *      (`execute(CALL, target, setValue)` then a `lastCaller` check).
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 2)
 * @custom:see sandbox/options/erc-725xy/adapter.js
 */
contract CVINExecuteTarget {
    /// @notice Last value written by {setValue}.
    uint256 public value;
    /// @notice `msg.sender` of the last {setValue} call (the ERC-725X account when called via `execute`).
    address public lastCaller;

    /// @notice Emitted by {setValue}.
    /// @param caller The caller.
    /// @param value The value written.
    event ValueSet(address indexed caller, uint256 value);

    /// @notice Stores `newValue` and the caller. Open to anyone. Emits {ValueSet}.
    /// @param newValue The value to store.
    function setValue(uint256 newValue) external {
        value = newValue;
        lastCaller = msg.sender;
        emit ValueSet(msg.sender, newValue);
    }

    /// @notice Always reverts with "CVINExecuteTarget: forced revert" (tests revert bubbling).
    function willRevert() external pure {
        revert("CVINExecuteTarget: forced revert");
    }
}
