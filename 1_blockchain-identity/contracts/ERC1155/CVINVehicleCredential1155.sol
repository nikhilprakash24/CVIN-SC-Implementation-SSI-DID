// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title CVINVehicleCredential1155
 * @dev ERC-1155 multi-token vehicle credential registry for connected vehicle
 *      identity (CVIN). Each token ID is a CREDENTIAL TYPE; a vehicle is an
 *      address whose balances represent the credentials it currently holds.
 *
 * Credential type token IDs:
 *   BIRTH_CERT        = 1  (vehicle birth certificate — holding it = identity exists)
 *   REGISTRATION      = 2  (jurisdictional registration)
 *   INSPECTION_CERT   = 3  (periodic technical inspection certificate)
 *   INSURANCE_CERT    = 4  (insurance coverage certificate)
 *   MAINTENANCE_BADGE = 5  (certified maintenance/service badge)
 *
 * Model (documented for the thesis gas comparison):
 * - Identity creation = registerVehicle(): mints exactly one BIRTH_CERT to the
 *   vehicle address and records its VIN.
 * - Issuance mints (onlyRole ISSUER_ROLE), revocation burns (onlyRole ISSUER_ROLE).
 * - Credentials are SOULBOUND-ISH: _update is overridden so that transfers
 *   between non-zero addresses are only possible when initiated by an
 *   ISSUER_ROLE holder (e.g. re-binding credentials on vehicle ownership
 *   change). Holder-initiated safeTransferFrom reverts.
 * - Per-token-type metadata URI via setTokenURI (attribute update operation).
 *
 * Fully spec-compliant ERC-1155 interface surface (inherits OZ 5.0.2 ERC1155);
 * the soulbound transfer restriction is an intentional application-level
 * deviation from ERC-1155's free transferability.
 */
contract CVINVehicleCredential1155 is ERC1155, AccessControl {
    // ============ Roles ============
    bytes32 public constant ISSUER_ROLE = keccak256("ISSUER_ROLE");

    // ============ Credential type token IDs ============
    uint256 public constant BIRTH_CERT = 1;
    uint256 public constant REGISTRATION = 2;
    uint256 public constant INSPECTION_CERT = 3;
    uint256 public constant INSURANCE_CERT = 4;
    uint256 public constant MAINTENANCE_BADGE = 5;

    // ============ Vehicle identity state ============

    /// @dev vehicle address => VIN
    mapping(address => string) public vehicleVIN;

    /// @dev keccak256(VIN) => vehicle address (uniqueness index)
    mapping(bytes32 => address) public vinHashToVehicle;

    /// @dev per-credential-type metadata URI (overrides the base uri)
    mapping(uint256 => string) private _tokenURIs;

    // ============ Events ============
    event VehicleRegistered(address indexed vehicle, bytes32 indexed vinHash, string vin);
    event CredentialIssued(address indexed vehicle, uint256 indexed credentialType, uint256 amount, address indexed issuer);
    event CredentialRevoked(address indexed vehicle, uint256 indexed credentialType, uint256 amount, address indexed issuer);
    event CredentialURIUpdated(uint256 indexed credentialType, string newURI);

    constructor() ERC1155("ipfs://cvin-vehicle-credentials/{id}.json") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ISSUER_ROLE, msg.sender);
    }

    // ============ Identity creation ============

    /**
     * @notice Register a new vehicle identity: mints one BIRTH_CERT credential
     *         to the vehicle address and binds its VIN.
     */
    function registerVehicle(address vehicle, string calldata vin)
        external
        onlyRole(ISSUER_ROLE)
    {
        require(vehicle != address(0), "CVIN1155: vehicle is zero address");
        require(bytes(vin).length > 0, "CVIN1155: empty VIN");
        require(balanceOf(vehicle, BIRTH_CERT) == 0, "CVIN1155: vehicle already registered");
        // D13: normalise (upper-case) and validate the ISO 3779 shape before hashing, so
        // "1hgbh41jxmn109186" and "1HGBH41JXMN109186" index the same vehicle.
        string memory normalizedVIN = _normalizeVIN(vin);
        bytes32 vinHash = keccak256(bytes(normalizedVIN));
        require(vinHashToVehicle[vinHash] == address(0), "CVIN1155: VIN already registered");

        vehicleVIN[vehicle] = normalizedVIN;
        vinHashToVehicle[vinHash] = vehicle;

        _mint(vehicle, BIRTH_CERT, 1, "");

        emit VehicleRegistered(vehicle, vinHash, normalizedVIN);
        emit CredentialIssued(vehicle, BIRTH_CERT, 1, msg.sender);
    }

    // ============ Credential issuance / revocation ============

    /**
     * @notice Issue a credential of a given type to a registered vehicle.
     */
    function issueCredential(address vehicle, uint256 credentialType, uint256 amount)
        external
        onlyRole(ISSUER_ROLE)
    {
        require(balanceOf(vehicle, BIRTH_CERT) > 0, "CVIN1155: vehicle not registered");
        require(credentialType != BIRTH_CERT, "CVIN1155: use registerVehicle for BIRTH_CERT");
        require(amount > 0, "CVIN1155: amount must be positive");

        _mint(vehicle, credentialType, amount, "");
        emit CredentialIssued(vehicle, credentialType, amount, msg.sender);
    }

    /**
     * @notice Revoke (burn) credentials held by a vehicle.
     */
    function revokeCredential(address vehicle, uint256 credentialType, uint256 amount)
        external
        onlyRole(ISSUER_ROLE)
    {
        require(balanceOf(vehicle, credentialType) >= amount, "CVIN1155: insufficient credential balance");

        _burn(vehicle, credentialType, amount);
        emit CredentialRevoked(vehicle, credentialType, amount, msg.sender);

        // Burning the BIRTH_CERT deregisters the vehicle identity
        if (credentialType == BIRTH_CERT && balanceOf(vehicle, BIRTH_CERT) == 0) {
            bytes32 vinHash = keccak256(bytes(vehicleVIN[vehicle]));
            delete vinHashToVehicle[vinHash];
            delete vehicleVIN[vehicle];
        }
    }

    // ============ Issuer-mediated transfer (vehicle ownership change) ============

    /**
     * @notice Move all units of a credential type from one vehicle address to
     *         another (e.g. identity re-binding after a sale). Issuer only —
     *         holders cannot transfer their own credentials.
     */
    function issuerTransferCredential(
        address from,
        address to,
        uint256 credentialType
    ) external onlyRole(ISSUER_ROLE) {
        // Found by the S2 sandbox smoke run (2026-10-04): a self-transfer deleted the
        // VIN mapping after re-writing it. Transfers to the same holder are rejected.
        require(from != to, "CVIN1155: transfer to same holder");
        uint256 amount = balanceOf(from, credentialType);
        require(amount > 0, "CVIN1155: nothing to transfer");
        _safeTransferFrom(from, to, credentialType, amount, "");

        if (credentialType == BIRTH_CERT) {
            string memory vin = vehicleVIN[from];
            bytes32 vinHash = keccak256(bytes(vin));
            vehicleVIN[to] = vin;
            vinHashToVehicle[vinHash] = to;
            delete vehicleVIN[from];
        }
    }

    // ============ Metadata (attribute update) ============

    function setTokenURI(uint256 credentialType, string calldata newURI)
        external
        onlyRole(ISSUER_ROLE)
    {
        _tokenURIs[credentialType] = newURI;
        emit CredentialURIUpdated(credentialType, newURI);
    }

    function uri(uint256 credentialType) public view override returns (string memory) {
        string memory tokenURI = _tokenURIs[credentialType];
        if (bytes(tokenURI).length > 0) {
            return tokenURI;
        }
        return super.uri(credentialType);
    }

    // ============ Views ============

    function isRegistered(address vehicle) external view returns (bool) {
        return balanceOf(vehicle, BIRTH_CERT) > 0;
    }

    function hasCredential(address vehicle, uint256 credentialType) external view returns (bool) {
        return balanceOf(vehicle, credentialType) > 0;
    }

    /**
     * @notice The key of the vinHashToVehicle index for a VIN, computed with the same
     *         normalisation as registerVehicle (upper-cased, ISO 3779 shape checked).
     */
    function vinHashOf(string calldata vin) public pure returns (bytes32) {
        return keccak256(bytes(_normalizeVIN(vin)));
    }

    /**
     * @notice VIN -> registered vehicle address, case-insensitive (zero address if none).
     */
    function vehicleForVIN(string calldata vin) external view returns (address) {
        return vinHashToVehicle[vinHashOf(vin)];
    }

    // ============ VIN normalisation ============

    /**
     * @dev ISO 3779 VIN normalisation and shape validation (defect D13).
     *      - exactly 17 characters;
     *      - lower-case ASCII letters are upper-cased before the VIN is stored or used
     *        as a key, so the same physical VIN cannot mint a second identity by case;
     *      - after upper-casing every character must be in [A-HJ-NPR-Z0-9]: the letters
     *        I, O and Q are excluded by ISO 3779 (confusable with 1 and 0).
     *      The ISO 3779 / FMVSS 115 check digit (position 9) is intentionally NOT
     *      enforced: it is mandatory only in North America, and the fixture VINs used
     *      across the test suites and demos do not carry a valid check digit.
     *      The same helper (identical logic) lives in CVINVehicleNFT and
     *      CVINVehicleLSP8; Solidity has no shared stdlib here.
     * @param vin Raw VIN as supplied by the caller (memory; mutated in place)
     * @return The normalised, validated VIN
     */
    function _normalizeVIN(string memory vin) internal pure returns (string memory) {
        bytes memory b = bytes(vin);
        require(b.length == 17, "CVIN1155: invalid VIN length");
        bytes32 word = bytes32(b); // one memory read for all 17 characters (bytes 17..31 are zero padding)
        for (uint256 i = 0; i < 17; ++i) {
            uint256 c = uint8(word[i]);
            if (((_VIN_LOWER_AZ >> c) & 1) == 1) {
                c -= 0x20; // 'a'..'z' -> 'A'..'Z'
                b[i] = bytes1(uint8(c)); // written back only when the character actually changes
            }
            require(((_VIN_ALLOWED >> c) & 1) == 1, "CVIN1155: invalid VIN character");
        }
        return string(b);
    }

    /// @dev Character-set bitmaps over the ASCII byte value (bit c set <=> byte c is in the set).
    ///      _VIN_ALLOWED: '0'..'9' (0x30..0x39) and 'A'..'Z' (0x41..0x5A) minus I (0x49), O (0x4F), Q (0x51).
    ///      _VIN_LOWER_AZ: 'a'..'z' (0x61..0x7A), the only characters normalisation rewrites.
    uint256 private constant _VIN_ALLOWED =
        (uint256(0x3FF) << 0x30)
        | ((((uint256(1) << 26) - 1) << 0x41) & ~((uint256(1) << 0x49) | (uint256(1) << 0x4F) | (uint256(1) << 0x51)));
    uint256 private constant _VIN_LOWER_AZ = ((uint256(1) << 26) - 1) << 0x61;

    // ============ Soulbound enforcement ============

    /**
     * @dev Block holder-initiated transfers: mint (from == 0) and burn (to == 0)
     *      always pass; a transfer between two non-zero addresses requires the
     *      transaction initiator (msg.sender) to hold ISSUER_ROLE.
     */
    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory values
    ) internal override {
        if (from != address(0) && to != address(0)) {
            require(
                hasRole(ISSUER_ROLE, _msgSender()),
                "CVIN1155: credentials are soulbound (issuer-mediated transfer only)"
            );
        }
        super._update(from, to, ids, values);
    }

    // ============ Required override ============

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC1155, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
