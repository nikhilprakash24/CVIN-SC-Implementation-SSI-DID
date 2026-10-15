// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/*
 * A Schnorr proof of knowledge of a secp256k1 key, verified on chain through the ecrecover precompile.
 *
 * Plan 1 to-do 1: compare a sigma-protocol verifier's gas with Groth16's. The trick (known as the "ecrecover hack"
 * for Schnorr) makes ecrecover compute R' = s*G - e*P and return its Ethereum address:
 *   ecrecover(h, v, r, sigma) = address( r^-1 * (sigma * Pt - h * G) ), where Pt has x = r and parity v - 27.
 * With r = px, Pt = P, sigma = -e*px and h = -s*px (mod n) this is address(s*G - e*P).
 * The prover sends (s, e) with e = keccak256(address(R) || parity || px || message) and s = k + e*x... with R = k*G
 * that gives s*G - e*P = R, so the verifier recomputes e from the recovered address and compares.
 * Python prover: 5_zkp-agent-identity/zkid/schnorr_evm.py.
 */
contract SchnorrEcrecoverVerifier {
    uint256 private constant Q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;

    function verify(uint8 parity, bytes32 px, bytes32 message, bytes32 e, bytes32 s) public pure returns (bool) {
        uint256 x = uint256(px);
        if (x == 0 || x >= Q || uint256(s) >= Q || uint256(e) >= Q || parity > 1) return false;
        bytes32 h = bytes32(Q - mulmod(uint256(s), x, Q));
        bytes32 sigma = bytes32(Q - mulmod(uint256(e), x, Q));
        address r = ecrecover(h, parity + 27, px, sigma);
        if (r == address(0)) return false;
        return e == keccak256(abi.encodePacked(r, parity, px, message));
    }

    event Proved(bytes32 indexed px, bytes32 message);

    // A state-changing wrapper so the verification can be measured as a transaction.
    function prove(uint8 parity, bytes32 px, bytes32 message, bytes32 e, bytes32 s) external {
        require(verify(parity, px, message, e, s), "invalid proof");
        emit Proved(px, message);
    }
}
