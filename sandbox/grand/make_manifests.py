#!/usr/bin/env python3
"""Generate the per-option feature manifests and the grand (union) manifest.

Sources, in order of authority:
  1. compiled ABIs (what each on-chain option can do)      -> stance 'implemented'
  2. 4_comparison-framework/results/gas_benchmark.json notes
     and the cv2x-testbed experiments                       -> stance 'measured-in-comparison'
  3. declared rules below for off-chain capabilities        -> 'implemented' / 'not-applicable'
A family with no evidence is 'not-applicable' with an auto reason and reviewed: false.
Manifests are skeletons until a human flips `reviewed: true` per family; `run.py matrix`
reports how many families are still unreviewed. Sandboxes reference code; they never copy it.
"""
import json, pathlib, re, runpy, yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
MX = runpy.run_path(str(ROOT / "4_comparison-framework/feature-matrix/make_feature_matrix.py"), run_name="imported")
FAMILIES, load, ART = MX["FAMILIES"], MX["load"], MX["ART"]
EXTRA = [("Off-chain creation (identity exists before any transaction)", None),
         ("Message signing / verification (off-chain hot path)", r"(sign_message|verify_message|get_current_pseudonym)")]
GAS = json.load(open(ROOT / "4_comparison-framework/results/gas_benchmark.json"))

OPTIONS = {  # slug: (display, kind, contract artifacts, benchmark key, provider path, experiment registers)
    "erc-1056-uport":   ("ERC-1056 / uPort-style", "on-chain", ["ERC1056/EthereumDIDRegistry.sol", "ERC1056/CVINVehicleDIDRegistry.sol"], "ERC-1056", None, []),
    "erc-1056-vehicle": ("ERC-1056 / vehicle profile", "on-chain", ["MOBI/ERC1056Registry.sol"], None, "cv2x-testbed/identity/erc1056_provider.py", ["#21", "#29"]),
    "erc-721":          ("ERC-721", "on-chain", ["ERC721/CVINVehicleNFT.sol", "ERC721/CVIN_NFT_DID_ERC721.sol", "ERC721/CVIN_NFT_DID_ERC721_Monolithic.sol"], "ERC-721", None, []),
    "erc-725":          ("ERC-725", "on-chain", ["ERC725/CVIN_DID_ERC725.sol"], "ERC-725", None, []),
    "erc-725xy":        ("ERC-725xy", "on-chain", ["ERC725xy/CVINVehicleERC725XY.sol", "ERC725xy/CVINExecuteTarget.sol"], "ERC-725xy", None, []),
    "erc-735":          ("ERC-735", "on-chain", ["ERC735/CVINVehicleClaimHolder.sol"], "ERC-735", None, []),
    "erc-1155":         ("ERC-1155", "on-chain", ["ERC1155/CVINVehicleCredential1155.sol"], "ERC-1155", None, []),
    "erc-4337":         ("ERC-4337", "on-chain", ["ERC4337/CVINVehicleAccount.sol", "ERC4337/CVINMinimalEntryPoint.sol"], "ERC-4337", None, []),
    "lsp8":             ("LSP8", "on-chain", ["LSP8/CVINVehicleLSP8.sol"], "LSP8", None, []),
    "cvin-combined":    ("CVIN-Combined (ERC-1056 + ERC-735 hybrid)", "on-chain", ["CVINCombined/CVINCombinedIdentity.sol"], "CVIN-Combined", None, []),
    "mobi-vid":         ("MOBI VID I + II (application profile)", "on-chain", ["MOBI/MOBIVIDRegistry.sol", "MOBI/MOBIVIDRegistryV2.sol"], "MOBI-VID-V2", "cv2x-testbed/identity/mobi_vid_provider.py", ["#30"]),
    "baseline-pki":     ("Baseline: IEEE 1609.2-style PKI (in-process)", "off-chain", [], None, "cv2x-testbed/identity/standard/pki_identity.py", ["#21", "#29"]),
    "baseline-centralized": ("Baseline: centralized registry (in-process)", "off-chain", [], None, "cv2x-testbed/identity/centralized_vehicle_registry.py", ["#21", "#30"]),
}
OFFCHAIN_CREATION = {"erc-1056-uport": "identity is implicit in the address (EthereumDIDRegistry identityOwner defaults to the identity itself); creation costs 0 gas",
                     "cvin-combined": "ERC-1056 base: identity is implicit in the address; creation costs 0 gas (S2 adapter returns implicit: true)",
                     }
OFFCHAIN_CREATION_NA = {"erc-4337": "ERC-4337 accounts are counterfactual in principle (CREATE2 + initCode), but this harness has no account factory and CVINMinimalEntryPoint rejects initCode, so creation is an explicit deployment here (S2 finding)"}
PROVIDER_METHOD_RX = re.compile(r"^\s+def ([a-z][a-z0-9_]+)\(", re.M)

def provider_methods(path):
    if not path: return []
    return sorted({m for m in PROVIDER_METHOD_RX.findall((ROOT / path).read_text()) if not m.startswith("_")})

def measured_names(bkey):
    """function names mentioned in the benchmark's notes for this standard"""
    names, ops = set(), {}
    for op, entry in (GAS.get(bkey) or {}).items():
        note = (entry.get("notes") or "") if isinstance(entry, dict) else ""
        ops[op] = note
        for tok in re.findall(r"\b([a-z][A-Za-z0-9]+)\s*\(", note): names.add(tok)
    return names, ops

grand = {"generated_from": ["1_blockchain-identity/artifacts", "4_comparison-framework/results/gas_benchmark.json", "cv2x-testbed/identity/*", "cv2x-testbed/scripts/experiment_*.py"],
         "families": [f for f, _ in FAMILIES] + [f for f, _ in EXTRA], "options": {}}
for slug, (display, kind, rels, bkey, prov, regs) in OPTIONS.items():
    fns, evs = [], []
    for rel in rels:
        a = load(rel); assert a, rel
        fns += [x["name"] for x in a["abi"] if x.get("type") == "function"]
        evs += [x["name"] for x in a["abi"] if x.get("type") == "event"]
    pm = provider_methods(prov)
    mnames, ops = measured_names(bkey) if bkey else (set(), {})
    fams = []
    for label, rx in FAMILIES + EXTRA:
        if label.startswith("Off-chain creation"):
            if slug in OFFCHAIN_CREATION: fams.append({"name": label, "stance": "implemented", "functions": [], "reason": OFFCHAIN_CREATION[slug], "reviewed": False})
            elif slug in OFFCHAIN_CREATION_NA: fams.append({"name": label, "stance": "not-applicable", "functions": [], "reason": OFFCHAIN_CREATION_NA[slug], "reviewed": False})
            elif kind == "off-chain": fams.append({"name": label, "stance": "implemented", "functions": [], "reason": "in-process baseline: creation is a local record, no transaction", "reviewed": False})
            else: fams.append({"name": label, "stance": "not-applicable", "functions": [], "reason": "creation requires a transaction (mint or deployment) — auto; review", "reviewed": False})
            continue
        matched = sorted({n for n in fns + evs + pm if re.search(rx, n.lower())})
        measured = sorted(n for n in matched if n in mnames or (kind == "off-chain" and n in {"register_vehicle", "sign_message", "verify_message", "revoke_credential", "get_crl", "register_vehicle_birth", "record_lifecycle_event", "transfer_ownership", "get_vehicle_history"}) or (slug in ("erc-1056-vehicle", "mobi-vid") and n in {"registerVehicle", "revokeIdentity", "getIdentityInfo", "registerVehicleBirth", "recordLifecycleEvent", "attestEvent", "transferVehicleOwnership", "getCompleteHistory", "changed", "isRevoked"}))
        if measured: stance, reason = "measured-in-comparison", f"measured via {', '.join(regs) if regs and not bkey else 'benchmark_gas.js'}"
        elif matched: stance, reason = "implemented", "present in the option's surface but not used by the comparison — asymmetry to discuss"
        else: stance, reason = "not-applicable", "no function or method in this family on this option — auto; review whether the standard defines it"
        fams.append({"name": label, "stance": stance, "functions": matched, "measured": measured, "reason": reason, "reviewed": False})
    man = {"option": display, "slug": slug, "kind": kind,
           "contracts": [f"1_blockchain-identity/contracts/{r}" for r in rels], "provider": prov,
           "benchmark_key": bkey, "experiments": regs, "benchmark_ops": ops, "families": fams,
           "surface": {"functions": len(set(fns)), "events": len(set(evs)), "provider_methods": len(pm)}}
    d = ROOT / "sandbox/options" / slug; d.mkdir(parents=True, exist_ok=True)
    (d / "manifest.yaml").write_text(yaml.safe_dump(man, sort_keys=False, allow_unicode=True, width=110))
    grand["options"][slug] = {"option": display, "kind": kind, "stances": {f["name"]: f["stance"] for f in fams}}
(ROOT / "sandbox/grand/manifest.yaml").write_text(yaml.safe_dump(grand, sort_keys=False, allow_unicode=True, width=110))
print("manifests:", len(OPTIONS), "| families:", len(grand["families"]))
