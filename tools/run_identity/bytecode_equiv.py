#!/usr/bin/env python3
"""Compare two compiled artifact trees with the Solidity metadata hash removed (after-action report 38).

    python3 tools/run_identity/bytecode_equiv.py <old artifacts dir> <new artifacts dir>

For every artifact with `bytecode` and `deployedBytecode`, the trailing CBOR metadata (its length is the last two
bytes) is stripped and the rest compared. Exit 0 when every artifact matches (a comments-only change), 1 otherwise.
A factory that embeds another contract's creation code carries that metadata mid-code and would show as differing,
which errs on the safe side.
"""
import json, pathlib, sys
def strip(h):
    h=h[2:] if h.startswith("0x") else h
    if len(h)<4: return h
    n=int(h[-4:],16); return h[:-(n*2+4)]
def load(root):
    out={}
    for p in pathlib.Path(root).rglob("*.json"):
        if p.name.endswith(".dbg.json") or "build-info" in p.parts: continue
        try: d=json.loads(p.read_text())
        except Exception: continue
        if "bytecode" in d and "deployedBytecode" in d:
            out[str(p.relative_to(root))]=(d["bytecode"],d["deployedBytecode"])
    return out
a,b=load(sys.argv[1]),load(sys.argv[2])
same_meta=diff=0
for k in sorted(set(a)|set(b)):
    if k not in a or k not in b: print("ONLY ONE SIDE",k); diff+=1; continue
    (ib,rb),(ib2,rb2)=a[k],b[k]
    if strip(ib)!=strip(ib2) or strip(rb)!=strip(rb2):
        print("DIFFERS beyond metadata:",k); diff+=1
    elif ib!=ib2: same_meta+=1
print(f"{len(a)} artifacts; {same_meta} differ only in the metadata hash; {diff} differ beyond it")
sys.exit(1 if diff else 0)
