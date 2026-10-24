// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title IERC735 - Claim Holder interface (self-contained, no external deps)
 * @dev Based on the ERC-735 draft standard (https://github.com/ethereum/EIPs/issues/735).
 *
 * Note on spec compliance: ERC-735 was never finalized as an EIP. This interface
 * reproduces the widely used draft (as deployed by ERC-725/735 identity stacks such
 * as Origin Protocol and ONCHAINID). The draft couples claim approval to ERC-734
 * key management (CLAIM key approval flow via `approve`); this implementation
 * replaces ERC-734 key management with a simple contract owner acting as the
 * MANAGEMENT key, which is documented in CVINVehicleClaimHolder below.
 * @author CVIN research project
 * @notice Draft ERC-735 claim-holder interface (no `changeClaim`/`approve`).
 * @custom:standard ERC-735 (Claim Holder, draft issue, never an EIP) https://github.com/ethereum/EIPs/issues/735
 */
interface IERC735 {
    /// @notice ERC-735: a claim was requested (emitted synchronously by addClaim in this repo).
    /// @param claimRequestId Request id (here: uint256(claimId)).
    /// @param topic Claim topic.
    /// @param scheme Signature scheme (1 = ECDSA).
    /// @param issuer Claim issuer.
    /// @param signature Issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    event ClaimRequested(
        uint256 indexed claimRequestId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    /// @notice ERC-735: a new claim was added.
    /// @param claimId claimId Claim identifier, keccak256(abi.encodePacked(issuer, topic)).
    /// @param topic Claim topic.
    /// @param scheme Signature scheme (1 = ECDSA).
    /// @param issuer Claim issuer.
    /// @param signature Issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    event ClaimAdded(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    /// @notice ERC-735: a claim was removed.
    /// @param claimId claimId Claim identifier, keccak256(abi.encodePacked(issuer, topic)).
    /// @param topic Claim topic.
    /// @param scheme Signature scheme (1 = ECDSA).
    /// @param issuer Claim issuer.
    /// @param signature Issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    event ClaimRemoved(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    /// @notice ERC-735: an existing claim was updated.
    /// @param claimId claimId Claim identifier, keccak256(abi.encodePacked(issuer, topic)).
    /// @param topic Claim topic.
    /// @param scheme Signature scheme (1 = ECDSA).
    /// @param issuer Claim issuer.
    /// @param signature Issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    event ClaimChanged(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    /// @notice ERC-735: returns a claim by id.
    /// @param claimId The claim identifier.
    /// @return topic Claim topic.
    /// @return scheme Signature scheme.
    /// @return issuer Claim issuer.
    /// @return signature Issuer signature.
    /// @return data Claim payload.
    /// @return uri Off-chain claim location.
    function getClaim(bytes32 claimId)
        external
        view
        returns (
            uint256 topic,
            uint256 scheme,
            address issuer,
            bytes memory signature,
            bytes memory data,
            string memory uri
        );

    /// @notice ERC-735: claim ids for a topic.
    /// @param topic Claim topic.
    /// @return claimIds The claim identifiers.
    function getClaimIdsByTopic(uint256 topic)
        external
        view
        returns (bytes32[] memory claimIds);

    /// @notice ERC-735: add or update a claim.
    /// @param topic Claim topic.
    /// @param scheme Signature scheme.
    /// @param issuer Claim issuer.
    /// @param signature Issuer signature.
    /// @param data Claim payload.
    /// @param uri Off-chain claim location.
    /// @return claimRequestId Request id (in this repo: the claimId).
    function addClaim(
        uint256 topic,
        uint256 scheme,
        address issuer,
        bytes calldata signature,
        bytes calldata data,
        string calldata uri
    ) external returns (bytes32 claimRequestId);

    /// @notice ERC-735: remove a claim.
    /// @param claimId The claim identifier.
    /// @return success True on removal.
    function removeClaim(bytes32 claimId) external returns (bool success);
}

/**
 * @title CVINVehicleClaimHolder
 * @author CVIN research project
 * @dev ERC-735 Claim Holder implementation for connected vehicle identity (CVIN).
 * @notice One contract instance = one vehicle identity. Deployment IS identity
 *         creation. Trusted issuers (manufacturer, inspection authority, insurer)
 *         sign attestations off-chain; the vehicle owner anchors them on-chain
 *         as ERC-735 claims.
 *
 * Vehicle-specific claim topics:
 *   VIN_ATTESTATION   = 1  (attestation binding this identity to a VIN)
 *   MANUFACTURER_CERT = 2  (manufacturer birth certificate)
 *   INSPECTION        = 3  (periodic technical inspection)
 *   INSURANCE         = 4  (insurance coverage attestation)
 *
 * Deviations from the ERC-735 draft (documented for the thesis gas comparison):
 * - Key management: the draft delegates authorization to ERC-734 keys
 *   (MANAGEMENT / CLAIM keys). Here a single `owner` address plays the
 *   MANAGEMENT-key role (addClaim/removeClaim gating, ownership transfer).
 * - Claim approval: the draft's asynchronous request/approve flow (ClaimRequested
 *   + approve()) is collapsed into synchronous addClaim; ClaimRequested is
 *   emitted with the resulting claimId for event-shape compatibility.
 * - Signature verification is enforced ON-CHAIN at addClaim time (the draft
 *   leaves verification to off-chain verifiers): the issuer must have ECDSA-signed
 *   keccak256(abi.encodePacked(identityAddress, topic, data)) with the standard
 *   "\x19Ethereum Signed Message:\n32" prefix. Contract-account issuers
 *   (ERC-1271) are therefore not supported.
 * - Issuer registry (docs/DEFECT_LOG.md D25a): the draft trusts any signer. Here
 *   the owner maintains an (issuer, topic) whitelist — authorizeIssuer /
 *   revokeIssuer / isAuthorizedIssuer — and addClaim requires the claim's issuer
 *   to be authorized for the claim's topic. The single exception is a
 *   SELF-ISSUED claim (issuer == owner): the ERC-735 draft lets an identity
 *   issue claims about itself, and the owner plays the identity's key here, so
 *   such a claim needs no registry entry (a verifier sees issuer == owner and
 *   reads it as self-asserted). Authorizations belong to the vehicle, not the
 *   owner: they survive transferOwnership (the new owner may revoke them).
 *   Revoking an issuer is forward-looking: claims it already issued stay until
 *   removeClaim.
 * - VIN binding (D25b): a VIN_ATTESTATION (topic 1) claim must attest THIS
 *   holder's VIN — see _encodesHolderVin for the exact encoding rule.
 * - Issuer revocation is sticky (REVIEW_02 K-2): when the ISSUER removes a
 *   claim, the signed content (issuer, keccak256(identity, topic, data)) is
 *   recorded in `revokedClaims`, and addClaim rejects that content from then
 *   on, so the owner cannot re-anchor a revoked attestation with the old
 *   signature. The key is the signed digest, not the signature bytes, so a
 *   re-encoded signature over the same content is rejected too. The issuer
 *   re-issues by signing new data (e.g. a new inspection record). An OWNER
 *   removal is not a revocation (the owner merely stops presenting a claim
 *   it holds) and records nothing, so the owner may re-anchor it later -
 *   unless the issuer revokes the content with revokeClaimContent(topic,
 *   data), which works whether or not the claim is currently anchored (an
 *   owner can no longer pre-empt revocation by removing the claim first).
 *   The signature still carries no nonce or expiry: an older, never-revoked
 *   claim for the same (issuer, topic) can be re-anchored after the issuer
 *   replaced it with newer data. Closing that needs an issuer-side nonce or
 *   expiry in the signed payload (not done; see docs/review02/PASS1_K.md).
 *
 * Self-contained: no OpenZeppelin imports (project pins OZ 5.0.2).
 * @custom:standard ERC-735 (Claim Holder, draft) https://github.com/ethereum/EIPs/issues/735
 * @custom:standard ERC-734 (Key Manager, draft; MANAGEMENT role = owner) https://github.com/ethereum/EIPs/issues/734
 * @custom:standard EIP-191 (signed data) https://eips.ethereum.org/EIPS/eip-191
 * @custom:standard EIP-2 (low-s signatures) https://eips.ethereum.org/EIPS/eip-2
 * @custom:standard ERC-173 (ownership surface) https://eips.ethereum.org/EIPS/eip-173
 * @custom:security No nonce or expiry in the signed payload: an older, never-revoked claim for the same
 *                  (issuer, topic) can be re-anchored after the issuer replaced it.
 * @custom:security ERC-1271 (contract) issuers are unsupported. No renounceOwnership.
 * @custom:security Signature scheme (EIP-191) differs from CVINCombinedIdentity (raw digest); signatures are not portable.
 * @custom:see docs/smart-contracts/04-account-claim-identity-erc725-735-4337-combined.md (section 3)
 * @custom:see sandbox/options/erc-735/adapter.js
 */
contract CVINVehicleClaimHolder is IERC735 {
    // ============ Vehicle claim topics ============
    /// @notice CVIN claim topic: VIN attestation (VIN-bound, see {_encodesHolderVin}).
    uint256 public constant VIN_ATTESTATION = 1;
    /// @notice CVIN claim topic: manufacturer birth certificate.
    uint256 public constant MANUFACTURER_CERT = 2;
    /// @notice CVIN claim topic: periodic technical inspection.
    uint256 public constant INSPECTION = 3;
    /// @notice CVIN claim topic: insurance coverage attestation.
    uint256 public constant INSURANCE = 4;

    /// @dev Signature scheme identifier: 1 = ECDSA (per ERC-735 draft convention)
    uint256 public constant ECDSA_SCHEME = 1;

    // ============ Identity state ============

    /// @notice Vehicle Identification Number this identity represents
    string public vin;

    /// @notice keccak256 hash of the VIN (stable identifier)
    bytes32 public vinHash;

    /// @notice Identity owner (plays the ERC-734 MANAGEMENT-key role)
    address public owner;

    /// @dev Stored ERC-735 claim (topic, scheme, issuer, signature, data, uri).
    struct Claim {
        uint256 topic;
        uint256 scheme;
        address issuer;
        bytes signature;
        bytes data;
        string uri;
    }

    /// @dev claimId => Claim. claimId = keccak256(abi.encodePacked(issuer, topic))
    mapping(bytes32 => Claim) private claims;

    /// @dev topic => list of claimIds
    mapping(uint256 => bytes32[]) private claimIdsByTopic;

    /// @dev Issuer registry (D25a): issuer => topic => authorized to issue on that topic
    mapping(address => mapping(uint256 => bool)) private authorizedIssuers;
    /// @notice Issuer-revoked claim content (REVIEW_02 K-2).
    /// @dev key = keccak256(abi.encodePacked(issuer, keccak256(abi.encodePacked(address(this), topic, data)))),
    ///      i.e. the issuer and the digest it signed. Set by an issuer
    ///      removal (the ClaimRemoved whose tx sender is the issuer) or by
    ///      revokeClaimContent (a tx from the issuer to that function). No extra event or view, to keep the per-vehicle
    ///      deployment cost of the fix small; verifiers query this getter.
    mapping(bytes32 => bool) public revokedClaims;

    // ============ Events (identity lifecycle, beyond ERC-735) ============
    /// @notice Emitted on construction and {transferOwnership}.
    /// @param previousOwner Previous owner (zero at construction).
    /// @param newOwner New owner.
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    /// @notice CVIN extension: emitted once at deployment (identity creation).
    /// @param vinHash keccak256 of the VIN.
    /// @param vin The VIN.
    /// @param owner Initial owner (deployer).
    event VehicleIdentityCreated(bytes32 indexed vinHash, string vin, address indexed owner);
    /// @notice CVIN extension (D25a): issuer whitelisted for a topic.
    /// @param issuer The issuer.
    /// @param topic The topic.
    event IssuerAuthorized(address indexed issuer, uint256 indexed topic);
    /// @notice CVIN extension (D25a): issuer removed from a topic whitelist.
    /// @param issuer The issuer.
    /// @param topic The topic.
    event IssuerRevoked(address indexed issuer, uint256 indexed topic);

    // ============ Modifiers ============
    /// @dev Restricts to {owner} (ERC-734 MANAGEMENT-key role).
    modifier onlyOwner() {
        require(msg.sender == owner, "ERC735: caller is not the owner");
        _;
    }

    // ============ Constructor: identity creation ============
    /// @notice Creates the vehicle identity; the deployer becomes owner.
    /// @dev CVIN extension. Non-empty VIN. Emits {OwnershipTransferred} and {VehicleIdentityCreated}.
    /// @param _vin The vehicle's VIN.
    constructor(string memory _vin) {
        require(bytes(_vin).length > 0, "ERC735: empty VIN");
        vin = _vin;
        vinHash = keccak256(bytes(_vin));
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
        emit VehicleIdentityCreated(vinHash, _vin, msg.sender);
    }

    // ============ ERC-735 functions ============

    /**
     * @notice Add (or update) a claim about this vehicle identity.
     * @dev Only the identity owner may anchor claims. Checks, in order:
     *      1. issuer != 0 and scheme == ECDSA_SCHEME;
     *      2. the issuer's EIP-191 ECDSA signature over
     *         keccak256(abi.encodePacked(address(this), topic, data)) recovers to
     *         `issuer` (see _recoverSigner for the scheme note) — who signed;
     *      3. that signer is authorized for `topic` (isAuthorizedIssuer), or the
     *         claim is self-issued (issuer == owner) — D25a — may they sign;
     *      4. for topic VIN_ATTESTATION, `data` encodes this holder's VIN
     *         (_encodesHolderVin) — D25b — is it about this vehicle.
     *      Re-adding a claim with the same (issuer, topic) updates it and
     *      emits ClaimChanged instead of ClaimAdded.
     *      Also rejects content in {revokedClaims} (K-2). A new claim emits
     *      ClaimRequested + ClaimAdded. ERC-735 + CVIN checks.
     * @param topic Claim topic.
     * @param scheme Must be ECDSA_SCHEME (1).
     * @param issuer Expected signer.
     * @param signature 65-byte EIP-191 signature over keccak256(abi.encodePacked(address(this), topic, data)).
     * @param data Claim payload (for topic 1 must end with the holder VIN).
     * @param uri Off-chain claim location.
     * @return claimRequestId The claimId, keccak256(abi.encodePacked(issuer, topic)).
     */
    function addClaim(
        uint256 topic,
        uint256 scheme,
        address issuer,
        bytes calldata signature,
        bytes calldata data,
        string calldata uri
    ) external onlyOwner returns (bytes32 claimRequestId) {
        require(issuer != address(0), "ERC735: issuer is zero address");
        require(scheme == ECDSA_SCHEME, "ERC735: unsupported signature scheme");
        bytes32 digest = keccak256(abi.encodePacked(address(this), topic, data));
        require(
            _recoverSigner(digest, signature) == issuer,
            "ERC735: invalid issuer signature"
        );
        require(
            !revokedClaims[keccak256(abi.encodePacked(issuer, digest))],
            "ERC735: claim revoked by issuer"
        );
        require(
            issuer == owner || authorizedIssuers[issuer][topic],
            "ERC735: issuer not authorized for topic"
        );
        if (topic == VIN_ATTESTATION) {
            require(_encodesHolderVin(data), "ERC735: VIN attestation does not match holder VIN");
        }

        bytes32 claimId = keccak256(abi.encodePacked(issuer, topic));
        bool exists = claims[claimId].issuer != address(0);

        claims[claimId] = Claim({
            topic: topic,
            scheme: scheme,
            issuer: issuer,
            signature: signature,
            data: data,
            uri: uri
        });

        if (exists) {
            emit ClaimChanged(claimId, topic, scheme, issuer, signature, data, uri);
        } else {
            claimIdsByTopic[topic].push(claimId);
            emit ClaimRequested(
                uint256(claimId),
                topic,
                scheme,
                issuer,
                signature,
                data,
                uri
            );
            emit ClaimAdded(claimId, topic, scheme, issuer, signature, data, uri);
        }

        return claimId;
    }

    /**
     * @notice Remove (revoke) a claim. Callable by the identity owner or the
     *         claim's issuer (issuer-side revocation).
     * @dev An issuer removal also records the claim's signed content in
     *      revokedClaims so addClaim cannot bring it back (K-2). An owner
     *      removal records nothing. Emits ClaimRemoved. ERC-735 (+K-2).
     * @param claimId The claim identifier.
     * @return success Always true (reverts if the claim does not exist).
     */
    function removeClaim(bytes32 claimId) external returns (bool success) {
        Claim memory claim = claims[claimId];
        require(claim.issuer != address(0), "ERC735: claim does not exist");
        require(
            msg.sender == owner || msg.sender == claim.issuer,
            "ERC735: caller is not owner nor issuer"
        );

        if (msg.sender == claim.issuer) {
            revokedClaims[
                keccak256(
                    abi.encodePacked(
                        claim.issuer,
                        keccak256(abi.encodePacked(address(this), claim.topic, claim.data))
                    )
                )
            ] = true;
        }

        _deleteClaim(claimId, claim);
        return true;
    }

    /**
     * @notice Issuer-side revocation of signed claim CONTENT, whether or not
     *         it is currently anchored (REVIEW_02 K-2, Pass 2).
     * @dev removeClaim needs the claim to exist, so an owner could pre-empt a
     *      revocation by removing the claim first (the issuer's removeClaim
     *      then reverts) and re-anchor the old signature later. This records
     *      keccak256(msg.sender, digest(topic, data)) unconditionally, i.e. it
     *      can only ever block claims signed by the caller itself, so it needs
     *      no access control. If the caller's claim for `topic` is anchored
     *      with exactly this data it is removed too; an anchored claim with
     *      other (e.g. re-issued) data is left alone. CVIN extension.
     *      Emits ClaimRemoved only if a matching claim was anchored.
     * @param topic Claim topic of the revoked content.
     * @param data Claim payload of the revoked content.
     */
    function revokeClaimContent(uint256 topic, bytes calldata data) external {
        bytes32 digest = keccak256(abi.encodePacked(address(this), topic, data));
        revokedClaims[keccak256(abi.encodePacked(msg.sender, digest))] = true;

        bytes32 claimId = keccak256(abi.encodePacked(msg.sender, topic));
        Claim memory claim = claims[claimId];
        if (claim.issuer != address(0) && keccak256(claim.data) == keccak256(data)) {
            _deleteClaim(claimId, claim);
        }
    }

    /// @dev Unindex (swap-and-pop), delete and emit ClaimRemoved.
    /// @param claimId The claim identifier.
    /// @param claim In-memory copy of the claim (used for the event).
    function _deleteClaim(bytes32 claimId, Claim memory claim) private {
        bytes32[] storage ids = claimIdsByTopic[claim.topic];
        for (uint256 i = 0; i < ids.length; i++) {
            if (ids[i] == claimId) {
                ids[i] = ids[ids.length - 1];
                ids.pop();
                break;
            }
        }

        delete claims[claimId];

        emit ClaimRemoved(
            claimId,
            claim.topic,
            claim.scheme,
            claim.issuer,
            claim.signature,
            claim.data,
            claim.uri
        );
    }

    /// @notice ERC-735: returns a claim by id (all-zero values if absent).
    /// @param claimId The claim identifier.
    /// @return topic Claim topic.
    /// @return scheme Signature scheme.
    /// @return issuer Claim issuer (zero if absent).
    /// @return signature Issuer signature.
    /// @return data Claim payload.
    /// @return uri Off-chain claim location.
    function getClaim(bytes32 claimId)
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
        Claim storage claim = claims[claimId];
        return (
            claim.topic,
            claim.scheme,
            claim.issuer,
            claim.signature,
            claim.data,
            claim.uri
        );
    }

    /// @notice ERC-735: claim ids currently anchored for a topic.
    /// @param topic Claim topic.
    /// @return claimIds The claim identifiers.
    function getClaimIdsByTopic(uint256 topic)
        external
        view
        returns (bytes32[] memory claimIds)
    {
        return claimIdsByTopic[topic];
    }

    /// @notice Convenience: check whether a live claim exists for (issuer, topic)
    /// @dev CVIN extension.
    /// @param issuer Claim issuer.
    /// @param topic Claim topic.
    /// @return True if anchored.
    function claimExists(address issuer, uint256 topic) external view returns (bool) {
        return claims[keccak256(abi.encodePacked(issuer, topic))].issuer != address(0);
    }

    // ============ Issuer registry (D25a) ============

    /**
     * @notice Authorize `issuer` to issue claims on `topic` for this vehicle.
     * @dev Owner-managed: the holder decides which authorities it recognises
     *      (an OEM for MANUFACTURER_CERT, a test centre for INSPECTION, ...).
     *      Reverts if already authorized so that every IssuerAuthorized event
     *      marks a real state change. Non-zero issuer. Emits {IssuerAuthorized}.
     *      CVIN extension (D25a).
     * @param issuer The issuer.
     * @param topic The topic.
     */
    function authorizeIssuer(address issuer, uint256 topic) external onlyOwner {
        require(issuer != address(0), "ERC735: issuer is zero address");
        require(!authorizedIssuers[issuer][topic], "ERC735: issuer already authorized");
        authorizedIssuers[issuer][topic] = true;
        emit IssuerAuthorized(issuer, topic);
    }

    /**
     * @notice Withdraw `issuer`'s right to issue claims on `topic`.
     * @dev Forward-looking: claims already anchored by `issuer` remain until
     *      removeClaim (the issuer keeps its issuer-side removal right).
     *      Owner only; reverts if not authorized. Emits {IssuerRevoked}. CVIN extension.
     * @param issuer The issuer.
     * @param topic The topic.
     */
    function revokeIssuer(address issuer, uint256 topic) external onlyOwner {
        require(authorizedIssuers[issuer][topic], "ERC735: issuer not authorized");
        authorizedIssuers[issuer][topic] = false;
        emit IssuerRevoked(issuer, topic);
    }

    /// @notice Whether `issuer` is currently authorized to issue claims on `topic`.
    ///         The self-issuance exemption (issuer == owner) is NOT reflected here.
    /// @dev CVIN extension.
    /// @param issuer The issuer.
    /// @param topic The topic.
    /// @return True if whitelisted.
    function isAuthorizedIssuer(address issuer, uint256 topic) external view returns (bool) {
        return authorizedIssuers[issuer][topic];
    }

    // ============ Ownership (MANAGEMENT-key role) ============

    /**
     * @notice Transfer the vehicle identity to a new owner (e.g. vehicle sale).
     * @dev Owner only; non-zero. Issuer authorisations persist. Emits {OwnershipTransferred}.
     *      ERC-173 surface / ERC-734 MANAGEMENT role.
     * @param newOwner The new owner.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "ERC735: new owner is zero address");
        address previousOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(previousOwner, newOwner);
    }

    // ============ Internal: VIN binding (D25b) ============

    /**
     * @dev Encoding rule for a VIN_ATTESTATION (topic 1) payload: the LAST
     *      bytes(vin).length bytes of `data` must equal bytes(vin), i.e.
     *      keccak256(data[data.length - |vin| :]) == vinHash. The attested VIN
     *      is therefore the trailing field of the payload, optionally preceded
     *      by an application prefix ("VIN:" / "vin:" as the L2 test and the gas
     *      benchmark use), and a bare `bytes(vin)` payload (as the demos use)
     *      satisfies it too. A payload naming any other VIN, a truncated VIN,
     *      or a VIN followed by further bytes is rejected. Structured payloads
     *      (JSON, ABI) are NOT accepted on topic 1 — they belong on the other
     *      topics, where no binding is imposed. CVIN extension (D25b).
     * @param data Claim payload.
     * @return True if the payload ends with this holder's VIN.
     */
    function _encodesHolderVin(bytes calldata data) internal view returns (bool) {
        bytes memory v = bytes(vin);
        uint256 n = v.length;
        if (data.length < n) {
            return false;
        }
        // keccak256(v) == vinHash by construction (constructor); hashing the
        // 17-byte memory copy is cheaper than a second cold SLOAD of vinHash.
        return keccak256(data[data.length - n:]) == keccak256(v);
    }

    // ============ Internal: ECDSA recovery ============

    /**
     * @dev SIGNATURE SCHEME (docs/DEFECT_LOG.md D25c). This contract verifies
     *      an EIP-191 "personal_sign" signature: the issuer signs
     *      keccak256(abi.encodePacked(address(this), topic, data)) and the
     *      contract re-applies the "\x19Ethereum Signed Message:\n32" prefix
     *      before ecrecover (ethers: signer.signMessage(getBytes(digest))). A
     *      RAW secp256k1 signature over the unprefixed digest is rejected here.
     *      CVINCombinedIdentity._recoverRawDigest does the OPPOSITE — it
     *      ecrecovers the raw digest keccak256(abi.encodePacked(registry,
     *      identity, topic, data)) and rejects an EIP-191 signature — so an
     *      issuer signature is not portable between the two claim contracts.
     *      Unifying the scheme is a design decision left to the author
     *      (recommendation in AFTER_ACTION_REPORT_05 §1 F7: EIP-191, matching
     *      the VC layer and the ERC-4337 account); this fix does not change it.
     *      Requires a 65-byte signature, normalises v (0/1 -> 27/28), enforces
     *      EIP-2 low-s, and reverts on a zero recovered address.
     * @param messageHash Unprefixed digest.
     * @param signature 65-byte r||s||v signature.
     * @return The recovered signer.
     */
    function _recoverSigner(bytes32 messageHash, bytes memory signature)
        internal
        pure
        returns (address)
    {
        require(signature.length == 65, "ERC735: invalid signature length");

        bytes32 prefixedHash = keccak256(
            abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
        );

        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(signature, 0x20))
            s := mload(add(signature, 0x40))
            v := byte(0, mload(add(signature, 0x60)))
        }
        if (v < 27) {
            v += 27;
        }
        require(v == 27 || v == 28, "ERC735: invalid signature v value");

        // EIP-2 malleability guard
        require(
            uint256(s) <= 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0,
            "ERC735: invalid signature s value"
        );

        address recovered = ecrecover(prefixedHash, v, r, s);
        require(recovered != address(0), "ERC735: invalid signature");
        return recovered;
    }
}
