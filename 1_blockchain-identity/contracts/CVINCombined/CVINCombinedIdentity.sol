// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINCombinedIdentity — the thesis's proposed hybrid (ERC-1056 + ERC-735)
 * @author CVIN research project
 * @notice Single-contract composition of an event-based lightweight identity
 *         registry with on-chain claim storage for the safety-critical subset
 *         of vehicle credentials.
 *
 * @dev DESIGN RATIONALE (thesis hypothesis):
 *
 *      ERC-1056 side — EVENTS ARE CHEAP. The vast majority of vehicle
 *      identity operations (attribute updates, service endpoints, rotating
 *      session keys/delegates, ownership transfer) do not need on-chain
 *      readability by other contracts; they only need a tamper-evident,
 *      indexable history from which an off-chain resolver builds the DID
 *      document. Emitting events + a single `changed` block pointer per
 *      identity costs a fraction of SSTORE-based registries, and every
 *      address is an identity by default (zero-cost identity creation).
 *
 *      ERC-735 side — SAFETY-CRITICAL CLAIMS MUST BE O(1) ON-CHAIN
 *      VERIFIABLE. A vehicle interacting with road infrastructure or another
 *      vehicle cannot walk an event log inside the EVM; type-approval,
 *      manufacturer attestation and periodic-inspection credentials are
 *      therefore stored on-chain as ERC-735-style claims whose issuer
 *      signature is verified with ecrecover AT ADD TIME, so any contract can
 *      later check `getClaim` in O(1) without re-verifying signatures.
 *
 *      Combining both in ONE contract gives a shared ownership model (the
 *      ERC-1056 `identityOwner` gates both attribute events and claim
 *      management) and lets the gas benchmark measure the hybrid's combined
 *      cost in a single deployment.
 *
 *      Signature scheme for claims: the issuer signs the RAW keccak256 digest
 *      keccak256(abi.encodePacked(address(this), identity, topic, data))
 *      (no EIP-191 envelope), binding the claim to this registry instance and
 *      the subject identity. This mirrors the bare-digest signing pattern of
 *      the ERC-1056 reference registry's signed meta-transactions.
 *
 *      Issuer revocation is sticky (REVIEW_02 K-2): when the ISSUER removes a
 *      claim, keccak256(issuer, digest) is recorded and addClaim rejects that
 *      signed content from then on. Keying on the digest rather than the
 *      signature bytes also rejects a malleated (high-s) copy of the old
 *      signature. The issuer re-issues by signing new data. An OWNER removal
 *      is not a revocation and records nothing; the issuer can still revoke
 *      the content afterwards with revokeClaimContent, which does not need
 *      the claim to be anchored (Pass 2). There is still no nonce or
 *      expiry in the signed payload, so an older, never-revoked claim for the
 *      same (issuer, topic) can be re-anchored after the issuer replaced it.
 *
 *      Shared registry: one deployment serves all identities (the identity is the
 *      vehicle address). Self-contained, no imports (project pins OZ 5.0.2, unused).
 *      Deviations: ERC-1056 `*Signed` meta-transaction variants and `nonce` are
 *      omitted; ERC-735 events carry `identity` and differ from the draft
 *      signatures (ClaimRemoved drops fields); no ClaimRequested/ClaimChanged
 *      (re-adding emits ClaimAdded again).
 * @custom:standard ERC-1056 (Lightweight Identity / did:ethr) https://eips.ethereum.org/EIPS/eip-1056
 * @custom:standard ERC-735 (Claim Holder, draft; claim side is ERC-735-style) https://github.com/ethereum/EIPs/issues/735
 * @custom:standard W3C DID Core (via did:ethr event resolution) https://www.w3.org/TR/did-core/
 * @custom:security No issuer registry and no VIN binding (unlike CVINVehicleClaimHolder): any identity
 *                  owner can anchor claims from any signer; verifiers must filter by issuer ({hasValidClaim}).
 * @custom:security No EIP-2 low-s check; revocation keys on the digest so a malleated signature cannot bypass it.
 * @custom:security `changeOwner` has no zero-address check (same as the ERC-1056 reference).
 * @custom:security `revokeDelegate` sets validTo = block.timestamp, so {validDelegate} (strict >) is false in that block.
 * @custom:security Raw-digest signatures (no EIP-191) are not portable to/from CVINVehicleClaimHolder.
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 5)
 * @custom:see sandbox/options/cvin-combined/adapter.js
 */
contract CVINCombinedIdentity {
    // ============ Claim topics (safety-critical subset) ============

    /// @notice Claim topic: VIN attestation (no VIN binding enforced).
    uint256 public constant CLAIM_TOPIC_VIN = 1; // VIN attestation
    /// @notice Claim topic: manufacturer / type approval.
    uint256 public constant CLAIM_TOPIC_MANUFACTURER = 2; // manufacturer / type approval
    /// @notice Claim topic: periodic technical inspection.
    uint256 public constant CLAIM_TOPIC_INSPECTION = 3; // periodic technical inspection

    /// @dev ECDSA over raw keccak256 digest (scheme id per ERC-735 convention).
    uint256 public constant SCHEME_ECDSA = 1;

    // ============ ERC-1056-style identity state ============

    /// @dev Explicit owner override; address(0) means self-owned (default).
    mapping(address => address) private _owners;

    /// @notice ERC-1056 delegate expiry.
    /// @dev delegates[identity][delegateType][delegate] = validity expiry timestamp.
    mapping(address => mapping(bytes32 => mapping(address => uint256))) public delegates;

    /// @notice ERC-1056 `changed` pointer (DID-event chain head).
    /// @dev Block number of the identity's last DID event (DIDOwnerChanged,
    ///      DIDDelegateChanged, DIDAttributeChanged): the head of the ERC-1056
    ///      changed -> previousChange event-log linked list. Claim add/remove
    ///      does not touch it (REVIEW_02 K-6), so a resolver walking the chain
    ///      never lands on a block that holds only a claim event.
    mapping(address => uint256) public changed;

    // ============ ERC-735-style claim state ============

    /// @dev Stored ERC-735-style claim (topic, scheme, issuer, signature, data, uri).
    struct Claim {
        uint256 topic;
        uint256 scheme;
        address issuer;
        bytes signature;
        bytes data;
        string uri;
    }

    /// @dev claims[identity][claimId] where claimId = keccak256(issuer, topic).
    mapping(address => mapping(bytes32 => Claim)) private _claims;

    /// @dev claimIdsByTopic[identity][topic] -> list of claim ids.
    mapping(address => mapping(uint256 => bytes32[])) private _claimIdsByTopic;

    /// @notice Issuer-revoked claim content (REVIEW_02 K-2).
    /// @dev key = keccak256(abi.encodePacked(issuer, keccak256(abi.encodePacked(address(this), identity, topic, data)))),
    ///      i.e. the issuer and the raw digest it signed. Set by an issuer
    ///      removal or by revokeClaimContent. No extra event or view, to keep the deployment
    ///      cost of the fix small; verifiers query this getter.
    mapping(bytes32 => bool) public revokedClaims;

    // ============ Events ============

    // ERC-1056-style
    /// @notice ERC-1056: identity owner changed.
    /// @param identity The identity.
    /// @param owner New owner.
    /// @param previousChange Previous `changed[identity]` block.
    event DIDOwnerChanged(address indexed identity, address owner, uint256 previousChange);
    /// @notice ERC-1056: delegate added or revoked.
    /// @param identity The identity.
    /// @param delegateType Delegate type (e.g. veriKey / sigAuth).
    /// @param delegate The delegate address.
    /// @param validTo Expiry timestamp (block.timestamp on revoke).
    /// @param previousChange Previous `changed[identity]` block.
    event DIDDelegateChanged(
        address indexed identity,
        bytes32 delegateType,
        address delegate,
        uint256 validTo,
        uint256 previousChange
    );
    /// @notice ERC-1056: attribute published or revoked (event-only storage).
    /// @param identity The identity.
    /// @param name Attribute name.
    /// @param value Attribute value.
    /// @param validTo Expiry timestamp (0 = revoked).
    /// @param previousChange Previous `changed[identity]` block.
    event DIDAttributeChanged(
        address indexed identity,
        bytes32 name,
        bytes value,
        uint256 validTo,
        uint256 previousChange
    );

    /**
     * @notice CVIN extension: ERC-1056-style change marker for the ERC-735 side.
     * @dev ERC-1056-style change marker for the ERC-735 side. Originally (defect
     *      D22) addClaim and removeClaim advanced `changed[identity]`, so without
     *      an event that carries `previousChange` the did:ethr pointer walk
     *      (changed -> previousChange -> ... -> 0) was cut at every claim
     *      operation. Emitted alongside ClaimAdded / ClaimRemoved with
     *      previousChange = the current `changed[identity]` value; `removed`
     *      distinguishes the two.
     * @custom:note Corrected stale text: claims NO LONGER advance `changed[identity]`
     *      (REVIEW_02 K-6, merge decision M-A). `previousChange` here is a correlation
     *      value only (the DID chain head at claim time), not a pointer the resolver follows.
     * @param identity The identity.
     * @param claimId The claim identifier.
     * @param topic Claim topic.
     * @param removed False for add/update, true for removal.
     * @param previousChange Current `changed[identity]` (correlation only).
     */
    event DIDClaimChanged(
        address indexed identity,
        bytes32 claimId,
        uint256 topic,
        bool removed,
        uint256 previousChange
    );

    // ERC-735-style
    /// @notice ERC-735-style: claim added or updated (also emitted on update).
    /// @param claimId keccak256(abi.encodePacked(issuer, topic)).
    /// @param identity The subject identity.
    /// @param topic Claim topic.
    /// @param scheme Signature scheme (1).
    /// @param issuer Claim issuer.
    /// @param signature Raw-digest issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    event ClaimAdded(
        bytes32 indexed claimId,
        address indexed identity,
        uint256 indexed topic,
        uint256 scheme,
        address issuer,
        bytes signature,
        bytes data,
        string uri
    );
    /// @notice ERC-735-style: claim removed.
    /// @param claimId The claim identifier.
    /// @param identity The subject identity.
    /// @param topic Claim topic.
    /// @param issuer Claim issuer.
    event ClaimRemoved(
        bytes32 indexed claimId,
        address indexed identity,
        uint256 indexed topic,
        address issuer
    );

    // ============ Modifiers ============

    /// @dev Restricts to {identityOwner}(`identity`). Reverts "CVINCombined: unauthorized".
    modifier onlyIdentityOwner(address identity) {
        require(msg.sender == identityOwner(identity), "CVINCombined: unauthorized");
        _;
    }

    // ============ ERC-1056-style: ownership ============

    /// @notice Every address is an identity; it owns itself until changed.
    /// @dev ERC-1056.
    /// @param identity The identity.
    /// @return The explicit owner, or `identity` itself.
    function identityOwner(address identity) public view returns (address) {
        address owner = _owners[identity];
        if (owner != address(0)) {
            return owner;
        }
        return identity;
    }

    /// @notice Transfer control of an identity (key rotation / vehicle sale).
    /// @dev ERC-1056. Identity owner only. No zero-address check. Emits {DIDOwnerChanged}; advances `changed`.
    /// @param identity The identity.
    /// @param newOwner The new owner.
    function changeOwner(
        address identity,
        address newOwner
    ) external onlyIdentityOwner(identity) {
        _owners[identity] = newOwner;
        emit DIDOwnerChanged(identity, newOwner, changed[identity]);
        changed[identity] = block.number;
    }

    // ============ ERC-1056-style: delegates ============

    /// @notice Add a delegate key (e.g. vehicle session/telematics key) with a TTL.
    /// @dev ERC-1056. Identity owner only. validTo = now + validity. Emits {DIDDelegateChanged}; advances `changed`.
    /// @param identity The identity.
    /// @param delegateType Delegate type.
    /// @param delegate The delegate address.
    /// @param validity Lifetime in seconds.
    function addDelegate(
        address identity,
        bytes32 delegateType,
        address delegate,
        uint256 validity
    ) external onlyIdentityOwner(identity) {
        uint256 validTo = block.timestamp + validity;
        delegates[identity][delegateType][delegate] = validTo;
        emit DIDDelegateChanged(identity, delegateType, delegate, validTo, changed[identity]);
        changed[identity] = block.number;
    }

    /// @notice Revoke a delegate immediately.
    /// @dev ERC-1056. Identity owner only. validTo = block.timestamp. Emits {DIDDelegateChanged}; advances `changed`.
    /// @param identity The identity.
    /// @param delegateType Delegate type.
    /// @param delegate The delegate address.
    function revokeDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) external onlyIdentityOwner(identity) {
        delegates[identity][delegateType][delegate] = block.timestamp;
        emit DIDDelegateChanged(identity, delegateType, delegate, block.timestamp, changed[identity]);
        changed[identity] = block.number;
    }

    /// @notice Check whether a delegate is currently valid.
    /// @dev ERC-1056. True iff expiry > block.timestamp.
    /// @param identity The identity.
    /// @param delegateType Delegate type.
    /// @param delegate The delegate address.
    /// @return True if valid.
    function validDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) external view returns (bool) {
        return delegates[identity][delegateType][delegate] > block.timestamp;
    }

    // ============ ERC-1056-style: attributes (event-only, cheap) ============

    /**
     * @notice Publish an identity attribute purely as an event — no storage
     *         write except the `changed` pointer. Off-chain resolvers rebuild
     *         the DID document by walking the event history.
     * @dev ERC-1056. Identity owner only. Emits {DIDAttributeChanged}; advances `changed`.
     * @param identity The identity.
     * @param name Attribute name.
     * @param value Attribute value.
     * @param validity Lifetime in seconds.
     */
    function setAttribute(
        address identity,
        bytes32 name,
        bytes calldata value,
        uint256 validity
    ) external onlyIdentityOwner(identity) {
        emit DIDAttributeChanged(identity, name, value, block.timestamp + validity, changed[identity]);
        changed[identity] = block.number;
    }

    /// @notice Revoke a previously published attribute (validTo = 0).
    /// @dev ERC-1056. Identity owner only. Emits {DIDAttributeChanged}; advances `changed`.
    /// @param identity The identity.
    /// @param name Attribute name.
    /// @param value Attribute value.
    function revokeAttribute(
        address identity,
        bytes32 name,
        bytes calldata value
    ) external onlyIdentityOwner(identity) {
        emit DIDAttributeChanged(identity, name, value, 0, changed[identity]);
        changed[identity] = block.number;
    }

    // ============ ERC-735-style: on-chain claims ============

    /**
     * @notice Add a safety-critical claim about `identity`, issued (signed)
     *         by `issuer`. The issuer signature over the raw digest
     *         keccak256(abi.encodePacked(address(this), identity, topic, data))
     *         is verified with ecrecover before the claim is stored, so later
     *         reads are O(1) and need no re-verification.
     * @dev ERC-735 style. Identity owner only. Rejects revoked content (K-2).
     *      No issuer whitelist, no VIN binding. Emits {ClaimAdded} and
     *      {DIDClaimChanged}(removed=false); does not advance `changed` (K-6).
     * @param identity The subject identity.
     * @param topic Claim topic.
     * @param scheme Must be SCHEME_ECDSA (1).
     * @param issuer Expected signer.
     * @param signature 65-byte raw-digest signature (v must be 27/28).
     * @param data Claim payload.
     * @param uri Off-chain claim location.
     * @return claimId keccak256(abi.encodePacked(issuer, topic))
     */
    function addClaim(
        address identity,
        uint256 topic,
        uint256 scheme,
        address issuer,
        bytes calldata signature,
        bytes calldata data,
        string calldata uri
    ) external onlyIdentityOwner(identity) returns (bytes32 claimId) {
        require(scheme == SCHEME_ECDSA, "CVINCombined: unsupported scheme");
        require(issuer != address(0), "CVINCombined: zero issuer");
        bytes32 digest = _claimDigest(identity, topic, data);
        require(
            _recoverRawDigest(digest, signature) == issuer,
            "CVINCombined: invalid claim signature"
        );
        require(
            !revokedClaims[keccak256(abi.encodePacked(issuer, digest))],
            "CVINCombined: claim revoked by issuer"
        );

        claimId = keccak256(abi.encodePacked(issuer, topic));

        // Only index the topic list on first insertion (re-adding updates in place).
        if (_claims[identity][claimId].issuer == address(0)) {
            _claimIdsByTopic[identity][topic].push(claimId);
        }

        _claims[identity][claimId] = Claim({
            topic: topic,
            scheme: scheme,
            issuer: issuer,
            signature: signature,
            data: data,
            uri: uri
        });

        emit ClaimAdded(claimId, identity, topic, scheme, issuer, signature, data, uri);
        // changed[] is deliberately NOT advanced (REVIEW_02 K-6): it is the ERC-1056
        // DID-event chain head and claims are not DID-document state. The claim history
        // stays indexable through DIDClaimChanged (defect D22); its last argument is the
        // chain head at the time of the claim, for correlation, not a pointer the
        // resolver walk follows (merge decision M-A, 2026-10-06).
        emit DIDClaimChanged(identity, claimId, topic, false, changed[identity]);
    }

    /// @notice Remove a claim (identity owner or the claim's issuer).
    /// @dev An issuer removal also records the signed content in revokedClaims
    ///      so addClaim cannot bring it back (K-2). An owner removal does not.
    ///      Emits {ClaimRemoved} and {DIDClaimChanged}(removed=true).
    /// @param identity The subject identity.
    /// @param claimId The claim identifier.
    function removeClaim(address identity, bytes32 claimId) external {
        Claim memory claim = _claims[identity][claimId];
        require(claim.issuer != address(0), "CVINCombined: claim not found");
        require(
            msg.sender == identityOwner(identity) || msg.sender == claim.issuer,
            "CVINCombined: unauthorized"
        );

        if (msg.sender == claim.issuer) {
            revokedClaims[
                keccak256(
                    abi.encodePacked(
                        claim.issuer,
                        keccak256(abi.encodePacked(address(this), identity, claim.topic, claim.data))
                    )
                )
            ] = true;
        }

        _deleteClaim(identity, claimId, claim.topic, claim.issuer);
    }

    /**
     * @notice Issuer-side revocation of signed claim CONTENT about `identity`,
     *         whether or not it is currently anchored (REVIEW_02 K-2, Pass 2).
     * @dev removeClaim needs the claim to exist, so an owner could pre-empt a
     *      revocation by removing the claim first (the issuer's removeClaim
     *      then reverts) and re-anchor the old signature later. This records
     *      keccak256(msg.sender, digest) unconditionally; it can only ever
     *      block claims signed by the caller itself, so it needs no access
     *      control. If the caller's claim for `topic` is anchored with exactly
     *      this data it is removed too; other (re-issued) data is left alone.
     *      CVIN extension. Emits {ClaimRemoved}/{DIDClaimChanged} only if anchored.
     * @param identity The subject identity.
     * @param topic Claim topic.
     * @param data Claim payload of the revoked content.
     */
    function revokeClaimContent(address identity, uint256 topic, bytes calldata data) external {
        revokedClaims[keccak256(abi.encodePacked(msg.sender, _claimDigest(identity, topic, data)))] = true;

        bytes32 claimId = keccak256(abi.encodePacked(msg.sender, topic));
        Claim storage claim = _claims[identity][claimId];
        if (claim.issuer != address(0) && keccak256(claim.data) == keccak256(data)) {
            _deleteClaim(identity, claimId, topic, msg.sender);
        }
    }

    /// @dev Unindex (swap-and-pop), delete and emit ClaimRemoved. changed[]
    ///      is not advanced (K-6), see addClaim. Also emits DIDClaimChanged(removed=true).
    /// @param identity The subject identity.
    /// @param claimId The claim identifier.
    /// @param topic Claim topic.
    /// @param issuer Claim issuer.
    function _deleteClaim(address identity, bytes32 claimId, uint256 topic, address issuer) private {
        bytes32[] storage ids = _claimIdsByTopic[identity][topic];
        for (uint256 i = 0; i < ids.length; i++) {
            if (ids[i] == claimId) {
                ids[i] = ids[ids.length - 1];
                ids.pop();
                break;
            }
        }

        delete _claims[identity][claimId];

        emit ClaimRemoved(claimId, identity, topic, issuer);
        emit DIDClaimChanged(identity, claimId, topic, true, changed[identity]);
    }

    /// @notice O(1) claim lookup for on-chain verifiers.
    /// @dev ERC-735 style (extra `identity` argument). All-zero values if absent.
    /// @param identity The subject identity.
    /// @param claimId The claim identifier.
    /// @return topic Claim topic.
    /// @return scheme Signature scheme.
    /// @return issuer Claim issuer (zero if absent).
    /// @return signature Issuer signature.
    /// @return data Claim payload.
    /// @return uri Off-chain claim location.
    function getClaim(
        address identity,
        bytes32 claimId
    )
        external
        view
        returns (
            uint256 topic,
            uint256 scheme,
            address issuer,
            bytes memory signature,
            bytes memory data,
            string memory uri
        )
    {
        Claim memory claim = _claims[identity][claimId];
        return (claim.topic, claim.scheme, claim.issuer, claim.signature, claim.data, claim.uri);
    }

    /// @notice All claim ids of a given topic for an identity.
    /// @dev ERC-735 style.
    /// @param identity The subject identity.
    /// @param topic Claim topic.
    /// @return The claim identifiers.
    function getClaimIdsByTopic(
        address identity,
        uint256 topic
    ) external view returns (bytes32[] memory) {
        return _claimIdsByTopic[identity][topic];
    }

    /// @notice Convenience predicate: does `identity` hold a claim on `topic` from `issuer`?
    /// @dev An empty slot (issuer == address(0)) is never a valid claim
    ///      (REVIEW_02 K-11: hasValidClaim(id, 0, address(0)) used to be true).
    ///      CVIN extension.
    /// @param identity The subject identity.
    /// @param topic Claim topic.
    /// @param issuer Required issuer.
    /// @return True if such a claim is anchored.
    function hasValidClaim(
        address identity,
        uint256 topic,
        address issuer
    ) external view returns (bool) {
        if (issuer == address(0)) {
            return false;
        }
        bytes32 claimId = keccak256(abi.encodePacked(issuer, topic));
        Claim storage claim = _claims[identity][claimId];
        return claim.issuer == issuer && claim.topic == topic;
    }

    // ============ Internal ============

    /// @dev The raw claim digest the issuer signs.
    /// @param identity The subject identity.
    /// @param topic Claim topic.
    /// @param data Claim payload.
    /// @return keccak256(abi.encodePacked(address(this), identity, topic, data)).
    function _claimDigest(
        address identity,
        uint256 topic,
        bytes calldata data
    ) internal view returns (bytes32) {
        return keccak256(abi.encodePacked(address(this), identity, topic, data));
    }

    /// @dev ecrecover over the raw (non-EIP-191) claim digest. Returns address(0)
    ///      for a non-65-byte signature or v not in {27, 28}; no low-s check.
    /// @param digest The raw digest.
    /// @param signature 65-byte r||s||v signature.
    /// @return The recovered signer, or address(0).
    function _recoverRawDigest(
        bytes32 digest,
        bytes calldata signature
    ) internal pure returns (address) {
        if (signature.length != 65) {
            return address(0);
        }
        bytes32 r = bytes32(signature[0:32]);
        bytes32 s = bytes32(signature[32:64]);
        uint8 v = uint8(signature[64]);
        if (v != 27 && v != 28) {
            return address(0);
        }
        return ecrecover(digest, v, r, s);
    }
}
