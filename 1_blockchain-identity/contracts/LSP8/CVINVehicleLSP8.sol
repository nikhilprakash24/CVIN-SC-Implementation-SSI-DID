// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title CVINVehicleLSP8
 * @author CVIN research project
 * @notice LSP8-style vehicle identity: one bytes32 token per vehicle (keccak256 of the normalised VIN)
 *         with a per-token key/value store; the contract owner is the issuing authority.
 * @dev Minimal, self-contained LSP8-flavored (LUKSO LSP8 Identifiable Digital
 *      Asset) vehicle identity contract for the CVIN thesis gas comparison.
 *      Does NOT import the LUKSO lsp-smart-contracts npm package.
 *
 * Model: each vehicle is a non-fungible token identified by
 *   bytes32 tokenId = keccak256(bytes(VIN))
 * with an LSP8-style per-token key-value metadata store
 * (setDataForTokenId / getDataForTokenId, DataChanged event).
 *
 * ============================================================================
 * REPRESENTATIVE IMPLEMENTATION — LSP8 feature coverage
 * ============================================================================
 * Implemented (LSP8-conformant signatures/semantics):
 * - bytes32 tokenIds (LSP8_TOKENID_FORMAT: hash of the VIN)
 * - totalSupply(), balanceOf(address), tokenOwnerOf(bytes32), tokenIdsOf(address)
 * - transfer(address from, address to, bytes32 tokenId, bool force, bytes data)
 *   with the LSP8 Transfer event shape
 *   (operator, from, to, tokenId, force, data)
 * - mint via mintVehicle() and burn/revoke via revokeVehicle() emitting
 *   Transfer from/to the zero address
 * - setDataForTokenId(bytes32,bytes32,bytes) / getDataForTokenId(bytes32,bytes32)
 *   and batch variants, emitting TokenIdDataChanged(tokenId, dataKey, dataValue)
 *   (LSP8's event name; a generic DataChanged is emitted as well for tooling)
 *
 * OMITTED relative to the full LSP8 standard (intentional — this contract is a
 * representative implementation for gas benchmarking, not a spec-complete one):
 * - LSP1 UniversalReceiver hooks: no _notifyTokenSender/_notifyTokenReceiver
 *   calls; the `force` flag is accepted but only checked against code-less
 *   recipients (no LSP1 interface probing).
 * - Operator management: authorizeOperator / revokeOperator / isOperatorFor /
 *   getOperatorsOf are not implemented; only the token owner (or the contract
 *   owner for revocation) can move a token.
 * - ERC725Y contract-level data store (setData/getData on the collection) and
 *   LSP4 DigitalAssetMetadata keys.
 * - ERC-165 interfaceId registration for LSP8 (0x3a271706).
 *
 * Access model: contract `owner` = issuing authority (mints, revokes, writes
 * token metadata); token owner = current vehicle owner (transfers the vehicle).
 * ============================================================================
 *
 * Extensions beyond LSP8: generic DataChanged event without tokenId, mintVehicle/revokeVehicle,
 * token-owner burn, hand-written owner/transferOwnership (no renounce), generation-scoped data
 * (REVIEW_02 K-8). Data keys are plain keccak256("CVIN_...") strings, not LSP2-encoded keys.
 * No dependencies are imported (not built on npm lukso/lsp-smart-contracts ^0.14.0 or OpenZeppelin).
 *
 * @custom:note The model line above says tokenId = keccak256(bytes(VIN)); since D13 it is the
 *              keccak256 of the NORMALISED (upper-cased) VIN, see tokenIdForVIN.
 * @custom:standard LUKSO LSP8 Identifiable Digital Asset (representative subset) https://docs.lukso.tech/standards/tokens/LSP8-Identifiable-Digital-Asset
 * @custom:standard ERC725Y-style key/value data (style only) https://docs.lukso.tech/standards/erc725
 * @custom:security force=false only checks that the recipient has code (no LSP1 probing); mint and
 *                  burn always use force=true.
 * @custom:security No operators: marketplaces or agents cannot move a token on the owner's behalf.
 * @custom:security DataChanged carries no tokenId and is ambiguous across tokens.
 * @custom:security After revoke the old data stays in storage and past events; only the getter hides it.
 * @custom:security tokenId is derived from the VIN alone, so anyone who knows a VIN can compute it.
 * @custom:security The token owner can burn their own identity.
 * @custom:see docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md
 * @custom:see sandbox/options/lsp8/adapter.js
 */
contract CVINVehicleLSP8 {
    // ============ Well-known metadata data keys (convenience constants) ============
    // keccak256("CVIN_VIN")
    /// @notice Data key keccak256("CVIN_VIN"): normalised VIN, written by mintVehicle.
    bytes32 public constant DATA_KEY_VIN = keccak256("CVIN_VIN");
    // keccak256("CVIN_REGISTRATION")
    /// @notice Data key keccak256("CVIN_REGISTRATION") (convenience constant).
    bytes32 public constant DATA_KEY_REGISTRATION = keccak256("CVIN_REGISTRATION");
    // keccak256("CVIN_INSPECTION")
    /// @notice Data key keccak256("CVIN_INSPECTION") (convenience constant).
    bytes32 public constant DATA_KEY_INSPECTION = keccak256("CVIN_INSPECTION");
    // keccak256("CVIN_INSURANCE")
    /// @notice Data key keccak256("CVIN_INSURANCE") (convenience constant).
    bytes32 public constant DATA_KEY_INSURANCE = keccak256("CVIN_INSURANCE");

    // ============ State ============

    /// @notice Contract owner = issuing authority
    /// @dev Hand-written Ownable-like owner (no renounce). CVIN extension.
    address public owner;

    /// @notice Collection name.
    string public name;
    /// @notice Collection symbol.
    string public symbol;

    /// @dev Number of live tokens (totalSupply).
    uint256 private _existingTokens;

    /// @dev Token owner plus the token's data generation, packed in one slot.
    ///      generation is bumped on every revoke (REVIEW_02 K-8): tokenId =
    ///      keccak256(VIN) is reused when a VIN is re-minted, and the data store
    ///      is keyed by generation, so a re-mint starts with an empty store
    ///      instead of inheriting the burned token's inspection data.
    struct TokenRecord {
        address owner;
        uint96 generation;
    }

    /// @dev tokenId => (token owner, data generation)
    mapping(bytes32 => TokenRecord) private _tokens;

    /// @dev owner => list of owned tokenIds
    mapping(address => bytes32[]) private _ownedTokens;

    /// @dev tokenId => index in _ownedTokens[owner]
    mapping(bytes32 => uint256) private _ownedTokensIndex;

    /// @dev LSP8-style per-token key-value store:
    ///      tokenId => generation => dataKey => value (generation: see TokenRecord)
    mapping(bytes32 => mapping(uint96 => mapping(bytes32 => bytes))) private _tokenIdData;

    // ============ Events ============

    /// @notice Emitted on mint (from = 0), transfer and revoke (to = 0).
    /// @dev LSP8 Transfer event shape
    /// @param operator msg.sender of the call
    /// @param from Previous owner
    /// @param to New owner
    /// @param tokenId bytes32 token ID
    /// @param force LSP8 force flag (true for mint and burn)
    /// @param data Caller-supplied data
    event Transfer(
        address operator,
        address indexed from,
        address indexed to,
        bytes32 indexed tokenId,
        bool force,
        bytes data
    );

    /// @notice Emitted when a per-token data value is written.
    /// @dev LSP8 event name for per-token data updates
    /// @param tokenId Token ID
    /// @param dataKey Data key
    /// @param dataValue New value
    event TokenIdDataChanged(
        bytes32 indexed tokenId,
        bytes32 indexed dataKey,
        bytes dataValue
    );

    /// @notice Generic data-change event without tokenId.
    /// @dev Generic ERC725Y-style event (emitted alongside TokenIdDataChanged). CVIN extension.
    /// @param dataKey Data key
    /// @param dataValue New value
    event DataChanged(bytes32 indexed dataKey, bytes dataValue);

    /// @notice Emitted when the issuing authority changes.
    /// @param previousOwner Previous contract owner
    /// @param newOwner New contract owner
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /// @notice Emitted when a vehicle token is minted.
    /// @dev CVIN extension.
    /// @param tokenId keccak256 of the normalised VIN
    /// @param vin Normalised VIN
    /// @param vehicleOwner Initial token owner
    event VehicleMinted(bytes32 indexed tokenId, string vin, address indexed vehicleOwner);
    /// @notice Emitted when a vehicle token is burned.
    /// @dev CVIN extension.
    /// @param tokenId Token ID
    /// @param previousOwner Token owner at revocation
    event VehicleRevoked(bytes32 indexed tokenId, address indexed previousOwner);

    // ============ Modifiers ============

    /// @dev Restricts to the contract owner (issuing authority).
    modifier onlyOwner() {
        require(msg.sender == owner, "LSP8: caller is not the contract owner");
        _;
    }

    // ============ Constructor ============

    /// @notice Deploys the collection; the deployer becomes the issuing authority.
    /// @dev Emits OwnershipTransferred(address(0), msg.sender).
    /// @param _name Collection name
    /// @param _symbol Collection symbol
    constructor(string memory _name, string memory _symbol) {
        name = _name;
        symbol = _symbol;
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }

    // ============ Views ============

    /// @notice LSP8: number of existing tokens.
    /// @return Live token count
    function totalSupply() external view returns (uint256) {
        return _existingTokens;
    }

    /// @notice LSP8: number of tokens owned by `tokenOwner`.
    /// @param tokenOwner Account to query
    /// @return Token count
    function balanceOf(address tokenOwner) external view returns (uint256) {
        return _ownedTokens[tokenOwner].length;
    }

    /// @notice LSP8: owner of `tokenId`.
    /// @dev Reverts if the token does not exist.
    /// @param tokenId Token ID
    /// @return Token owner
    function tokenOwnerOf(bytes32 tokenId) public view returns (address) {
        address tokenOwner = _tokens[tokenId].owner;
        require(tokenOwner != address(0), "LSP8: tokenId does not exist");
        return tokenOwner;
    }

    /// @notice LSP8: tokenIds owned by `tokenOwner` (order changes on removal, swap-and-pop).
    /// @param tokenOwner Account to query
    /// @return Owned tokenIds
    function tokenIdsOf(address tokenOwner) external view returns (bytes32[] memory) {
        return _ownedTokens[tokenOwner];
    }

    /// @notice Compute the tokenId for a VIN: keccak256 of the NORMALISED VIN string
    ///         (upper-cased, ISO 3779 shape checked — see _normalizeVIN), so a
    ///         lower-cased VIN resolves to the same tokenId as its upper-cased form.
    /// @dev Reverts on an invalid VIN shape. CVIN extension.
    /// @param vin VIN (any case)
    /// @return The bytes32 tokenId
    function tokenIdForVIN(string calldata vin) public pure returns (bytes32) {
        return keccak256(bytes(_normalizeVIN(vin)));
    }

    /// @notice Whether `tokenId` currently exists.
    /// @dev CVIN extension.
    /// @param tokenId Token ID
    /// @return True if minted and not revoked
    function exists(bytes32 tokenId) public view returns (bool) {
        return _tokens[tokenId].owner != address(0);
    }

    // ============ Identity creation (mint) ============

    /**
     * @notice Mint a vehicle identity token to `vehicleOwner`.
     *         tokenId = keccak256(bytes(vin)). The VIN is stored in the
     *         token's data store under DATA_KEY_VIN.
     * @dev Access: onlyOwner. The VIN is normalised (D13), so tokenId = keccak256 of the NORMALISED VIN
     *      (the line above predates D13). Writes DATA_KEY_VIN to the current generation. Emits
     *      TokenIdDataChanged, DataChanged, Transfer (force=true) and VehicleMinted. CVIN over LSP8 _mint.
     * @custom:note "tokenId = keccak256(bytes(vin))" above is stale wording: the hash is over the normalised VIN.
     * @param vehicleOwner Initial token owner (non-zero)
     * @param vin VIN (any case; ISO 3779 shape checked)
     * @return tokenId The minted token ID
     */
    function mintVehicle(address vehicleOwner, string calldata vin)
        external
        onlyOwner
        returns (bytes32 tokenId)
    {
        require(vehicleOwner != address(0), "LSP8: mint to zero address");
        require(bytes(vin).length > 0, "LSP8: empty VIN");
        // D13: normalise (upper-case) and validate the ISO 3779 shape before hashing, so
        // "1hgbh41jxmn109186" and "1HGBH41JXMN109186" derive the same tokenId.
        string memory normalizedVIN = _normalizeVIN(vin);
        tokenId = keccak256(bytes(normalizedVIN));
        TokenRecord storage record = _tokens[tokenId];
        require(record.owner == address(0), "LSP8: tokenId already minted");

        _addTokenTo(vehicleOwner, tokenId);
        _existingTokens += 1;

        _tokenIdData[tokenId][record.generation][DATA_KEY_VIN] = bytes(normalizedVIN);
        emit TokenIdDataChanged(tokenId, DATA_KEY_VIN, bytes(normalizedVIN));
        emit DataChanged(DATA_KEY_VIN, bytes(normalizedVIN));

        emit Transfer(msg.sender, address(0), vehicleOwner, tokenId, true, "");
        emit VehicleMinted(tokenId, normalizedVIN, vehicleOwner);
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
     *      CVINVehicleCredential1155; Solidity has no shared stdlib here.
     * @param vin Raw VIN as supplied by the caller (memory; mutated in place)
     * @return The normalised, validated VIN
     */
    function _normalizeVIN(string memory vin) internal pure returns (string memory) {
        bytes memory b = bytes(vin);
        require(b.length == 17, "LSP8: invalid VIN length");
        bytes32 word = bytes32(b); // one memory read for all 17 characters (bytes 17..31 are zero padding)
        for (uint256 i = 0; i < 17; ++i) {
            uint256 c = uint8(word[i]);
            if (((_VIN_LOWER_AZ >> c) & 1) == 1) {
                c -= 0x20; // 'a'..'z' -> 'A'..'Z'
                b[i] = bytes1(uint8(c)); // written back only when the character actually changes
            }
            require(((_VIN_ALLOWED >> c) & 1) == 1, "LSP8: invalid VIN character");
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

    // ============ Transfer (LSP8 signature) ============

    /**
     * @notice Transfer a vehicle identity token. LSP8 function signature.
     * @dev Operators are not implemented: msg.sender must be the current token
     *      owner. `force` is only checked against code-less recipients (no
     *      LSP1 probing — see header).
     *      Requires `from` == token owner == msg.sender, `to` non-zero and `to != from`; with
     *      force=false `to` must have code. Emits Transfer. LSP8 (subset).
     * @param from Current token owner
     * @param to Recipient
     * @param tokenId Token ID
     * @param force If false, an EOA recipient is rejected
     * @param data Data echoed in the Transfer event
     */
    function transfer(
        address from,
        address to,
        bytes32 tokenId,
        bool force,
        bytes calldata data
    ) external {
        address tokenOwner = tokenOwnerOf(tokenId);
        require(tokenOwner == from, "LSP8: transfer from incorrect owner");
        require(msg.sender == tokenOwner, "LSP8: caller is not the token owner");
        require(to != address(0), "LSP8: transfer to zero address");
        require(to != from, "LSP8: cannot transfer to self");
        if (!force) {
            require(to.code.length > 0, "LSP8: recipient is an EOA (use force=true)");
        }

        _removeTokenFrom(from, tokenId);
        _addTokenTo(to, tokenId);

        emit Transfer(msg.sender, from, to, tokenId, force, data);
    }

    // ============ Revocation (burn) ============

    /**
     * @notice Revoke (burn) a vehicle identity token. Callable by the issuing
     *         authority (contract owner) or the current token owner.
     *         The token's data store is retired by bumping its generation
     *         (REVIEW_02 K-8): getDataForTokenId returns empty for the burned
     *         token and for any later re-mint of the same VIN. The old values
     *         stay in storage (unreachable) and in past events.
     * @dev Access: contract owner or token owner. Emits Transfer (to address(0), force=true) and
     *      VehicleRevoked. CVIN extension (~ LSP8 _burn).
     * @param tokenId Token ID
     * @param data Data echoed in the Transfer event
     */
    function revokeVehicle(bytes32 tokenId, bytes calldata data) external {
        address tokenOwner = tokenOwnerOf(tokenId);
        require(
            msg.sender == owner || msg.sender == tokenOwner,
            "LSP8: caller is not authority nor token owner"
        );

        _removeTokenFrom(tokenOwner, tokenId);
        _tokens[tokenId].generation += 1;
        _existingTokens -= 1;

        emit Transfer(msg.sender, tokenOwner, address(0), tokenId, true, data);
        emit VehicleRevoked(tokenId, tokenOwner);
    }

    // ============ LSP8 per-token data store ============

    /**
     * @notice Set a data key-value pair for a specific tokenId (LSP8 signature).
     *         Only the issuing authority may write vehicle metadata.
     * @dev Access: onlyOwner. The token must exist; writes to its current generation.
     *      Emits TokenIdDataChanged and DataChanged. LSP8.
     * @param tokenId Token ID
     * @param dataKey Data key
     * @param dataValue Value to store (empty bytes clears the slot)
     */
    function setDataForTokenId(
        bytes32 tokenId,
        bytes32 dataKey,
        bytes calldata dataValue
    ) external onlyOwner {
        TokenRecord storage record = _tokens[tokenId];
        require(record.owner != address(0), "LSP8: tokenId does not exist");
        _tokenIdData[tokenId][record.generation][dataKey] = dataValue;
        emit TokenIdDataChanged(tokenId, dataKey, dataValue);
        emit DataChanged(dataKey, dataValue);
    }

    /// @notice LSP8: read a per-token data value.
    /// @dev Reads the current generation; empty for nonexistent or revoked tokens.
    /// @param tokenId Token ID
    /// @param dataKey Data key
    /// @return The stored value
    function getDataForTokenId(bytes32 tokenId, bytes32 dataKey)
        external
        view
        returns (bytes memory)
    {
        return _tokenIdData[tokenId][_tokens[tokenId].generation][dataKey];
    }

    /// @notice Batch variant (LSP8 signature)
    /// @dev Access: onlyOwner. Arrays must have equal length; every token must exist.
    ///      Emits TokenIdDataChanged and DataChanged per item.
    /// @param tokenIds Token IDs
    /// @param dataKeys Data keys
    /// @param dataValues Values
    function setDataBatchForTokenIds(
        bytes32[] calldata tokenIds,
        bytes32[] calldata dataKeys,
        bytes[] calldata dataValues
    ) external onlyOwner {
        require(
            tokenIds.length == dataKeys.length && dataKeys.length == dataValues.length,
            "LSP8: array length mismatch"
        );
        for (uint256 i = 0; i < tokenIds.length; i++) {
            TokenRecord storage record = _tokens[tokenIds[i]];
            require(record.owner != address(0), "LSP8: tokenId does not exist");
            _tokenIdData[tokenIds[i]][record.generation][dataKeys[i]] = dataValues[i];
            emit TokenIdDataChanged(tokenIds[i], dataKeys[i], dataValues[i]);
            emit DataChanged(dataKeys[i], dataValues[i]);
        }
    }

    /// @notice Batch read variant (LSP8 signature)
    /// @param tokenIds Token IDs
    /// @param dataKeys Data keys (same length)
    /// @return dataValues Stored values (current generation)
    function getDataBatchForTokenIds(
        bytes32[] calldata tokenIds,
        bytes32[] calldata dataKeys
    ) external view returns (bytes[] memory dataValues) {
        require(tokenIds.length == dataKeys.length, "LSP8: array length mismatch");
        dataValues = new bytes[](tokenIds.length);
        for (uint256 i = 0; i < tokenIds.length; i++) {
            dataValues[i] = _tokenIdData[tokenIds[i]][_tokens[tokenIds[i]].generation][dataKeys[i]];
        }
    }

    // ============ Contract ownership (issuing authority) ============

    /// @notice Transfer the issuing authority to `newOwner`.
    /// @dev Access: onlyOwner. Rejects address(0); there is no renounce. Emits OwnershipTransferred.
    /// @param newOwner New contract owner
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "LSP8: new owner is zero address");
        address previousOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(previousOwner, newOwner);
    }

    // ============ Internal enumeration helpers ============

    /// @dev Sets the token owner and appends to the enumeration list.
    /// @param to New owner
    /// @param tokenId Token ID
    function _addTokenTo(address to, bytes32 tokenId) private {
        _tokens[tokenId].owner = to;
        _ownedTokensIndex[tokenId] = _ownedTokens[to].length;
        _ownedTokens[to].push(tokenId);
    }

    /// @dev Swap-and-pop removal from the enumeration list; clears the token owner.
    /// @param from Current owner
    /// @param tokenId Token ID
    function _removeTokenFrom(address from, bytes32 tokenId) private {
        // swap and pop
        bytes32[] storage tokens = _ownedTokens[from];
        uint256 index = _ownedTokensIndex[tokenId];
        uint256 lastIndex = tokens.length - 1;
        if (index != lastIndex) {
            bytes32 lastTokenId = tokens[lastIndex];
            tokens[index] = lastTokenId;
            _ownedTokensIndex[lastTokenId] = index;
        }
        tokens.pop();
        delete _ownedTokensIndex[tokenId];
        _tokens[tokenId].owner = address(0);
    }
}
