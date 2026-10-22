#!/usr/bin/env python3
"""Runs and the promote step (WM-2 step A4; TSR phase 5; defect D56).

A producer writes its outputs into an untracked run directory, `runs/<name>/<run-id>/`, together with a
`manifest.json`: the producer, the stamp taken when the run started, and each output with its sha256 and
the tracked result path it is meant for. Nothing tracked changes. Promotion copies the outputs to their
result paths, and only when all of these hold:

  1. the manifest names a producer of record (tools/run_identity/scopes.json);
  2. the stamp says the producer's code was clean (`code_dirty` false, not missing);
  3. the stamp's commit is HEAD (a run of an earlier commit is promoted from that commit, not this one);
  4. the producer's scope is the one stamped (same `scope_sha`), and is still clean now;
  5. every output's bytes match its recorded sha256;
  6. every destination lies under one of the producer's declared result paths.

    python3 tools/run_identity/promote.py runs/security-matrix/<run-id>        # promote one run
    python3 tools/run_identity/promote.py --latest security-matrix            # the newest run of that name
    python3 tools/run_identity/promote.py --latest security-matrix --dry-run  # checks and diff, no copy
Exit 0 promoted (or would promote); 1 refused, with every reason printed.

From a producer (Python):  d = new_run(__file__, "name"); ...write files into d...;
                           write_manifest(d, __file__, stamp_at_start, {"out.json": "<result path>"})
The JS helper (1_blockchain-identity/scripts/lib/run_stamp.js: newRun, writeManifest) writes the same format.
"""
import datetime
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = ROOT / "runs"
sys.path.insert(0, str(HERE))
import stamp as _stamp  # noqa: E402


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def new_run(producer, name):
    short = _stamp._git("rev-parse", "--short", "HEAD") or "nocommit"
    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S-%fZ") + "_" + short
    d = RUNS / name / run_id
    d.mkdir(parents=True, exist_ok=False)
    return d


def write_manifest(run_dir, producer, stamp, outputs):
    run_dir = pathlib.Path(run_dir)
    key = _stamp.rel(producer) if pathlib.Path(producer).is_absolute() else producer
    doc = {"format": "run-manifest/1", "producer": key, "run_id": run_dir.name, "stamp": stamp,
           "outputs": [{"file": f, "dest": dest, "sha256": sha256(run_dir / f)} for f, dest in outputs.items()]}
    (run_dir / "manifest.json").write_text(json.dumps(doc, indent=1) + "\n")
    return doc


def _norm_stamp(st):
    """JS and Python stamps use different field names; read both."""
    dirty = st.get("code_dirty", st.get("dirty"))
    commit = st.get("commit_full") or st.get("commitFull") or st.get("commit")
    return dirty, commit, st.get("scope_sha", st.get("scopeSha")), st.get("scope")


def check(run_dir):
    """Reasons the run may not be promoted (empty list = promotable), and the manifest."""
    run_dir = pathlib.Path(run_dir)
    mf = run_dir / "manifest.json"
    if not mf.is_file():
        return [f"{run_dir}: no manifest.json (not a run directory)"], None
    doc = json.loads(mf.read_text())
    reasons = []
    producer = doc.get("producer")
    scopes = json.loads(_stamp.SCOPES.read_text())["scopes"]
    if producer not in scopes:
        return [f"producer {producer!r} is not a producer of record"], doc
    dirty, commit, scope_sha, scope = _norm_stamp(doc.get("stamp") or {})
    if dirty is not False:
        reasons.append(f"the run's stamp says the producing code was {'dirty' if dirty else 'of unknown state'} "
                       f"(code_dirty={dirty}): not a run of record")
    head = _stamp._git("rev-parse", "HEAD")
    if not commit or not head or not head.startswith(str(commit)):
        reasons.append(f"the run was made at {commit}, HEAD is {head}: promote it from its own commit")
    now = _stamp.stamp(producer)
    if scope_sha != now["scope_sha"]:
        reasons.append(f"the producer's scope changed since the run (scope_sha {scope_sha} -> {now['scope_sha']})")
    if now["code_dirty"] is not False:
        reasons.append("the producer's code is dirty now: an edit after the run would be promoted under its stamp")
    allowed = scopes[producer]["results"]
    for o in doc.get("outputs", []):
        src = run_dir / o["file"]
        if not src.is_file():
            reasons.append(f"{o['file']}: missing from the run directory")
            continue
        if sha256(src) != o["sha256"]:
            reasons.append(f"{o['file']}: bytes differ from the manifest's sha256 (edited after the run)")
        if not any(o["dest"].startswith(r) for r in allowed):
            reasons.append(f"{o['file']}: destination {o['dest']} is not one of the producer's result paths {allowed}")
    if not doc.get("outputs"):
        reasons.append("the manifest lists no outputs")
    return reasons, doc


def promote(run_dir, dry_run=False):
    run_dir = pathlib.Path(run_dir)
    reasons, doc = check(run_dir)
    if reasons:
        for r in reasons:
            print("REFUSED:", r)
        return 1
    for o in doc["outputs"]:
        dest = ROOT / o["dest"]
        same = dest.is_file() and sha256(dest) == o["sha256"]
        if dry_run:
            print(f"would promote {o['file']} -> {o['dest']}" + (" (identical to the tracked file)" if same else ""))
            if dest.is_file() and not same:
                subprocess.run(["git", "--no-pager", "diff", "--no-index", "--stat", str(dest), str(run_dir / o["file"])])
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run_dir / o["file"], dest)
        print(f"promoted {o['file']} -> {o['dest']}")
    if not dry_run:
        (run_dir / "promoted.json").write_text(json.dumps(
            {"promoted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
             "head": _stamp._git("rev-parse", "HEAD")}, indent=1) + "\n")
    return 0


def latest(name):
    runs = sorted(p for p in (RUNS / name).glob("*") if (p / "manifest.json").is_file())
    if not runs:
        raise SystemExit(f"no runs under {RUNS / name}")
    return runs[-1]


def main(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if argv[:1] == ["--latest"] and len(argv) == 2:
        return promote(latest(argv[1]), dry)
    if len(argv) == 1:
        return promote(argv[0], dry)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
