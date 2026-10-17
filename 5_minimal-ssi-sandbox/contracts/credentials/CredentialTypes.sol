// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CredentialTypes
/// @notice Typed credential families for the VID layer. Types are bytes32 ids;
///         the on-chain anchor passed to F5 (issueCredential) is a *typed hash*
///         so that the credential's type and schema are bound into the anchor
///         without any extra on-chain write:
///
///             credentialHash = keccak256(abi.encode(TYPE_ID, schemaHash, contentHash))
///
///         A verifier that holds the off-chain credential recomputes the typed
///         hash and compares it with the anchor read via F6. Typing therefore
///         costs zero additional gas at issuance (the "off-chain typing" path).
///         TypedCredentialRegistry offers the alternative "on-chain typing" path
///         (one extra write per credential) for verifiers that need queryability
///         without the content. Measuring the two is part of the HDA campaign
///         (doc 01 §7, doc 10).
library CredentialTypes {
    // MOBI VID I — immutable birth certificate (OEM-issued)
    bytes32 internal constant VID_BIRTH = keccak256("cvin.vid.birth.v1");
    // The "car id": jurisdictional registration (DMV-issued): plate, owner DID, validity
    bytes32 internal constant VEHICLE_REGISTRATION = keccak256("cvin.vid.registration.v1");
    // Driver's licence (DMV-issued to a person DID)
    bytes32 internal constant DRIVER_LICENCE = keccak256("cvin.person.driver-licence.v1");

    // MOBI VID II — lifecycle event family (11 types; issuer role-gated by endorsement)
    bytes32 internal constant EV_MAINTENANCE = keccak256("cvin.vid.event.maintenance.v1");
    bytes32 internal constant EV_REPAIR = keccak256("cvin.vid.event.repair.v1");
    bytes32 internal constant EV_ACCIDENT = keccak256("cvin.vid.event.accident.v1");
    bytes32 internal constant EV_RECALL = keccak256("cvin.vid.event.recall.v1");
    bytes32 internal constant EV_INSPECTION = keccak256("cvin.vid.event.inspection.v1");
    bytes32 internal constant EV_MODIFICATION = keccak256("cvin.vid.event.modification.v1");
    bytes32 internal constant EV_THEFT_REPORT = keccak256("cvin.vid.event.theft-report.v1");
    bytes32 internal constant EV_RECOVERY = keccak256("cvin.vid.event.recovery.v1");
    bytes32 internal constant EV_INSURANCE_CLAIM = keccak256("cvin.vid.event.insurance-claim.v1");
    bytes32 internal constant EV_REGISTRATION = keccak256("cvin.vid.event.registration.v1");
    bytes32 internal constant EV_DECOMMISSION = keccak256("cvin.vid.event.decommission.v1");

    function typedHash(bytes32 typeId, bytes32 schemaHash, bytes32 contentHash) internal pure returns (bytes32) {
        return keccak256(abi.encode(typeId, schemaHash, contentHash));
    }
}
