#!/usr/bin/env python3
"""Every [@KEY] cited in docs/zkp/*.md must be defined as '### [KEY]' in docs/zkp/SOURCES_ZKP.md.

    python3 docs/zkp/check_citations.py          # exit 1 and list the unresolved keys
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
DEFINED = set(re.findall(r"^### \[([^\]]+)\]", (HERE / "SOURCES_ZKP.md").read_text(), re.M))


def keys_in(text):
    """Keys in [@A], [@A; @B] and [@A, partial]; the literal placeholder [@KEY] is ignored."""
    out = []
    for group in re.findall(r"\[(@[^\]]+)\]", text):
        out += [k for k in re.findall(r"@([A-Za-z0-9.\-]+)", group) if k != "KEY"]
    return out


def unresolved(paths):
    bad = {}
    for p in paths:
        for key in keys_in(p.read_text()):
            if key not in DEFINED:
                bad.setdefault(p.name, set()).add(key)
    return bad


if __name__ == "__main__":
    docs = sorted(HERE.glob("*.md"))
    bad = unresolved(docs)
    cited = sum(len(keys_in(p.read_text())) for p in docs)
    for name, keys in bad.items():
        print(f"{name}: unresolved {sorted(keys)}")
    print(f"{cited} citations in {len(docs)} documents; {len(DEFINED)} sources defined; "
          f"{sum(len(k) for k in bad.values())} unresolved")
    sys.exit(1 if bad else 0)
