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
 */
interface IERC735 {
    event ClaimRequested(
        uint256 indexed claimRequestId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    event ClaimAdded(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    event ClaimRemoved(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

    event ClaimChanged(
        bytes32 indexed claimId,
        uint256 indexed topic,
        uint256 scheme,
        address indexed issuer,
        bytes signature,
        bytes data,
        string uri
    );

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

    function getClaimIdsByTopic(uint256 topic)
        external
        view
        returns (bytes32[] memory claimIds);

    function addClaim(
        uint256 topic,
        uint256 scheme,
        address issuer,
        bytes calldata signature,
        bytes calldata data,
        string calldata uri
    ) external returns (bytes32 claimRequestId);

    function removeClaim(bytes32 claimId) external returns (bool success);
}

/**
 * @title CVINVehicleClaimHolder
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
 */
contract CVINVehicleClaimHolder is IERC735 {
    // ============ Vehicle claim topics ============
    uint256 public constant VIN_ATTESTATION = 1;
    uint256 public constant MANUFACTURER_CERT = 2;
    uint256 public constant INSPECTION = 3;
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

    // ============ Events (identity lifecycle, beyond ERC-735) ============
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event VehicleIdentityCreated(bytes32 indexed vinHash, string vin, address indexed owner);
    event IssuerAuthorized(address indexed issuer, uint256 indexed topic);
    event IssuerRevoked(address indexed issuer, uint256 indexed topic);

    // ============ Modifiers ============
    modifier onlyOwner() {
        require(msg.sender == owner, "ERC735: caller is not the owner");
        _;
    }

    // ============ Constructor: identity creation ============
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
        require(
            _recoverSigner(
                keccak256(abi.encodePacked(address(this), topic, data)),
                signature
            ) == issuer,
            "ERC735: invalid issuer signature"
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
     */
    function removeClaim(bytes32 claimId) external returns (bool success) {
        Claim memory claim = claims[claimId];
        require(claim.issuer != address(0), "ERC735: claim does not exist");
        require(
            msg.sender == owner || msg.sender == claim.issuer,
            "ERC735: caller is not owner nor issuer"
        );

        // Remove from topic index (swap and pop)
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
        return true;
    }

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

    function getClaimIdsByTopic(uint256 topic)
        external
        view
        returns (bytes32[] memory claimIds)
    {
        return claimIdsByTopic[topic];
    }

    /// @notice Convenience: check whether a live claim exists for (issuer, topic)
    function claimExists(address issuer, uint256 topic) external view returns (bool) {
        return claims[keccak256(abi.encodePacked(issuer, topic))].issuer != address(0);
    }

    // ============ Issuer registry (D25a) ============

    /**
     * @notice Authorize `issuer` to issue claims on `topic` for this vehicle.
     * @dev Owner-managed: the holder decides which authorities it recognises
     *      (an OEM for MANUFACTURER_CERT, a test centre for INSPECTION, ...).
     *      Reverts if already authorized so that every IssuerAuthorized event
     *      marks a real state change.
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
     */
    function revokeIssuer(address issuer, uint256 topic) external onlyOwner {
        require(authorizedIssuers[issuer][topic], "ERC735: issuer not authorized");
        authorizedIssuers[issuer][topic] = false;
        emit IssuerRevoked(issuer, topic);
    }

    /// @notice Whether `issuer` is currently authorized to issue claims on `topic`.
    ///         The self-issuance exemption (issuer == owner) is NOT reflected here.
    function isAuthorizedIssuer(address issuer, uint256 topic) external view returns (bool) {
        return authorizedIssuers[issuer][topic];
    }

    // ============ Ownership (MANAGEMENT-key role) ============

    /**
     * @notice Transfer the vehicle identity to a new owner (e.g. vehicle sale).
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
     *      topics, where no binding is imposed.
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
