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
 * - Credentials are SOULBOUND: the standard safeTransferFrom / safeBatchTransferFrom
 *   entry points always revert (for holders, operators and issuers alike). The only
 *   paths that move a credential between two addresses are the issuer-mediated
 *   issuerTransferCredential (one type) and issuerTransferIdentity (the BIRTH_CERT
 *   together with every other credential the vehicle holds), both of which keep the
 *   VIN indexes bound to the holder of the BIRTH_CERT (defect D7, fixed 2026-10-04).
 * - Invariants kept by the issuer paths and by revokeCredential (defect D8):
 *     (i)   a non-BIRTH credential is only ever held by a registered vehicle;
 *     (ii)  a BIRTH_CERT is only burned, or moved on its own, when the vehicle holds
 *           no other credential (no orphaned credentials on a non-vehicle address);
 *     (iii) credential types are 1..255, so the set a vehicle holds is a bitmap the
 *           contract can enumerate (credentialTypesOf) and move atomically.
 *   The issuer model itself is unchanged and documented rather than fixed: ISSUER_ROLE
 *   is one flat, registry-wide role; any issuer may revoke a credential issued by
 *   another issuer, because a fungible balance is not linked to its issuer on-chain.
 * - Per-token-type metadata URI via setTokenURI (attribute update operation); the
 *   standard URI(value, id) event is emitted alongside CredentialURIUpdated.
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

    /// @dev Highest credential type id (exclusive): the held-type set is a 256-bit bitmap.
    uint256 public constant MAX_CREDENTIAL_TYPE = 255;

    /// @dev vehicle address => bitmap of non-BIRTH credential types with a positive balance
    ///      (bit t set <=> balanceOf(vehicle, t) > 0). Maintained in _update.
    mapping(address => uint256) private _heldTypes;

    // ============ Events ============
    event VehicleRegistered(address indexed vehicle, bytes32 indexed vinHash, string vin);
    event CredentialIssued(address indexed vehicle, uint256 indexed credentialType, uint256 amount, address indexed issuer);
    event CredentialRevoked(address indexed vehicle, uint256 indexed credentialType, uint256 amount, address indexed issuer);
    event CredentialURIUpdated(uint256 indexed credentialType, string newURI);
    /// @dev The whole identity (BIRTH_CERT + every held credential type) moved to a new address.
    event IdentityRebound(address indexed from, address indexed to, bytes32 indexed vinHash, uint256 credentialTypesMoved);

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
        require(credentialType <= MAX_CREDENTIAL_TYPE, "CVIN1155: credential type out of range");
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
        // D8: burning the BIRTH_CERT deregisters the vehicle; it must not leave credentials
        // orphaned on an address that is no longer a vehicle.
        if (credentialType == BIRTH_CERT) {
            require(_heldTypes[vehicle] == 0, "CVIN1155: revoke the vehicle's other credentials first");
        }

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
     * @notice Move all units of ONE credential type from one vehicle address to
     *         another. Issuer only — holders cannot transfer their own credentials.
     *         A non-BIRTH type may only go to a registered vehicle (invariant i); the
     *         BIRTH_CERT may only move on its own when the vehicle holds nothing else
     *         (invariant ii) — use issuerTransferIdentity to move an identity together
     *         with its credentials.
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

        if (credentialType == BIRTH_CERT) {
            require(balanceOf(to, BIRTH_CERT) == 0, "CVIN1155: recipient already registered");
            require(_heldTypes[from] == 0, "CVIN1155: identity holds other credentials (use issuerTransferIdentity)");
            _safeTransferFrom(from, to, credentialType, amount, "");
            _rebindVIN(from, to);
        } else {
            require(balanceOf(to, BIRTH_CERT) > 0, "CVIN1155: recipient not registered");
            _safeTransferFrom(from, to, credentialType, amount, "");
        }
    }

    /**
     * @notice Move a whole vehicle identity — the BIRTH_CERT and every credential type
     *         the vehicle holds — to a new address in one transaction, re-binding the
     *         VIN indexes (defect D7). Issuer only. The recipient must not be a
     *         registered vehicle already.
     */
    function issuerTransferIdentity(address from, address to) external onlyRole(ISSUER_ROLE) {
        require(from != to, "CVIN1155: transfer to same holder");
        require(to != address(0), "CVIN1155: recipient is zero address");
        require(balanceOf(from, BIRTH_CERT) > 0, "CVIN1155: vehicle not registered");
        require(balanceOf(to, BIRTH_CERT) == 0, "CVIN1155: recipient already registered");

        uint256[] memory types = credentialTypesOf(from);
        uint256 n = types.length;
        uint256[] memory ids = new uint256[](n + 1);
        uint256[] memory amounts = new uint256[](n + 1);
        ids[0] = BIRTH_CERT;
        amounts[0] = balanceOf(from, BIRTH_CERT);
        for (uint256 i = 0; i < n; ++i) {
            ids[i + 1] = types[i];
            amounts[i + 1] = balanceOf(from, types[i]);
        }
        _safeBatchTransferFrom(from, to, ids, amounts, "");
        bytes32 vinHash = _rebindVIN(from, to);
        emit IdentityRebound(from, to, vinHash, n);
    }

    /// @dev Move the VIN indexes from the old BIRTH_CERT holder to the new one.
    function _rebindVIN(address from, address to) private returns (bytes32 vinHash) {
        string memory vin = vehicleVIN[from];
        vinHash = keccak256(bytes(vin));
        vehicleVIN[to] = vin;
        vinHashToVehicle[vinHash] = to;
        delete vehicleVIN[from];
    }

    // ============ Metadata (attribute update) ============

    function setTokenURI(uint256 credentialType, string calldata newURI)
        external
        onlyRole(ISSUER_ROLE)
    {
        _tokenURIs[credentialType] = newURI;
        emit URI(newURI, credentialType); // ERC-1155 standard event (D8: was never emitted)
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
     * @notice Every non-BIRTH credential type the vehicle currently holds (ascending).
     *         Enumerable because types are bounded to 1..255 (bitmap per vehicle).
     */
    function credentialTypesOf(address vehicle) public view returns (uint256[] memory types) {
        uint256 bits = _heldTypes[vehicle];
        uint256 count;
        for (uint256 b = bits; b != 0; b &= b - 1) ++count;
        types = new uint256[](count);
        uint256 k;
        for (uint256 t = 2; bits != 0 && t <= MAX_CREDENTIAL_TYPE; ++t) {
            if ((bits >> t) & 1 == 1) {
                types[k++] = t;
                bits &= ~(uint256(1) << t);
            }
        }
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
     * @dev The standard transfer entry points are closed for everyone (D7): before the
     *      fix an issuer that was also an approved operator could move the BIRTH_CERT
     *      through safeTransferFrom without the VIN re-binding. Mint and burn still go
     *      through _update; the only inter-address moves are the issuer paths above,
     *      which call the internal _safeTransferFrom / _safeBatchTransferFrom directly.
     */
    function safeTransferFrom(address, address, uint256, uint256, bytes memory) public pure override {
        revert("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
    }

    function safeBatchTransferFrom(address, address, uint256[] memory, uint256[] memory, bytes memory)
        public
        pure
        override
    {
        revert("CVIN1155: credentials are soulbound (issuer-mediated transfer only)");
    }

    /**
     * @dev Keeps the per-vehicle bitmap of held credential types in step with balances
     *      (D8 invariants). Only non-BIRTH types with a positive balance are tracked; ids
     *      above MAX_CREDENTIAL_TYPE cannot exist because issueCredential rejects them.
     */
    function _update(
        address from,
        address to,
        uint256[] memory ids,
        uint256[] memory values
    ) internal override {
        super._update(from, to, ids, values);
        for (uint256 i = 0; i < ids.length; ++i) {
            uint256 id = ids[i];
            if (id == BIRTH_CERT || values[i] == 0) continue;
            uint256 mask = uint256(1) << id;
            if (to != address(0) && (_heldTypes[to] & mask) == 0) {
                _heldTypes[to] |= mask;
            }
            if (from != address(0) && balanceOf(from, id) == 0) {
                _heldTypes[from] &= ~mask;
            }
        }
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
