// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {CredentialTypes} from "./CredentialTypes.sol";

/// @notice Test-only probe exposing the library's typed hash so the JS library's
///         encoding can be asserted equal to the Solidity encoding.
contract TypedHashProbe {
    function probe(bytes32 t, bytes32 s, bytes32 c) external pure returns (bytes32) {
        return CredentialTypes.typedHash(t, s, c);
    }
}
