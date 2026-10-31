#!/usr/bin/env python3
"""Gate for TDP-003, the interface control document (runbook phase 9; after-action report 27).

Every backticked identifier in sections 2 to 7 of docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md must occur, as a
literal substring, in at least one source file the section names (the SOURCES table below). Call parentheses and
their arguments are stripped before matching (`issue_credential(credential_type, ...)` checks `issue_credential`).
A token that names a file must exist in the tree (by path or by basename). A dotted name is checked part by part.
Tokens that are not identifiers are skipped and counted: those containing a space, an angle bracket, a `{`, a quote,
or starting with `--` or `#`, and tokens shorter than 3 characters.

    python3 docs/tdp/check_icd.py            # report; exit 1 on any identifier not found
    python3 docs/tdp/check_icd.py --check    # same (the flag is accepted so the CI document step reads uniformly)
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/tdp/TDP-003_INTERFACE_CONTROL_DOCUMENT.md"
SOURCES = {
    "## 2.": ["1_blockchain-identity/benchmarks/adapters/IdentityAdapter.js", "docs/CVIN-DATA-COLLECTION-FRAMEWORK.md",
              "1_blockchain-identity/results/metrics/latest/meta.json"],
    "## 3.": ["cv2x-testbed/identity/base.py", "cv2x-testbed/identity/centralized_provider.py", "cv2x-testbed/identity/erc1056_provider.py",
              "cv2x-testbed/identity/mobi_vid_provider.py", "cv2x-testbed/identity/standard/pki_identity.py", "cv2x-testbed/contracts/ERC1056Registry.sol",
              "1_blockchain-identity/contracts/ERC1056/EthereumDIDRegistry.sol"],
    "## 4.": ["2_w3c-ssi-layer/verifiable-credentials/vc_issuer.py", "2_w3c-ssi-layer/verifiable-credentials/vc_verifier.py",
              "2_w3c-ssi-layer/verifiable-credentials/vc_holder.py", "2_w3c-ssi-layer/did-resolution/did_resolver.py"],
    "## 5.": ["cv2x-testbed/sumo/sumo_identity_integration.py", "cv2x-testbed/sumo/infrastructure_layer.py"],
    "## 6.": ["cv2x-testbed/identity/freshness.py", "cv2x-testbed/sumo/infrastructure_layer.py", "cv2x-testbed/identity/erc1056_provider.py",
              "cv2x-testbed/scripts/experiment_freshness_k.py"],
    "## 7.": ["tools/run_identity/stamp.py", "tools/run_identity/producers.json", "cv2x-testbed/results/freshness_k.json",
              "cv2x-testbed/sumo/sumo_identity_integration.py", "docs/MEASUREMENT_CONDITIONS.md", "sandbox/options/erc-1056-uport/manifest.yaml",
              "1_blockchain-identity/scripts/lib/run_stamp.js"],
}
SKIP = re.compile(r"[ <{\"']|^--|^#")


def sections():
    cur, out = None, {}
    for line in DOC.read_text().splitlines():
        if line.startswith("## "):
            cur = next((k for k in SOURCES if line.startswith(k)), None)
            continue
        if cur:
            out.setdefault(cur, []).append(line)
    return out


def main():
    texts = {}
    missing, checked, skipped = [], 0, []
    for sec, lines in sections().items():
        srcs = []
        for f in SOURCES[sec]:
            p = ROOT / f
            if not p.exists():
                raise SystemExit(f"source named for section {sec} does not exist: {f}")
            srcs.append(texts.setdefault(f, p.read_text(errors="replace")))
        for tok in re.findall(r"`([^`]+)`", "\n".join(lines)):
            t = re.sub(r"\(.*\)$", "", tok).strip()
            if len(t) < 3 or SKIP.search(t):
                skipped.append(tok)
                continue
            checked += 1
            if t.endswith((".py", ".js", ".md", ".json", ".yaml", ".sol", ".sh")):
                # a file name: it must exist in the tree (by path, or by basename anywhere outside node_modules)
                if (ROOT / t).exists() or any(q.as_posix().endswith("/" + t) for q in ROOT.rglob(pathlib.Path(t).name) if "node_modules" not in q.parts):
                    continue
                missing.append((sec, tok))
                continue
            # a dotted name checks each part (CredentialIssuer.issue_credential)
            parts = t.split(".") if "." in t and " " not in t else [t]
            if not all(any(part in s for s in srcs) for part in parts):
                missing.append((sec, tok))
    for sec, tok in missing:
        print(f"NOT IN SOURCE ({sec.strip('# .')}): `{tok}`")
    print(f"{checked} identifiers checked, {len(missing)} not found, {len(skipped)} skipped as non-identifiers")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
