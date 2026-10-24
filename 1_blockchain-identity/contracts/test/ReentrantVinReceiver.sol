// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ICVINVehicleNFTMint
/// @notice The one CVINVehicleNFT function the attacker calls.
interface ICVINVehicleNFTMint {
    /// @notice See CVINVehicleNFT.mintVehicle.
    /// @param to Recipient.
    /// @param vin 17-character VIN.
    /// @param make Vehicle make.
    /// @param model Vehicle model.
    /// @param year Model year.
    /// @param color Colour.
    /// @param metadataURI Token URI.
    /// @return tokenId The minted token id.
    function mintVehicle(
        address to,
        string memory vin,
        string memory make,
        string memory model,
        uint16 year,
        string memory color,
        string memory metadataURI
    ) external returns (uint256);
}

/// @title ReentrantVinReceiver (test-only attacker)
/// @author CVIN research project
/// @notice Test fixture: an ERC-721 receiver that re-enters `CVINVehicleNFT.mintVehicle`
///         from `onERC721Received` with the same VIN, to prove the one-token-per-VIN invariant
///         holds during the `_safeMint` callback.
/// @dev Must hold MANUFACTURER_ROLE on the target for the re-entry to pass the role check.
///      Used only by test/L2-identity-system/per-option/ERC721/mintReentrancy.regression.test.js.
/// @custom:see docs/smart-contracts/03-token-standards-erc721-erc1155-lsp8.md
contract ReentrantVinReceiver {
    /// @notice The NFT contract to re-enter.
    ICVINVehicleNFTMint public immutable nft;
    /// @notice VIN to mint a second time during the callback.
    string public vin;
    /// @notice True once the re-entrant mint has been attempted.
    bool public attempted;
    /// @notice True if the re-entrant mint succeeded (the bug).
    bool public reentrySucceeded;

    /// @param nft_ Target CVINVehicleNFT.
    constructor(ICVINVehicleNFTMint nft_) {
        nft = nft_;
    }

    /// @notice Mint `vin_` to this contract; the callback re-enters with the same VIN.
    /// @param vin_ A 17-character VIN.
    function attack(string calldata vin_) external {
        vin = vin_;
        nft.mintVehicle(address(this), vin_, "Make", "Model", 2024, "Black", "ipfs://x");
    }

    /// @notice ERC-721 receiver hook; re-enters once and records whether it succeeded.
    /// @return The ERC-721 receiver magic value.
    function onERC721Received(address, address, uint256, bytes calldata) external returns (bytes4) {
        if (!attempted) {
            attempted = true;
            try nft.mintVehicle(address(this), vin, "Make", "Model", 2024, "Black", "ipfs://y") {
                reentrySucceeded = true;
            } catch {}
        }
        return this.onERC721Received.selector;
    }
}
