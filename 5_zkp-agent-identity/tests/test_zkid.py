"""Tests for the zkid primitives: correctness against reference libraries, and the three properties of a
zero-knowledge proof made executable (completeness, special soundness by extraction, honest-verifier zero knowledge
by simulation). Seeded (CVIN_SEED, default 1) so every run is reproducible."""
import os
import random

import coincurve
import pytest
from eth_utils import keccak as ref_keccak

from zkid import ec, hashing, merkle, nullifier, sigma
from zkid.ec import G, H, INFINITY, N, scalar_mult

SEED = int(os.environ.get("CVIN_SEED", "1"))


@pytest.fixture
def rng():
    return random.Random(SEED)


# ------------------------------------------------------------------ curve and hashes against references

def test_curve_matches_libsecp256k1(rng):
    for _ in range(5):
        k = rng.randrange(1, N)
        ours = scalar_mult(k, G).encode()
        ref = coincurve.PrivateKey(k.to_bytes(32, "big")).public_key.format(compressed=True)
        assert ours == ref


def test_group_order_and_encoding(rng):
    assert scalar_mult(N, G) == INFINITY
    assert G.on_curve() and H.on_curve()
    p = scalar_mult(rng.randrange(1, N), G)
    assert ec.decode(p.encode()) == p
    with pytest.raises(ValueError):
        ec.decode(b"\x05" + bytes(32))


def test_keccak_matches_ethereum(rng):
    assert hashing.keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
    for n in (1, 55, 135, 136, 137, 300):
        data = bytes(rng.randrange(256) for _ in range(n))
        assert hashing.keccak256(data) == ref_keccak(data)


# ------------------------------------------------------------------ Schnorr: completeness, soundness, ZK

def test_schnorr_completeness_and_binding(rng):
    x = rng.randrange(1, N)
    P = scalar_mult(x, G)
    proof = sigma.schnorr_prove(x, b"verifier-A|nonce-1", rng)
    assert sigma.schnorr_verify(P, proof, b"verifier-A|nonce-1")
    # bound to its context: a replay to another verifier, or with another nonce, fails
    assert not sigma.schnorr_verify(P, proof, b"verifier-B|nonce-1")
    assert not sigma.schnorr_verify(P, proof, b"verifier-A|nonce-2")
    # bound to the key and to every field
    assert not sigma.schnorr_verify(scalar_mult(x + 1, G), proof, b"verifier-A|nonce-1")
    assert not sigma.schnorr_verify(P, sigma.SchnorrProof(proof.R, (proof.s + 1) % N), b"verifier-A|nonce-1")


def test_schnorr_special_soundness_extracts_the_witness(rng):
    """A prover that can answer two challenges for one commitment must know x: the extractor computes it."""
    x = rng.randrange(1, N)
    prover = sigma.SchnorrProver(x)
    R = prover.commit(rng)
    k_state = prover._k
    e1 = rng.randrange(1, N)
    s1 = prover.respond(e1)
    prover._k = k_state  # rewind the prover (only an extractor in a proof of soundness can do this)
    e2 = rng.randrange(1, N)
    s2 = prover.respond(e2)
    assert sigma.schnorr_check(prover.P, R, e1, s1) and sigma.schnorr_check(prover.P, R, e2, s2)
    assert sigma.extract_schnorr(e1, s1, e2, s2) == x


def test_nonce_reuse_leaks_the_key(rng):
    """The same extraction is an attack when a real prover reuses a nonce (the PS3 / Android wallet failures)."""
    x = rng.randrange(1, N)
    k = rng.randrange(1, N)
    P, R = scalar_mult(x, G), scalar_mult(k, G)
    e1 = sigma._schnorr_challenge(P, R, b"ctx-1")
    e2 = sigma._schnorr_challenge(P, R, b"ctx-2")
    s1, s2 = (k + e1 * x) % N, (k + e2 * x) % N
    assert sigma.extract_schnorr(e1, s1, e2, s2) == x


def test_schnorr_honest_verifier_zero_knowledge(rng):
    """The simulator never sees x, yet its transcripts are accepting, and the response is uniform in both worlds."""
    x = rng.randrange(1, N)
    P = scalar_mult(x, G)
    sims, reals = [], []
    for _ in range(200):
        R, e, s = sigma.simulate_schnorr(P, rng)
        assert sigma.schnorr_check(P, R, e, s)
        sims.append(s / N)
        prover = sigma.SchnorrProver(x)
        R2 = prover.commit(rng)
        e2 = rng.randrange(1, N)
        reals.append(prover.respond(e2) / N)
    # both are uniform on [0, 1): means near 1/2 (a coarse distribution check, not a proof)
    assert abs(sum(sims) / len(sims) - 0.5) < 0.08
    assert abs(sum(reals) / len(reals) - 0.5) < 0.08


# ------------------------------------------------------------------ Pedersen

def test_pedersen_opening_proof(rng):
    v, r = 2021, rng.randrange(1, N)
    C = sigma.pedersen_commit(v, r)
    p = sigma.opening_prove(v, r, C, b"ctx", rng)
    assert sigma.opening_verify(C, p, b"ctx")
    assert not sigma.opening_verify(C + G, p, b"ctx")
    assert not sigma.opening_verify(C, p, b"other")


def test_pedersen_binding_needs_an_unknown_trapdoor(rng):
    """If anyone knew t = log_G H they could open one commitment to any value. hash_to_curve is why nobody does."""
    t = rng.randrange(1, N)
    H_bad = scalar_mult(t, G)
    v1, r1 = 2015, rng.randrange(1, N)
    C = scalar_mult(v1, G) + scalar_mult(r1, H_bad)
    v2 = 2024
    r2 = ((v1 - v2) * pow(t, -1, N) + r1) % N  # equivocate
    assert scalar_mult(v2, G) + scalar_mult(r2, H_bad) == C


def test_dleq(rng):
    x = rng.randrange(1, N)
    G2 = ec.hash_to_curve(b"another base")
    p = sigma.dleq_prove(x, G, G2, b"ctx", rng)
    assert sigma.dleq_verify(G, scalar_mult(x, G), G2, scalar_mult(x, G2), p, b"ctx")
    assert not sigma.dleq_verify(G, scalar_mult(x, G), G2, scalar_mult(x + 1, G2), p, b"ctx")


# ------------------------------------------------------------------ bits, ranges, thresholds

@pytest.mark.parametrize("b", [0, 1])
def test_bit_proof(rng, b):
    r = rng.randrange(1, N)
    C = sigma.pedersen_commit(b, r)
    p = sigma.bit_prove(b, r, C, b"ctx", rng)
    assert sigma.bit_verify(C, p, b"ctx")


def test_bit_proof_cannot_cover_a_two(rng):
    r = rng.randrange(1, N)
    C = sigma.pedersen_commit(2, r)
    with pytest.raises(ValueError):
        sigma.bit_prove(2, r, C)
    for claimed in (0, 1):  # an honest-looking proof for the wrong value fails
        assert not sigma.bit_verify(C, sigma.bit_prove(claimed, r, C, b"", rng))


def test_range_proof(rng):
    v, r = 37, rng.randrange(1, N)
    C = sigma.pedersen_commit(v, r)
    p = sigma.range_prove(v, r, C, 8, b"ctx", rng)
    assert sigma.range_verify(C, p, 8, b"ctx")
    assert not sigma.range_verify(C + G, p, 8, b"ctx")
    assert not sigma.range_verify(C, p, 8, b"other")
    with pytest.raises(ValueError):
        sigma.range_prove(300, r, sigma.pedersen_commit(300, r), 8)


def test_threshold_proof_model_year(rng):
    """'Model year >= 2020' without the model year: the predicate ZK-VIN proves, here as a sigma protocol."""
    r = rng.randrange(1, N)
    C = sigma.pedersen_commit(2022, r)
    p = sigma.threshold_prove(2022, r, C, 2020, 6, b"insurer|n1", rng)
    assert sigma.threshold_verify(C, 2020, p, 6, b"insurer|n1")
    assert not sigma.threshold_verify(C, 2021 + 2, p, 6, b"insurer|n1")  # proof is for t = 2020 only
    with pytest.raises(ValueError):  # 2018 < 2020: no honest proof exists
        sigma.threshold_prove(2018, r, sigma.pedersen_commit(2018, r), 2020, 6)


def test_threshold_forgery_with_wraparound_fails(rng):
    """A cheat commits to v < t and tries to prove v - t mod N as a small number; the bit structure forbids it."""
    r = rng.randrange(1, N)
    C = sigma.pedersen_commit(2018, r)
    Ct = C - scalar_mult(2020, G)  # commits to -2 mod N
    fake = sigma.range_prove(2, r, sigma.pedersen_commit(2, r), 6, b"", rng)
    assert not sigma.range_verify(Ct, fake, 6, b"")


# ------------------------------------------------------------------ Merkle and nullifiers

@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 9])
def test_merkle_inclusion(n):
    leaves = [f"WMI-{i:03d}".encode() for i in range(n)]
    t = merkle.MerkleTree(leaves)
    for i, leaf in enumerate(leaves):
        assert merkle.verify_inclusion(leaf, t.prove(i), t.root)
    assert not merkle.verify_inclusion(b"WMI-999", t.prove(0), t.root)


def test_merkle_inner_node_is_not_a_leaf():
    t = merkle.MerkleTree([b"a", b"b", b"c", b"d"])
    inner = t.levels[1][0]
    assert not merkle.verify_inclusion(inner, t.prove(0)[1:], t.root)


def test_scoped_nullifiers(rng):
    s = b"vehicle-salt"
    assert nullifier.hash_nullifier(s, b"toll:A") == nullifier.hash_nullifier(s, b"toll:A")
    assert nullifier.hash_nullifier(s, b"toll:A") != nullifier.hash_nullifier(s, b"toll:B")
    x = rng.randrange(1, N)
    P = scalar_mult(x, G)
    nf, proof = nullifier.key_nullifier(x, b"rsu:42", b"n1", rng)
    assert nullifier.key_nullifier_verify(P, b"rsu:42", nf, proof, b"n1")
    assert not nullifier.key_nullifier_verify(P, b"rsu:43", nf, proof, b"n1")
    nf2, _ = nullifier.key_nullifier(x, b"rsu:43", b"n1", rng)
    assert nf2 != nf
