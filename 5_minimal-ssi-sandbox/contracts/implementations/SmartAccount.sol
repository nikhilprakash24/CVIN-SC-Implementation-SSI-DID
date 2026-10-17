// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title SmartAccount — minimal ERC-4337 (v0.7 layout) account used by option O6.
/// @notice The account IS the DID. Authorisation is the account's own validation logic:
///         `validateUserOp` checks an ECDSA signature over the userOpHash against the owner
///         key or a session key, and returns ERC-4337 `validationData` with the session key's
///         validUntil/validAfter packed in — the standard's native time-bounded delegation.
///         `validateCaller` is the same key set evaluated for a direct caller (no EntryPoint).
/// @dev Written fresh: the PackedUserOperation struct is the v0.7 layout; no EntryPoint is
///      deployed in the sandbox (the registry plays the entry-point role for the direct path;
///      scenario S1/S7 use the direct path, test/o6_native.js exercises validateUserOp with a
///      real signed op). Validation keys ≈ ERC-7579 validators reduced to an address set.
contract SmartAccount {
    struct PackedUserOperation {
        address sender; uint256 nonce; bytes initCode; bytes callData; bytes32 accountGasLimits;
        uint256 preVerificationGas; bytes32 gasFees; bytes paymasterAndData; bytes signature;
    }
    struct SessionKey { uint48 validAfter; uint48 validUntil; bool exists; }

    event ValidationKeyAdded(address indexed key);
    event ValidationKeyRemoved(address indexed key);
    event SessionKeySet(address indexed key, uint48 validAfter, uint48 validUntil);
    event Executed(address indexed target, uint256 value, bytes4 selector);

    error NotAuthorized();

    address public immutable manager;
    address public owner;
    mapping(address => bool) public isValidationKey;  // owner-class keys (full authority)
    mapping(address => SessionKey) public sessionKeys; // time-bounded keys
    uint256 public validationKeyCount;
    mapping(bytes32 => bytes) private _store;

    uint256 private constant SIG_VALIDATION_FAILED = 1;

    constructor(address owner_, address manager_) {
        owner = owner_; manager = manager_;
        isValidationKey[owner_] = true; validationKeyCount = 1;
        emit ValidationKeyAdded(owner_);
    }

    modifier auth() { if (msg.sender != manager && !isValidationKey[msg.sender]) revert NotAuthorized(); _; }

    // ---- ERC-4337 validation ----
    /// @return validationData 0 = valid now; SIG_VALIDATION_FAILED = bad sig; else packed
    ///         (validUntil << 160 | validAfter << 208) per ERC-4337 for session keys.
    function validateUserOp(PackedUserOperation calldata userOp, bytes32 userOpHash, uint256 /*missingAccountFunds*/)
        external view returns (uint256 validationData)
    {
        bytes32 ethHash = keccak256(abi.encodePacked("\x19Ethereum Signed Message:\n32", userOpHash));
        address signer = _recover(ethHash, userOp.signature);
        if (signer == address(0)) return SIG_VALIDATION_FAILED;
        if (isValidationKey[signer]) return 0;
        SessionKey storage s = sessionKeys[signer];
        if (!s.exists) return SIG_VALIDATION_FAILED;
        return (uint256(s.validUntil) << 160) | (uint256(s.validAfter) << 208);
    }

    /// @notice Direct-path equivalent: is `caller` authorised at this moment?
    function validateCaller(address caller) public view returns (bool) {
        if (isValidationKey[caller]) return true;
        SessionKey storage s = sessionKeys[caller];
        return s.exists && block.timestamp >= s.validAfter && block.timestamp < s.validUntil;
    }

    function sessionValid(address key) external view returns (bool) {
        SessionKey storage s = sessionKeys[key];
        return s.exists && block.timestamp >= s.validAfter && block.timestamp < s.validUntil;
    }

    // ---- key management (owner-class or manager) ----
    function addValidationKey(address key) external auth { if (!isValidationKey[key]) { isValidationKey[key] = true; validationKeyCount += 1; emit ValidationKeyAdded(key); } }
    function removeValidationKey(address key) external auth { if (isValidationKey[key]) { isValidationKey[key] = false; validationKeyCount -= 1; emit ValidationKeyRemoved(key); } }
    function setSessionKey(address key, uint48 validAfter, uint48 validUntil) external auth { sessionKeys[key] = SessionKey(validAfter, validUntil, true); emit SessionKeySet(key, validAfter, validUntil); }

    // ---- execution and data ----
    function execute(address target, uint256 value, bytes calldata data) external auth returns (bytes memory r) {
        bool ok; (ok, r) = target.call{value: value}(data); require(ok, "call");
        emit Executed(target, value, bytes4(data));
    }
    function getData(bytes32 k) external view returns (bytes memory) { return _store[k]; }
    function setData(bytes32 k, bytes calldata v) external auth { _store[k] = v; }

    function _recover(bytes32 h, bytes memory sig) internal pure returns (address) {
        if (sig.length != 65) return address(0);
        bytes32 r; bytes32 s; uint8 v;
        assembly { r := mload(add(sig, 32)) s := mload(add(sig, 64)) v := byte(0, mload(add(sig, 96))) }
        if (v < 27) v += 27;
        if (v != 27 && v != 28) return address(0);
        return ecrecover(h, v, r, s);
    }
    receive() external payable {}
}
