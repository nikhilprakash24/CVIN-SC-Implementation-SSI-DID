// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./EthereumDIDRegistry.sol";

/**
 * @title CVINVehicleDIDRegistry
 * @author CVIN research project
 * @notice Provides convenience functions for vehicle identity lifecycle
 * @dev Vehicle-specific DID management using ERC-1056 (CVIN extension).
 *      Holds a reference to an EthereumDIDRegistry (composition, no inheritance,
 *      no OpenZeppelin). Two modes: direct mode (the owner calls the registry
 *      itself; this contract only holds the VIN<->DID index) and
 *      wrapper-controlled mode (the owner calls didRegistry.changeOwner(did,
 *      address(this)); the wrapper then tracks the vehicle owner in
 *      vehicleOwners and forwards attribute/delegate writes).
 *      Identity model: DID = the vehicle owner's address.
 *
 * Features:
 * - VIN-to-DID mapping
 * - Vehicle-specific attributes
 * - Ownership transfer tracking
 * - Service history references
 * - Credential issuance delegation
 * @custom:standard ERC-1056 Ethereum Lightweight Identity, https://github.com/ethereum/EIPs/issues/1056
 * @custom:standard did:ethr DID method, https://github.com/decentralized-identity/ethr-did-resolver/blob/master/doc/did-method-spec.md
 * @custom:standard W3C DID Core v1.0, https://www.w3.org/TR/did-core/
 * @custom:standard ISO 3779 Vehicle Identification Number (17 characters), https://www.iso.org/standard/52200.html
 * @custom:security No way back: no function returns ERC-1056 control via changeOwner, so a DID handed to the wrapper stays locked in it (no key rotation, no signed operations).
 * @custom:security createVehicleDID binds an arbitrary address without the owner's consent; a second VIN for the same address overwrites didToVIN but leaves the old vinToDID entry.
 * @custom:security DID is conflated with the owner address: a direct-mode transfer re-keys the VIN to a different DID, so the vehicle identifier is not stable.
 * @custom:security The VIN is stored and emitted in plaintext (didToVIN, VehicleDIDCreated).
 * @custom:security Attribute and delegate keys are keccak256 hashes of names, not did:ethr-conformant names.
 * @custom:security No revokeAttribute passthrough: a service endpoint set in wrapper mode cannot be revoked.
 * @custom:see docs/smart-contracts/01-erc1056-did-registry.md
 * @custom:see sandbox/options/erc-1056-uport/adapter.js
 */
contract CVINVehicleDIDRegistry {
    // ============ State Variables ============

    /// @notice The underlying ERC-1056 registry
    /// @dev The underlying ERC-1056 registry (set once in the constructor)
    EthereumDIDRegistry public didRegistry;

    /// @notice DID registered for a VIN hash
    /// @dev Mapping from VIN hash to DID address (key = keccak256(abi.encodePacked(vin)))
    mapping(bytes32 => address) public vinToDID;

    /// @notice VIN registered for a DID
    /// @dev Mapping from DID to VIN (for reverse lookup). Plaintext VIN on-chain.
    mapping(address => string) public didToVIN;

    /// @notice Whether an address may call createVehicleDID
    /// @dev Authorized manufacturers who can create vehicle DIDs
    mapping(address => bool) public authorizedManufacturers;

    /// @notice Admin of this wrapper (the deployer)
    /// @dev Contract owner; not transferable
    address public owner;

    /// @notice Vehicle owner while this wrapper controls the DID
    /// @dev Vehicle owner recorded by this registry while it holds ERC-1056
    ///      control of a DID (see vehicleOwnerOf). address(0) means "the DID
    ///      address itself", mirroring identityOwner()'s default, so
    ///      createVehicleDID needs no extra storage write.
    mapping(address => address) public vehicleOwners;

    // ============ Attribute Keys (bytes32) ============

    /// @notice Attribute key keccak256("did/vehicle/vin") (VID-I)
    bytes32 public constant DID_VIN = keccak256("did/vehicle/vin");
    /// @notice Attribute key keccak256("did/vehicle/make") (VID-I)
    bytes32 public constant DID_MAKE = keccak256("did/vehicle/make");
    /// @notice Attribute key keccak256("did/vehicle/model") (VID-I)
    bytes32 public constant DID_MODEL = keccak256("did/vehicle/model");
    /// @notice Attribute key keccak256("did/vehicle/year") (VID-I)
    bytes32 public constant DID_YEAR = keccak256("did/vehicle/year");
    /// @notice Attribute key keccak256("did/vehicle/color") (VID-I)
    bytes32 public constant DID_COLOR = keccak256("did/vehicle/color");
    /// @notice Attribute key keccak256("did/vehicle/engineNumber") (VID-I)
    bytes32 public constant DID_ENGINE = keccak256("did/vehicle/engineNumber");
    /// @notice Attribute key keccak256("did/vehicle/manufacturingDate") (VID-I)
    bytes32 public constant DID_MANUFACTURING_DATE =
        keccak256("did/vehicle/manufacturingDate");
    /// @notice Attribute key keccak256("did/vehicle/autonomyLevel") (VID-I)
    bytes32 public constant DID_AUTONOMY_LEVEL =
        keccak256("did/vehicle/autonomyLevel");

    // Service Endpoints
    /// @notice Service-endpoint key keccak256("did/svc/CredentialService")
    bytes32 public constant SVC_CREDENTIAL_SERVICE =
        keccak256("did/svc/CredentialService");
    /// @notice Service-endpoint key keccak256("did/svc/MessagingService")
    bytes32 public constant SVC_MESSAGING = keccak256("did/svc/MessagingService");
    /// @notice Service-endpoint key keccak256("did/svc/TelemetryService")
    bytes32 public constant SVC_TELEMETRY = keccak256("did/svc/TelemetryService");

    /// @notice Validity (100 years) of the attributes written by setVehicleAttributes
    /// @dev Validity of the "permanent" vehicle attributes written by
    ///      setVehicleAttributes. EthereumDIDRegistry computes
    ///      block.timestamp + validity with checked arithmetic, so the value
    ///      must be finite; 100 years matches
    ///      MOBIVIDRegistry.PERMANENT_ATTRIBUTE_VALIDITY.
    uint256 public constant VEHICLE_ATTRIBUTE_VALIDITY = 100 * 365 days;

    // Delegate Types
    /// @notice Delegate type keccak256("veriKey")
    bytes32 public constant DELEGATE_VERIKEY = keccak256("veriKey");
    /// @notice Delegate type keccak256("sigAuth")
    bytes32 public constant DELEGATE_SIGAUTH = keccak256("sigAuth");

    /**
     * @notice Validity (100 years) of permanent birth attributes; same value as VEHICLE_ATTRIBUTE_VALIDITY
     * @dev Validity (seconds) used for the "permanent" birth attributes written
     *      by setVehicleAttributes. EthereumDIDRegistry.setAttribute computes
     *      `block.timestamp + validity` under Solidity 0.8 checked arithmetic,
     *      so the former `type(uint256).max` overflowed (panic 0x11) and the
     *      eight-attribute birth record was unreachable (defect D18). 100 years
     *      is effectively permanent for a vehicle lifecycle and never overflows.
     *      Same constant as MOBIVIDRegistry.PERMANENT_ATTRIBUTE_VALIDITY.
     * @custom:note Duplicate of VEHICLE_ATTRIBUTE_VALIDITY and unused inside this
     *      contract (setVehicleAttributes reads VEHICLE_ATTRIBUTE_VALIDITY); kept
     *      because the D18 regression test reads it.
     */
    uint256 public constant PERMANENT_ATTRIBUTE_VALIDITY = 100 * 365 days;

    // ============ Events ============

    /**
     * @notice Emitted when a manufacturer registers a VIN for a DID.
     * @dev CVIN extension; emitted by createVehicleDID. Carries the plaintext VIN.
     * @param did The vehicle DID (equals the owner address)
     * @param vin The 17-character VIN
     * @param owner The initial vehicle owner
     * @param manufacturer The authorised manufacturer that registered it
     */
    event VehicleDIDCreated(
        address indexed did,
        string vin,
        address indexed owner,
        address indexed manufacturer
    );

    /**
     * @notice Emitted when vehicle ownership changes.
     * @dev CVIN extension; emitted by transferVehicleOwnership and by
     *      updateOwnershipMapping (there as (oldDID, oldDID, newDID)).
     * @param did The vehicle DID (the old DID in the direct flow)
     * @param previousOwner The previous owner
     * @param newOwner The new owner (the new DID in the direct flow)
     */
    event VehicleOwnershipTransferred(
        address indexed did,
        address indexed previousOwner,
        address indexed newOwner
    );

    /**
     * @notice Emitted when the manufacturer role is granted or revoked.
     * @dev CVIN extension; emitted by setAuthorizedManufacturer.
     * @param manufacturer The affected address
     * @param authorized True if granted, false if revoked
     */
    event ManufacturerAuthorized(address indexed manufacturer, bool authorized);

    // ============ Modifiers ============

    /// @notice Restricts a call to the wrapper admin (`owner`).
    modifier onlyContractOwner() {
        require(msg.sender == owner, "CVINRegistry: not owner");
        _;
    }

    /// @notice Restricts a call to an authorised manufacturer.
    modifier onlyAuthorizedManufacturer() {
        require(
            authorizedManufacturers[msg.sender],
            "CVINRegistry: not authorized manufacturer"
        );
        _;
    }

    /**
     * @notice Restricts a call to the vehicle owner of `did`.
     * @dev Requires `msg.sender == vehicleOwnerOf(did)`.
     * @param did Vehicle DID
     */
    modifier onlyVehicleOwner(address did) {
        require(
            msg.sender == vehicleOwnerOf(did),
            "CVINRegistry: not vehicle owner"
        );
        _;
    }

    // ============ Constructor ============

    /**
     * @notice Bind the wrapper to an ERC-1056 registry.
     * @dev CVIN extension. The deployer becomes `owner` and the first authorised
     *      manufacturer. The registry address is not validated.
     * @param _didRegistry Address of the deployed EthereumDIDRegistry
     */
    constructor(address _didRegistry) {
        didRegistry = EthereumDIDRegistry(_didRegistry);
        owner = msg.sender;
        authorizedManufacturers[msg.sender] = true;
    }

    // ============ Admin Functions ============

    /**
     * @notice Grant or revoke the manufacturer role.
     * @dev CVIN extension. `onlyContractOwner`; emits ManufacturerAuthorized.
     * @param manufacturer Address to update
     * @param authorized True to grant, false to revoke
     */
    function setAuthorizedManufacturer(
        address manufacturer,
        bool authorized
    ) external onlyContractOwner {
        authorizedManufacturers[manufacturer] = authorized;
        emit ManufacturerAuthorized(manufacturer, authorized);
    }

    // ============ Vehicle DID Creation ============

    /**
     * @notice Create a new vehicle DID with comprehensive attributes
     * @param vin Vehicle Identification Number
     * @param vehicleOwner Initial owner address
     * @param make Vehicle make (e.g., "Honda")
     * @param model Vehicle model (e.g., "Accord")
     * @param year Manufacturing year
     * @param color Vehicle color
     * @param engineNumber Engine identification number
     * @param manufacturingDate Date of manufacture (timestamp)
     * @param autonomyLevel SAE autonomy level
     * @return did The created DID address
     * @dev CVIN extension. `onlyAuthorizedManufacturer`; requires a 17-byte VIN not
     *      yet registered; sets did = vehicleOwner, stores vinToDID/didToVIN and
     *      emits VehicleDIDCreated. Called by the sandbox adapter's create().
     * @custom:note make, model, year, color, engineNumber, manufacturingDate and
     *      autonomyLevel are accepted but ignored: no attributes are written here
     *      (use setVehicleAttributes or didRegistry.setAttribute).
     */
    function createVehicleDID(
        string memory vin,
        address vehicleOwner,
        string memory make,
        string memory model,
        uint16 year,
        string memory color,
        string memory engineNumber,
        uint256 manufacturingDate,
        string memory autonomyLevel
    ) external onlyAuthorizedManufacturer returns (address did) {
        // Validate VIN
        require(bytes(vin).length == 17, "CVINRegistry: invalid VIN length");

        bytes32 vinHash = keccak256(abi.encodePacked(vin));
        require(vinToDID[vinHash] == address(0), "CVINRegistry: VIN already registered");

        // In ERC-1056, the vehicleOwner's address IS the DID
        // Any Ethereum address is implicitly a valid DID
        did = vehicleOwner;

        // Store VIN mapping
        vinToDID[vinHash] = did;
        didToVIN[did] = vin;

        // Note: In ERC-1056, attributes are set by the DID owner (vehicle owner)
        // The manufacturer just creates the registration mapping
        // Attributes: the vehicle owner either calls didRegistry.setAttribute
        // directly, or hands ERC-1056 control to this registry and calls
        // setVehicleAttributes(did, ...) (one tx for the whole VID-I set).

        emit VehicleDIDCreated(did, vin, vehicleOwner, msg.sender);

        return did;
    }

    /**
     * @notice Publish the vehicle attribute set (VID-I data) for a DID in one
     *         transaction, as eight ERC-1056 DIDAttributeChanged events.
     * @dev Wrapper-controlled mode only: ERC-1056 lets only the identity owner
     *      write attributes, so the vehicle owner must first hand ERC-1056
     *      control of the DID to this registry
     *      (didRegistry.changeOwner(did, address(this))), exactly as for
     *      setServiceEndpoint / addVerificationDelegate. The caller must be
     *      the vehicle owner as this registry defines it (vehicleOwnerOf).
     *      In the direct ERC-1056 flow the owner calls
     *      didRegistry.setAttribute itself.
     *
     *      REVIEW_02 K-1: the previous version took no DID (it used
     *      msg.sender as the DID, which is never the ERC-1056 owner once the
     *      registry holds control) and passed validity = type(uint256).max,
     *      so `block.timestamp + validity` overflowed (panic 0x11). It
     *      reverted on every call.
     *      `onlyVehicleOwner(did)`; requires identityOwner(did) == this and a
     *      registered VIN; the registry emits 8x DIDAttributeChanged.
     * @param did Vehicle DID
     * @param make Vehicle make
     * @param model Vehicle model
     * @param year Manufacturing year
     * @param color Vehicle color
     * @param engineNumber Engine identification
     * @param manufacturingDate Manufacturing date
     * @param autonomyLevel SAE autonomy level
     */
    function setVehicleAttributes(
        address did,
        string memory make,
        string memory model,
        uint16 year,
        string memory color,
        string memory engineNumber,
        uint256 manufacturingDate,
        string memory autonomyLevel
    ) external onlyVehicleOwner(did) {
        require(
            didRegistry.identityOwner(did) == address(this),
            "CVINRegistry: registry does not control DID"
        );
        string memory vin = didToVIN[did];
        require(bytes(vin).length > 0, "CVINRegistry: DID not registered");

        uint256 validity = VEHICLE_ATTRIBUTE_VALIDITY;

        // Set all vehicle attributes
        didRegistry.setAttribute(did, DID_VIN, bytes(vin), validity);
        didRegistry.setAttribute(did, DID_MAKE, bytes(make), validity);
        didRegistry.setAttribute(did, DID_MODEL, bytes(model), validity);
        didRegistry.setAttribute(did, DID_YEAR, abi.encodePacked(year), validity);
        didRegistry.setAttribute(did, DID_COLOR, bytes(color), validity);
        didRegistry.setAttribute(did, DID_ENGINE, bytes(engineNumber), validity);
        didRegistry.setAttribute(did, DID_MANUFACTURING_DATE, abi.encodePacked(manufacturingDate), validity);
        didRegistry.setAttribute(did, DID_AUTONOMY_LEVEL, bytes(autonomyLevel), validity);
    }

    // ============ Ownership Management ============

    /**
     * @notice Transfer vehicle ownership in a single step via this registry
     * @dev Requires this contract to hold ERC-1056 control of the DID (the
     *      vehicle owner calls didRegistry.changeOwner(did, address(this))
     *      once). The DID itself is unchanged; only its owner record moves.
     *      For the direct ERC-1056 flow use updateOwnershipMapping instead.
     *      CVIN extension; `onlyVehicleOwner(did)`; newOwner must be non-zero;
     *      emits VehicleOwnershipTransferred.
     * @param did Vehicle DID
     * @param newOwner New vehicle owner address
     */
    function transferVehicleOwnership(
        address did,
        address newOwner
    ) external onlyVehicleOwner(did) {
        require(newOwner != address(0), "CVINRegistry: new owner is zero address");
        require(
            didRegistry.identityOwner(did) == address(this),
            "CVINRegistry: registry does not control DID"
        );

        address previousOwner = vehicleOwnerOf(did);
        vehicleOwners[did] = newOwner;

        emit VehicleOwnershipTransferred(did, previousOwner, newOwner);
    }

    /**
     * @notice Transfer vehicle ownership
     * @dev In ERC-1056, the owner must call didRegistry.changeOwner() directly.
     *      This function updates the VIN mapping after ownership transfer.
     *      CVIN extension, direct mode. Callable by anyone: the only check is
     *      identityOwner(oldOwnerDID) == newOwnerDID. Moves the VIN to
     *      newOwnerDID and emits VehicleOwnershipTransferred(old, old, new).
     * @custom:note The in-body comment "Verify caller is the new owner" is stale:
     *      msg.sender is not checked. That is safe: the result is fixed by the ERC-1056
     *      owner's own changeOwner, so any caller can only perform the sync it already
     *      authorised (a permissionless follow-up, not a takeover).
     * @param oldOwnerDID Old owner's DID (address)
     * @param newOwnerDID New owner's DID (address)
     */
    function updateOwnershipMapping(
        address oldOwnerDID,
        address newOwnerDID
    ) external {
        // Get VIN from old owner
        string memory vin = didToVIN[oldOwnerDID];
        require(bytes(vin).length > 0, "CVINRegistry: VIN not found");

        // Verify caller is the new owner (they should have completed changeOwner on DID registry)
        require(
            didRegistry.identityOwner(oldOwnerDID) == newOwnerDID,
            "CVINRegistry: ownership not transferred in DID registry"
        );

        bytes32 vinHash = keccak256(abi.encodePacked(vin));

        // Update mappings
        delete didToVIN[oldOwnerDID];
        vinToDID[vinHash] = newOwnerDID;
        didToVIN[newOwnerDID] = vin;

        emit VehicleOwnershipTransferred(oldOwnerDID, oldOwnerDID, newOwnerDID);
    }

    // ============ Service Endpoints ============

    /**
     * @notice Set service endpoint for vehicle
     * @param did Vehicle DID
     * @param endpointType Type of endpoint (CREDENTIAL_SERVICE, MESSAGING, etc.)
     * @param endpointURL URL of the service
     * @param validity Validity period in seconds
     * @dev ERC-1056 passthrough to didRegistry.setAttribute. `onlyVehicleOwner(did)`;
     *      reverts in the registry unless this wrapper controls the DID. The registry
     *      emits DIDAttributeChanged. No matching revoke function exists.
     */
    function setServiceEndpoint(
        address did,
        bytes32 endpointType,
        string memory endpointURL,
        uint validity
    ) external onlyVehicleOwner(did) {
        didRegistry.setAttribute(did, endpointType, bytes(endpointURL), validity);
    }

    // ============ Delegate Management (Verification Keys) ============

    /**
     * @notice Add verification key delegate for credential issuance
     * @param did Vehicle DID
     * @param delegateAddress Address of the delegate
     * @param delegateType Type of delegate (VERIKEY, SIGAUTH)
     * @param validity Validity period in seconds
     * @dev ERC-1056 passthrough to didRegistry.addDelegate. `onlyVehicleOwner(did)`;
     *      wrapper-controlled mode only; the registry emits DIDDelegateChanged.
     */
    function addVerificationDelegate(
        address did,
        address delegateAddress,
        bytes32 delegateType,
        uint validity
    ) external onlyVehicleOwner(did) {
        didRegistry.addDelegate(did, delegateType, delegateAddress, validity);
    }

    /**
     * @notice Revoke verification delegate
     * @param did Vehicle DID
     * @param delegateAddress Address of the delegate
     * @param delegateType Type of delegate
     * @dev ERC-1056 passthrough to didRegistry.revokeDelegate. `onlyVehicleOwner(did)`;
     *      wrapper-controlled mode only; the registry emits DIDDelegateChanged (validTo 0).
     */
    function revokeVerificationDelegate(
        address did,
        address delegateAddress,
        bytes32 delegateType
    ) external onlyVehicleOwner(did) {
        didRegistry.revokeDelegate(did, delegateType, delegateAddress);
    }

    // ============ Query Functions ============

    /**
     * @notice Get DID address from VIN
     * @param vin Vehicle Identification Number
     * @dev CVIN extension; reads vinToDID[keccak256(vin)].
     * @return DID address (address(0) if not found)
     */
    function getDIDFromVIN(string memory vin) external view returns (address) {
        bytes32 vinHash = keccak256(abi.encodePacked(vin));
        return vinToDID[vinHash];
    }

    /**
     * @notice Get VIN from DID address
     * @param did DID address
     * @dev CVIN extension; reads didToVIN. Used by the sandbox adapter's resolve().
     * @return VIN string (empty if not found)
     */
    function getVINFromDID(address did) external view returns (string memory) {
        return didToVIN[did];
    }

    /**
     * @notice Resolve the vehicle owner of a DID
     * @dev ERC-1056 only lets the identity owner mutate a DID, so the wrapper
     *      functions above (service endpoints, delegates) can only act once the
     *      vehicle owner has handed ERC-1056 control of the DID to this contract
     *      via didRegistry.changeOwner(did, address(this)). While this contract
     *      is the ERC-1056 owner, the vehicle owner is tracked in vehicleOwners
     *      (defaulting to the DID address itself, the initial owner set by
     *      createVehicleDID). Otherwise the ERC-1056 owner is authoritative.
     * @param did Vehicle DID
     * @return Vehicle owner address
     */
    function vehicleOwnerOf(address did) public view returns (address) {
        address controller = didRegistry.identityOwner(did);
        if (controller != address(this)) {
            return controller;
        }
        address recorded = vehicleOwners[did];
        return recorded == address(0) ? did : recorded;
    }

    /**
     * @notice Get vehicle owner
     * @dev CVIN extension; alias for vehicleOwnerOf.
     * @param did Vehicle DID
     * @return Owner address
     */
    function getVehicleOwner(address did) external view returns (address) {
        return vehicleOwnerOf(did);
    }

    /**
     * @notice Check if a delegate is valid
     * @param did Vehicle DID
     * @param delegateType Type of delegate
     * @param delegateAddress Delegate address
     * @dev ERC-1056 passthrough to didRegistry.validDelegate.
     * @return True if delegate is currently valid
     */
    function isValidDelegate(
        address did,
        bytes32 delegateType,
        address delegateAddress
    ) external view returns (bool) {
        return didRegistry.validDelegate(did, delegateType, delegateAddress);
    }
}
