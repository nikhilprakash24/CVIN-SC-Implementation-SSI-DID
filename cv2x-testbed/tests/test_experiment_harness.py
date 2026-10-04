"""
Review 02, T-6: experiment_pki_vs_erc1056.measure() must snapshot the RPC
counter right after the timed region, before the untimed check() (whose
post-condition call previously inflated revoke_credential from 5 to 8 RPCs).
"""

from types import SimpleNamespace

from experiment_pki_vs_erc1056 import Backend, measure


class _Counter:
    def __init__(self):
        self.count = 0
        self.methods = []

    def call(self, method):
        self.count += 1
        self.methods.append(method)

    def reset(self):
        self.count = 0
        self.methods = []


def test_rpc_snapshot_excludes_untimed_check():
    rpc = _Counter()
    prov = SimpleNamespace(last_receipt=None)
    backend = Backend('fake', prov, False, rpc)

    def run(_):
        rpc.call('timed_a')
        rpc.call('timed_b')
        return True

    def check(_, __):
        rpc.call('post_check_eth_call')   # untimed post-condition
        return {}

    samples = measure(backend, 'op', n=3, warmup=1, prepare=lambda i: i, run=run, check=check)
    assert [s.rpc_calls for s in samples] == [2, 2, 2]
    assert samples[0].extra['rpc_methods'] == ['timed_a', 'timed_b']


def test_registry_artifact_provenance_recorded(tmp_path):
    """Pass 2: the #21 run records which bytecode it deployed (stale tracked artifact, Q-9)."""
    import hashlib, json
    from experiment_pki_vs_erc1056 import TRACKED_REGISTRY_ARTIFACT, registry_artifact_info
    info = registry_artifact_info(TRACKED_REGISTRY_ARTIFACT)
    with open(TRACKED_REGISTRY_ARTIFACT) as f:
        bytecode = json.load(f)["bytecode"]
    assert info["registry_bytecode_sha256"] == hashlib.sha256(bytecode.encode()).hexdigest()
    assert info["registry_artifact"] == "artifacts/contracts/ERC1056Registry.sol/ERC1056Registry.json"
