// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ERC1056Registry.sol";

/**
 * @title MOBI VID Registry
 * @author CVIN research project
 * @notice MOBI VID I vehicle birth certificates on a shared ERC-1056 registry:
 *         manufacturer-issued births, salted VIN-hash lookup, recorded ownership
 *         transfers, on-chain key anchoring and stored delegations.
 * @dev Implements MOBI Vehicle Identity (VID) 1.0 standard on top of ERC-1056
 *
 * Standards Compliance:
 * - MOBI VID I (Vehicle Birth Certificate)
 * - W3C Decentralized Identifiers (DIDs) v1.0
 * - ERC-1056 (Ethereum DID Registry)
 * - SSI (Self-Sovereign Identity) principles
 *
 * Key Features:
 * - Immutable vehicle birth certificates
 * - VIN privacy protection (hash + encrypted storage)
 * - Manufacturer authorization system
 * - Ownership transfer with complete history
 * - W3C DID compliance
 * - Gas-optimized storage
 *
 * Design: `MOBIVIDRegistry is ERC1056Registry`; no OpenZeppelin bases. MOBI
 * VID I/II are consortium documents with no Solidity ABI, so every interface
 * here is the repo's own MOBI profile (CVIN extension). Deviations from the
 * repo's MOBI_VID1_TECHNICAL_SPEC.md draft: `lookupByVINHash` (not
 * findVehicleByVINHash), finite PERMANENT_ATTRIBUTE_VALIDITY instead of the
 * overflowing type(uint256).max, `VehicleBirth.blockNumber`, and the K-3/K-4/
 * D11b/D54 changes. Restores canonical ERC-1056 delegate storage and
 * `validDelegate`, and blocks the plain `changeOwner` for born vehicles.
 *
 * @custom:standard MOBI Vehicle Identity (VID I / VID II) https://dlt.mobi/standards/
 * @custom:standard ERC-1056 Ethereum Lightweight Identity https://eips.ethereum.org/EIPS/eip-1056
 * @custom:standard W3C DID Core v1.0 https://www.w3.org/TR/did-core/
 * @custom:standard did:ethr DID method https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md
 * @custom:security Birth and manufacturer-path key attributes are written with the owner as ERC-1056 actor
 *                  without the owner's signature, so the event looks owner-authored though the manufacturer sent it.
 * @custom:security Vehicle identities are key-less addresses chosen by the manufacturer (derived from the VIN by
 *                  callers); control exists only through `owners[]`.
 * @custom:security The registering manufacturer can still anchor the first key after its authorisation is revoked
 *                  (anchorVehicleKey checks vehicleBirths[id].manufacturer, not authorizedManufacturers).
 * @custom:security Single-EOA registry authority, auto-authorised as manufacturer; one-step hand-over with no event.
 * @custom:security `encryptedVIN` is public ciphertext; confidentiality rests on the off-chain AEAD. The VIN-hash
 *                  formula is not enforced (some callers use an unsalted keccak256(vin), which is dictionary-attackable).
 * @custom:security Revocation is inherited: owner-only and terminal; no authority can decommission a vehicle.
 * @custom:see docs/smart-contracts/02-mobi-vid.md
 * @custom:see sandbox/options/mobi-vid/adapter.js (wraps MOBIVIDRegistryV2)
 */
contract MOBIVIDRegistry is ERC1056Registry {

    // ============ STRUCTS ============

    /**
     * @dev Vehicle Birth Certificate (MOBI VID I)
     * Immutable anchor for vehicle identity
     * @notice Birth record written once by registerVehicleBirth; there is no update path.
     * @custom:note `vinHash` formula is caller-defined (not enforced on-chain); `birthCertHash` is, per the SSI
     *              layer, a keccak256 content hash of the signed birth VC, not an IPFS hash (field comments are stale).
     */
    struct VehicleBirth {
        bytes32 vinHash;              // SHA256(VIN + salt + vehicleDID) - for searchability
        string encryptedVIN;          // Encrypted VIN - only owner can decrypt
        bytes32 birthCertHash;        // IPFS hash of full birth certificate data
        uint256 timestamp;            // Birth registration timestamp
        address manufacturer;         // Authorized manufacturer address
        address firstOwner;           // First owner DID
        uint256 blockNumber;          // Block when registered
        bool exists;                  // True if vehicle birth was registered
    }

    /**
     * @dev Ownership Transfer Record (MOBI VID II support)
     * @notice One entry per transferVehicleOwnership; the first owner is not an entry.
     */
    struct OwnershipTransfer {
        address from;
        address to;
        uint256 timestamp;
        uint256 blockNumber;
        uint256 odometer;             // Odometer reading at transfer
        string registrationAuthority; // Government authority that processed transfer
    }

    // ============ CONSTANTS ============

    /**
     * @dev Validity period used for "permanent" birth attributes.
     *
     * ERC1056Registry.setAttribute computes `block.timestamp + validity`
     * with Solidity 0.8 checked arithmetic, so passing type(uint256).max
     * overflows and reverts with panic 0x11. A finite 100-year validity is
     * effectively permanent for a vehicle lifecycle and never overflows.
     * @notice Validity (100 years) used for birth attributes and anchored vehicle keys.
     */
    uint256 public constant PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days;

    // ============ STORAGE ============

    /// @notice Registry authority (can authorize manufacturers)
    /// @dev Set to the deployer; changed only by transferRegistryAuthority.
    address public registryAuthority;

    /// @notice Authorized manufacturers (can register vehicle births)
    mapping(address => bool) public authorizedManufacturers;

    /// @notice VIN hash to vehicle identity mapping (for lookups)
    mapping(bytes32 => address) public vinHashToIdentity;

    /// @notice Vehicle birth certificates (vehicleIdentity => VehicleBirth)
    mapping(address => VehicleBirth) public vehicleBirths;

    /// @notice Ownership history (vehicleIdentity => array of transfers)
    /// @dev Starts at the first transfer; the first owner is recorded only in VehicleBirth.
    mapping(address => OwnershipTransfer[]) public ownershipHistory;

    // ============ EVENTS ============

    /**
     * @notice Emitted when a vehicle birth certificate is registered
     * @dev CVIN extension (MOBI VID I profile).
     * @param vehicleIdentity The vehicle identity (DID address)
     * @param vinHash The registered VIN hash
     * @param manufacturer The registering manufacturer (msg.sender)
     * @param firstOwner The first owner
     * @param birthCertHash Hash of the birth certificate data / VC
     * @param timestamp Block timestamp of registration
     */
    event VehicleBirthRegistered(
        address indexed vehicleIdentity,
        bytes32 indexed vinHash,
        address indexed manufacturer,
        address firstOwner,
        bytes32 birthCertHash,
        uint256 timestamp
    );

    /**
     * @notice Emitted when vehicle ownership is transferred
     * @dev CVIN extension; emitted alongside the ERC-1056 DIDOwnerChanged.
     * @param vehicleIdentity The vehicle identity
     * @param from Previous owner
     * @param to New owner
     * @param odometer Odometer reading at transfer
     * @param timestamp Block timestamp of the transfer
     */
    event VehicleOwnershipTransferred(
        address indexed vehicleIdentity,
        address indexed from,
        address indexed to,
        uint256 odometer,
        uint256 timestamp
    );

    /**
     * @notice Emitted when a manufacturer is authorized
     * @param manufacturer The manufacturer address
     * @param timestamp Block timestamp
     */
    event ManufacturerAuthorized(
        address indexed manufacturer,
        uint256 timestamp
    );

    /**
     * @notice Emitted when manufacturer authorization is revoked
     * @param manufacturer The manufacturer address
     * @param timestamp Block timestamp
     */
    event ManufacturerAuthorizationRevoked(
        address indexed manufacturer,
        uint256 timestamp
    );

    // ============ MODIFIERS ============

    /// @notice Requires msg.sender to be the registry authority.
    modifier onlyRegistryAuthority() {
        require(
            msg.sender == registryAuthority,
            "Only registry authority can perform this action"
        );
        _;
    }

    /// @notice Requires msg.sender to be an authorized manufacturer.
    modifier onlyAuthorizedManufacturer() {
        require(
            authorizedManufacturers[msg.sender],
            "Only authorized manufacturers can register vehicles"
        );
        _;
    }

    /// @notice Requires that no birth certificate exists for `vehicleIdentity`.
    /// @param vehicleIdentity The vehicle identity
    modifier vehicleNotRegistered(address vehicleIdentity) {
        require(
            !vehicleBirths[vehicleIdentity].exists,
            "Vehicle already registered"
        );
        _;
    }

    /// @notice Requires that a birth certificate exists for `vehicleIdentity`.
    /// @param vehicleIdentity The vehicle identity
    modifier vehicleRegistered(address vehicleIdentity) {
        require(
            vehicleBirths[vehicleIdentity].exists,
            "Vehicle not registered"
        );
        _;
    }

    // ============ CONSTRUCTOR ============

    /// @notice Makes the deployer the registry authority and an authorized manufacturer.
    /// @dev Emits ManufacturerAuthorized(deployer). The auto-authorisation is "for testing".
    constructor() {
        registryAuthority = msg.sender;
        // Automatically authorize deployer as first manufacturer (for testing)
        authorizedManufacturers[msg.sender] = true;
        emit ManufacturerAuthorized(msg.sender, block.timestamp);
    }

    // ============ MANUFACTURER MANAGEMENT ============

    /**
     * @notice Authorize a manufacturer to register vehicle births
     * @dev onlyRegistryAuthority; rejects the zero address and duplicates.
     *      Emits ManufacturerAuthorized. CVIN extension (MOBI profile).
     * @param manufacturer Address of manufacturer to authorize
     */
    function authorizeManufacturer(address manufacturer)
        external
        onlyRegistryAuthority
    {
        require(manufacturer != address(0), "Invalid manufacturer address");
        require(!authorizedManufacturers[manufacturer], "Manufacturer already authorized");

        authorizedManufacturers[manufacturer] = true;
        emit ManufacturerAuthorized(manufacturer, block.timestamp);
    }

    /**
     * @notice Revoke manufacturer authorization
     * @dev onlyRegistryAuthority. Emits ManufacturerAuthorizationRevoked. Existing
     *      births are unaffected, and the revoked manufacturer keeps its
     *      first-key anchoring right on vehicles it registered.
     * @param manufacturer Address of manufacturer to revoke
     */
    function revokeManufacturerAuthorization(address manufacturer)
        external
        onlyRegistryAuthority
    {
        require(authorizedManufacturers[manufacturer], "Manufacturer not authorized");

        authorizedManufacturers[manufacturer] = false;
        emit ManufacturerAuthorizationRevoked(manufacturer, block.timestamp);
    }

    /**
     * @notice Transfer registry authority (e.g., to a DAO or government)
     * @dev onlyRegistryAuthority; one-step, non-zero check only.
     * @custom:security Emits no event, and has no two-step acceptance.
     * @param newAuthority Address of new registry authority
     */
    function transferRegistryAuthority(address newAuthority)
        external
        onlyRegistryAuthority
    {
        require(newAuthority != address(0), "Invalid authority address");
        registryAuthority = newAuthority;
    }

    // ============ VEHICLE BIRTH REGISTRATION (MOBI VID I) ============

    /**
     * @dev Register vehicle birth certificate
     *
     * This is the core MOBI VID I function. It creates an immutable
     * birth certificate that serves as the anchor for all future
     * vehicle identity operations.
     *
     * onlyAuthorizedManufacturer, vehicleNotRegistered. Rejects zero values,
     * duplicate VIN hashes and any identity with DID history (K-4). Sets
     * owners[vehicleIdentity] = firstOwner directly, writes the optional
     * keccak256("mobi/vid/birth/attributes") attribute with firstOwner as the
     * ERC-1056 actor, then emits VehicleBirthRegistered and DIDOwnerChanged
     * (and DIDAttributeChanged if attributes are given). MOBI VID I.
     * @notice Register the birth certificate of a new vehicle (authorized manufacturer only).
     *
     * @param vehicleIdentity Address that will represent this vehicle (vehicle DID)
     * @param vinHash Hash of VIN for privacy-preserving searchability
     * @param encryptedVIN Encrypted VIN (only owner can decrypt)
     * @param birthCertHash IPFS hash of complete birth certificate data
     *        (in practice a keccak256 content hash of the signed birth VC)
     * @param firstOwner DID of first owner
     * @param birthAttributes Additional attributes (manufacturer data, specs, etc.)
     */
    function registerVehicleBirth(
        address vehicleIdentity,
        bytes32 vinHash,
        string calldata encryptedVIN,
        bytes32 birthCertHash,
        address firstOwner,
        bytes calldata birthAttributes
    )
        external
        onlyAuthorizedManufacturer
        vehicleNotRegistered(vehicleIdentity)
    {
        require(vehicleIdentity != address(0), "Invalid vehicle identity");
        require(vinHash != bytes32(0), "Invalid VIN hash");
        require(firstOwner != address(0), "Invalid first owner");
        require(vinHashToIdentity[vinHash] == address(0), "VIN hash already registered");
        // REVIEW_02 K-4: only a pristine identity can be born. changed[] is
        // advanced by every path that writes DID state (changeOwner,
        // setAttribute, addDelegate, revoke*, revokeIdentity, and a previous
        // birth), so changed == 0 means: no ERC-1056 owner other than itself,
        // not revoked, and no published DID history. Without this an
        // authorised manufacturer could take over any did:ethr in use, or
        // re-birth a revoked vehicle. One SLOAD, re-read warm below.
        require(changed[vehicleIdentity] == 0, "MOBIVID: identity already has DID history");

        // Create birth certificate
        vehicleBirths[vehicleIdentity] = VehicleBirth({
            vinHash: vinHash,
            encryptedVIN: encryptedVIN,
            birthCertHash: birthCertHash,
            timestamp: block.timestamp,
            manufacturer: msg.sender,
            firstOwner: firstOwner,
            blockNumber: block.number,
            exists: true
        });

        // Map VIN hash to vehicle identity for lookups
        vinHashToIdentity[vinHash] = vehicleIdentity;

        // Set initial owner in ERC-1056
        owners[vehicleIdentity] = firstOwner;

        // Store birth attributes as ERC-1056 attributes
        // This allows W3C DID document construction from events
        //
        // ORDERING / ACTOR CONSTRAINT: ERC1056Registry.setAttribute is
        // guarded by onlyOwner(identity, actor). The line above has just set
        // owners[vehicleIdentity] = firstOwner, so from this point on the
        // ONLY actor that passes that check is firstOwner. Passing
        // msg.sender (the manufacturer) as the actor — as this function
        // originally did — reverts whenever manufacturer != firstOwner,
        // which made every realistic birth registration fail.
        //
        // The manufacturer's authority to perform birth registration is
        // already enforced by the onlyAuthorizedManufacturer modifier on
        // this function; the ERC-1056 attribute is written with firstOwner
        // as the actor (on behalf of the brand-new identity owner) as part
        // of this single atomic registration transaction. This preserves the
        // ERC-1056 invariant that only the current identity owner writes
        // attributes, without weakening the registry's access control.
        if (birthAttributes.length > 0) {
            bytes32 attrName = keccak256("mobi/vid/birth/attributes");
            setAttribute(
                vehicleIdentity,
                firstOwner,
                attrName,
                birthAttributes,
                PERMANENT_ATTRIBUTE_VALIDITY  // finite ~100y; avoids overflow panic
            );
        }

        emit VehicleBirthRegistered(
            vehicleIdentity,
            vinHash,
            msg.sender,
            firstOwner,
            birthCertHash,
            block.timestamp
        );

        // Also emit DIDOwnerChanged for DID resolution
        emit DIDOwnerChanged(vehicleIdentity, firstOwner, changed[vehicleIdentity]);
        changed[vehicleIdentity] = block.number;
    }

    // ============ VEHICLE KEY ANCHORING (defect D11b) ============

    /**
     * @dev Name of the ERC-1056 attribute that carries the vehicle's secp256k1
     *      verification key — the same name registerVehicle / updateVehicleKey
     *      and the testbed resolvers already use, so one event walk finds the
     *      key whichever path published it.
     * @notice ERC-1056 attribute name of the vehicle's verification key.
     * @custom:security keccak name, not the did:ethr ASCII-padded name (see ERC1056Registry).
     */
    bytes32 public constant VEHICLE_KEY_ATTRIBUTE = keccak256("did/pub/secp256k1/veriKey/base64");

    /// @notice True once a verification key has been anchored for the vehicle.
    /// @dev vehicle identity => a verification key has been anchored on-chain
    mapping(address => bool) public vehicleKeyAnchored;

    // ============ DELEGATIONS (WM-2 C2, defect D54) ============
    // The MOBI registry stores delegations, as the canonical ERC-1056 registry does:
    // identity => delegateType => delegate => validTo. The ERC1056Registry base (the
    // testbed's vehicle profile) stays event-only; only this registry, whose
    // attestEvent must check a vehicle owner's consent, keeps them in storage.
    /// @notice Stored delegations: identity => delegateType => delegate => validTo.
    /// @dev Canonical ERC-1056 storage restored (WM-2 C2, D54); read by validDelegate.
    mapping(address => mapping(bytes32 => mapping(address => uint))) public delegates;

    /// @dev Emits DIDDelegateChanged via super (onlyOwner, notRevoked), then stores
    ///      validTo = now + validity. ERC-1056 canonical storage.
    /// @param identity The identity address
    /// @param actor The address acting (must be the current owner)
    /// @param delegateType Type of delegate
    /// @param delegate The delegate address
    /// @param validity Validity period in seconds
    function addDelegate(
        address identity,
        address actor,
        bytes32 delegateType,
        address delegate,
        uint validity
    ) internal override {
        super.addDelegate(identity, actor, delegateType, delegate, validity);
        delegates[identity][delegateType][delegate] = block.timestamp + validity;
    }

    /// @dev Emits DIDDelegateChanged via super (onlyOwner, notRevoked), then sets
    ///      the stored validTo to now. ERC-1056 canonical storage.
    /// @param identity The identity address
    /// @param actor The address acting (must be the current owner)
    /// @param delegateType Type of delegate
    /// @param delegate The delegate address
    function revokeDelegate(
        address identity,
        address actor,
        bytes32 delegateType,
        address delegate
    ) internal override {
        super.revokeDelegate(identity, actor, delegateType, delegate);
        delegates[identity][delegateType][delegate] = block.timestamp;
    }

    /// @dev True while `delegate` holds an unexpired delegation of `delegateType`
    ///      for `identity`, and the identity is not revoked.
    ///      ERC-1056 plus a revocation check. Used by MOBIVIDRegistryV2.attestEvent
    ///      with delegateType bytes32("veriKey") (ASCII-padded, not keccak).
    /// @notice Check whether `delegate` is a currently valid delegate of `identity`.
    /// @param identity The identity address
    /// @param delegateType Type of delegate
    /// @param delegate The delegate address
    /// @return True if the delegation is unexpired and the identity is not revoked
    function validDelegate(
        address identity,
        bytes32 delegateType,
        address delegate
    ) public view returns (bool) {
        return !revoked[identity] && delegates[identity][delegateType][delegate] > block.timestamp;
    }

    /// @notice Emitted when a vehicle verification key is anchored.
    /// @dev CVIN extension (D11b); emitted with the DIDAttributeChanged it accompanies.
    /// @param vehicleIdentity The vehicle identity
    /// @param keyHash keccak256 of the public key
    /// @param anchoredBy msg.sender (owner or registering manufacturer)
    /// @param validTo Expiry of the key attribute
    event VehicleKeyAnchored(
        address indexed vehicleIdentity,
        bytes32 indexed keyHash,
        address indexed anchoredBy,
        uint256 validTo
    );

    /**
     * @dev Anchor the vehicle's verification key on-chain as a DIDAttributeChanged
     *      event with the vehicle-lifetime validity, so that a verifier holding no
     *      off-chain registration record can still resolve the key that signs the
     *      vehicle's V2X messages (defect D11b: before this the key was generated
     *      off-chain after the birth and never published).
     *
     *      Who may anchor:
     *      - the current identity owner, at any time (a rotation with lifetime
     *        validity; updateVehicleKey remains the 1-year variant);
     *      - the manufacturer that registered the birth, exactly once and only
     *        while the vehicle has never changed hands — the birth session. After
     *        the first sale only the owner can publish keys, so the manufacturer
     *        holds no standing power over a vehicle it no longer controls.
     *      The attribute is written with the identity owner as the ERC-1056 actor,
     *      exactly as the birth attributes are, preserving the base invariant that
     *      attributes are owner-authored.
     *      CVIN extension. vehicleRegistered, notRevoked. Accepts a 65- or
     *      33-byte secp256k1 key. Emits DIDAttributeChanged and VehicleKeyAnchored.
     * @notice Publish the vehicle's secp256k1 verification key with vehicle-lifetime validity.
     * @param vehicleIdentity The vehicle identity
     * @param publicKey Uncompressed (65-byte) or compressed (33-byte) secp256k1 public key
     */
    function anchorVehicleKey(address vehicleIdentity, bytes calldata publicKey)
        external
        vehicleRegistered(vehicleIdentity)
        notRevoked(vehicleIdentity)
    {
        require(
            publicKey.length == 65 || publicKey.length == 33,
            "Invalid secp256k1 public key length"
        );
        address owner = identityOwner(vehicleIdentity);
        if (msg.sender != owner) {
            require(
                msg.sender == vehicleBirths[vehicleIdentity].manufacturer,
                "Only the identity owner or the registering manufacturer"
            );
            require(!vehicleKeyAnchored[vehicleIdentity], "Vehicle key already anchored");
            require(
                ownershipHistory[vehicleIdentity].length == 0,
                "Vehicle has changed hands: only the owner can anchor"
            );
        }
        vehicleKeyAnchored[vehicleIdentity] = true;
        setAttribute(vehicleIdentity, owner, VEHICLE_KEY_ATTRIBUTE, publicKey, PERMANENT_ATTRIBUTE_VALIDITY);
        emit VehicleKeyAnchored(
            vehicleIdentity,
            keccak256(publicKey),
            msg.sender,
            block.timestamp + PERMANENT_ATTRIBUTE_VALIDITY
        );
    }

    // ============ VEHICLE OWNERSHIP (MOBI VID II) ============

    /**
     * @dev The inherited public ERC-1056 changeOwner would move a registered
     *      vehicle without an ownershipHistory record (odometer, authority).
     *      REVIEW_02 K-3: registered vehicles must use
     *      transferVehicleOwnership; identities with no birth certificate keep
     *      plain ERC-1056 behaviour.
     * @notice Plain ERC-1056 owner change, disabled for vehicles with a birth certificate.
     * @param identity The identity address
     * @param newOwner The new owner
     */
    function changeOwner(address identity, address newOwner) public override {
        require(
            !vehicleBirths[identity].exists,
            "MOBIVID: use transferVehicleOwnership"
        );
        super.changeOwner(identity, newOwner);
    }

    /**
     * @dev Transfer vehicle ownership
     *
     * This implements MOBI VID II functionality by tracking
     * ownership changes while preserving the immutable birth certificate.
     * vehicleRegistered, onlyOwner(msg.sender), not revoked, non-zero newOwner.
     * Appends an OwnershipTransfer, then emits DIDOwnerChanged and
     * VehicleOwnershipTransferred.
     * @notice Transfer a registered vehicle to `newOwner` and record the transfer (owner only).
     * @custom:security `odometer` and `authority` are caller-supplied and unvalidated.
     *
     * @param vehicleIdentity Vehicle DID
     * @param newOwner New owner DID
     * @param odometer Odometer reading at transfer
     * @param authority Registration authority (e.g., "CA DMV")
     */
    function transferVehicleOwnership(
        address vehicleIdentity,
        address newOwner,
        uint256 odometer,
        string calldata authority
    )
        external
        vehicleRegistered(vehicleIdentity)
        onlyOwner(vehicleIdentity, msg.sender)
    {
        require(newOwner != address(0), "Invalid new owner");
        require(!revoked[vehicleIdentity], "Vehicle identity is revoked");

        address currentOwner = identityOwner(vehicleIdentity);

        // Record ownership transfer
        ownershipHistory[vehicleIdentity].push(OwnershipTransfer({
            from: currentOwner,
            to: newOwner,
            timestamp: block.timestamp,
            blockNumber: block.number,
            odometer: odometer,
            registrationAuthority: authority
        }));

        // Update owner in ERC-1056
        changeOwner(vehicleIdentity, msg.sender, newOwner);

        emit VehicleOwnershipTransferred(
            vehicleIdentity,
            currentOwner,
            newOwner,
            odometer,
            block.timestamp
        );
    }

    // ============ QUERY FUNCTIONS ============

    /**
     * @notice Get vehicle birth certificate
     * @dev Reverts if the vehicle is not registered. MOBI VID I.
     * @param vehicleIdentity Vehicle DID
     * @return Birth certificate data
     */
    function getVehicleBirth(address vehicleIdentity)
        external
        view
        returns (VehicleBirth memory)
    {
        require(vehicleBirths[vehicleIdentity].exists, "Vehicle not registered");
        return vehicleBirths[vehicleIdentity];
    }

    /**
     * @notice Lookup vehicle identity by VIN hash
     * @dev MOBI VID I. Also used by the did:mobi resolution path.
     * @param vinHash Hash of VIN
     * @return vehicleIdentity Vehicle DID (or zero address if not found)
     */
    function lookupByVINHash(bytes32 vinHash)
        external
        view
        returns (address)
    {
        return vinHashToIdentity[vinHash];
    }

    /**
     * @notice Get ownership history for a vehicle
     * @dev vehicleRegistered. Excludes the first owner.
     * @param vehicleIdentity Vehicle DID
     * @return Array of ownership transfers
     */
    function getOwnershipHistory(address vehicleIdentity)
        external
        view
        vehicleRegistered(vehicleIdentity)
        returns (OwnershipTransfer[] memory)
    {
        return ownershipHistory[vehicleIdentity];
    }

    /**
     * @notice Get ownership history count
     * @param vehicleIdentity Vehicle DID
     * @return Number of ownership transfers
     */
    function getOwnershipHistoryCount(address vehicleIdentity)
        external
        view
        returns (uint256)
    {
        return ownershipHistory[vehicleIdentity].length;
    }

    /**
     * @notice Check if vehicle exists
     * @param vehicleIdentity Vehicle DID
     * @return True if vehicle birth certificate exists
     */
    function vehicleExists(address vehicleIdentity)
        external
        view
        returns (bool)
    {
        return vehicleBirths[vehicleIdentity].exists;
    }

    /**
     * @notice Get complete vehicle information (combines birth + ERC-1056 data)
     * @dev vehicleRegistered.
     * @param vehicleIdentity Vehicle DID
     * @return birth Birth certificate
     * @return currentOwner Current owner address
     * @return isRevoked Whether identity is revoked
     * @return transferCount Number of ownership transfers
     */
    function getVehicleInfo(address vehicleIdentity)
        external
        view
        vehicleRegistered(vehicleIdentity)
        returns (
            VehicleBirth memory birth,
            address currentOwner,
            bool isRevoked,
            uint256 transferCount
        )
    {
        return (
            vehicleBirths[vehicleIdentity],
            identityOwner(vehicleIdentity),
            revoked[vehicleIdentity],
            ownershipHistory[vehicleIdentity].length
        );
    }

    // ============ W3C DID COMPLIANCE HELPERS ============

    /**
     * @notice Get DID string for vehicle
     * @dev W3C DID / did:ethr identifier helper; tested in MOBIVIDRegistry.regression.test.js.
     * @param vehicleIdentity Vehicle address
     * @return DID string in format: did:ethr:0x{chainId hex}:0x{40 lowercase hex}
     *
     * The chain id is the minimal (unpadded) lowercase hex of block.chainid
     * with a 0x prefix, as the did:ethr method specification writes it;
     * the address is the 0x-prefixed, zero-padded 40-hex-char form. Earlier
     * revisions omitted the 0x on the address (defect D10), which made the
     * string a non-conformant did:ethr identifier.
     *      (Review-02 K-15 is the same fix, made independently on the parallel trunk.)
     *
     * Note: This is a view helper. In practice, DID resolution
     * happens off-chain by parsing events.
     */
    function getVehicleDID(address vehicleIdentity)
        external
        view
        returns (string memory)
    {
        // Format: did:ethr:0x{chainId hex}:0x{40 lowercase hex address},
        // e.g. did:ethr:0x7a69:0x70997970c51812dc3a010c7d01b50e0d17dc79c8.
        // Review-02 K-15: earlier revisions omitted the "0x" before the
        // address, which did:ethr (and the repo's did_resolver.py) rejects.
        return string(abi.encodePacked(
            "did:ethr:0x",
            _toHexString(block.chainid),
            ":0x",
            _toHexString(uint256(uint160(vehicleIdentity)), 20)
        ));
    }

    // ============ INTERNAL HELPERS ============

    /**
     * @dev Convert uint to hex string
     *      Minimal lowercase hex without prefix ("0" for 0).
     * @param value Value to convert
     * @return Hex string
     */
    function _toHexString(uint256 value) internal pure returns (string memory) {
        if (value == 0) {
            return "0";
        }
        uint256 temp = value;
        uint256 length = 0;
        while (temp != 0) {
            length++;
            temp >>= 4;
        }
        bytes memory buffer = new bytes(length);
        while (value != 0) {
            length -= 1;
            buffer[length] = bytes1(uint8(48 + uint256(value & 0xf)));
            if (uint8(buffer[length]) > 57) {
                buffer[length] = bytes1(uint8(buffer[length]) + 39);
            }
            value >>= 4;
        }
        return string(buffer);
    }

    /**
     * @dev Convert uint to hex string with padding
     *      Zero-padded lowercase hex of exactly 2*length chars; reverts if
     *      `value` does not fit.
     * @param value Value to convert
     * @param length Desired string length
     * @return Hex string
     */
    function _toHexString(uint256 value, uint256 length) internal pure returns (string memory) {
        bytes memory buffer = new bytes(2 * length);
        for (uint256 i = 2 * length; i > 0; --i) {
            buffer[i - 1] = bytes1(uint8(48 + uint256(value & 0xf)));
            if (uint8(buffer[i - 1]) > 57) {
                buffer[i - 1] = bytes1(uint8(buffer[i - 1]) + 39);
            }
            value >>= 4;
        }
        require(value == 0, "Hex length insufficient");
        return string(buffer);
    }
}
