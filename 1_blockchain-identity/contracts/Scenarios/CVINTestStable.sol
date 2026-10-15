// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title CVINTestStable
 * @notice Test-only 6-decimal stablecoin with EIP-2612 permit, used as the
 *         settlement asset of the toll-corridor scenario (X1). It stands in for
 *         a regulated stablecoin; nothing about it is production-grade.
 */
contract CVINTestStable is ERC20, ERC20Permit, Ownable {
    constructor() ERC20("CVIN Test Stable", "cUSD") ERC20Permit("CVIN Test Stable") Ownable(msg.sender) {}

    function decimals() public pure override returns (uint8) {
        return 6;
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}
