// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Groth16Verifier} from "./AgeGateVerifier.sol";

/// @title ZKAgeGate — the on-chain verification path for a credential predicate (HDA doc 02 §3).
/// @notice Admits a presentation if a Groth16 proof shows that the holder's committed birth
///         year is <= maxBirthYear, i.e. the holder is old enough, without revealing it. The
///         commitment must be the one the issuer put in the credential (bound off-chain to the
///         credential's typed anchor by the issuer's signature; see lib/vid/credentials.js).
///         `admit` is a transaction so that the verifier's gas is measurable; `check` is the
///         same verification as a free view for the off-chain path.
contract ZKAgeGate {
    error InvalidProof();
    error Replay();

    event Admitted(bytes32 indexed presentationId, uint256 indexed commitment, uint256 maxBirthYear);

    Groth16Verifier public immutable verifier;
    mapping(bytes32 => bool) public admitted;

    constructor(Groth16Verifier verifier_) { verifier = verifier_; }

    function check(uint[2] calldata a, uint[2][2] calldata b, uint[2] calldata c, uint256 commitment, uint256 maxBirthYear)
        external view returns (bool)
    {
        return verifier.verifyProof(a, b, c, [commitment, maxBirthYear]);
    }

    /// @param presentationId the F8 presentation id this proof accompanies (replay-protected here too)
    function admit(bytes32 presentationId, uint[2] calldata a, uint[2][2] calldata b, uint[2] calldata c, uint256 commitment, uint256 maxBirthYear)
        external
    {
        if (admitted[presentationId]) revert Replay();
        if (!verifier.verifyProof(a, b, c, [commitment, maxBirthYear])) revert InvalidProof();
        admitted[presentationId] = true;
        emit Admitted(presentationId, commitment, maxBirthYear);
    }
}
