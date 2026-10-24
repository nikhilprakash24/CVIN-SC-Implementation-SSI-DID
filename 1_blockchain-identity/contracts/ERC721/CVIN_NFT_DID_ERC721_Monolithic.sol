// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/interfaces/IERC165.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Metadata.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";

/**
 * @title CVIN_NFT_DID_ERC721_Monolithic
 * @author CVIN research project
 * @notice Hand-written ERC-721 (core + Metadata) with ERC-2981 royalties in a single file,
 *         the same surface as CVIN_NFT_DID_ERC721 without the toll functions.
 * @dev Exists to compare the gas cost of OpenZeppelin inheritance with a monolithic file. Uses
 *      OpenZeppelin Contracts 5.0.2 only for Ownable, Strings and the interface types (IERC165,
 *      IERC2981, IERC721, IERC721Metadata, IERC721Receiver). Deviations from ERC-721 / OZ v5:
 *      does not inherit IERC721 in Solidity (`is IERC165, IERC2981, Ownable`) but still reports
 *      IERC721 in supportsInterface; no Enumerable extension; setApprovalForAll rejects
 *      `operator == msg.sender`; `_transfer` emits an Approval event while clearing approvals;
 *      `mint` uses `_mint`, not a safe mint. The D-series balance fix (`+= 1` instead of
 *      `+= tokenId`) is covered by balanceCountsTokens.regression.test.js.
 * @custom:standard ERC-721 Non-Fungible Token (core + Metadata) https://eips.ethereum.org/EIPS/eip-721
 * @custom:standard ERC-2981 NFT Royalty Standard https://eips.ethereum.org/EIPS/eip-2981
 * @custom:standard ERC-165 Standard Interface Detection https://eips.ethereum.org/EIPS/eip-165
 * @custom:security _burn, _setTokenRoyalty and _resetTokenRoyalty are internal and never called:
 *                  no burn, and per-token royalties are unreachable.
 * @custom:security The stored URI is prefixed by the placeholder base URI. No VIN binding.
 * @custom:see docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md
 */
contract CVIN_NFT_DID_ERC721_Monolithic is IERC165, IERC2981, Ownable {
    using Strings for uint256;

    // ERC721 related mappings and events
    /// @dev ERC-721 core: tokenId => owner (address(0) = nonexistent).
    mapping(uint256 => address) private _owners;
    /// @dev ERC-721 core: owner => number of tokens held.
    mapping(address => uint256) private _balances;
    /// @dev ERC-721 core: tokenId => single approved address.
    mapping(uint256 => address) private _tokenApprovals;
    /// @dev ERC-721 core: owner => operator => approved for all.
    mapping(address => mapping(address => bool)) private _operatorApprovals;

    /// @notice ERC-721 Transfer event (declared locally).
    /// @param from Previous owner (address(0) on mint)
    /// @param to New owner
    /// @param tokenId Token ID
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    /// @notice ERC-721 Approval event (declared locally). Also emitted when approvals are cleared on transfer.
    /// @param owner Token owner
    /// @param approved Approved address (address(0) when cleared)
    /// @param tokenId Token ID
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    /// @notice ERC-721 ApprovalForAll event (declared locally).
    /// @param owner Token owner
    /// @param operator Operator
    /// @param approved Whether the operator is approved
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    // ERC721URIStorage related mapping
    /// @dev URIStorage: tokenId => stored URI suffix.
    mapping(uint256 => string) private _tokenURIs;

    // EIP-2981 related variables and events
    /// @dev ERC-2981 royalty record: receiver and fee in basis points (denominator 10000).
    struct RoyaltyInfo {
        address receiver;
        uint96 royaltyFraction;
    }
    /// @dev ERC-2981 default royalty, set by the constructor.
    RoyaltyInfo private _defaultRoyaltyInfo;
    /// @dev ERC-2981 per-token royalties (never written: _setTokenRoyalty is unused).
    mapping(uint256 => RoyaltyInfo) private _tokenRoyaltyInfo;

    /// @notice Constructor: sets name, symbol and the default royalty.
    /// @dev OpenZeppelin v5: Ownable requires the initial owner to be passed explicitly
    ///      (Ownable(msg.sender)). Emits OwnershipTransferred.
    /// @param name ERC-721 collection name
    /// @param symbol ERC-721 collection symbol
    /// @param royaltyReceiver Default ERC-2981 royalty receiver (non-zero)
    /// @param royaltyFeeNumerator Default royalty in basis points (<= 10000)
    constructor(string memory name, string memory symbol, address royaltyReceiver, uint96 royaltyFeeNumerator)
        Ownable(msg.sender)
    {
        _name = name;
        _symbol = symbol;
        _setDefaultRoyalty(royaltyReceiver, royaltyFeeNumerator);
    }

    // ERC721 functions
    /// @dev ERC-721 Metadata collection name.
    string private _name;
    /// @dev ERC-721 Metadata collection symbol.
    string private _symbol;

    /// @notice ERC-721 Metadata collection name.
    /// @return The name
    function name() public view returns (string memory) {
        return _name;
    }

    /// @notice ERC-721 Metadata collection symbol.
    /// @return The symbol
    function symbol() public view returns (string memory) {
        return _symbol;
    }

    /// @notice ERC-721: number of tokens held by `owner`.
    /// @dev Reverts for the zero address.
    /// @param owner Account to query
    /// @return Token count
    function balanceOf(address owner) public view returns (uint256) {
        require(owner != address(0), "Balance query for the zero address");
        return _balances[owner];
    }

    /// @notice ERC-721: owner of `tokenId`.
    /// @dev Reverts if the token does not exist.
    /// @param tokenId Token ID
    /// @return Owner address
    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "Owner query for nonexistent token");
        return owner;
    }

    /// @dev Constant placeholder base URI "https://baseuri.example.com/".
    /// @return The base URI
    function _baseURI() internal view returns (string memory) {
        return "https://baseuri.example.com/";
    }

    /// @notice ERC-721 Metadata URI of `tokenId`.
    /// @dev base + stored URI, or base + decimal tokenId if none is stored. Reverts if nonexistent.
    /// @param tokenId Token ID
    /// @return The token URI
    function tokenURI(uint256 tokenId) public view returns (string memory) {
        require(_exists(tokenId), "URI query for nonexistent token");
        string memory _tokenURI = _tokenURIs[tokenId];
        string memory base = _baseURI();

        // If there is no base URI, return the token URI.
        if (bytes(base).length == 0) {
            return _tokenURI;
        }
        // If both are set, concatenate the baseURI and tokenURI (via abi.encodePacked).
        if (bytes(_tokenURI).length > 0) {
            return string(abi.encodePacked(base, _tokenURI));
        }

        return string(abi.encodePacked(base, tokenId.toString()));
    }

    /// @notice ERC-721: approve `to` to transfer `tokenId`.
    /// @dev Caller must be the owner or an approved operator; `to` must not be the owner. Emits Approval.
    /// @param to Address to approve
    /// @param tokenId Token ID
    function approve(address to, uint256 tokenId) public {
        address owner = ownerOf(tokenId);
        require(to != owner, "Approval to current owner");

        require(
            msg.sender == owner || isApprovedForAll(owner, msg.sender),
            "Approve caller is not owner nor approved for all"
        );

        _approve(to, tokenId);
    }

    /// @notice ERC-721: approved address for `tokenId`.
    /// @dev Reverts if the token does not exist.
    /// @param tokenId Token ID
    /// @return Approved address (address(0) if none)
    function getApproved(uint256 tokenId) public view returns (address) {
        require(_exists(tokenId), "Approved query for nonexistent token");

        return _tokenApprovals[tokenId];
    }

    /// @notice ERC-721: (un)approve `operator` for all of the caller's tokens.
    /// @dev Deviation: rejects `operator == msg.sender`. Emits ApprovalForAll.
    /// @param operator Operator address
    /// @param approved Approval status
    function setApprovalForAll(address operator, bool approved) public {
        require(operator != msg.sender, "Approve to caller");

        _operatorApprovals[msg.sender][operator] = approved;
        emit ApprovalForAll(msg.sender, operator, approved);
    }

    /// @notice ERC-721: whether `operator` is approved for all tokens of `owner`.
    /// @param owner Token owner
    /// @param operator Operator
    /// @return Approval status
    function isApprovedForAll(address owner, address operator) public view returns (bool) {
        return _operatorApprovals[owner][operator];
    }

    /// @notice ERC-721: transfer `tokenId` from `from` to `to` (no receiver check).
    /// @dev Caller must be owner, approved or operator. Emits Approval (clear) and Transfer.
    /// @param from Current owner
    /// @param to Recipient (non-zero)
    /// @param tokenId Token ID
    function transferFrom(address from, address to, uint256 tokenId) public {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Caller is not owner nor approved");

        _transfer(from, to, tokenId);
    }

    /// @notice ERC-721: safe transfer with empty data.
    /// @param from Current owner
    /// @param to Recipient
    /// @param tokenId Token ID
    function safeTransferFrom(address from, address to, uint256 tokenId) public {
        safeTransferFrom(from, to, tokenId, "");
    }

    /// @notice ERC-721: transfer, then require onERC721Received acceptance if `to` is a contract.
    /// @dev Caller must be owner, approved or operator. Emits Approval (clear) and Transfer.
    /// @param from Current owner
    /// @param to Recipient
    /// @param tokenId Token ID
    /// @param _data Data forwarded to onERC721Received
    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory _data) public {
        require(_isApprovedOrOwner(msg.sender, tokenId), "Caller is not owner nor approved");
        _safeTransfer(from, to, tokenId, _data);
    }

    /// @dev Transfer plus receiver acceptance check.
    /// @param from Current owner
    /// @param to Recipient
    /// @param tokenId Token ID
    /// @param _data Data forwarded to onERC721Received
    function _safeTransfer(address from, address to, uint256 tokenId, bytes memory _data) internal {
        _transfer(from, to, tokenId);
        require(_checkOnERC721Received(from, to, tokenId, _data), "Transfer to non ERC721Receiver implementer");
    }

    /// @dev True if `tokenId` has an owner.
    /// @param tokenId Token ID
    /// @return Existence flag
    function _exists(uint256 tokenId) internal view returns (bool) {
        return _owners[tokenId] != address(0);
    }

    /// @dev Reverts if nonexistent; true if `spender` is owner, approved or operator.
    /// @param spender Account to check
    /// @param tokenId Token ID
    /// @return Authorisation flag
    function _isApprovedOrOwner(address spender, uint256 tokenId) internal view returns (bool) {
        require(_exists(tokenId), "Operator query for nonexistent token");
        address owner = ownerOf(tokenId);
        return (spender == owner || getApproved(tokenId) == spender || isApprovedForAll(owner, spender));
    }

    /// @dev Mints `tokenId` to `to` (no receiver check). Emits Transfer.
    /// @param to Recipient (non-zero)
    /// @param tokenId Token ID (must not exist)
    function _mint(address to, uint256 tokenId) internal {
        require(to != address(0), "Mint to the zero address");
        require(!_exists(tokenId), "Token already minted");

        // Balance counts tokens held, so it moves by 1 per mint/burn/transfer
        // (the original monolithic draft mistakenly added the tokenId itself).
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(address(0), to, tokenId);
    }

    /// @dev Burns `tokenId`, clearing its approval. Emits Approval and Transfer. Never called.
    /// @param tokenId Token ID
    function _burn(uint256 tokenId) internal {
        address owner = ownerOf(tokenId);

        _approve(address(0), tokenId);

        _balances[owner] -= 1;
        delete _owners[tokenId];

        emit Transfer(owner, address(0), tokenId);
    }

    /// @dev Moves `tokenId`; clears approval (emits Approval, unlike OZ v5) and emits Transfer.
    /// @param from Current owner (must match)
    /// @param to Recipient (non-zero)
    /// @param tokenId Token ID
    function _transfer(address from, address to, uint256 tokenId) internal {
        require(ownerOf(tokenId) == from, "Transfer of token that is not own");
        require(to != address(0), "Transfer to the zero address");

        _approve(address(0), tokenId);

        _balances[from] -= 1;
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(from, to, tokenId);
    }

    /// @dev Sets the single approval for `tokenId`. Emits Approval.
    /// @param to Approved address
    /// @param tokenId Token ID
    function _approve(address to, uint256 tokenId) internal {
        _tokenApprovals[tokenId] = to;
        emit Approval(ownerOf(tokenId), to, tokenId);
    }

    /// @dev Calls onERC721Received on contract recipients; bubbles up revert reasons.
    /// @param from Previous owner
    /// @param to Recipient
    /// @param tokenId Token ID
    /// @param _data Forwarded data
    /// @return True if `to` is an EOA or returned the expected selector
    function _checkOnERC721Received(address from, address to, uint256 tokenId, bytes memory _data) private returns (bool) {
        if (to.code.length > 0) {
            try IERC721Receiver(to).onERC721Received(msg.sender, from, tokenId, _data) returns (bytes4 retval) {
                return retval == IERC721Receiver.onERC721Received.selector;
            } catch (bytes memory reason) {
                if (reason.length == 0) {
                    revert("Transfer to non ERC721Receiver implementer");
                } else {
                    assembly {
                        revert(add(32, reason), mload(reason))
                    }
                }
            }
        } else {
            return true;
        }
    }

    // ERC721URIStorage functions
    /// @dev Stores the URI suffix of an existing token.
    /// @param tokenId Token ID
    /// @param _tokenURI URI suffix
    function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal {
        require(_exists(tokenId), "URI set of nonexistent token");
        _tokenURIs[tokenId] = _tokenURI;
    }

    // EIP-2981 functions
    /// @notice ERC-2981 royalty for a sale of `_tokenId` at `_salePrice`.
    /// @dev Per-token royalty if set (never, in practice), else the default; amount = price * fee / 10000.
    /// @param _tokenId Token ID
    /// @param _salePrice Sale price
    /// @return receiver Royalty receiver
    /// @return royaltyAmount Royalty amount in the sale currency
    function royaltyInfo(uint256 _tokenId, uint256 _salePrice) external view override returns (address receiver, uint256 royaltyAmount) {
        RoyaltyInfo memory royalty = _tokenRoyaltyInfo[_tokenId];

        if (royalty.receiver == address(0)) {
            royalty = _defaultRoyaltyInfo;
        }

        royaltyAmount = (_salePrice * royalty.royaltyFraction) / 10000;
        return (royalty.receiver, royaltyAmount);
    }

    /// @dev ERC-2981 per-token royalty setter. Never called.
    /// @param tokenId Token ID
    /// @param receiver Royalty receiver (non-zero)
    /// @param feeNumerator Fee in basis points (<= 10000)
    function _setTokenRoyalty(uint256 tokenId, address receiver, uint96 feeNumerator) internal {
        require(feeNumerator <= 10000, "ERC2981: royalty fee will exceed salePrice");
        require(receiver != address(0), "ERC2981: Invalid parameters");

        _tokenRoyaltyInfo[tokenId] = RoyaltyInfo(receiver, feeNumerator);
    }

    /// @dev ERC-2981 default royalty setter (constructor only).
    /// @param receiver Royalty receiver (non-zero)
    /// @param feeNumerator Fee in basis points (<= 10000)
    function _setDefaultRoyalty(address receiver, uint96 feeNumerator) internal {
        require(feeNumerator <= 10000, "ERC2981: royalty fee will exceed salePrice");
        require(receiver != address(0), "ERC2981: Invalid parameters");

        _defaultRoyaltyInfo = RoyaltyInfo(receiver, feeNumerator);
    }

    /// @dev Clears a per-token royalty. Never called.
    /// @param tokenId Token ID
    function _resetTokenRoyalty(uint256 tokenId) internal {
        delete _tokenRoyaltyInfo[tokenId];
    }

    /// @notice ERC-165 interface detection.
    /// @dev Hand-written list: IERC165, IERC721, IERC721Metadata, IERC2981.
    /// @param interfaceId Interface identifier
    /// @return True if supported
    function supportsInterface(bytes4 interfaceId) public view override(IERC165) returns (bool) {
        return
            interfaceId == type(IERC165).interfaceId ||
            interfaceId == type(IERC721).interfaceId ||
            interfaceId == type(IERC721Metadata).interfaceId ||
            interfaceId == type(IERC2981).interfaceId;
    }

    // Public mint function
    /// @notice Mint `tokenId` to `to` and set its URI.
    /// @dev Access: onlyOwner. Uses `_mint` (no receiver check). Emits Transfer.
    /// @param to Recipient
    /// @param tokenId Token ID to mint
    /// @param uri Token URI suffix (prefixed by _baseURI)
    function mint(address to, uint256 tokenId, string memory uri) public onlyOwner {
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }
}