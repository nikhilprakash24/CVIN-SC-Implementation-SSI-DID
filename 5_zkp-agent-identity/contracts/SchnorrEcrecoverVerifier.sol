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
/// @title SchnorrEcrecoverVerifier
/// @author CVIN research project
/// @notice Verifies a Schnorr proof of knowledge of a secp256k1 private key, using the ecrecover precompile.
/// @dev Gas baseline for Plan 1 to-do 1 (sigma protocol vs Groth16). ecrecover is used to compute
///      address(s*G - e*P) and the Fiat-Shamir challenge e = keccak256(addr(R) || parity || px || message)
///      is recomputed and compared. The proof is not tied to any ERC-1056 identity. Python prover:
///      5_zkp-agent-identity/zkid/schnorr_evm.py; gas is recorded by scripts/measure_gas.js.
/// @custom:standard Schnorr identification / Fiat-Shamir (non-interactive PoK of a discrete log), secp256k1 (https://www.secg.org/sec2-v2.pdf)
/// @custom:standard ecrecover precompile 0x01 (Ethereum Yellow Paper, Appendix E: https://ethereum.github.io/yellowpaper/paper.pdf)
/// @custom:security No replay protection: the same (px, message, e, s) can be resubmitted to `prove`; `message` must carry any nonce or context.
/// @custom:security Research gas baseline only; it proves key knowledge, not control of any on-chain identity.
/// @custom:see docs/smart-contracts/05-zkp-and-idtx.md (section 3.2)
/// @custom:see 5_zkp-agent-identity/test-contracts/zkvin_gate.test.js (Schnorr verifier test)
contract SchnorrEcrecoverVerifier {
    /// @dev secp256k1 group order n.
    uint256 private constant Q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141;

    /// @notice Checks a Schnorr proof that the prover knows the private key of the point (px, parity).
    /// @dev Returns false (never reverts) on out-of-range inputs, on a failed ecrecover, or on a challenge mismatch.
    ///      Computes h = n - s*px and sigma = n - e*px (mod n), so ecrecover(h, parity+27, px, sigma) = address(s*G - e*P).
    ///      If s*px or e*px is 0 mod n, h or sigma becomes n, which ecrecover rejects (harmless).
    /// @param parity y-parity of the public key P (0 or 1).
    /// @param px x-coordinate of the public key P; must be non-zero and below n.
    /// @param message Context bound into the challenge (carry any nonce here).
    /// @param e Fiat-Shamir challenge, below n.
    /// @param s Response s = k + e*x mod n, below n.
    /// @return True if the recomputed challenge equals `e`.
    function verify(uint8 parity, bytes32 px, bytes32 message, bytes32 e, bytes32 s) public pure returns (bool) {
        uint256 x = uint256(px);
        if (x == 0 || x >= Q || uint256(s) >= Q || uint256(e) >= Q || parity > 1) return false;
        bytes32 h = bytes32(Q - mulmod(uint256(s), x, Q));
        bytes32 sigma = bytes32(Q - mulmod(uint256(e), x, Q));
        address r = ecrecover(h, parity + 27, px, sigma);
        if (r == address(0)) return false;
        return e == keccak256(abi.encodePacked(r, parity, px, message));
    }

    /// @notice Emitted by `prove` after a proof verifies.
    /// @param px x-coordinate of the proven public key.
    /// @param message The message bound into the proof.
    event Proved(bytes32 indexed px, bytes32 message);

    /// @notice State-changing wrapper around `verify`, so verification gas can be measured as a transaction.
    /// @dev Reverts with "invalid proof" if `verify` returns false; otherwise emits `Proved`.
    /// @param parity y-parity of the public key P (0 or 1).
    /// @param px x-coordinate of the public key P.
    /// @param message Context bound into the challenge.
    /// @param e Fiat-Shamir challenge.
    /// @param s Schnorr response.
    function prove(uint8 parity, bytes32 px, bytes32 message, bytes32 e, bytes32 s) external {
        require(verify(parity, px, message, e, s), "invalid proof");
        emit Proved(px, message);
    }
}
