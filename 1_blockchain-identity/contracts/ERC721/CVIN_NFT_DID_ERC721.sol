// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";

contract CVIN_NFT_DID_ERC721 is ERC721, ERC721URIStorage, Ownable, ERC2981 {
    constructor(
        string memory name,
        string memory symbol,
        address royaltyReceiver,
        uint96 royaltyFeeNumerator
    ) ERC721(name, symbol) Ownable(msg.sender) {
        _setDefaultRoyalty(royaltyReceiver, royaltyFeeNumerator);
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return "https://baseuri.example.com/";
    }

    function _update(address to, uint256 tokenId, address auth)
        internal
        virtual
        override(ERC721)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function tokenURI(uint256 tokenId) public view virtual override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, ERC721URIStorage, ERC2981) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    function mint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }

    // ============ Identity-based transactions (toll scenario) ============
    //
    // The vehicle NFT is the vehicle's identity: a toll operator (contract
    // owner) records when a vehicle entered a tolled zone, and only the
    // holder of that identity can settle the toll in native coin.

    /// @dev Latest toll-zone entry timestamp per vehicle token
    mapping(uint256 => uint256) private _entryTimestamps;

    event EntryRecorded(uint256 indexed tokenId, uint256 timestamp);
    event TollPaid(uint256 indexed tokenId, address indexed payer, uint256 amount);

    /// @notice Record the time a vehicle entered a tolled zone (operator only)
    function recordEntry(uint256 tokenId, uint256 timestamp) public onlyOwner {
        _requireOwned(tokenId);
        _entryTimestamps[tokenId] = timestamp;
        emit EntryRecorded(tokenId, timestamp);
    }

    /// @notice Latest recorded entry timestamp for a vehicle (0 if none)
    function getEntryTimestamp(uint256 tokenId) public view returns (uint256) {
        return _entryTimestamps[tokenId];
    }

    /// @notice Pay a toll for a vehicle. The caller must hold the vehicle's
    ///         identity token; the amount is forwarded to the toll operator.
    function payToll(uint256 tokenId) public payable {
        require(ownerOf(tokenId) == msg.sender, "CVIN_NFT: caller is not vehicle owner");
        require(msg.value > 0, "CVIN_NFT: toll must be greater than zero");

        (bool sent, ) = payable(owner()).call{value: msg.value}("");
        require(sent, "CVIN_NFT: toll transfer failed");

        emit TollPaid(tokenId, msg.sender, msg.value);
    }
}
