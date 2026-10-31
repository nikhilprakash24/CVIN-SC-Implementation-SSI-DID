pragma circom 2.1.6;

/*
 * ZK-VIN: the zero-knowledge VIN tier deferred in Phase 1 (scope change SC-12, idea I-09).
 *
 * Statement. "I know a VIN (17 characters), a model year and a salt such that
 *   (1) Poseidon(packed VIN, model year, region, salt) equals the commitment anchored on chain for my identity;
 *   (2) the VIN's world manufacturer identifier (its first three characters) is a leaf of the authorised-manufacturer
 *       Merkle tree whose root is public;
 *   (3) the model year is at least the verifier's minimum;
 *   (4) the region in the commitment is the verifier's region;
 * and the nullifier for this verifier's scope is Poseidon(salt, scope), bound to this verifier's challenge."
 *
 * Public: commitment, mfrRoot, minModelYear, region, scope, challenge. Output: nullifier.
 * Private: vin[17] (character codes 0..63), modelYear, salt, the Merkle path.
 *
 * What the verifier learns: that the statement is true, and a nullifier that is stable within its scope and
 * unlinkable across scopes (the salt is secret). Not the VIN, not the model year, not the manufacturer.
 *
 * Research artefact. The Groth16 keys in ../artifacts come from a single-party local setup whose toxic waste this
 * host could have kept; a deployment needs a multi-party ceremony (Plan 1 to-do 11).
 */

include "../node_modules/circomlib/circuits/poseidon.circom";
include "../node_modules/circomlib/circuits/comparators.circom";
include "../node_modules/circomlib/circuits/bitify.circom";

// Poseidon Merkle inclusion; pathIndices[i] = 1 when the running node is the right child at level i.
template MerkleInclusion(depth) {
    signal input leaf;
    signal input pathElements[depth];
    signal input pathIndices[depth];
    signal output root;

    signal cur[depth + 1];
    signal left[depth];
    signal right[depth];
    component h[depth];

    cur[0] <== leaf;
    for (var i = 0; i < depth; i++) {
        pathIndices[i] * (1 - pathIndices[i]) === 0;
        left[i] <== cur[i] + pathIndices[i] * (pathElements[i] - cur[i]);
        right[i] <== pathElements[i] + pathIndices[i] * (cur[i] - pathElements[i]);
        h[i] = Poseidon(2);
        h[i].inputs[0] <== left[i];
        h[i].inputs[1] <== right[i];
        cur[i + 1] <== h[i].out;
    }
    root <== cur[depth];
}

template ZkVin(depth) {
    // private
    signal input vin[17];
    signal input modelYear;
    signal input salt;
    signal input mfrPath[depth];
    signal input mfrIdx[depth];
    // public
    signal input commitment;
    signal input mfrRoot;
    signal input minModelYear;
    signal input region;
    signal input scope;
    signal input challenge;
    // public output
    signal output nullifier;

    // (0) every character is a 6-bit code; pack the VIN into one field element (102 bits < 254)
    component chr[17];
    var packed = 0;
    var base = 1;
    for (var i = 0; i < 17; i++) {
        chr[i] = Num2Bits(6);
        chr[i].in <== vin[i];
        packed += vin[i] * base;
        base *= 64;
    }
    signal vinPacked;
    vinPacked <== packed;

    // (1) the commitment opens to this VIN, model year, region and salt
    component c = Poseidon(4);
    c.inputs[0] <== vinPacked;
    c.inputs[1] <== modelYear;
    c.inputs[2] <== region;
    c.inputs[3] <== salt;
    commitment === c.out;

    // (2) the manufacturer (WMI = first three characters) is authorised
    signal wmi;
    wmi <== vin[0] + 64 * vin[1] + 4096 * vin[2];
    component m = MerkleInclusion(depth);
    m.leaf <== wmi;
    for (var i = 0; i < depth; i++) {
        m.pathElements[i] <== mfrPath[i];
        m.pathIndices[i] <== mfrIdx[i];
    }
    mfrRoot === m.root;

    // (3) model year >= minimum; both range-checked to 12 bits so the comparator is sound
    component myBits = Num2Bits(12);
    myBits.in <== modelYear;
    component minBits = Num2Bits(12);
    minBits.in <== minModelYear;
    component ge = GreaterEqThan(12);
    ge.in[0] <== modelYear;
    ge.in[1] <== minModelYear;
    ge.out === 1;

    // (4) region equality is enforced by (1): the public region is an input of the commitment

    // nullifier for this scope
    component nf = Poseidon(2);
    nf.inputs[0] <== salt;
    nf.inputs[1] <== scope;
    nullifier <== nf.out;

    // bind the verifier's challenge into the proof (a public input with a constraint on it)
    signal challengeSquared;
    challengeSquared <== challenge * challenge;
}

component main { public [commitment, mfrRoot, minModelYear, region, scope, challenge] } = ZkVin(4);
