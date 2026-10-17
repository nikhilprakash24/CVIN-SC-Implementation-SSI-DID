// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

/// @title ERC-8004 registries (sandbox implementation of the Draft spec, read 2026-10-17)
/// @notice Three per-chain singletons: Identity (ERC-721 + URIStorage, agentId = tokenId,
///         agentURI = tokenURI, on-chain metadata), Reputation (client feedback as signed
///         fixed-point values with tags; summary filtered by client set), Validation
///         (request/response hooks for zkML / TEE / re-execution validators).
/// @dev Fidelity reference — the curated deployments (github.com/erc-8004/erc-8004-contracts,
///      as of 2026-10-06): Ethereum mainnet IdentityRegistry 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432,
///      ReputationRegistry 0x8004BAa17C55a88189AE136b182e5fdA19dE9b63 (same addresses on Base,
///      BSC, Gnosis, Mantle, Abstract, Injective, 0G). The Validation Registry is specified but
///      reported as not production-deployed (DIGEST-LEVEL). Function names, argument shapes and
///      events follow the EIP text; EIP-712 agentWallet verification is omitted (noted).
///      `wrapper` is the IMinimalSSI compliance layer (O7_ERC8004): it is treated as an
///      approved operator for every agent so the twelve functions can act on the owner's behalf
///      after their own authorisation check — the Stage 31 "compliance layer ERC-8004 lacks".
contract IdentityRegistry8004 is ERC721URIStorage {
    struct MetadataEntry { string metadataKey; bytes metadataValue; }
    event Registered(uint256 indexed agentId, string agentURI, address indexed owner);
    event URIUpdated(uint256 indexed agentId, string newURI, address indexed updatedBy);
    event MetadataSet(uint256 indexed agentId, string indexed indexedMetadataKey, string metadataKey, bytes metadataValue);

    error NotOwnerOrOperator();
    error ReservedKey();

    address public immutable wrapper;
    uint256 private _next = 1;
    mapping(uint256 => mapping(string => bytes)) private _meta;
    mapping(uint256 => address) private _agentWallet;

    constructor(address wrapper_) ERC721("ERC-8004 Agents", "AGENT") { wrapper = wrapper_; }

    function isOwnerOrOperator(uint256 agentId, address who) public view returns (bool) {
        address o = ownerOf(agentId);
        return who == o || who == wrapper || isApprovedForAll(o, who) || getApproved(agentId) == who;
    }
    modifier onlyAgent(uint256 agentId) { if (!isOwnerOrOperator(agentId, msg.sender)) revert NotOwnerOrOperator(); _; }

    function register() external returns (uint256 agentId) { return _register(msg.sender, ""); }
    function register(string calldata agentURI) external returns (uint256 agentId) { return _register(msg.sender, agentURI); }
    /// @dev wrapper-only overload so the compliance layer can mint for a controller.
    function registerFor(address owner_, string calldata agentURI) external returns (uint256 agentId) {
        if (msg.sender != wrapper) revert NotOwnerOrOperator();
        return _register(owner_, agentURI);
    }
    function _register(address owner_, string memory agentURI) internal returns (uint256 agentId) {
        agentId = _next++;
        _mint(owner_, agentId);
        if (bytes(agentURI).length != 0) _setTokenURI(agentId, agentURI);
        _agentWallet[agentId] = owner_;
        emit MetadataSet(agentId, "agentWallet", "agentWallet", abi.encodePacked(owner_));
        emit Registered(agentId, agentURI, owner_);
    }
    function setAgentURI(uint256 agentId, string calldata newURI) external onlyAgent(agentId) { _setTokenURI(agentId, newURI); emit URIUpdated(agentId, newURI, msg.sender); }
    function getMetadata(uint256 agentId, string memory metadataKey) external view returns (bytes memory) { return _meta[agentId][metadataKey]; }
    function setMetadata(uint256 agentId, string memory metadataKey, bytes memory metadataValue) external onlyAgent(agentId) {
        if (keccak256(bytes(metadataKey)) == keccak256("agentWallet")) revert ReservedKey();
        _meta[agentId][metadataKey] = metadataValue;
        emit MetadataSet(agentId, metadataKey, metadataKey, metadataValue);
    }
    function getAgentWallet(uint256 agentId) external view returns (address) { return _agentWallet[agentId]; }
    function unsetAgentWallet(uint256 agentId) external onlyAgent(agentId) { _agentWallet[agentId] = address(0); }
    function exists(uint256 agentId) external view returns (bool) { return _ownerOf(agentId) != address(0); }

    function _update(address to, uint256 tokenId, address auth) internal override returns (address from) {
        from = super._update(to, tokenId, auth);
        if (from != address(0)) _agentWallet[tokenId] = address(0); // cleared on transfer per spec
    }
}

contract ReputationRegistry8004 {
    struct Feedback { int128 value; uint8 valueDecimals; string tag1; string tag2; bool isRevoked; bool exists; }
    event NewFeedback(uint256 indexed agentId, address indexed clientAddress, uint64 feedbackIndex, int128 value, uint8 valueDecimals, string indexed indexedTag1, string tag1, string tag2, string endpoint, string feedbackURI, bytes32 feedbackHash);
    event FeedbackRevoked(uint256 indexed agentId, address indexed clientAddress, uint64 indexed feedbackIndex);
    event ResponseAppended(uint256 indexed agentId, address indexed clientAddress, uint64 feedbackIndex, address indexed responder, string responseURI, bytes32 responseHash);

    error SelfFeedback();
    error BadDecimals();
    error UnknownAgent();
    error NotClient();

    IdentityRegistry8004 private _identity;
    mapping(uint256 => mapping(address => mapping(uint64 => Feedback))) private _fb;
    mapping(uint256 => mapping(address => uint64)) private _last;
    mapping(uint256 => address[]) private _clients;
    mapping(uint256 => mapping(address => bool)) private _isClient;
    mapping(uint256 => mapping(address => mapping(uint64 => uint64))) private _responses;

    function initialize(address identityRegistry_) external { require(address(_identity) == address(0), "init"); _identity = IdentityRegistry8004(identityRegistry_); }
    function getIdentityRegistry() external view returns (address) { return address(_identity); }

    struct FeedbackInput { int128 value; uint8 valueDecimals; string tag1; string tag2; string endpoint; string feedbackURI; bytes32 feedbackHash; }

    function giveFeedback(uint256 agentId, int128 value, uint8 valueDecimals, string calldata tag1, string calldata tag2, string calldata endpoint, string calldata feedbackURI, bytes32 feedbackHash) external {
        _give(msg.sender, agentId, FeedbackInput(value, valueDecimals, tag1, tag2, endpoint, feedbackURI, feedbackHash));
    }
    /// @dev Wrapper-only overload: the IMinimalSSI/ISetC compliance layer forwards the real client
    ///      address so the spec's "not owner/operator" rule is applied to the client, not the wrapper.
    function giveFeedbackFor(address client, uint256 agentId, int128 value, uint8 valueDecimals, string calldata tag1, string calldata tag2, string calldata endpoint, string calldata feedbackURI, bytes32 feedbackHash) external {
        if (msg.sender != _identity.wrapper()) revert NotClient();
        _give(client, agentId, FeedbackInput(value, valueDecimals, tag1, tag2, endpoint, feedbackURI, feedbackHash));
    }
    function _isOwnerOrOp(uint256 agentId, address who) internal view returns (bool) {
        address o = _identity.ownerOf(agentId);
        return who == o || _identity.isApprovedForAll(o, who) || _identity.getApproved(agentId) == who;
    }
    function _give(address client, uint256 agentId, FeedbackInput memory f) internal {
        if (!_identity.exists(agentId)) revert UnknownAgent();
        if (f.valueDecimals > 18) revert BadDecimals();
        if (_isOwnerOrOp(agentId, client)) revert SelfFeedback(); // MUST NOT be owner/operator
        uint64 idx = ++_last[agentId][client];
        _fb[agentId][client][idx] = Feedback(f.value, f.valueDecimals, f.tag1, f.tag2, false, true);
        if (!_isClient[agentId][client]) { _isClient[agentId][client] = true; _clients[agentId].push(client); }
        emit NewFeedback(agentId, client, idx, f.value, f.valueDecimals, f.tag1, f.tag1, f.tag2, f.endpoint, f.feedbackURI, f.feedbackHash);
    }
    function revokeFeedback(uint256 agentId, uint64 feedbackIndex) external {
        Feedback storage f = _fb[agentId][msg.sender][feedbackIndex];
        if (!f.exists) revert NotClient();
        f.isRevoked = true;
        emit FeedbackRevoked(agentId, msg.sender, feedbackIndex);
    }
    function appendResponse(uint256 agentId, address clientAddress, uint64 feedbackIndex, string calldata responseURI, bytes32 responseHash) external {
        _responses[agentId][clientAddress][feedbackIndex] += 1;
        emit ResponseAppended(agentId, clientAddress, feedbackIndex, msg.sender, responseURI, responseHash);
    }
    /// @notice Average over the given clients (non-empty, per spec: unfiltered summaries are Sybil-prone). Values
    ///         are normalised to 0 decimals for the summary (sandbox simplification; spec leaves aggregation open).
    function getSummary(uint256 agentId, address[] calldata clientAddresses, string calldata tag1, string calldata tag2)
        external view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals)
    {
        (count, summaryValue) = _summary(agentId, clientAddresses, _h(tag1), _h(tag2));
        summaryValueDecimals = 0;
    }
    function _h(string calldata s) internal pure returns (bytes32) { return bytes(s).length == 0 ? bytes32(0) : keccak256(bytes(s)); }
    function _summary(uint256 agentId, address[] calldata clients, bytes32 h1, bytes32 h2) internal view returns (uint64 count, int128 summaryValue) {
        int256 sum;
        for (uint256 c = 0; c < clients.length; c++) {
            (uint64 n, int256 s) = _sumClient(agentId, clients[c], h1, h2);
            count += n; sum += s;
        }
        summaryValue = count == 0 ? int128(0) : int128(sum / int256(uint256(count)));
    }
    function _sumClient(uint256 agentId, address cl, bytes32 h1, bytes32 h2) internal view returns (uint64 n, int256 s) {
        uint64 last = _last[agentId][cl];
        for (uint64 i = 1; i <= last; i++) {
            Feedback storage f = _fb[agentId][cl][i];
            if (f.isRevoked) continue;
            if (h1 != bytes32(0) && keccak256(bytes(f.tag1)) != h1) continue;
            if (h2 != bytes32(0) && keccak256(bytes(f.tag2)) != h2) continue;
            s += int256(f.value) / int256(10 ** uint256(f.valueDecimals));
            n++;
        }
    }
    function readFeedback(uint256 agentId, address clientAddress, uint64 feedbackIndex) external view returns (int128 value, uint8 valueDecimals, string memory tag1, string memory tag2, bool isRevoked) {
        Feedback storage f = _fb[agentId][clientAddress][feedbackIndex]; return (f.value, f.valueDecimals, f.tag1, f.tag2, f.isRevoked);
    }
    function getClients(uint256 agentId) external view returns (address[] memory) { return _clients[agentId]; }
    function getLastIndex(uint256 agentId, address clientAddress) external view returns (uint64) { return _last[agentId][clientAddress]; }
    function getResponseCount(uint256 agentId, address clientAddress, uint64 feedbackIndex) external view returns (uint64) { return _responses[agentId][clientAddress][feedbackIndex]; }
}

contract ValidationRegistry8004 {
    struct Validation { address validatorAddress; uint256 agentId; uint8 response; bytes32 responseHash; string tag; uint256 lastUpdate; bool requested; bool responded; }
    event ValidationRequest(address indexed validatorAddress, uint256 indexed agentId, string requestURI, bytes32 indexed requestHash);
    event ValidationResponse(address indexed validatorAddress, uint256 indexed agentId, bytes32 indexed requestHash, uint8 response, string responseURI, bytes32 responseHash, string tag);

    error NotOwnerOrOperator();
    error NotValidator();
    error UnknownRequest();
    error BadResponse();

    IdentityRegistry8004 private _identity;
    mapping(bytes32 => Validation) private _val;
    mapping(uint256 => bytes32[]) private _byAgent;
    mapping(address => bytes32[]) private _byValidator;

    function initialize(address identityRegistry_) external { require(address(_identity) == address(0), "init"); _identity = IdentityRegistry8004(identityRegistry_); }
    function getIdentityRegistry() external view returns (address) { return address(_identity); }

    function validationRequest(address validatorAddress, uint256 agentId, string calldata requestURI, bytes32 requestHash) external {
        if (!_identity.isOwnerOrOperator(agentId, msg.sender)) revert NotOwnerOrOperator();
        Validation storage v = _val[requestHash];
        if (!v.requested) { _byAgent[agentId].push(requestHash); _byValidator[validatorAddress].push(requestHash); }
        v.validatorAddress = validatorAddress; v.agentId = agentId; v.requested = true; v.lastUpdate = block.timestamp;
        emit ValidationRequest(validatorAddress, agentId, requestURI, requestHash);
    }
    function validationResponse(bytes32 requestHash, uint8 response, string calldata responseURI, bytes32 responseHash, string calldata tag) external {
        Validation storage v = _val[requestHash];
        if (!v.requested) revert UnknownRequest();
        if (msg.sender != v.validatorAddress) revert NotValidator();
        if (response > 100) revert BadResponse();
        v.response = response; v.responseHash = responseHash; v.tag = tag; v.lastUpdate = block.timestamp; v.responded = true;
        emit ValidationResponse(v.validatorAddress, v.agentId, requestHash, response, responseURI, responseHash, tag);
    }
    function getValidationStatus(bytes32 requestHash) external view returns (address validatorAddress, uint256 agentId, uint8 response, bytes32 responseHash, string memory tag, uint256 lastUpdate) {
        Validation storage v = _val[requestHash]; return (v.validatorAddress, v.agentId, v.response, v.responseHash, v.tag, v.lastUpdate);
    }
    function requestState(bytes32 requestHash) external view returns (bool requested, bool responded) { Validation storage v = _val[requestHash]; return (v.requested, v.responded); }
    function getSummary(uint256 agentId, address[] calldata validatorAddresses, string calldata tag) external view returns (uint64 count, uint8 averageResponse) {
        uint256 sum; bytes32[] storage hs = _byAgent[agentId];
        for (uint256 i = 0; i < hs.length; i++) {
            Validation storage v = _val[hs[i]];
            if (!v.responded) continue;
            if (validatorAddresses.length != 0) { bool ok; for (uint256 j = 0; j < validatorAddresses.length; j++) if (validatorAddresses[j] == v.validatorAddress) { ok = true; break; } if (!ok) continue; }
            if (bytes(tag).length != 0 && keccak256(bytes(v.tag)) != keccak256(bytes(tag))) continue;
            sum += v.response; count++;
        }
        averageResponse = count == 0 ? 0 : uint8(sum / count);
    }
    function getAgentValidations(uint256 agentId) external view returns (bytes32[] memory) { return _byAgent[agentId]; }
    function getValidatorRequests(address validatorAddress) external view returns (bytes32[] memory) { return _byValidator[validatorAddress]; }
}
