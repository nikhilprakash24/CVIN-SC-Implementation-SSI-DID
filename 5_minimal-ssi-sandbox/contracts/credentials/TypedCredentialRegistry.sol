// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IMinimalSSI} from "../interfaces/IMinimalSSI.sol";
import {EndorsementRegistry} from "../governance/EndorsementRegistry.sol";
import {CredentialTypes} from "./CredentialTypes.sol";

/// @title TypedCredentialRegistry
/// @notice Optional on-chain typing of credentials anchored through F5, plus the
///         composite read that the VID layer's verifiers use:
///
///             verifyTyped(credentialId, typeId, schemaHash, contentHash)
///               = F6 verifyCredential  (issued, not revoked, not expired, issuer active)
///               ∧ anchor == typedHash  (content integrity + type binding)
///               ∧ isEndorsed(issuer, typeId)  (issuer entitlement, G4)
///
///         The registry stores nothing about credential content. `declare` is the
///         *on-chain typing* path (one SSTORE-class write per credential) for
///         verifiers that need to discover a credential's type without holding its
///         content; the default path is *off-chain typing* (zero extra gas), where
///         the verifier recomputes the typed hash from the credential it holds.
///
/// @dev Because IMinimalSSI.verifyCredential does not return the anchored hash
///      (it returns validity, issuer, revoked, expired), the anchor comparison in
///      verifyTyped requires the anchor to be known. O1 exposes no getter for the
///      anchored hash — this is recorded as FINDING F-VID-1: the minimal interface
///      proves *status* on-chain but leaves *content binding* to the off-chain
///      verifier unless the implementation adds a getter or the credentialId itself
///      commits to the hash. O1 derives credentialId = keccak(issuer, subject, hash,
///      nonce) — so the id commits to the hash but is not recomputable without the
///      nonce. The registry therefore records the anchor at declare-time (on-chain
///      typing path) or trusts the issuer's signed credential (off-chain path).
contract TypedCredentialRegistry {
    struct Declared {
        bytes32 typeId;
        bytes32 typedHash;
        bytes32 issuer;
        uint256 declaredAt;
    }

    error NotAuthorized();
    error AlreadyDeclared();

    event CredentialDeclared(bytes32 indexed credentialId, bytes32 indexed typeId, bytes32 indexed issuer, bytes32 typedHash);

    IMinimalSSI public immutable ssi;
    EndorsementRegistry public immutable endorsements;
    mapping(bytes32 => Declared) private _declared;

    constructor(IMinimalSSI ssi_, EndorsementRegistry endorsements_) {
        ssi = ssi_;
        endorsements = endorsements_;
    }

    /// @notice On-chain typing path: the issuer (per F6's reported issuer) records
    ///         the credential's type and typed hash. Costs one write; buys queryability.
    function declare(bytes32 credentialId, bytes32 typeId, bytes32 schemaHash, bytes32 contentHash) external {
        (bool valid, bytes32 issuer, , ) = ssi.verifyCredential(credentialId);
        if (!valid) revert NotAuthorized();
        if (endorsements.adapter().controllerOf(issuer) != msg.sender) revert NotAuthorized();
        if (_declared[credentialId].declaredAt != 0) revert AlreadyDeclared();
        bytes32 th = CredentialTypes.typedHash(typeId, schemaHash, contentHash);
        _declared[credentialId] = Declared(typeId, th, issuer, block.timestamp);
        emit CredentialDeclared(credentialId, typeId, issuer, th);
    }

    function declared(bytes32 credentialId)
        external view returns (bytes32 typeId, bytes32 typedHash, bytes32 issuer, uint256 declaredAt)
    {
        Declared storage d = _declared[credentialId];
        return (d.typeId, d.typedHash, d.issuer, d.declaredAt);
    }

    /// @notice Composite verification used by VID verifiers (view; never reverts).
    /// @param typeId       expected credential type
    /// @param schemaHash   expected schema hash
    /// @param contentHash  keccak256 of the canonical off-chain credential content
    /// @return statusValid F6 result (issued, not revoked, not expired, issuer active)
    /// @return endorsed    issuer entitled for typeId now (G4)
    /// @return typeBound   true if the credential was declared on-chain and its typed
    ///                     hash matches; false if undeclared (off-chain path applies)
    /// @return issuer      the anchoring issuer DID
    function verifyTyped(bytes32 credentialId, bytes32 typeId, bytes32 schemaHash, bytes32 contentHash)
        external view
        returns (bool statusValid, bool endorsed, bool typeBound, bytes32 issuer)
    {
        (statusValid, issuer, , ) = ssi.verifyCredential(credentialId);
        if (issuer == bytes32(0)) return (false, false, false, bytes32(0));
        (endorsed, ) = endorsements.isEndorsed(issuer, typeId);
        Declared storage d = _declared[credentialId];
        typeBound = d.declaredAt != 0
            && d.typeId == typeId
            && d.typedHash == CredentialTypes.typedHash(typeId, schemaHash, contentHash);
    }
}
