// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ClaimHolderAccount — ERC-725Y store + ERC-734 purpose keys + ERC-735 claims (option O4).
/// @notice The "725xy" identity: one contract per identity holding (a) a key-value store,
///         (b) keys with purposes (1 MANAGEMENT, 2 ACTION, 3 CLAIM, 4 ENCRYPTION), and (c)
///         claims made ABOUT this identity by issuers, each identified by keccak(issuer, topic).
///         This is the only EVM pattern in the inventory with a native credential object
///         (the claim) — the "claims-assisted" Set B path in ARCHITECTURE.md §5.
/// @dev Written fresh for the sandbox from the ERC-734/735 drafts (Origin Protocol lineage);
///      no external package. The registry (O4_ERC725xy) is the `manager` and acts only after
///      checking that msg.sender holds a MANAGEMENT key here. Claim data holds the credential
///      content hash; the W3C gap (no JSON-LD context / issuanceDate / cryptosuite URL, uint256 scheme)
///      is exactly the gap the thesis records for ERC-735.
contract ClaimHolderAccount {
    uint256 public constant MANAGEMENT = 1;
    uint256 public constant ACTION = 2;
    uint256 public constant CLAIM = 3;
    uint256 public constant ENCRYPTION = 4;

    struct Key { uint256 purpose; uint256 keyType; bytes32 key; bool exists; }
    struct Claim { uint256 topic; uint256 scheme; address issuer; bytes signature; bytes data; string uri; bool exists; }

    event KeyAdded(bytes32 indexed key, uint256 indexed purpose, uint256 indexed keyType);
    event KeyRemoved(bytes32 indexed key, uint256 indexed purpose, uint256 indexed keyType);
    event ClaimAdded(bytes32 indexed claimId, uint256 indexed topic, uint256 scheme, address indexed issuer, bytes signature, bytes data, string uri);
    event ClaimRemoved(bytes32 indexed claimId, uint256 indexed topic, uint256 scheme, address indexed issuer, bytes signature, bytes data, string uri);
    event DataChanged(bytes32 indexed dataKey, bytes dataValue);

    error NotAuthorized();

    address public immutable manager;
    mapping(bytes32 => Key) private _keys;
    mapping(uint256 => bytes32[]) private _keysByPurpose;
    uint256 public keyCount;
    mapping(bytes32 => Claim) private _claims;
    mapping(uint256 => bytes32[]) private _claimsByTopic;
    mapping(bytes32 => bytes) private _store;

    constructor(address controller, address manager_) {
        manager = manager_;
        bytes32 k = keccak256(abi.encodePacked(controller));
        _keys[k] = Key(MANAGEMENT, 1, k, true);
        _keysByPurpose[MANAGEMENT].push(k);
        keyCount = 1;
        emit KeyAdded(k, MANAGEMENT, 1);
    }

    modifier auth() {
        if (msg.sender != manager && !keyHasPurpose(keccak256(abi.encodePacked(msg.sender)), MANAGEMENT)) revert NotAuthorized();
        _;
    }

    // ---- ERC-734 ----
    function getKey(bytes32 key) external view returns (uint256 purpose, uint256 keyType, bytes32 k) {
        Key storage x = _keys[key]; return (x.purpose, x.keyType, x.key);
    }
    function keyHasPurpose(bytes32 key, uint256 purpose) public view returns (bool) {
        Key storage x = _keys[key]; return x.exists && x.purpose == purpose;
    }
    function getKeysByPurpose(uint256 purpose) external view returns (bytes32[] memory) { return _keysByPurpose[purpose]; }
    function addKey(bytes32 key, uint256 purpose, uint256 keyType) external auth returns (bool) {
        if (_keys[key].exists) return false;
        _keys[key] = Key(purpose, keyType, key, true);
        _keysByPurpose[purpose].push(key);
        keyCount += 1;
        emit KeyAdded(key, purpose, keyType);
        return true;
    }
    function removeKey(bytes32 key) external auth returns (bool) {
        Key storage x = _keys[key];
        if (!x.exists) return false;
        emit KeyRemoved(key, x.purpose, x.keyType);
        bytes32[] storage arr = _keysByPurpose[x.purpose];
        for (uint256 i = 0; i < arr.length; i++) if (arr[i] == key) { arr[i] = arr[arr.length - 1]; arr.pop(); break; }
        delete _keys[key];
        keyCount -= 1;
        return true;
    }

    // ---- ERC-735 ----
    /// @dev Called by an issuer's ACTION/CLAIM key or by the manager on an issuer's behalf; the
    ///      registry passes the issuer's account address as `issuer` and vouches for it.
    function addClaim(uint256 topic, uint256 scheme, address issuer, bytes calldata signature, bytes calldata data, string calldata uri)
        external returns (bytes32 claimId)
    {
        if (msg.sender != manager && msg.sender != issuer && !keyHasPurpose(keccak256(abi.encodePacked(msg.sender)), CLAIM)) revert NotAuthorized();
        claimId = keccak256(abi.encodePacked(issuer, topic));
        if (!_claims[claimId].exists) _claimsByTopic[topic].push(claimId);
        _claims[claimId] = Claim(topic, scheme, issuer, signature, data, uri, true);
        emit ClaimAdded(claimId, topic, scheme, issuer, signature, data, uri);
    }
    function removeClaim(bytes32 claimId) external returns (bool) {
        Claim storage c = _claims[claimId];
        if (!c.exists) return false;
        if (msg.sender != manager && msg.sender != c.issuer && !keyHasPurpose(keccak256(abi.encodePacked(msg.sender)), MANAGEMENT)) revert NotAuthorized();
        emit ClaimRemoved(claimId, c.topic, c.scheme, c.issuer, c.signature, c.data, c.uri);
        bytes32[] storage arr = _claimsByTopic[c.topic];
        for (uint256 i = 0; i < arr.length; i++) if (arr[i] == claimId) { arr[i] = arr[arr.length - 1]; arr.pop(); break; }
        delete _claims[claimId];
        return true;
    }
    function getClaim(bytes32 claimId) external view returns (uint256 topic, uint256 scheme, address issuer, bytes memory signature, bytes memory data, string memory uri) {
        Claim storage c = _claims[claimId]; return (c.topic, c.scheme, c.issuer, c.signature, c.data, c.uri);
    }
    function hasClaim(bytes32 claimId) external view returns (bool) { return _claims[claimId].exists; }
    function getClaimIdsByTopic(uint256 topic) external view returns (bytes32[] memory) { return _claimsByTopic[topic]; }

    // ---- ERC-725Y ----
    function getData(bytes32 dataKey) external view returns (bytes memory) { return _store[dataKey]; }
    function setData(bytes32 dataKey, bytes calldata dataValue) external auth { _store[dataKey] = dataValue; emit DataChanged(dataKey, dataValue); }
}
