pragma circom 2.0.0;
include "poseidon.circom";
include "comparators.circom";

// AgeGate (HDA doc 02 §4, C-2): prove birthYear <= maxBirthYear without revealing birthYear,
// where commitment = Poseidon(birthYear, salt) is the value the issuer placed in the credential.
// Public: commitment, maxBirthYear. Private: birthYear, salt.
template AgeGate() {
    signal input birthYear;      // private
    signal input salt;           // private
    signal input commitment;     // public
    signal input maxBirthYear;   // public (= currentYear - 18)

    component h = Poseidon(2);
    h.inputs[0] <== birthYear;
    h.inputs[1] <== salt;
    h.out === commitment;

    component le = LessEqThan(16);
    le.in[0] <== birthYear;
    le.in[1] <== maxBirthYear;
    le.out === 1;
}
component main {public [commitment, maxBirthYear]} = AgeGate();
