#!/usr/bin/env python3
"""Appendix to the progress report: commits per pass, from the git history (after-action report 24).

    python3 docs/make_progress_appendix.py          # writes docs/PROGRESS_APPENDIX_2026-07_TO_2026-10.md
    python3 docs/make_progress_appendix.py --check  # fails if the committed appendix is stale

A pass starts at the commit that opens its after-action report (a subject line matching "report N opened" or
"after-action report N opened") and ends before the next pass's opening commit. Commits before the first opening
commit in range are listed as "before the reports". Only the first-parent line of the current branch is read.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/PROGRESS_APPENDIX_2026-07_TO_2026-10.md"
SINCE = "2026-07-01"
OPEN = re.compile(r"(?:after-action )?report (\d+) opened", re.I)


def git(*a):
    return subprocess.check_output(["git", "-C", str(ROOT), *a], text=True)


def build():
    rows = [l.split("\t", 3) for l in git("log", "--first-parent", "--reverse", f"--since={SINCE}",
                                           "--format=%h%x09%ad%x09%an%x09%s", "--date=short").splitlines()]
    passes, cur = [], {"n": None, "label": "before the reports", "commits": []}
    for h, d, a, s in rows:
        m = OPEN.search(s)
        if m:
            passes.append(cur)
            cur = {"n": int(m.group(1)), "label": f"report {int(m.group(1))}", "commits": []}
        cur["commits"].append((h, d, a, s))
    passes.append(cur)
    L = ["# Appendix: Commits per Pass, July 2026 Onwards", "",
         "**Generated** by `docs/make_progress_appendix.py` from the branch's first-parent history since "
         f"{SINCE}; do not edit. A pass runs from the commit that opens its after-action report to the commit before "
         "the next opening. Author identities are as git records them.", ""]
    total = 0
    for p in passes:
        if not p["commits"]:
            continue
        total += len(p["commits"])
        first, last = p["commits"][0][1], p["commits"][-1][1]
        L += [f"## {p['label']} ({first} to {last}, {len(p['commits'])} commits)", "", "| Commit | Date | Subject |", "|---|---|---|"]
        for h, d, a, s in p["commits"]:
            s = s.replace("|", "\\|")
            L.append(f"| `{h}` | {d} | {s[:140]}{'…' if len(s) > 140 else ''} |")
        L.append("")
    L.append(f"{total} commits in {sum(1 for p in passes if p['commits'])} groups.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    text = build()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != text:
            print("STALE: run python3 docs/make_progress_appendix.py"); sys.exit(1)
        print("progress appendix current"); sys.exit(0)
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
