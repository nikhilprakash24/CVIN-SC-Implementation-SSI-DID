"""
Review 02, T-12 (comparison_framework.py):

* `benchmark_verification` discarded the verify result, so a failing verify
  was timed and reported as a verification time;
* the PKI enrollment and credential-request benchmarks passed `ca=None`, so
  they always raised and the benchmark printed "Error" and reported 0 ms.

Both tests below fail on the pre-fix code.
"""

from identity.comparison_framework import IdentitySystemBenchmark
from identity.standard.pki_identity import VehiclePKI_CA, VehiclePKIIdentity


class AlwaysFails:
    """An identity system whose signature check always fails."""

    def sign_message(self, message):
        return {'message': message, 'signature': '00'}

    def verify_message(self, signed, crl):
        return False, 0.05


def _small(bench, system, kind):
    return bench.run_full_benchmark(system, kind, enrollment_iterations=2,
                                    credential_iterations=2, signing_iterations=20,
                                    verification_iterations=20)


def test_failed_verifications_are_not_reported_as_timings():
    m = _small(IdentitySystemBenchmark("fail"), AlwaysFails(), "DID")
    assert m.verification_success_count == 0
    assert m.verification_failure_count == 20
    assert m.verification_time_ms == 0.0


def test_benchmark_verification_returns_outcome_per_iteration():
    out = IdentitySystemBenchmark("fail").benchmark_verification(
        AlwaysFails(), {'message': {}}, set(), iterations=3)
    assert [ok for _, ok in out] == [False, False, False]


def test_pki_benchmark_uses_the_ca_and_all_verifies_succeed():
    ca = VehiclePKI_CA("Bench-CA")
    v = VehiclePKIIdentity("BENCH")
    v.generate_keypair()
    v.request_enrollment_certificate(ca)
    v.request_pseudonym_certificates(ca, count=2)
    m = _small(IdentitySystemBenchmark("pki", ca=ca), v, "PKI")
    assert m.enrollment_time_ms > 0          # was 0.0: request_enrollment_certificate(None) raised
    assert m.credential_request_time_ms > 0  # was 0.0: request_pseudonym_certificates(None) raised
    assert m.verification_success_count == 20
    assert m.verification_failure_count == 0
    assert m.verification_time_ms > 0
