// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {PackedUserOperation, IAccount} from "./CVINVehicleAccount.sol";

/**
 * @title CVINMinimalEntryPoint
 * @author CVIN research project
 * @notice SIMPLIFIED RESEARCH HARNESS — NOT the canonical ERC-4337 EntryPoint.
 *
 * @dev This contract exists solely to measure the gas overhead of the 4337
 *      indirection (EntryPoint -> validateUserOp -> account call) against
 *      direct EOA-to-contract calls for the thesis gas benchmark. It takes a
 *      SINGLE user operation, calls the account's validateUserOp, then
 *      executes the operation's callData on the account. Deliberately omitted
 *      relative to the canonical v0.7 EntryPoint:
 *
 *      - NO bundler mempool / handleOps batching (single op per call)
 *      - NO paymaster support (paymasterAndData is hashed but ignored)
 *      - NO signature aggregation
 *      - NO gas accounting, deposits, stakes, or refunds
 *        (missingAccountFunds is always passed as 0; the gas-limit fields of
 *        the packed op are hashed for v0.7 hash-compatibility but not enforced)
 *      - NO initCode / counterfactual account deployment (initCode must be empty)
 *      - Nonces are a plain per-sender sequence (no v0.7 key||sequence split)
 *      - The inner call reverts the whole transaction on failure instead of
 *        emitting UserOperationRevertReason (simpler for test assertions)
 *
 *      The userOpHash computation mirrors the v0.7 scheme:
 *      keccak256(abi.encode(hash(packedFields), address(this), block.chainid)).
 * @custom:standard ERC-4337 (simplified; canonical entry point is handleOps) https://eips.ethereum.org/EIPS/eip-4337
 * @custom:security Not a canonical EntryPoint: no gas accounting, deposits or paymasters; anyone may call {handleOp}.
 * @custom:security The nonce is bumped before validation, but any failure reverts the whole transaction, so no nonce is consumed.
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 4b)
 * @custom:see sandbox/options/erc-4337/adapter.js
 */
contract CVINMinimalEntryPoint {
    /// @notice Plain sequential nonce per account (replay protection).
    mapping(address => uint256) public nonces;

    /// @notice Emitted after a user operation executed successfully.
    /// @dev `success` is always true, since failures revert.
    /// @param userOpHash The v0.7-style op hash.
    /// @param sender The account.
    /// @param nonce The consumed nonce.
    /// @param success Inner call result (always true).
    event UserOperationHandled(
        bytes32 indexed userOpHash,
        address indexed sender,
        uint256 nonce,
        bool success
    );

    /**
     * @notice Compute the hash the account owner must sign (v0.7-style).
     * @dev keccak256(abi.encode(packedHash, address(this), block.chainid)); dynamic fields are pre-hashed.
     * @param userOp The packed user operation (signature excluded from the hash).
     * @return The user operation hash.
     */
    function getUserOpHash(
        PackedUserOperation calldata userOp
    ) public view returns (bytes32) {
        bytes32 packedHash = keccak256(
            abi.encode(
                userOp.sender,
                userOp.nonce,
                keccak256(userOp.initCode),
                keccak256(userOp.callData),
                userOp.accountGasLimits,
                userOp.preVerificationGas,
                userOp.gasFees,
                keccak256(userOp.paymasterAndData)
            )
        );
        return keccak256(abi.encode(packedHash, address(this), block.chainid));
    }

    /**
     * @notice Validate and execute a single user operation.
     * @dev 1. checks + bumps the sender nonce,
     *      2. calls the account's validateUserOp (must return 0),
     *      3. calls the account with the operation's callData.
     *      Open to any caller (bundler/EOA). Rejects non-empty initCode. Bubbles up
     *      the account's revert. Emits {UserOperationHandled}. Simplified ERC-4337
     *      (canonical: handleOps).
     * @param userOp The packed user operation.
     */
    function handleOp(PackedUserOperation calldata userOp) external {
        require(userOp.initCode.length == 0, "CVINEntryPoint: initCode unsupported");
        require(userOp.nonce == nonces[userOp.sender], "CVINEntryPoint: invalid nonce");
        nonces[userOp.sender] = userOp.nonce + 1;

        bytes32 userOpHash = getUserOpHash(userOp);

        uint256 validationData = IAccount(userOp.sender).validateUserOp(
            userOp,
            userOpHash,
            0 // no deposit/prefund system in this harness
        );
        require(validationData == 0, "CVINEntryPoint: signature validation failed");

        (bool success, bytes memory ret) = userOp.sender.call(userOp.callData);
        if (!success) {
            // bubble up the account's revert reason
            assembly {
                revert(add(ret, 32), mload(ret))
            }
        }

        emit UserOperationHandled(userOpHash, userOp.sender, userOp.nonce, success);
    }
}
