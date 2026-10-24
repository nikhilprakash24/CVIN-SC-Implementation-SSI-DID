// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./MOBIVIDRegistry.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/MessageHashUtils.sol";

/**
 * @title MOBI VID Registry V2
 * @author CVIN research project
 * @notice MOBI VID II lifecycle events: role-gated event issuance with VC hashes
 *         and multi-party, owner-consented, EIP-191-signed attestations.
 * @dev Extends MOBI VID Registry with VID 2.0 lifecycle events
 *
 * Standards Compliance:
 * - MOBI VID I (Vehicle Birth Certificate) - from base contract
 * - MOBI VID II (Lifecycle Events) - NEW
 * - W3C Decentralized Identifiers (DIDs) v1.0
 * - W3C Verifiable Credentials v1.1
 * - ERC-1056 (Ethereum DID Registry)
 * - SSI (Self-Sovereign Identity) principles
 *
 * Key Features:
 * - Lifecycle event tracking (maintenance, accidents, recalls, etc.)
 * - Multi-party event issuance
 * - Event attestations from multiple signers
 * - Role-based access control for issuers
 * - Verifiable Credential integration
 * - Complete vehicle history
 *
 * Design: `MOBIVIDRegistryV2 is MOBIVIDRegistry is ERC1056Registry`. Imports
 * OpenZeppelin Contracts 5.0.2 `ECDSA` and `MessageHashUtils` (libraries, not
 * bases). The role => event-type matrix is fixed at deploy by
 * _initializeAllowedIssuers (no setter). Deviations from the repo's
 * MOBI_VID2_SSI_DESIGN.md: no OWNERSHIP_TRANSFER event type (ownership uses
 * transferVehicleOwnership), REGISTRATION and DECOMMISSION added, IssuerRole
 * has NONE, and attestations live in `eventAttestations[eventId]`. The VC
 * integration is only the opaque `credentialHash`; no VC is parsed on-chain.
 *
 * @custom:standard MOBI Vehicle Identity (VID II) https://dlt.mobi/standards/
 * @custom:standard ERC-1056 Ethereum Lightweight Identity https://eips.ethereum.org/EIPS/eip-1056
 * @custom:standard EIP-191 Signed Data Standard https://eips.ethereum.org/EIPS/eip-191
 * @custom:standard EIP-2 (low-s signatures, via OpenZeppelin ECDSA) https://eips.ethereum.org/EIPS/eip-2
 * @custom:standard W3C Verifiable Credentials Data Model v1.1 https://www.w3.org/TR/vc-data-model/
 * @custom:standard W3C DID Core v1.0 https://www.w3.org/TR/did-core/
 * @custom:security Issuer roles are registry-wide (one role per address); organisational roles can file events
 *                  against any vehicle by design. OWNER is scoped at use time to the current owner (K-15).
 * @custom:security Lifecycle events are append-only: they cannot be revoked or corrected, and de-authorising an
 *                  issuer does not invalidate past events. DECOMMISSION / THEFT_REPORT do not freeze the identity.
 * @custom:security Odometer values are not checked for monotonicity on-chain (rollback detection is off-chain).
 * @custom:security getEventsByType / getOdometerHistory are unbounded loops (fine for eth_call only).
 * @custom:security Attestation signatures use ad-hoc domain separation (contract, chainid), not EIP-712, and are
 *                  stored on-chain after verification (gas cost).
 * @custom:security `jurisdiction` is a free-form, unvalidated string.
 * @custom:see docs/smart-contracts/02-mobi-vid.md
 * @custom:see sandbox/options/mobi-vid/adapter.js
 */
contract MOBIVIDRegistryV2 is MOBIVIDRegistry {

    // ============ ENUMS ============

    /**
     * @notice Types of lifecycle events (ordinals 0-10).
     */
    enum EventType {
        MAINTENANCE,        // Regular service (oil change, tire rotation, etc.)
        REPAIR,            // Breakdown repair
        ACCIDENT,          // Collision or damage
        RECALL,            // Manufacturer recall
        INSPECTION,        // Safety or emissions inspection
        MODIFICATION,      // Aftermarket modifications
        THEFT_REPORT,      // Vehicle reported stolen
        RECOVERY,          // Stolen vehicle recovered
        INSURANCE_CLAIM,   // Insurance claim filed
        REGISTRATION,      // DMV registration/renewal
        DECOMMISSION      // Vehicle scrapped/totaled
    }

    /**
     * @notice Roles for event issuers (ordinals 0-8).
     * @dev Separate from MOBIVIDRegistry.authorizedManufacturers. The per-role
     *      comments describe intent; the authoritative permissions are in
     *      _initializeAllowedIssuers.
     */
    enum IssuerRole {
        NONE,              // Not authorized
        MANUFACTURER,      // Can issue recalls, updates, decommissions
        DEALER,            // Can issue maintenance, repairs, sales
        SERVICE_CENTER,    // Can issue maintenance, repairs
        INSURANCE_COMPANY, // Can issue claims, appraisals
        GOVERNMENT_DMV,    // Can issue registrations, inspections
        POLICE,            // Can issue theft reports, accidents
        INSPECTION_STATION,// Can issue safety/emissions tests
        OWNER              // Can report events (unverified) on a vehicle it currently owns
    }

    // ============ STRUCTS ============

    /**
     * @dev Lifecycle Event (MOBI VID II)
     * Represents a mutable event in the vehicle's history
     * @notice One recorded lifecycle event of a vehicle.
     * @custom:note Despite "mutable" above, no function modifies a stored event (append-only). `dataHash` is a
     *              content hash in practice, not an IPFS hash. `verified` is derived from the issuer's role.
     */
    struct LifecycleEvent {
        bytes32 eventId;           // Unique event identifier
        EventType eventType;       // Type of event
        address issuer;            // DID of issuer
        uint256 timestamp;         // When event occurred
        uint256 odometer;          // Odometer reading at event
        bytes32 dataHash;          // IPFS hash of detailed event data
        bytes32 credentialHash;    // Hash of W3C Verifiable Credential
        bool verified;             // Official verification status
        string jurisdiction;       // Legal jurisdiction (e.g., "CA-USA")
        uint256 blockNumber;       // Block when recorded
    }

    /**
     * @dev Event Attestation
     * Multiple parties can attest to an event
     * @notice One verified attestation of an event.
     */
    struct EventAttestation {
        address attester;          // DID of attester
        IssuerRole role;           // Role of attester
        bytes signature;           // Signature of event data
        uint256 timestamp;         // When attested
    }

    // ============ STORAGE ============

    /// @notice Authorized issuers (address => role)
    /// @dev One role per address; NONE means not authorized.
    mapping(address => IssuerRole) public authorizedIssuers;

    /// @notice Vehicle lifecycle events (vehicleIdentity => eventId => LifecycleEvent)
    mapping(address => mapping(bytes32 => LifecycleEvent)) public lifecycleEvents;

    /// @notice Vehicle event IDs list (vehicleIdentity => array of eventIds)
    mapping(address => bytes32[]) public vehicleEventIds;

    /// @notice Event attestations (eventId => array of attestations)
    mapping(bytes32 => EventAttestation[]) public eventAttestations;

    /// @notice eventId => attester => attested (WM-2 C2, D54: one attestation per attester)
    mapping(bytes32 => mapping(address => bool)) public hasAttested;

    /// @notice Event count per vehicle
    mapping(address => uint256) public vehicleEventCount;

    /// @notice Event type statistics (vehicleIdentity => eventType => count)
    mapping(address => mapping(EventType => uint256)) public eventTypeCount;

    /// @notice Allowed issuers per event type
    /// @dev Filled once by _initializeAllowedIssuers in the constructor; no setter.
    mapping(EventType => mapping(IssuerRole => bool)) public allowedIssuers;

    // ============ EVENTS ============

    /**
     * @notice Emitted when a lifecycle event is recorded
     * @param vehicleIdentity The vehicle identity
     * @param eventId The new event id
     * @param eventType The event type
     * @param issuer The issuer (msg.sender)
     * @param odometer Odometer reading supplied by the issuer
     * @param timestamp Block timestamp
     */
    event LifecycleEventRecorded(
        address indexed vehicleIdentity,
        bytes32 indexed eventId,
        EventType indexed eventType,
        address issuer,
        uint256 odometer,
        uint256 timestamp
    );

    /**
     * @notice Emitted when an event is attested
     * @param eventId The attested event
     * @param attester The attester (msg.sender)
     * @param role The attester's role at attestation time
     * @param timestamp Block timestamp
     */
    event EventAttested(
        bytes32 indexed eventId,
        address indexed attester,
        IssuerRole role,
        uint256 timestamp
    );

    /**
     * @notice Emitted when an issuer is authorized
     * @param issuer The issuer address
     * @param role The role granted
     * @param timestamp Block timestamp
     */
    event IssuerAuthorized(
        address indexed issuer,
        IssuerRole role,
        uint256 timestamp
    );

    /**
     * @notice Emitted when an issuer authorization is revoked
     * @param issuer The issuer address
     * @param timestamp Block timestamp
     */
    event IssuerAuthorizationRevoked(
        address indexed issuer,
        uint256 timestamp
    );

    // ============ MODIFIERS ============

    /// @notice Requires msg.sender's role to be allowed to issue `eventType`.
    /// @dev Role-matrix check only (see isAuthorizedIssuer).
    /// @param eventType The event type being issued
    modifier onlyAuthorizedIssuer(EventType eventType) {
        require(
            isAuthorizedIssuer(msg.sender, eventType),
            "Not authorized to issue this event type"
        );
        _;
    }

    // ============ CONSTRUCTOR ============

    /// @notice Runs the MOBIVIDRegistry constructor, then fills the role => event-type matrix.
    constructor() MOBIVIDRegistry() {
        // Initialize allowed issuers for each event type
        _initializeAllowedIssuers();
    }

    // ============ ISSUER MANAGEMENT ============

    /**
     * @notice Authorize an issuer with a specific role
     * @dev onlyRegistryAuthority. Overwrites any existing role; NONE is rejected.
     *      Emits IssuerAuthorized.
     * @param issuer Address to authorize
     * @param role Role to assign
     */
    function authorizeIssuer(address issuer, IssuerRole role)
        external
        onlyRegistryAuthority
    {
        require(issuer != address(0), "Invalid issuer address");
        require(role != IssuerRole.NONE, "Invalid role");

        authorizedIssuers[issuer] = role;
        emit IssuerAuthorized(issuer, role, block.timestamp);
    }

    /**
     * @notice Revoke issuer authorization
     * @dev onlyRegistryAuthority. Sets the role to NONE; past events stay valid.
     *      Emits IssuerAuthorizationRevoked.
     * @param issuer Address to revoke
     */
    function revokeIssuerAuthorization(address issuer)
        external
        onlyRegistryAuthority
    {
        require(authorizedIssuers[issuer] != IssuerRole.NONE, "Issuer not authorized");

        authorizedIssuers[issuer] = IssuerRole.NONE;
        emit IssuerAuthorizationRevoked(issuer, block.timestamp);
    }

    /**
     * @notice Check if address is authorized to issue event type.
     * Role check only: recordLifecycleEvent also requires an OWNER-role
     * issuer to be the vehicle's current owner (K-15).
     * @param issuer Address to check
     * @param eventType Type of event
     * @return True if authorized
     */
    function isAuthorizedIssuer(address issuer, EventType eventType)
        public
        view
        returns (bool)
    {
        IssuerRole role = authorizedIssuers[issuer];
        if (role == IssuerRole.NONE) return false;

        return allowedIssuers[eventType][role];
    }

    // ============ EVENT ISSUANCE (MOBI VID II) ============

    /**
     * @dev Record a lifecycle event
     *
     * This is the core MOBI VID II function
     * vehicleRegistered, onlyAuthorizedIssuer; rejects revoked vehicles; an
     * OWNER-role caller must be the current owner (K-15). eventId =
     * keccak256(vehicle, eventType, msg.sender, block.timestamp, count).
     * Emits LifecycleEventRecorded.
     * @notice Record a lifecycle event for a registered vehicle (authorized issuer only).
     *
     * @param vehicleIdentity Vehicle DID
     * @param eventType Type of event
     * @param odometer Odometer reading
     * @param dataHash IPFS hash of detailed event data
     * @param credentialHash Hash of W3C Verifiable Credential
     * @param jurisdiction Legal jurisdiction
     * @return eventId Unique event identifier
     */
    function recordLifecycleEvent(
        address vehicleIdentity,
        EventType eventType,
        uint256 odometer,
        bytes32 dataHash,
        bytes32 credentialHash,
        string calldata jurisdiction
    )
        external
        vehicleRegistered(vehicleIdentity)
        onlyAuthorizedIssuer(eventType)
        returns (bytes32 eventId)
    {
        require(!revoked[vehicleIdentity], "Vehicle identity is revoked");

        // Review-02 K-15: OWNER is a global role, so on its own it let any
        // OWNER-role address file MAINTENANCE, ACCIDENT, MODIFICATION,
        // THEFT_REPORT or INSURANCE_CLAIM events against any vehicle. An
        // OWNER-role issuer must also be the vehicle's current ERC-1056
        // owner, so a previous owner loses the right on transfer. The
        // organisational roles (service centre, police, insurer, DMV, ...)
        // keep their registry-wide scope by design.
        if (authorizedIssuers[msg.sender] == IssuerRole.OWNER) {
            require(
                identityOwner(vehicleIdentity) == msg.sender,
                "OWNER role: not the current owner of this vehicle"
            );
        }

        // Generate unique event ID
        eventId = keccak256(abi.encodePacked(
            vehicleIdentity,
            eventType,
            msg.sender,
            block.timestamp,
            vehicleEventCount[vehicleIdentity]
        ));

        // Create event
        lifecycleEvents[vehicleIdentity][eventId] = LifecycleEvent({
            eventId: eventId,
            eventType: eventType,
            issuer: msg.sender,
            timestamp: block.timestamp,
            odometer: odometer,
            dataHash: dataHash,
            credentialHash: credentialHash,
            verified: _isVerifiedIssuer(msg.sender),
            jurisdiction: jurisdiction,
            blockNumber: block.number
        });

        // Add to vehicle's event list
        vehicleEventIds[vehicleIdentity].push(eventId);

        // Update counters
        vehicleEventCount[vehicleIdentity]++;
        eventTypeCount[vehicleIdentity][eventType]++;

        emit LifecycleEventRecorded(
            vehicleIdentity,
            eventId,
            eventType,
            msg.sender,
            odometer,
            block.timestamp
        );

        return eventId;
    }

    /**
     * @notice Attest to an event
     * @dev Allows multiple parties to sign off on an event
     *
     * The attester must sign the domain-separated attestation digest
     *
     *     keccak256(abi.encodePacked(
     *         address(this), block.chainid, vehicleIdentity, eventId))
     *
     * wrapped with the EIP-191 ("\x19Ethereum Signed Message:\n32") prefix.
     * The signature is recovered on-chain and MUST match msg.sender.
     *
     * SECURITY (before/after): earlier revisions stored `signature` verbatim
     * and NEVER verified it on-chain (no ecrecover) — the call was gated only
     * by the attester's role, so any role-holder could record a garbage or
     * forged attestation signature (a replay/forgery gap). This revision binds
     * the signature to this contract, this chain, the vehicle and the event,
     * and rejects anything that does not recover to the attester.
     *
     * Access: the event must exist, the caller must hold a role other than
     * NONE, and must be the current owner or a valid bytes32("veriKey")
     * delegate of the vehicle (D54; a sigAuth delegation does not count), and
     * may attest once. Emits EventAttested.
     * @custom:note hasAttested is set before the signature check; a revert rolls it back.
     *
     * @param eventId Event to attest
     * @param vehicleIdentity Vehicle DID
     * @param signature EIP-191 signature over the attestation digest, by msg.sender
     */
    function attestEvent(
        bytes32 eventId,
        address vehicleIdentity,
        bytes calldata signature
    )
        external
    {
        require(
            lifecycleEvents[vehicleIdentity][eventId].eventId == eventId,
            "Event does not exist"
        );
        require(
            authorizedIssuers[msg.sender] != IssuerRole.NONE,
            "Not authorized to attest"
        );
        // WM-2 C2 (D54): a role is authority, not consent. The attester must also
        // be the vehicle's current owner or a valid veriKey delegate of it, and
        // may attest an event once.
        require(
            msg.sender == identityOwner(vehicleIdentity) ||
                validDelegate(vehicleIdentity, "veriKey", msg.sender),
            "Attester is not the vehicle's owner or delegate"
        );
        require(!hasAttested[eventId][msg.sender], "Already attested");
        hasAttested[eventId][msg.sender] = true;

        // ---- On-chain attestation signature verification (security fix) ----
        // Bind the signature to (contract, chain, vehicle, event) to stop
        // cross-contract / cross-chain replay, then recover the signer.
        // OpenZeppelin ECDSA.recover enforces EIP-2 low-s malleability and
        // rejects the zero address (it reverts on a malformed signature).
        bytes32 attestationHash = keccak256(
            abi.encodePacked(address(this), block.chainid, vehicleIdentity, eventId)
        );
        address recovered = ECDSA.recover(
            MessageHashUtils.toEthSignedMessageHash(attestationHash),
            signature
        );
        require(recovered == msg.sender, "Invalid attestation signature");

        // Create attestation
        EventAttestation memory attestation = EventAttestation({
            attester: msg.sender,
            role: authorizedIssuers[msg.sender],
            signature: signature,
            timestamp: block.timestamp
        });

        eventAttestations[eventId].push(attestation);

        emit EventAttested(
            eventId,
            msg.sender,
            authorizedIssuers[msg.sender],
            block.timestamp
        );
    }

    // ============ QUERY FUNCTIONS ============

    /**
     * @notice Get all event IDs for a vehicle
     * @dev vehicleRegistered.
     * @param vehicleIdentity Vehicle DID
     * @return Array of event IDs
     */
    function getVehicleEvents(address vehicleIdentity)
        external
        view
        vehicleRegistered(vehicleIdentity)
        returns (bytes32[] memory)
    {
        return vehicleEventIds[vehicleIdentity];
    }

    /**
     * @notice Get event details
     * @dev Reverts if the event does not exist.
     * @param vehicleIdentity Vehicle DID
     * @param eventId Event ID
     * @return Event details
     */
    function getEvent(address vehicleIdentity, bytes32 eventId)
        external
        view
        returns (LifecycleEvent memory)
    {
        require(
            lifecycleEvents[vehicleIdentity][eventId].eventId == eventId,
            "Event does not exist"
        );
        return lifecycleEvents[vehicleIdentity][eventId];
    }

    /**
     * @notice Get event attestations
     * @param eventId Event ID
     * @return Array of attestations
     */
    function getEventAttestations(bytes32 eventId)
        external
        view
        returns (EventAttestation[] memory)
    {
        return eventAttestations[eventId];
    }

    /**
     * @notice Get event count by type
     * @param vehicleIdentity Vehicle DID
     * @param eventType Type of event
     * @return Count of events of that type
     */
    function getEventTypeCount(address vehicleIdentity, EventType eventType)
        external
        view
        returns (uint256)
    {
        return eventTypeCount[vehicleIdentity][eventType];
    }

    /**
     * @notice Get complete vehicle history (VID I + VID II)
     * @dev vehicleRegistered. CVIN extension.
     * @param vehicleIdentity Vehicle DID
     * @return birth Birth certificate
     * @return eventCount Number of lifecycle events
     * @return lastEvent Most recent event ID
     */
    function getCompleteHistory(address vehicleIdentity)
        external
        view
        vehicleRegistered(vehicleIdentity)
        returns (
            VehicleBirth memory birth,
            uint256 eventCount,
            bytes32 lastEvent
        )
    {
        birth = vehicleBirths[vehicleIdentity];
        eventCount = vehicleEventCount[vehicleIdentity];

        if (eventCount > 0) {
            lastEvent = vehicleEventIds[vehicleIdentity][eventCount - 1];
        }

        return (birth, eventCount, lastEvent);
    }

    /**
     * @notice Get events by type
     * @dev O(n) loop over all events of the vehicle; for eth_call use.
     * @param vehicleIdentity Vehicle DID
     * @param eventType Type of events to retrieve
     * @return eventIds Array of event IDs of specified type
     */
    function getEventsByType(address vehicleIdentity, EventType eventType)
        external
        view
        returns (bytes32[] memory eventIds)
    {
        bytes32[] memory allEvents = vehicleEventIds[vehicleIdentity];
        uint256 count = eventTypeCount[vehicleIdentity][eventType];

        eventIds = new bytes32[](count);
        uint256 index = 0;

        for (uint256 i = 0; i < allEvents.length; i++) {
            if (lifecycleEvents[vehicleIdentity][allEvents[i]].eventType == eventType) {
                eventIds[index] = allEvents[i];
                index++;
            }
        }

        return eventIds;
    }

    /**
     * @notice Get odometer history (for fraud detection)
     * @dev O(n) loop; values are returned as recorded, without a monotonicity check.
     * @param vehicleIdentity Vehicle DID
     * @return odometerReadings Array of odometer readings with timestamps
     * @return timestamps Block timestamps of the corresponding events
     */
    function getOdometerHistory(address vehicleIdentity)
        external
        view
        returns (uint256[] memory odometerReadings, uint256[] memory timestamps)
    {
        bytes32[] memory allEvents = vehicleEventIds[vehicleIdentity];
        odometerReadings = new uint256[](allEvents.length);
        timestamps = new uint256[](allEvents.length);

        for (uint256 i = 0; i < allEvents.length; i++) {
            LifecycleEvent memory evt = lifecycleEvents[vehicleIdentity][allEvents[i]];
            odometerReadings[i] = evt.odometer;
            timestamps[i] = evt.timestamp;
        }

        return (odometerReadings, timestamps);
    }

    // ============ INTERNAL FUNCTIONS ============

    /**
     * @dev Initialize allowed issuers for each event type
     *      Called once from the constructor; the matrix cannot be changed later.
     */
    function _initializeAllowedIssuers() internal {
        // MAINTENANCE: Dealer, Service Center, Owner
        allowedIssuers[EventType.MAINTENANCE][IssuerRole.DEALER] = true;
        allowedIssuers[EventType.MAINTENANCE][IssuerRole.SERVICE_CENTER] = true;
        allowedIssuers[EventType.MAINTENANCE][IssuerRole.OWNER] = true;

        // REPAIR: Dealer, Service Center
        allowedIssuers[EventType.REPAIR][IssuerRole.DEALER] = true;
        allowedIssuers[EventType.REPAIR][IssuerRole.SERVICE_CENTER] = true;

        // ACCIDENT: Police, Insurance, Owner
        allowedIssuers[EventType.ACCIDENT][IssuerRole.POLICE] = true;
        allowedIssuers[EventType.ACCIDENT][IssuerRole.INSURANCE_COMPANY] = true;
        allowedIssuers[EventType.ACCIDENT][IssuerRole.OWNER] = true;

        // RECALL: Manufacturer only
        allowedIssuers[EventType.RECALL][IssuerRole.MANUFACTURER] = true;

        // INSPECTION: Inspection Station, Government DMV
        allowedIssuers[EventType.INSPECTION][IssuerRole.INSPECTION_STATION] = true;
        allowedIssuers[EventType.INSPECTION][IssuerRole.GOVERNMENT_DMV] = true;

        // MODIFICATION: Service Center, Owner
        allowedIssuers[EventType.MODIFICATION][IssuerRole.SERVICE_CENTER] = true;
        allowedIssuers[EventType.MODIFICATION][IssuerRole.OWNER] = true;

        // THEFT_REPORT: Police, Owner
        allowedIssuers[EventType.THEFT_REPORT][IssuerRole.POLICE] = true;
        allowedIssuers[EventType.THEFT_REPORT][IssuerRole.OWNER] = true;

        // RECOVERY: Police only
        allowedIssuers[EventType.RECOVERY][IssuerRole.POLICE] = true;

        // INSURANCE_CLAIM: Insurance, Owner
        allowedIssuers[EventType.INSURANCE_CLAIM][IssuerRole.INSURANCE_COMPANY] = true;
        allowedIssuers[EventType.INSURANCE_CLAIM][IssuerRole.OWNER] = true;

        // REGISTRATION: Government DMV only
        allowedIssuers[EventType.REGISTRATION][IssuerRole.GOVERNMENT_DMV] = true;

        // DECOMMISSION: Manufacturer, Government DMV
        allowedIssuers[EventType.DECOMMISSION][IssuerRole.MANUFACTURER] = true;
        allowedIssuers[EventType.DECOMMISSION][IssuerRole.GOVERNMENT_DMV] = true;
    }

    /**
     * @dev Check if issuer is verified (government, manufacturer, etc.)
     *      Verified roles: MANUFACTURER, GOVERNMENT_DMV, POLICE, DEALER,
     *      INSPECTION_STATION. Sets LifecycleEvent.verified.
     * @param issuer Address to check
     * @return True if verified issuer
     */
    function _isVerifiedIssuer(address issuer) internal view returns (bool) {
        IssuerRole role = authorizedIssuers[issuer];

        // Verified roles
        return (
            role == IssuerRole.MANUFACTURER ||
            role == IssuerRole.GOVERNMENT_DMV ||
            role == IssuerRole.POLICE ||
            role == IssuerRole.DEALER ||
            role == IssuerRole.INSPECTION_STATION
        );
    }
}
