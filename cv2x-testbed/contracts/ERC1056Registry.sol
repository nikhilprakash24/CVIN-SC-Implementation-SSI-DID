// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ERC1056 DID Registry for Connected Vehicles
 * @author CVIN research project
 * @notice Shared ERC-1056 ("vehicle profile") DID registry: any address is a
 *         did:ethr identity, with owner, delegate and attribute changes
 *         published as events, plus a terminal identity revocation.
 * @dev Lightweight Ethereum DID Registry (ERC-1056 compliant)
 *
 * Based on: https://github.com/uport-project/ethr-did-registry
 *
 * This contract manages decentralized identifiers (DIDs) for vehicles
 * in a gas-efficient manner suitable for V2X applications.
 *
 * Key Features:
 * - Minimal on-chain storage (gas efficient)
 * - Event-based DID document construction
 * - Delegate management for key rotation
 * - Attribute storage for metadata
 * - Revocation support (terminal; DIDRevoked carries previousChange so the
 *   did:ethr change list stays walkable through the revocation)
 *
 * Design: no imports, no OpenZeppelin bases. Kept from canonical ERC-1056:
 * `owners`, `changed`, `nonce`, the three DID*Changed events with
 * `previousChange`, the identity-self-owner fallback and the internal
 * (identity, actor, ...) / public (identity, ...) split. Removed: every
 * `*Signed` meta-transaction variant, the `delegates` mapping and
 * `validDelegate` (delegations are event-only here; MOBIVIDRegistry stores
 * them again). Added (CVIN extension): `revoked` / `revokedAt`,
 * `revokeIdentity` + `DIDRevoked`, the `notRevoked` freeze, and the vehicle
 * convenience functions `registerVehicle` / `updateVehicleKey` plus views.
 * Also deployed on its own by the testbed as the "ERC-1056 / vehicle
 * profile" option; in the MOBI group it is the base of MOBIVIDRegistry.
 *
 * @custom:standard ERC-1056 Ethereum Lightweight Identity https://eips.ethereum.org/EIPS/eip-1056
 * @custom:standard did:ethr DID method https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md
 * @custom:standard W3C DID Core v1.0 https://www.w3.org/TR/did-core/
 * @custom:security `nonce` is declared but never read or written (no signed variants).
 * @custom:security No on-chain `validDelegate`: delegate validity must be derived by replaying DIDDelegateChanged events.
 * @custom:security The vehicle key attribute name is keccak256("did/pub/secp256k1/veriKey/base64"), not the
 *                  did:ethr ASCII-padded bytes32 name, so a stock ethr-did-resolver does not recognise it as a
 *                  verification method; the repo's own resolvers match the keccak name.
 * @custom:security Revocation is owner-only; no authority can revoke an identity.
 * @custom:security Several changes in one block share one `changed` value; resolvers must take the minimum
 *                  `previousChange` per block when walking the list.
 * @custom:see docs/smart-contracts/02-mobi-vid.md
 * @custom:see sandbox/options/erc-1056-vehicle/ (standalone adapter)
 */
contract ERC1056Registry {

    // Events for DID document changes
    /// @notice Emitted when the owner (controller) of `identity` changes.
    /// @dev ERC-1056 canonical layout. Emitted by changeOwner and by
    ///      MOBIVIDRegistry.registerVehicleBirth / transferVehicleOwnership.
    /// @param identity The identity whose owner changed.
    /// @param owner The new owner.
    /// @param previousChange Block number of the previous change of `identity` (0 if none).
    event DIDOwnerChanged(
        address indexed identity,
        address owner,
        uint previousChange
    );

    /// @notice Emitted when a delegate is added to or revoked from `identity`.
    /// @dev ERC-1056 canonical layout; a revocation is emitted with `validTo = block.timestamp`.
    /// @param identity The identity.
    /// @param delegateType Delegate type (e.g. "veriKey", "sigAuth").
    /// @param delegate The delegate address.
    /// @param validTo Unix time until which the delegation is valid.
    /// @param previousChange Block number of the previous change of `identity`.
    event DIDDelegateChanged(
        address indexed identity,
        bytes32 delegateType,
        address delegate,
        uint validTo,
        uint previousChange
    );

    /// @notice Emitted when an attribute of `identity` is set or revoked.
    /// @dev ERC-1056 canonical layout; a revocation is emitted with `validTo = block.timestamp`.
    /// @param identity The identity.
    /// @param name Attribute name.
    /// @param value Attribute value (e.g. a public key).
    /// @param validTo Unix time until which the attribute is valid.
    /// @param previousChange Block number of the previous change of `identity`.
    event DIDAttributeChanged(
        address indexed identity,
        bytes32 name,
        bytes value,
        uint validTo,
        uint previousChange
    );

    /**
     * @dev Emitted once per identity by revokeIdentity. Carries `previousChange`
     *      (the block of the previous change) like the three ERC-1056 events, so
     *      the `changed(identity)` -> previousChange linked list that a did:ethr
     *      resolver walks is NOT severed by revocation (defect D21).
     *      CVIN extension (not part of ERC-1056).
     * @notice Emitted once when `identity` is permanently revoked.
     * @param identity The revoked identity.
     * @param revokedAt Block timestamp of the revocation.
     * @param previousChange Block number of the previous change of `identity`.
     */
    event DIDRevoked(
        address indexed identity,
        uint revokedAt,
        uint previousChange
    );

    // Storage
    /// @notice Explicit owner of each identity; zero means the identity owns itself.
    /// @dev ERC-1056. Read through identityOwner().
    mapping(address => address) public owners;
    /// @notice Block number of the last change of each identity (head of the event linked list).
    /// @dev ERC-1056.
    mapping(address => uint) public changed;
    /// @notice ERC-1056 meta-transaction nonce.
    /// @dev Unused: no `*Signed` functions exist in this registry.
    mapping(address => uint) public nonce;
    /// @notice True once an identity has been revoked with revokeIdentity.
    /// @dev CVIN extension.
    mapping(address => bool) public revoked;

    // Revocation tracking
    /// @notice Block timestamp at which an identity was revoked (0 if not revoked).
    /// @dev CVIN extension.
    mapping(address => uint) public revokedAt;

    /// @notice Requires `actor` to be the current owner of `identity`.
    /// @dev ERC-1056 access control; `actor` is msg.sender on the public paths.
    /// @param identity The identity being modified.
    /// @param actor The address acting on the identity.
    modifier onlyOwner(address identity, address actor) {
        require(
            actor == identityOwner(identity),
            "Only owner can perform this action"
        );
        _;
    }

    /**
     * @dev Revocation is terminal: every mutator (ownership, delegates,
     *      attributes, a second revocation) reverts once the identity is
     *      revoked, so `revokedAt` and the ownership record are frozen at
     *      decommissioning time (defects D16 / D21). CVIN extension.
     * @notice Requires `identity` not to be revoked.
     * @param identity The identity being modified.
     */
    modifier notRevoked(address identity) {
        require(!revoked[identity], "Identity is revoked");
        _;
    }

    /**
     * @notice Get the owner of an identity
     * @dev ERC-1056.
     * @param identity The identity address
     * @return The owner address (defaults to identity itself)
     */
    function identityOwner(address identity) public view returns (address) {
        address owner = owners[identity];
        if (owner != address(0)) {
            return owner;
        }
        return identity;
    }

    /**
     * @notice Check if identity is revoked
     * @dev CVIN extension.
     * @param identity The identity address
     * @return True if revokeIdentity has been called for `identity`
     */
    function isRevoked(address identity) public view returns (bool) {
        return revoked[identity];
    }

    /**
     * @dev Transfer ownership of an identity. A revoked identity is frozen
     *      (REVIEW_02 K-3: it used to be re-assignable after revocation).
     *      ERC-1056 internal form; requires onlyOwner(identity, actor) and
     *      notRevoked. Emits DIDOwnerChanged and advances `changed`.
     * @param identity The identity address
     * @param actor The address acting (must be the current owner)
     * @param newOwner The new owner
     */
    function changeOwner(
        address identity,
        address actor,
        address newOwner
    ) internal onlyOwner(identity, actor) notRevoked(identity) {
        owners[identity] = newOwner;
        emit DIDOwnerChanged(identity, newOwner, changed[identity]);
        changed[identity] = block.number;
    }

    /// @notice Transfer ownership of `identity` to `newOwner` (caller must be the owner).
    /// @dev virtual so a registry that keeps its own ownership record (e.g.
    ///      MOBIVIDRegistry.ownershipHistory) can stop this path bypassing it.
    ///      ERC-1056. Emits DIDOwnerChanged. Reverts if the identity is revoked.
    /// @param identity The identity address
    /// @param newOwner The new owner
    function changeOwner(address identity, address newOwner) public virtual {
        changeOwner(identity, msg.sender, newOwner);
    }

    /**
     * @dev Add a delegate to an identity
     * Delegates can be used for key rotation without changing the DID
     * ERC-1056 internal form, event-only here (nothing stored); virtual so
     * MOBIVIDRegistry can store the delegation. Requires onlyOwner and
     * notRevoked. Emits DIDDelegateChanged with validTo = now + validity.
     *
     * @param identity The identity address
     * @param actor The address acting (must be the current owner)
     * @param delegateType Type of delegate (e.g., "sigAuth" for signing)
     * @param delegate The delegate address
     * @param validity Validity period in seconds
     */
    function addDelegate(
        address identity,
        address actor,
        bytes32 delegateType,
        address delegate,
        uint validity
    ) internal virtual onlyOwner(identity, actor) notRevoked(identity) {
        uint validTo = block.timestamp + validity;

        emit DIDDelegateChanged(
            identity,
            delegateType,
            delegate,
            validTo,
            changed[identity]
        );

        changed[identity] = block.number;
    }

    /// @notice Add a delegate of `delegateType` to `identity` for `validity` seconds (caller must be the owner).
    /// @dev ERC-1056. Emits DIDDelegateChanged.
    /// @param identity The identity address
    /// @param delegateType Type of delegate (e.g. "veriKey", "sigAuth")
    /// @param delegate The delegate address
    /// @param validity Validity period in seconds
    function addDelegate(
        address identity,
        bytes32 delegateType,
        address delegate,
        uint validity
    ) public {
        addDelegate(identity, msg.sender, delegateType, delegate, validity);
    }

    /**
     * @dev Revoke a delegate (rejected on a revoked identity, K-3)
     *      ERC-1056 internal form; virtual so MOBIVIDRegistry can update its
     *      stored delegation. Emits DIDDelegateChanged with validTo = now.
     * @param identity The identity address
     * @param actor The address acting (must be the current owner)
     * @param delegateType Type of delegate
     * @param delegate The delegate address
     */
    function revokeDelegate(
        address identity,
        address actor,
        bytes32 delegateType,
        address delegate
    ) internal virtual onlyOwner(identity, actor) notRevoked(identity) {
        emit DIDDelegateChanged(
            identity,
            delegateType,
            delegate,
            block.timestamp,  // validTo = now (expired)
            changed[identity]
        );

        changed[identity] = block.number;
    }

    /// @notice Revoke a delegate of `identity` (caller must be the owner).
    /// @dev ERC-1056. Emits DIDDelegateChanged with validTo = block.timestamp.
    /// @param identity The identity address
    /// @param delegateType Type of delegate
    /// @param delegate The delegate address
    function revokeDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) public {
        revokeDelegate(identity, msg.sender, delegateType, delegate);
    }

    /**
     * @dev Set an attribute for an identity
     * Attributes store metadata like public keys, service endpoints, etc.
     * ERC-1056 internal form; requires onlyOwner and notRevoked. Emits
     * DIDAttributeChanged with validTo = now + validity (checked arithmetic,
     * so a huge `validity` reverts with panic 0x11).
     *
     * @param identity The identity address
     * @param actor The address acting (must be the current owner)
     * @param name Attribute name (e.g., "did/pub/secp256k1/veriKey")
     * @param value Attribute value (e.g., public key)
     * @param validity Validity period in seconds
     */
    function setAttribute(
        address identity,
        address actor,
        bytes32 name,
        bytes memory value,
        uint validity
    ) internal onlyOwner(identity, actor) notRevoked(identity) {
        uint validTo = block.timestamp + validity;

        emit DIDAttributeChanged(
            identity,
            name,
            value,
            validTo,
            changed[identity]
        );

        changed[identity] = block.number;
    }

    /// @notice Set an attribute of `identity` for `validity` seconds (caller must be the owner).
    /// @dev ERC-1056. Emits DIDAttributeChanged.
    /// @param identity The identity address
    /// @param name Attribute name
    /// @param value Attribute value
    /// @param validity Validity period in seconds
    function setAttribute(
        address identity,
        bytes32 name,
        bytes calldata value,
        uint validity
    ) public {
        setAttribute(identity, msg.sender, name, value, validity);
    }

    /**
     * @dev Revoke an attribute (rejected on a revoked identity, K-3)
     *      ERC-1056 internal form. Emits DIDAttributeChanged with validTo = now.
     * @param identity The identity address
     * @param actor The address acting (must be the current owner)
     * @param name Attribute name
     * @param value Attribute value being revoked
     */
    function revokeAttribute(
        address identity,
        address actor,
        bytes32 name,
        bytes memory value
    ) internal onlyOwner(identity, actor) notRevoked(identity) {
        emit DIDAttributeChanged(
            identity,
            name,
            value,
            block.timestamp,  // validTo = now (expired)
            changed[identity]
        );

        changed[identity] = block.number;
    }

    /// @notice Revoke an attribute of `identity` (caller must be the owner).
    /// @dev ERC-1056. Emits DIDAttributeChanged with validTo = block.timestamp.
    /// @param identity The identity address
    /// @param name Attribute name
    /// @param value Attribute value being revoked
    function revokeAttribute(
        address identity,
        bytes32 name,
        bytes calldata value
    ) public {
        revokeAttribute(identity, msg.sender, name, value);
    }

    /**
     * @dev Revoke entire identity (for vehicle decommissioning or security).
     *      Terminal and single-shot: a second call reverts instead of moving
     *      `revokedAt`, and the DIDRevoked event links back to the previous
     *      change so the resolver's pointer walk reaches the full history.
     *      CVIN extension. Owner only (onlyOwner with msg.sender); emits DIDRevoked.
     * @notice Permanently revoke `identity`; afterwards every mutator reverts.
     * @param identity The identity address
     */
    function revokeIdentity(address identity) public onlyOwner(identity, msg.sender) {
        require(!revoked[identity], "Identity already revoked");

        revoked[identity] = true;
        revokedAt[identity] = block.timestamp;

        emit DIDRevoked(identity, block.timestamp, changed[identity]);
        changed[identity] = block.number;
    }

    /**
     * @notice Get the block number when identity was last changed
     * @dev CVIN extension (canonical ERC-1056 exposes `changed` directly).
     *      Start point of the off-chain event walk.
     * @param identity The identity address
     * @return Block number of the last change (0 if never changed)
     */
    function lastChanged(address identity) public view returns (uint) {
        return changed[identity];
    }

    /**
     * @dev Utility: Register a new vehicle identity with public key
     * This is a convenience function for vehicle registration
     * CVIN extension. Writes the keccak256("did/pub/secp256k1/veriKey/base64")
     * attribute with 1-year validity; because setAttribute is onlyOwner with
     * actor = msg.sender, the caller must effectively be `vehicleIdentity`.
     * Emits DIDAttributeChanged.
     * @notice Publish the vehicle's public key for a self-owned, unrevoked identity.
     * @param vehicleIdentity The vehicle identity address
     * @param publicKey The vehicle's public key
     * @custom:security The "already registered" guard only checks that the identity is still self-owned,
     *                  so the same identity can call this again and publish another key.
     */
    function registerVehicle(
        address vehicleIdentity,
        bytes calldata publicKey
    ) public {
        require(!revoked[vehicleIdentity], "Identity already revoked");
        require(identityOwner(vehicleIdentity) == vehicleIdentity, "Identity already registered");

        // Set public key as attribute
        bytes32 keyName = keccak256("did/pub/secp256k1/veriKey/base64");
        setAttribute(
            vehicleIdentity,
            msg.sender,
            keyName,
            publicKey,
            31536000  // 1 year validity
        );
    }

    /**
     * @dev Utility: Update vehicle public key (key rotation)
     *      CVIN extension. onlyOwner, notRevoked; writes a new 1-year key
     *      attribute. Emits DIDAttributeChanged.
     * @notice Publish a new public key for `vehicleIdentity` (caller must be the owner).
     * @param vehicleIdentity The vehicle identity address
     * @param newPublicKey The new public key
     * @custom:security The previous key attribute is NOT revoked; it stays valid until its own validTo.
     */
    function updateVehicleKey(
        address vehicleIdentity,
        bytes calldata newPublicKey
    ) public onlyOwner(vehicleIdentity, msg.sender) notRevoked(vehicleIdentity) {
        bytes32 keyName = keccak256("did/pub/secp256k1/veriKey/base64");

        // Revoke old key
        // In a full implementation, we'd fetch the old key value
        // For simplicity, we just set a new one

        // Set new key
        setAttribute(
            vehicleIdentity,
            msg.sender,
            keyName,
            newPublicKey,
            31536000  // 1 year validity
        );
    }

    /**
     * @notice Get identity metadata
     * @dev CVIN extension; aggregate read.
     * @param identity The identity address
     * @return owner Current owner (identity itself if unset)
     * @return lastChangedBlock Block of the last change
     * @return isRevoked Whether the identity is revoked
     * @return revokedTimestamp Revocation timestamp (0 if not revoked)
     */
    function getIdentityInfo(address identity) public view returns (
        address owner,
        uint lastChangedBlock,
        bool isRevoked,
        uint revokedTimestamp
    ) {
        return (
            identityOwner(identity),
            changed[identity],
            revoked[identity],
            revokedAt[identity]
        );
    }
}
