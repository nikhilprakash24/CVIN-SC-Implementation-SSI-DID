#!/usr/bin/env python3
"""Check that repo-rooted references under docs/idtx_core/ resolve.

Stdlib-only. Scans every .md under docs/idtx_core/ and checks ONLY references that are
unambiguous repo-rooted paths, i.e. that start with a known top-level directory
(docs/, 1_blockchain-identity/, phase2/, ...). These are the citations that must resolve.

Deliberately NOT checked (by design, to avoid false positives):
  - bare basenames cited in prose (`ANALYSIS.md`, `IdtxExecutor.sol`) -- shorthand, not a link;
  - the FUNCTION_MAP path-key shorthands `A/...` and `C/...` (defined inline in that file);
  - external URLs and in-page #anchors.
Line/column suffixes (file.sol:123) are stripped. Exit 1 if any repo-rooted path is missing.
"""
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROOT = os.path.join(REPO, "docs", "idtx_core")

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# backtick path rooted at a known top-level dir (repo-rooted citations only)
BACKTICK = re.compile(r"`((?:docs|1_blockchain-identity|2_w3c-ssi-layer|3_cv2x-testbed|4_comparison-framework|5_zkp-agent-identity|cv2x-testbed|phase2|sandbox|tools)/[\w./-]*\.(?:sol|js|py|md|json|yml|csv|ts))(?::\d+(?:,\d+)*)?`")
TOPDIRS = ("docs/", "1_blockchain-identity/", "2_w3c-ssi-layer/", "3_cv2x-testbed/",
           "4_comparison-framework/", "5_zkp-agent-identity/", "cv2x-testbed/",
           "phase2/", "sandbox/", "tools/")


def resolve(src_file, target):
    target = target.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None  # skip external / anchor
    target = re.sub(r":\d+(?:,\d+)*$", "", target)  # strip :line[,col]
    # relative markdown link to a sibling doc (contains a slash or ends .md/.svg): resolve against src dir
    if target.startswith(("./", "../")) or (("/" in target) and not target.startswith(TOPDIRS)):
        if target.startswith(("./", "../")):
            return os.path.join(os.path.dirname(src_file), target)
        return None  # shorthand path key (A/, C/, p1-relative handled below)
    if target.startswith(TOPDIRS):
        return os.path.join(REPO, target)
    # a p1/-relative or figures/-relative link from a docs/idtx_core file
    if target.startswith(("p1/", "figures/")):
        return os.path.join(os.path.dirname(src_file), target)
    return None  # bare basename or unknown shorthand -- not checkable


def main():
    missing = []
    checked = 0
    for dirpath, _, files in os.walk(ROOT):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            targets = set(MD_LINK.findall(text))
            targets |= {m for m in BACKTICK.findall(text)}
            for t in targets:
                cand = resolve(path, t)
                if cand is None:
                    continue
                checked += 1
                if not os.path.exists(cand):
                    missing.append((os.path.relpath(path, REPO), t))
    if missing:
        print(f"MISSING {len(missing)} of {checked} checked references:")
        for src, t in sorted(missing):
            print(f"  {src}: {t}")
        return 1
    print(f"idtx-core links OK: {checked} references resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
