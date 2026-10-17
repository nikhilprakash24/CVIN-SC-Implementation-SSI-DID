// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ERC725Account — minimal ERC-725X/Y account used by option O3.
/// @notice One contract per identity. ERC-725Y: a generic bytes32 → bytes key-value store
///         (`getData`/`setData`, `DataChanged`). ERC-725X: `execute` for generic calls.
///         The DID Document IS the data store; nothing about the identity lives anywhere else.
/// @dev Written fresh for the sandbox (the ERC725Alliance package pins OpenZeppelin 4.x,
///      which conflicts with the 5.x pin used by O2). Authorisation: the owner (the DID
///      controller), or the manager (the O3 registry acting on the owner's behalf after it
///      has checked `msg.sender == owner`) — the key-manager pattern reduced to two roles.
contract ERC725Account {
    event DataChanged(bytes32 indexed dataKey, bytes dataValue);
    event Executed(uint256 indexed operationType, address indexed target, uint256 value, bytes4 indexed selector);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    error NotOwner();

    address public owner;
    address public immutable manager;
    mapping(bytes32 => bytes) private _store;

    constructor(address owner_, address manager_) { owner = owner_; manager = manager_; }

    modifier auth() { if (msg.sender != owner && msg.sender != manager) revert NotOwner(); _; }

    // ---- ERC-725Y ----
    function getData(bytes32 dataKey) external view returns (bytes memory) { return _store[dataKey]; }
    function setData(bytes32 dataKey, bytes calldata dataValue) external auth {
        _store[dataKey] = dataValue;
        emit DataChanged(dataKey, dataValue);
    }

    // ---- ERC-725X (operation 0 = CALL) ----
    function execute(uint256 operationType, address target, uint256 value, bytes calldata data)
        external payable auth returns (bytes memory result)
    {
        require(operationType == 0, "op");
        bool ok;
        (ok, result) = target.call{value: value}(data);
        require(ok, "call");
        emit Executed(operationType, target, value, bytes4(data));
    }

    function transferOwnership(address newOwner) external auth {
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    receive() external payable {}
}
