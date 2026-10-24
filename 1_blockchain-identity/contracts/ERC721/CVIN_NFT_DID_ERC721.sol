// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

/**
 * @title CVIN_NFT_DID_ERC721
 * @author CVIN research project
 * @notice OpenZeppelin-based ERC-721 vehicle NFT with ERC-2981 royalties and a toll scenario
 *         (the toll operator records zone entries; the token holder pays the toll).
 * @dev Inherits OpenZeppelin Contracts 5.0.2 ERC721, ERC721URIStorage, Ownable and ERC2981.
 *      The owner mints with a caller-chosen tokenId via `_mint` (not `_safeMint`). The constructor
 *      sets a default royalty. `_baseURI()` is hard-coded, so stored URIs are PREFIXED by it
 *      (e.g. "ipfs://x" resolves to "https://baseuri.example.com/ipfs://x"). Despite the name,
 *      there is no VIN binding and no DID string. Used for the OZ-vs-monolithic gas comparison
 *      with CVIN_NFT_DID_ERC721_Monolithic.
 * @custom:standard ERC-721 Non-Fungible Token (core + Metadata) https://eips.ethereum.org/EIPS/eip-721
 * @custom:standard ERC-2981 NFT Royalty Standard https://eips.ethereum.org/EIPS/eip-2981
 * @custom:standard ERC-165 Standard Interface Detection https://eips.ethereum.org/EIPS/eip-165
 * @custom:security payToll does not check that an entry was recorded and accepts any positive amount.
 * @custom:security Royalties on a vehicle identity are a carry-over from the NFT template.
 * @custom:security The stored URI is prefixed by the placeholder base URI.
 * @custom:see docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md
 */
contract CVIN_NFT_DID_ERC721 is ERC721, ERC721URIStorage, Ownable, ERC2981 {
    /// @notice Deploys the collection and sets the default royalty.
    /// @dev Ownable(msg.sender): the deployer is owner (toll operator and minter). Emits OwnershipTransferred.
    /// @param name ERC-721 collection name
    /// @param symbol ERC-721 collection symbol
    /// @param royaltyReceiver Default ERC-2981 royalty receiver (non-zero)
    /// @param royaltyFeeNumerator Default royalty in basis points (denominator 10000)
    constructor(
        string memory name,
        string memory symbol,
        address royaltyReceiver,
        uint96 royaltyFeeNumerator
    ) ERC721(name, symbol) Ownable(msg.sender) {
        _setDefaultRoyalty(royaltyReceiver, royaltyFeeNumerator);
    }

    /// @dev ERC-721 Metadata base URI: the constant placeholder "https://baseuri.example.com/".
    /// @return The base URI
    function _baseURI() internal view virtual override returns (string memory) {
        return "https://baseuri.example.com/";
    }

    /// @dev Pass-through override of the OZ v5 ERC721 transfer hook.
    /// @param to New holder
    /// @param tokenId Token being moved
    /// @param auth Account whose approval is checked
    /// @return The previous owner
    function _update(address to, uint256 tokenId, address auth)
        internal
        virtual
        override(ERC721)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    /// @notice Metadata URI of `tokenId`: base URI + stored URI.
    /// @dev ERC-721 Metadata via ERC721URIStorage. Reverts for a nonexistent token.
    /// @param tokenId Token ID
    /// @return The concatenated URI
    function tokenURI(uint256 tokenId) public view virtual override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    /// @notice ERC-165 interface detection.
    /// @dev Merges ERC721, ERC721URIStorage (EIP-4906 id) and ERC2981.
    /// @param interfaceId Interface identifier
    /// @return True if supported
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, ERC721URIStorage, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    /// @notice Mint `tokenId` to `to` and set its URI.
    /// @dev Access: onlyOwner. Uses `_mint` (no onERC721Received check); the caller picks the tokenId.
    /// Emits Transfer and MetadataUpdate (OZ URIStorage). ERC-721.
    /// @param to Recipient
    /// @param tokenId Token ID to mint
    /// @param uri Token URI suffix (prefixed by _baseURI)
    function mint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    // ============ Identity-based transactions (toll scenario) ============
    //
    // The vehicle NFT is the vehicle's identity: a toll operator (contract
    // owner) records when a vehicle entered a tolled zone, and only the
    // holder of that identity can settle the toll in native coin.

    /// @dev Latest toll-zone entry timestamp per vehicle token. CVIN extension (toll).
    mapping(uint256 => uint256) private _entryTimestamps;

    /// @notice Emitted when the operator records a toll-zone entry.
    /// @dev CVIN extension (toll).
    /// @param tokenId Vehicle token ID
    /// @param timestamp Recorded entry timestamp (caller-supplied)
    event EntryRecorded(uint256 indexed tokenId, uint256 timestamp);
    /// @notice Emitted when a holder pays a toll.
    /// @dev CVIN extension (toll).
    /// @param tokenId Vehicle token ID
    /// @param payer Token holder who paid
    /// @param amount Amount forwarded to the operator, in wei
    event TollPaid(uint256 indexed tokenId, address indexed payer, uint256 amount);

    /// @notice Record the time a vehicle entered a tolled zone (operator only)
    /// @dev Access: onlyOwner. The token must exist; the timestamp is arbitrary (not checked against
    ///      block.timestamp) and overwrites the previous one. Emits EntryRecorded. CVIN extension.
    /// @param tokenId Vehicle token ID
    /// @param timestamp Entry timestamp to store
    function recordEntry(uint256 tokenId, uint256 timestamp) public onlyOwner {
        _requireOwned(tokenId);
        _entryTimestamps[tokenId] = timestamp;
        emit EntryRecorded(tokenId, timestamp);
    }

    /// @notice Latest recorded entry timestamp for a vehicle (0 if none)
    /// @dev CVIN extension (toll).
    /// @param tokenId Vehicle token ID
    /// @return The stored entry timestamp
    function getEntryTimestamp(uint256 tokenId) public view returns (uint256) {
        return _entryTimestamps[tokenId];
    }

    /// @notice Pay a toll for a vehicle. The caller must hold the vehicle's
    ///         identity token; the amount is forwarded to the toll operator.
    /// @dev Access: current ownerOf(tokenId). Requires msg.value > 0 and owner() != address(0)
    ///      (D9 fix). Forwards ETH to owner() with a low-level call. Emits TollPaid. CVIN extension.
    /// @param tokenId Vehicle token ID
    function payToll(uint256 tokenId) public payable {
        require(ownerOf(tokenId) == msg.sender, "CVIN_NFT: caller is not vehicle owner");
        require(msg.value > 0, "CVIN_NFT: toll must be greater than zero");
        // D9 (docs/DEFECT_LOG.md, fixed 2026-10-04): after renounceOwnership the toll was
        // forwarded to address(0) and burned. With no operator there is nobody to pay.
        address operator = owner();
        require(operator != address(0), "CVIN_NFT: no toll operator (ownership renounced)");

        (bool sent, ) = payable(operator).call{value: msg.value}("");
        require(sent, "CVIN_NFT: toll transfer failed");

        emit TollPaid(tokenId, msg.sender, msg.value);
    }
}
