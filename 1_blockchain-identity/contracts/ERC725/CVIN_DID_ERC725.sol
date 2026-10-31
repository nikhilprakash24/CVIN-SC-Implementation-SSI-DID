// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CVIN_SCBasedAccOrID_DID_ERC725Basic
 * @author CVIN research project
 * @notice Basic ERC-725 (v1-era, 2017 "Identity") per-vehicle proxy account. Deploying
 *         the contract creates the identity; the deployer becomes the owner.
 * @dev Interface-shape baseline for the CVIN benchmarks. Self-contained: no imports, no
 *      inheritance, no OpenZeppelin (the project pins npm openzeppelin/contracts 5.0.2, unused here).
 *      Deviations from ERC-725 v1 / ERC-734:
 *      - Authorisation is a single `_owner` address (inline `require`), not purpose-1
 *        MANAGEMENT keys. Keys are stored but never authorise anything.
 *      - One purpose per key; no `keyHasPurpose`, `getKeysByPurpose` or execution IDs.
 *      - `execute` is a stub that only emits `Executed`; `approve` has an empty body.
 *      - No VIN or data store.
 * @custom:standard ERC-725 (v1 Identity, superseded by 725X/725Y) https://eips.ethereum.org/EIPS/eip-725
 * @custom:standard ERC-734 (Key Manager, draft; simplified key model) https://github.com/ethereum/EIPs/issues/734
 * @custom:standard ERC-173 (ownership-like surface) https://eips.ethereum.org/EIPS/eip-173
 * @custom:security `execute` performs no call and is not payable; `approve` has no access check and does nothing.
 * @custom:security `transferOwnership` has no zero-address check.
 * @custom:security `addKey` on an existing id overwrites the struct and pushes a duplicate into `allKeys`;
 *                  `removeKey` removes one copy only and emits `KeyRemoved` even for unknown keys.
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 1)
 * @custom:see sandbox/options/erc-725/adapter.js
 */
contract CVIN_SCBasedAccOrID_DID_ERC725Basic {
    /// @dev Owner (controller) of the identity. Stands in for ERC-734 MANAGEMENT keys. Set to the deployer in the constructor.
    address private _owner;

    // Events
    /// @notice Emitted when ownership changes (including at construction and on renounce).
    /// @param previousOwner The previous owner (zero at construction).
    /// @param newOwner The new owner (zero on renounce).
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    /// @notice Emitted when a key is added (or overwritten).
    /// @dev ERC-725 v1 / ERC-734 event shape.
    /// @param key The key identifier.
    /// @param purpose ERC-734 purpose (1=MANAGEMENT, 2=ACTION, 3=CLAIM, 4=ENCRYPTION); informational only here.
    /// @param keyType Key type (e.g. 1 = ECDSA); informational only.
    event KeyAdded(bytes32 indexed key, uint256 indexed purpose, uint256 indexed keyType);
    /// @notice Emitted by `removeKey` (also for keys that did not exist).
    /// @param key The key identifier.
    event KeyRemoved(bytes32 indexed key);
    /// @notice Emitted by the `execute` stub. No call is actually performed.
    /// @param operationType Requested operation type (e.g. 0 = CALL).
    /// @param to Requested target.
    /// @param value Requested value (not transferred).
    /// @param data Requested calldata (not executed).
    event Executed(uint256 indexed operationType, address indexed to, uint256 value, bytes data);

    /// @dev Key record, simplified ERC-734 layout (one purpose per key). Fields: `purpose` (ERC-734 purpose code), `keyType` (key type code),
    ///      `key` (the key identifier, e.g. keccak256(abi.encode(addr)) in the sandbox adapter).
    struct Key {
        uint256 purpose;
        uint256 keyType;
        bytes32 key;
    }

    /// @dev Keys by key identifier.
    mapping(bytes32 => Key) private keys;
    /// @dev List of all key identifiers (may contain duplicates, see contract-level security note).
    bytes32[] private allKeys;

    /// @notice Creates the identity; the deployer becomes owner.
    /// @dev Emits `OwnershipTransferred(address(0), msg.sender)`.
    constructor() {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    /// @notice Returns the current owner.
    /// @dev ERC-173-like.
    /// @return The owner address.
    function owner() public view returns (address) {
        return _owner;
    }

    /// @notice Transfers control of the identity.
    /// @dev Owner only. Emits `OwnershipTransferred`. No zero-address check.
    /// @param newOwner The new owner.
    function transferOwnership(address newOwner) public {
        require(msg.sender == _owner, "Only owner can transfer ownership");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }

    /// @notice Permanently gives up ownership (owner becomes zero).
    /// @dev Owner only. Emits `OwnershipTransferred`. OZ-Ownable-like.
    function renounceOwnership() public {
        require(msg.sender == _owner, "Only owner can renounce ownership");
        emit OwnershipTransferred(_owner, address(0));
        _owner = address(0);
    }

    /// @notice Returns a key record.
    /// @dev ERC-725 v1 / ERC-734. Unknown keys return zeros.
    /// @param _key The key identifier.
    /// @return purpose The key's purpose.
    /// @return keyType The key's type.
    /// @return key The stored key identifier.
    function getKey(bytes32 _key) public view returns (uint256 purpose, uint256 keyType, bytes32 key) {
        Key memory k = keys[_key];
        return (k.purpose, k.keyType, k.key);
    }

    /// @notice Returns all key identifiers.
    /// @dev CVIN extension (enumeration).
    /// @return The `allKeys` array.
    function getKeys() public view returns (bytes32[] memory) {
        return allKeys;
    }

    /// @notice Adds (or overwrites) a key.
    /// @dev Owner only. Emits `KeyAdded`. ERC-725 v1 / ERC-734 with one purpose per key;
    ///      always pushes to `allKeys`, so re-adding creates a duplicate entry.
    /// @param _key The key identifier.
    /// @param _purpose ERC-734 purpose code.
    /// @param _type Key type code.
    function addKey(bytes32 _key, uint256 _purpose, uint256 _type) public {
        require(msg.sender == _owner, "Only owner can add keys");
        keys[_key] = Key({purpose: _purpose, keyType: _type, key: _key});
        allKeys.push(_key);
        emit KeyAdded(_key, _purpose, _type);
    }

    /// @notice Removes a key.
    /// @dev Owner only. Emits `KeyRemoved` (even if absent). O(n) swap-and-pop of the first match.
    /// @param _key The key identifier.
    function removeKey(bytes32 _key) public {
        require(msg.sender == _owner, "Only owner can remove keys");
        delete keys[_key];
        for (uint256 i = 0; i < allKeys.length; i++) {
            if (allKeys[i] == _key) {
                allKeys[i] = allKeys[allKeys.length - 1];
                allKeys.pop();
                break;
            }
        }
        emit KeyRemoved(_key);
    }

    /// @notice ERC-725 v1 `execute` STUB: emits `Executed` but performs no call.
    /// @dev Owner only. Not payable; `_value` is not transferred. Kept for interface shape only.
    /// @param _operationType Requested operation type.
    /// @param _to Requested target.
    /// @param _value Requested value.
    /// @param _data Requested calldata.
    function execute(uint256 _operationType, address _to, uint256 _value, bytes memory _data) public {
        require(msg.sender == _owner, "Only owner can execute operations");
        // Implementation for different operation types (e.g., CALL, DELEGATECALL, etc.)
        emit Executed(_operationType, _to, _value, _data);
    }

    /// @notice ERC-725 v1 `approve` STUB: empty body, no access check, no effect.
    /// @param _id Execution id (unused; no execution ids exist).
    /// @param _approve Approval flag (unused).
    function approve(uint256 _id, bool _approve) public {
        // Implementation for approving or rejecting an operation
    }
}
