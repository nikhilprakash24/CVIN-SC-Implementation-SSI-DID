// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title CVINVehicleNFT
 * @author CVIN research project
 * @dev ERC-721 based Vehicle Identity with DID integration
 * @notice Each NFT represents a unique vehicle identity
 *
 * Features:
 * - VIN-based vehicle identity
 * - Ownership tracking via NFT ownership
 * - Complete transfer history on-chain
 * - Vehicle metadata stored on IPFS
 * - DID resolution (did:nft:erc721:{contractAddress}:{tokenId})
 * - Role-based access (manufacturers, inspectors, service centers)
 * - Enumerable for efficient queries
 *
 * Design: built on OpenZeppelin Contracts 5.0.2 (ERC721, ERC721URIStorage,
 * ERC721Enumerable, AccessControl, Strings). Sequential tokenIds start at 1
 * (0 = "no token" sentinel in vinToTokenId). The constructor grants
 * DEFAULT_ADMIN_ROLE and MANUFACTURER_ROLE to the deployer. Revocation is a soft
 * `active=false` flag (deactivateVehicle); there is no burn path. Deviations from
 * plain ERC-721: none at the interface level; the CVIN extensions (VIN maps,
 * metadata struct, transfer history, service records, did:nft string) are additive.
 * `_setTokenURI` (OZ 5.0.2) emits the EIP-4906 MetadataUpdate event, but EIP-4906
 * is not declared by this contract.
 *
 * @custom:standard ERC-721 Non-Fungible Token (core, Metadata, Enumerable) https://eips.ethereum.org/EIPS/eip-721
 * @custom:standard ERC-165 Standard Interface Detection https://eips.ethereum.org/EIPS/eip-165
 * @custom:standard W3C DID Core (did:nft is not a registered DID method) https://www.w3.org/TR/did-core/
 * @custom:security Reentrancy window: mintVehicle calls _safeMint (onERC721Received on a contract recipient)
 *                  before the VIN maps and metadata are written. Caller must hold MANUFACTURER_ROLE.
 * @custom:security No burn: a deactivated vehicle can still be transferred and still receive service
 *                  records (neither path checks `active`).
 * @custom:security transferHistory and serviceRecords are unbounded arrays; the whole-array getters can
 *                  exceed view gas limits for long histories.
 * @custom:security INSPECTOR_ROLE is granted by grantInspectorRole but no function checks it. Service
 *                  records are unsigned free-form strings.
 * @custom:security The did:nft contract address is lower-case hex, not EIP-55 checksummed.
 * @custom:see docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md
 * @custom:see sandbox/options/erc-721/adapter.js (the sandbox adapter wraps only this ERC-721 contract)
 */
contract CVINVehicleNFT is ERC721, ERC721URIStorage, ERC721Enumerable, AccessControl {
    // ============ State Variables ============

    /// @dev Token ID counter (OpenZeppelin v5 pattern). Starts at 1; the next id to mint.
    uint256 private _nextTokenId = 1;

    /// @notice Role allowed to mint vehicle NFTs (mintVehicle).
    /// @dev Role definitions. Granted to the deployer by the constructor. CVIN extension.
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    /// @notice Inspector role.
    /// @dev CVIN extension. Grantable via grantInspectorRole but not checked by any function.
    bytes32 public constant INSPECTOR_ROLE = keccak256("INSPECTOR_ROLE");
    /// @notice Role allowed to append service records (addServiceRecord).
    /// @dev CVIN extension.
    bytes32 public constant SERVICE_CENTER_ROLE = keccak256("SERVICE_CENTER_ROLE");

    /// @notice Normalised VIN => token ID (0 if not minted).
    /// @dev Mapping from VIN to token ID. Keyed by the normalised (upper-case) VIN only; use
    ///      getTokenIdFromVIN for a case-insensitive lookup.
    mapping(string => uint256) public vinToTokenId;

    /// @notice Token ID => normalised VIN.
    /// @dev Mapping from token ID to VIN. Duplicates vehicleMetadata[tokenId].vin.
    mapping(uint256 => string) public tokenIdToVIN;

    /// @notice On-chain vehicle metadata stored per token.
    /// @dev Vehicle metadata. Fields: vin (normalised), make, model, year, color, manufacturer
    ///      (minting account), mintTimestamp, active (soft-revocation flag). CVIN extension.
    struct VehicleMetadata {
        string vin;
        string make;
        string model;
        uint16 year;
        string color;
        address manufacturer;
        uint256 mintTimestamp;
        bool active;
    }

    /// @notice Token ID => VehicleMetadata.
    mapping(uint256 => VehicleMetadata) public vehicleMetadata;

    /// @notice One ownership change (the mint is recorded with from = address(0)).
    /// @dev Transfer history entry: from, to, timestamp, blockNumber. CVIN extension.
    struct TransferRecord {
        address from;
        address to;
        uint256 timestamp;
        uint256 blockNumber;
    }

    /// @notice Token ID => ordered list of TransferRecord (mint first).
    /// @dev Unbounded array; appended by mintVehicle and _update.
    mapping(uint256 => TransferRecord[]) public transferHistory;

    /// @notice Token ID => append-only list of service record URIs.
    /// @dev Service records (references to off-chain data). Unbounded, unsigned strings.
    mapping(uint256 => string[]) public serviceRecords;

    // ============ Events ============

    /// @notice Emitted when a vehicle NFT is minted.
    /// @dev CVIN extension, emitted after the ERC-721 Transfer event.
    /// @param tokenId The new token ID
    /// @param vin The normalised VIN
    /// @param owner Initial holder
    /// @param manufacturer Account holding MANUFACTURER_ROLE that minted
    event VehicleMinted(
        uint256 indexed tokenId,
        string vin,
        address indexed owner,
        address indexed manufacturer
    );

    /// @notice Emitted on every holder-to-holder transfer (not on mint or burn).
    /// @dev CVIN extension, emitted from _update alongside the ERC-721 Transfer event.
    /// @param tokenId Token being transferred
    /// @param from Previous holder
    /// @param to New holder
    /// @param timestamp Block timestamp of the transfer
    event VehicleTransferred(
        uint256 indexed tokenId,
        address indexed from,
        address indexed to,
        uint256 timestamp
    );

    /// @notice Emitted when a service record URI is appended.
    /// @dev CVIN extension.
    /// @param tokenId Vehicle token ID
    /// @param recordURI The appended URI
    /// @param addedBy Account holding SERVICE_CENTER_ROLE
    event ServiceRecordAdded(
        uint256 indexed tokenId,
        string recordURI,
        address indexed addedBy
    );

    /// @notice Emitted when a vehicle is soft-revoked.
    /// @dev CVIN extension.
    /// @param tokenId Vehicle token ID
    /// @param by Admin account that deactivated it
    event VehicleDeactivated(uint256 indexed tokenId, address indexed by);

    // ============ Constructor ============

    /// @notice Deploys the collection "CVIN Vehicle Identity" (CVIN-VID).
    /// @dev Grants DEFAULT_ADMIN_ROLE and MANUFACTURER_ROLE to msg.sender (emits RoleGranted twice).
    constructor() ERC721("CVIN Vehicle Identity", "CVIN-VID") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MANUFACTURER_ROLE, msg.sender);
    }

    // ============ Minting Functions ============

    /**
     * @notice Mint a new vehicle NFT (manufacturer only)
     * @param to Initial owner address
     * @param vin Vehicle Identification Number
     * @param make Vehicle make
     * @param model Vehicle model
     * @param year Manufacturing year
     * @param color Vehicle color
     * @param metadataURI IPFS URI for comprehensive metadata
     * @return tokenId The minted token ID
     * @dev Access: MANUFACTURER_ROLE. Normalises the VIN (ISO 3779, D13), requires it to be unique
     *      and `to != address(0)`, `_safeMint`s, sets the token URI, writes the VIN maps and metadata
     *      and pushes a mint TransferRecord. Emits Transfer, MetadataUpdate (OZ URIStorage) and
     *      VehicleMinted. CVIN extension wrapping the ERC-721 mint.
     * @custom:security _safeMint invokes onERC721Received before the VIN maps/metadata are written.
     */
    function mintVehicle(
        address to,
        string memory vin,
        string memory make,
        string memory model,
        uint16 year,
        string memory color,
        string memory metadataURI
    ) external onlyRole(MANUFACTURER_ROLE) returns (uint256) {
        // D13: normalise (upper-case) and validate the ISO 3779 shape before the
        // uniqueness check, so "1hgbh41jxmn109186" and "1HGBH41JXMN109186" are one vehicle.
        vin = _normalizeVIN(vin);
        require(vinToTokenId[vin] == 0, "CVINVehicleNFT: VIN already minted");
        require(to != address(0), "CVINVehicleNFT: mint to zero address");

        uint256 tokenId = _nextTokenId++;


        // Mint NFT
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);

        // Store mappings
        vinToTokenId[vin] = tokenId;
        tokenIdToVIN[tokenId] = vin;

        // Store metadata
        vehicleMetadata[tokenId] = VehicleMetadata({
            vin: vin,
            make: make,
            model: model,
            year: year,
            color: color,
            manufacturer: msg.sender,
            mintTimestamp: block.timestamp,
            active: true
        });

        // Record initial "transfer" (mint)
        transferHistory[tokenId].push(TransferRecord({
            from: address(0),
            to: to,
            timestamp: block.timestamp,
            blockNumber: block.number
        }));

        emit VehicleMinted(tokenId, vin, to, msg.sender);

        return tokenId;
    }

    // ============ Transfer Override ============

    /**
     * @dev Override _update to track transfer history
     *      ERC-721 (OZ v5) transfer hook. For a transfer that is neither a mint nor a burn,
     *      appends a TransferRecord and emits VehicleTransferred, then defers to OZ for the
     *      authorisation check (`auth`) and the Enumerable bookkeeping.
     * @param to New holder (address(0) for a burn, which never happens here)
     * @param tokenId Token being moved
     * @param auth Account whose approval is checked by OZ (address(0) to skip)
     * @return The previous owner, as returned by ERC721._update
     */
    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable)
        returns (address)
    {
        address from = _ownerOf(tokenId);

        // Record transfer if not minting
        if (from != address(0) && to != address(0)) {
            transferHistory[tokenId].push(TransferRecord({
                from: from,
                to: to,
                timestamp: block.timestamp,
                blockNumber: block.number
            }));

            emit VehicleTransferred(tokenId, from, to, block.timestamp);
        }

        return super._update(to, tokenId, auth);
    }

    // ============ Service Records ============

    /**
     * @notice Add service record reference
     * @param tokenId Vehicle token ID
     * @param recordURI IPFS URI of service record
     * @dev Access: SERVICE_CENTER_ROLE. The token must exist; `active` is not checked.
     *      Emits ServiceRecordAdded. CVIN extension.
     */
    function addServiceRecord(uint256 tokenId, string memory recordURI)
        external
        onlyRole(SERVICE_CENTER_ROLE)
    {
        require(_ownerOf(tokenId) != address(0), "CVINVehicleNFT: token does not exist");
        serviceRecords[tokenId].push(recordURI);
        emit ServiceRecordAdded(tokenId, recordURI, msg.sender);
    }

    /**
     * @notice Get all service records for a vehicle
     * @param tokenId Vehicle token ID
     * @return Array of service record URIs
     * @dev Returns the whole unbounded array. CVIN extension.
     */
    function getServiceRecords(uint256 tokenId)
        external
        view
        returns (string[] memory)
    {
        return serviceRecords[tokenId];
    }

    // ============ Transfer History ============

    /**
     * @notice Get complete transfer history for a vehicle
     * @param tokenId Vehicle token ID
     * @return Array of transfer records
     * @dev Mint record first. Returns the whole unbounded array. CVIN extension.
     */
    function getTransferHistory(uint256 tokenId)
        external
        view
        returns (TransferRecord[] memory)
    {
        return transferHistory[tokenId];
    }

    /**
     * @notice Get ownership chain (all previous owners)
     * @param tokenId Vehicle token ID
     * @return Array of owner addresses
     * @dev The `to` of every TransferRecord, in order (initial holder first). CVIN extension.
     */
    function getOwnershipChain(uint256 tokenId)
        external
        view
        returns (address[] memory)
    {
        TransferRecord[] memory history = transferHistory[tokenId];
        address[] memory owners = new address[](history.length);

        for (uint i = 0; i < history.length; i++) {
            owners[i] = history[i].to;
        }

        return owners;
    }

    // ============ Vehicle Management ============

    /**
     * @notice Deactivate vehicle (end-of-life, total loss, etc.)
     * @param tokenId Vehicle token ID
     * @dev Access: DEFAULT_ADMIN_ROLE. Soft revoke: sets `active=false`; the token is NOT burned and
     *      can still be transferred. Emits VehicleDeactivated. CVIN extension.
     */
    function deactivateVehicle(uint256 tokenId)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(_ownerOf(tokenId) != address(0), "CVINVehicleNFT: token does not exist");
        vehicleMetadata[tokenId].active = false;
        emit VehicleDeactivated(tokenId, msg.sender);
    }

    /**
     * @notice Check if vehicle is active
     * @param tokenId Vehicle token ID
     * @return True if vehicle is active
     * @dev Returns false for a nonexistent token. CVIN extension.
     */
    function isVehicleActive(uint256 tokenId) external view returns (bool) {
        return vehicleMetadata[tokenId].active;
    }

    // ============ DID Resolution ============

    /**
     * @notice Get DID for a vehicle
     * @param tokenId Vehicle token ID
     * @return DID string (did:nft:erc721:{contractAddress}:{tokenId})
     * @dev Reverts if the token does not exist. The address is lower-case hex (not EIP-55).
     *      Only the string is produced; there is no on-chain DID document or resolver.
     *      CVIN extension (did:nft).
     */
    function getVehicleDID(uint256 tokenId) external view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "CVINVehicleNFT: token does not exist");

        return string(abi.encodePacked(
            "did:nft:erc721:",
            toHexString(address(this)),
            ":",
            Strings.toString(tokenId)
        ));
    }

    /**
     * @notice Get token ID from VIN
     * @param vin Vehicle Identification Number
     * @return Token ID
     * @dev Case-insensitive (same normalisation as mintVehicle); reverts on an invalid VIN shape
     *      or if the VIN is not minted. CVIN extension.
     */
    function getTokenIdFromVIN(string memory vin) external view returns (uint256) {
        // Same normalisation as mintVehicle: a lower-cased VIN finds the upper-cased identity.
        // (The raw public mapping vinToTokenId is keyed by the normalised VIN only.)
        uint256 tokenId = vinToTokenId[_normalizeVIN(vin)];
        require(tokenId != 0, "CVINVehicleNFT: VIN not found");
        return tokenId;
    }

    /**
     * @notice Get VIN from token ID
     * @param tokenId Token ID
     * @return VIN string
     * @dev Reverts if the token does not exist. CVIN extension.
     */
    function getVINFromTokenId(uint256 tokenId) external view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "CVINVehicleNFT: token does not exist");
        return tokenIdToVIN[tokenId];
    }

    // ============ Query Functions ============

    /**
     * @notice Get all vehicles owned by an address
     * @param owner Owner address
     * @return Array of token IDs
     * @dev Loops ERC721Enumerable.tokenOfOwnerByIndex. CVIN extension.
     */
    function getVehiclesByOwner(address owner) external view returns (uint256[] memory) {
        uint256 balance = balanceOf(owner);
        uint256[] memory tokens = new uint256[](balance);

        for (uint256 i = 0; i < balance; i++) {
            tokens[i] = tokenOfOwnerByIndex(owner, i);
        }

        return tokens;
    }

    /**
     * @notice Get total number of vehicles minted
     * @return Total supply
     * @dev `_nextTokenId - 1`, i.e. the number of tokens ever minted (equals totalSupply() because
     *      there is no burn). CVIN extension.
     */
    function getTotalVehicles() external view returns (uint256) {
        return _nextTokenId - 1;
    }

    // ============ Role Management ============

    /// @notice Grant MANUFACTURER_ROLE to `account`.
    /// @dev Access: DEFAULT_ADMIN_ROLE (also enforced by grantRole). Emits RoleGranted. CVIN extension.
    /// @param account Account to grant the role to
    function grantManufacturerRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        grantRole(MANUFACTURER_ROLE, account);
    }

    /// @notice Grant INSPECTOR_ROLE to `account`.
    /// @dev Access: DEFAULT_ADMIN_ROLE. Emits RoleGranted. The role is not checked anywhere. CVIN extension.
    /// @param account Account to grant the role to
    function grantInspectorRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        grantRole(INSPECTOR_ROLE, account);
    }

    /// @notice Grant SERVICE_CENTER_ROLE to `account`.
    /// @dev Access: DEFAULT_ADMIN_ROLE. Emits RoleGranted. CVIN extension.
    /// @param account Account to grant the role to
    function grantServiceCenterRole(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        grantRole(SERVICE_CENTER_ROLE, account);
    }

    // ============ Helper Functions ============

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
     *      The same helper (identical logic) lives in CVINVehicleCredential1155 and
     *      CVINVehicleLSP8; Solidity has no shared stdlib here.
     * @param vin Raw VIN as supplied by the caller (memory; mutated in place)
     * @return The normalised, validated VIN
     */
    function _normalizeVIN(string memory vin) internal pure returns (string memory) {
        bytes memory b = bytes(vin);
        require(b.length == 17, "CVINVehicleNFT: invalid VIN length");
        bytes32 word = bytes32(b); // one memory read for all 17 characters (bytes 17..31 are zero padding)
        for (uint256 i = 0; i < 17; ++i) {
            uint256 c = uint8(word[i]);
            if (((_VIN_LOWER_AZ >> c) & 1) == 1) {
                c -= 0x20; // 'a'..'z' -> 'A'..'Z'
                b[i] = bytes1(uint8(c)); // written back only when the character actually changes
            }
            require(((_VIN_ALLOWED >> c) & 1) == 1, "CVINVehicleNFT: invalid VIN character");
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

    /// @dev Lower-case "0x"-prefixed hex encoding of an address (not EIP-55 checksummed). CVIN helper.
    /// @param addr Address to encode
    /// @return The 42-character hex string
    function toHexString(address addr) internal pure returns (string memory) {
        bytes memory buffer = new bytes(40);
        for (uint256 i = 0; i < 20; i++) {
            bytes1 b = bytes1(uint8(uint256(uint160(addr)) / (2**(8*(19 - i)))));
            bytes1 hi = bytes1(uint8(b) / 16);
            bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
            buffer[2*i] = char(hi);
            buffer[2*i+1] = char(lo);
        }
        return string(abi.encodePacked("0x", string(buffer)));
    }

    /// @dev Maps a nibble (0-15) to its lower-case ASCII hex digit. CVIN helper.
    /// @param b Nibble value
    /// @return c ASCII character
    function char(bytes1 b) internal pure returns (bytes1 c) {
        if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
        else return bytes1(uint8(b) + 0x57);
    }

    // ============ Required Overrides ============

    /// @notice Metadata URI of `tokenId`.
    /// @dev ERC-721 Metadata. Resolves the ERC721/ERC721URIStorage override; no base URI, so the stored
    /// URI is returned unchanged. Reverts for a nonexistent token.
    /// @param tokenId Token ID
    /// @return The stored token URI
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    /// @notice ERC-165 interface detection.
    /// @dev Merges ERC721, ERC721Enumerable, ERC721URIStorage (EIP-4906 id) and AccessControl.
    /// @param interfaceId Interface identifier
    /// @return True if supported
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    /// @dev Required OZ v5 override for ERC721Enumerable; pure pass-through.
    /// @param account Account whose balance changes
    /// @param value Amount to add
    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }
}
