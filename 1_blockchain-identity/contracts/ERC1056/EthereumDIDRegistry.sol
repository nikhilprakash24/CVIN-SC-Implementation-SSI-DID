// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EthereumDIDRegistry
 * @author CVIN research project (Solidity 0.8 port of uPort / DIF ethr-did-registry)
 * @notice Single shared contract for all DIDs (did:ethr method)
 * @dev ERC-1056 Lightweight Identity Registry.
 *      Gas-efficient, event-based architecture with minimal on-chain storage.
 *      Near-verbatim port of the upstream registry; no inheritance, no imports,
 *      no OpenZeppelin dependency. Owner/delegate/attribute changes are emitted
 *      as events chained through `previousChange`; off-chain resolvers walk
 *      `changed[identity]` -> `previousChange` to rebuild the DID Document.
 *
 * Based on: https://github.com/uport-project/ethr-did-registry
 * EIP: https://github.com/ethereum/EIPs/issues/1056
 *
 * Features:
 * - Implicit DID creation (any Ethereum address is a valid DID)
 * - Off-chain DID Document resolution via events
 * - Temporary delegates (time-bound verification keys)
 * - Flexible attributes (service endpoints, custom properties)
 * - Meta-transactions (gasless operations via signatures)
 * - Minimal gas costs (events only, no storage for attributes)
 * @custom:standard ERC-1056 Ethereum Lightweight Identity, https://github.com/ethereum/EIPs/issues/1056
 * @custom:standard did:ethr DID method, https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md
 * @custom:standard W3C DID Core v1.0, https://www.w3.org/TR/did-core/
 * @custom:standard ERC-191 signed data (version 0x00 layout, raw digest), https://eips.ethereum.org/EIPS/eip-191
 * @custom:security `block.timestamp + validity` is checked arithmetic: validity = type(uint256).max reverts (panic 0x11), cf. defect D18.
 * @custom:security Signed digests contain no chainid, so signatures replay across chains with the same registry address; the nonce is per owner and shared across all identities that owner controls.
 * @custom:security Attributes exist only as events; no contract can read an attribute value on-chain.
 * @custom:security changeOwner(identity, address(0)) deactivates the DID for did:ethr resolvers, yet identityOwner then returns `identity` again, so the original key regains on-chain control (inherited from upstream).
 * @custom:security No identity-level revocation and no guardians/recovery; revocation is per delegate and per attribute.
 * @custom:security Delegates carry no on-chain authority; integrators must call validDelegate themselves.
 * @custom:see docs/smart-contracts/01-erc1056-did-registry.md
 * @custom:see sandbox/options/erc-1056-uport/adapter.js
 */
contract EthereumDIDRegistry {
    // ============ Events ============

    /**
     * @notice Emitted when DID owner changes.
     * @dev Emitted when DID owner changes (ERC-1056). An `owner` of address(0)
     *      means the DID is deactivated per did:ethr.
     * @param identity The DID being modified
     * @param owner The new owner address
     * @param previousChange Block number of previous change
     */
    event DIDOwnerChanged(
        address indexed identity,
        address owner,
        uint previousChange
    );

    /**
     * @notice Emitted when a delegate is added or revoked.
     * @dev Emitted when a delegate is added or revoked (ERC-1056).
     * @param identity The DID being modified
     * @param delegateType Type of delegate (e.g., "veriKey", "sigAuth")
     * @param delegate The delegate address
     * @param validTo Expiration timestamp (0 = revoked)
     * @param previousChange Block number of previous change
     */
    event DIDDelegateChanged(
        address indexed identity,
        bytes32 delegateType,
        address delegate,
        uint validTo,
        uint previousChange
    );

    /**
     * @notice Emitted when an attribute is set or revoked.
     * @dev Emitted when an attribute is set or revoked (ERC-1056). This event is
     *      the only place attribute values are recorded.
     * @param identity The DID being modified
     * @param name Attribute name (e.g., "did/pub/Ed25519/veriKey")
     * @param value Attribute value (public key, endpoint URL, etc.)
     * @param validTo Expiration timestamp (0 = revoked)
     * @param previousChange Block number of previous change
     */
    event DIDAttributeChanged(
        address indexed identity,
        bytes32 name,
        bytes value,
        uint validTo,
        uint previousChange
    );

    // ============ State Variables ============

    /// @notice Explicit owner of each identity; zero means the identity owns itself.
    /// @dev Mapping from identity address to owner address. Read via identityOwner.
    mapping(address => address) public owners;

    /// @notice Block number of the identity's most recent change (head of the event chain).
    /// @dev Mapping from identity to block number of last change
    mapping(address => uint) public changed;

    /// @notice Meta-transaction nonce of a signer.
    /// @dev Mapping from identity to nonce (for meta-transactions). Indexed by
    ///      the current owner (signer), not by the identity being modified.
    mapping(address => uint) public nonce;

    /// @notice Expiry timestamp of each (identity, delegateType, delegate) triple.
    /// @dev Mapping from identity to delegate type to delegate address to validity
    mapping(address => mapping(bytes32 => mapping(address => uint)))
        public delegates;

    // ============ Modifiers ============

    /**
     * @notice Restricts a call to the current owner of `identity`.
     * @dev Ensures sender is authorized to modify the identity
     *      (`actor == identityOwner(identity)`); reverts "DIDRegistry: unauthorized".
     * @param identity The DID being modified
     * @param actor The address attempting modification
     */
    modifier onlyOwner(address identity, address actor) {
        require(
            actor == identityOwner(identity),
            "DIDRegistry: unauthorized"
        );
        _;
    }

    // ============ Core Functions ============

    /**
     * @notice Get the owner of a DID
     * @dev ERC-1056 §identityOwner. Anyone may call.
     * @param identity The DID address
     * @return The owner address (defaults to identity if no owner set)
     */
    function identityOwner(address identity) public view returns (address) {
        address owner = owners[identity];
        if (owner != address(0)) {
            return owner;
        }
        return identity;
    }

    /**
     * @notice Check if a delegate is currently valid
     * @dev ERC-1056 §validDelegate: `delegates[..] > block.timestamp`.
     * @param identity The DID address
     * @param delegateType Type of delegate
     * @param delegate The delegate address
     * @return True if delegate is valid (not expired)
     */
    function validDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) public view returns (bool) {
        uint validity = delegates[identity][delegateType][delegate];
        return (validity > block.timestamp);
    }

    // ============ Owner Management ============

    /**
     * @notice Change the owner of a DID
     * @dev ERC-1056 §changeOwner. `onlyOwner`; emits DIDOwnerChanged and updates
     *      `changed`. Passing address(0) deactivates the DID (see contract caveats).
     * @param identity The DID to modify
     * @param newOwner The new owner address
     */
    function changeOwner(
        address identity,
        address newOwner
    ) public onlyOwner(identity, msg.sender) {
        owners[identity] = newOwner;
        emit DIDOwnerChanged(identity, newOwner, changed[identity]);
        changed[identity] = block.number;
    }

    /**
     * @notice Change owner via signed message (meta-transaction)
     * @dev ERC-1056 §changeOwnerSigned. Any relayer may submit; the signature must
     *      recover to identityOwner(identity) over
     *      keccak256(0x19 || 0x00 || this || nonce[owner] || identity || "changeOwner" || newOwner)
     *      (raw digest, no "\x19Ethereum Signed Message" prefix, no chainid).
     *      Increments `nonce[signer]`; emits DIDOwnerChanged.
     * @param identity The DID to modify
     * @param sigV ECDSA signature V
     * @param sigR ECDSA signature R
     * @param sigS ECDSA signature S
     * @param newOwner The new owner address
     */
    function changeOwnerSigned(
        address identity,
        uint8 sigV,
        bytes32 sigR,
        bytes32 sigS,
        address newOwner
    ) public {
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0x19),
                bytes1(0),
                this,
                nonce[identityOwner(identity)],
                identity,
                "changeOwner",
                newOwner
            )
        );

        address signer = ecrecover(hash, sigV, sigR, sigS);
        require(signer == identityOwner(identity), "DIDRegistry: invalid signature");

        nonce[signer]++;
        owners[identity] = newOwner;
        emit DIDOwnerChanged(identity, newOwner, changed[identity]);
        changed[identity] = block.number;
    }

    // ============ Delegate Management ============

    /**
     * @notice Add a delegate with specific validity period
     * @dev ERC-1056 §addDelegate. `onlyOwner`; stores `block.timestamp + validity`
     *      (checked, overflow reverts) and emits DIDDelegateChanged.
     * @param identity The DID to modify
     * @param delegateType Type of delegate (e.g., keccak256("veriKey"))
     * @param delegate The delegate address
     * @param validity Validity period in seconds
     */
    function addDelegate(
        address identity,
        bytes32 delegateType,
        address delegate,
        uint validity
    ) public onlyOwner(identity, msg.sender) {
        uint validTo = block.timestamp + validity;
        delegates[identity][delegateType][delegate] = validTo;
        emit DIDDelegateChanged(
            identity,
            delegateType,
            delegate,
            validTo,
            changed[identity]
        );
        changed[identity] = block.number;
    }

    /**
     * @notice Add delegate via signed message (meta-transaction)
     * @dev ERC-1056 §addDelegateSigned. Digest: 0x19 || 0x00 || this || nonce[owner]
     *      || identity || "addDelegate" || delegateType || delegate || validity.
     *      Increments `nonce[signer]`; emits DIDDelegateChanged.
     * @param identity The DID to modify
     * @param sigV ECDSA signature V
     * @param sigR ECDSA signature R
     * @param sigS ECDSA signature S
     * @param delegateType Type of delegate (e.g., keccak256("veriKey"))
     * @param delegate The delegate address
     * @param validity Validity period in seconds
     */
    function addDelegateSigned(
        address identity,
        uint8 sigV,
        bytes32 sigR,
        bytes32 sigS,
        bytes32 delegateType,
        address delegate,
        uint validity
    ) public {
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0x19),
                bytes1(0),
                this,
                nonce[identityOwner(identity)],
                identity,
                "addDelegate",
                delegateType,
                delegate,
                validity
            )
        );

        address signer = ecrecover(hash, sigV, sigR, sigS);
        require(signer == identityOwner(identity), "DIDRegistry: invalid signature");

        nonce[signer]++;
        uint validTo = block.timestamp + validity;
        delegates[identity][delegateType][delegate] = validTo;
        emit DIDDelegateChanged(
            identity,
            delegateType,
            delegate,
            validTo,
            changed[identity]
        );
        changed[identity] = block.number;
    }

    /**
     * @notice Revoke a delegate
     * @dev ERC-1056 §revokeDelegate. `onlyOwner`; sets validity to 0 and emits
     *      DIDDelegateChanged with validTo = 0.
     * @param identity The DID to modify
     * @param delegateType Type of delegate
     * @param delegate The delegate address
     */
    function revokeDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) public onlyOwner(identity, msg.sender) {
        delegates[identity][delegateType][delegate] = 0;
        emit DIDDelegateChanged(
            identity,
            delegateType,
            delegate,
            0,
            changed[identity]
        );
        changed[identity] = block.number;
    }

    /**
     * @notice Revoke delegate via signed message
     * @dev ERC-1056 §revokeDelegateSigned. Digest: 0x19 || 0x00 || this || nonce[owner]
     *      || identity || "revokeDelegate" || delegateType || delegate.
     *      Increments `nonce[signer]`; emits DIDDelegateChanged (validTo 0).
     * @param identity The DID to modify
     * @param sigV ECDSA signature V
     * @param sigR ECDSA signature R
     * @param sigS ECDSA signature S
     * @param delegateType Type of delegate
     * @param delegate The delegate address
     */
    function revokeDelegateSigned(
        address identity,
        uint8 sigV,
        bytes32 sigR,
        bytes32 sigS,
        bytes32 delegateType,
        address delegate
    ) public {
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0x19),
                bytes1(0),
                this,
                nonce[identityOwner(identity)],
                identity,
                "revokeDelegate",
                delegateType,
                delegate
            )
        );

        address signer = ecrecover(hash, sigV, sigR, sigS);
        require(signer == identityOwner(identity), "DIDRegistry: invalid signature");

        nonce[signer]++;
        delegates[identity][delegateType][delegate] = 0;
        emit DIDDelegateChanged(identity, delegateType, delegate, 0, changed[identity]);
        changed[identity] = block.number;
    }

    // ============ Attribute Management ============

    /**
     * @notice Set an attribute for a DID
     * @dev ERC-1056 §setAttribute. `onlyOwner`; event-only (no storage except
     *      `changed`); emits DIDAttributeChanged with validTo = block.timestamp + validity.
     * @param identity The DID to modify
     * @param name Attribute name (e.g., keccak256("did/pub/Ed25519/veriKey"))
     * @param value Attribute value (encoded public key, URL, etc.)
     * @param validity Validity period in seconds
     */
    function setAttribute(
        address identity,
        bytes32 name,
        bytes memory value,
        uint validity
    ) public onlyOwner(identity, msg.sender) {
        uint validTo = block.timestamp + validity;
        emit DIDAttributeChanged(identity, name, value, validTo, changed[identity]);
        changed[identity] = block.number;
    }

    /**
     * @notice Set attribute via signed message
     * @dev ERC-1056 §setAttributeSigned. Digest: 0x19 || 0x00 || this || nonce[owner]
     *      || identity || "setAttribute" || name || value || validity.
     *      Increments `nonce[signer]`; emits DIDAttributeChanged.
     * @param identity The DID to modify
     * @param sigV ECDSA signature V
     * @param sigR ECDSA signature R
     * @param sigS ECDSA signature S
     * @param name Attribute name
     * @param value Attribute value
     * @param validity Validity period in seconds
     */
    function setAttributeSigned(
        address identity,
        uint8 sigV,
        bytes32 sigR,
        bytes32 sigS,
        bytes32 name,
        bytes memory value,
        uint validity
    ) public {
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0x19),
                bytes1(0),
                this,
                nonce[identityOwner(identity)],
                identity,
                "setAttribute",
                name,
                value,
                validity
            )
        );

        address signer = ecrecover(hash, sigV, sigR, sigS);
        require(signer == identityOwner(identity), "DIDRegistry: invalid signature");

        nonce[signer]++;
        uint validTo = block.timestamp + validity;
        uint previousChange = changed[identity];
        changed[identity] = block.number;
        emit DIDAttributeChanged(identity, name, value, validTo, previousChange);
    }

    /**
     * @notice Revoke an attribute
     * @dev ERC-1056 §revokeAttribute. `onlyOwner`; emits DIDAttributeChanged with
     *      validTo = 0.
     * @param identity The DID to modify
     * @param name Attribute name
     * @param value Attribute value (must match to revoke)
     */
    function revokeAttribute(
        address identity,
        bytes32 name,
        bytes memory value
    ) public onlyOwner(identity, msg.sender) {
        emit DIDAttributeChanged(identity, name, value, 0, changed[identity]);
        changed[identity] = block.number;
    }

    /**
     * @notice Revoke attribute via signed message
     * @dev ERC-1056 §revokeAttributeSigned. Digest: 0x19 || 0x00 || this || nonce[owner]
     *      || identity || "revokeAttribute" || name || value.
     *      Increments `nonce[signer]`; emits DIDAttributeChanged (validTo 0).
     * @param identity The DID to modify
     * @param sigV ECDSA signature V
     * @param sigR ECDSA signature R
     * @param sigS ECDSA signature S
     * @param name Attribute name
     * @param value Attribute value (must match to revoke)
     */
    function revokeAttributeSigned(
        address identity,
        uint8 sigV,
        bytes32 sigR,
        bytes32 sigS,
        bytes32 name,
        bytes memory value
    ) public {
        bytes32 hash = keccak256(
            abi.encodePacked(
                bytes1(0x19),
                bytes1(0),
                this,
                nonce[identityOwner(identity)],
                identity,
                "revokeAttribute",
                name,
                value
            )
        );

        address signer = ecrecover(hash, sigV, sigR, sigS);
        require(signer == identityOwner(identity), "DIDRegistry: invalid signature");

        nonce[signer]++;
        uint previousChange = changed[identity];
        changed[identity] = block.number;
        emit DIDAttributeChanged(identity, name, value, 0, previousChange);
    }
}
