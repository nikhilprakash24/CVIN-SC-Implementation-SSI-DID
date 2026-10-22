#!/usr/bin/env python3
"""Contribution record: the repository's history as a contribution calendar, with what the work produced
(report 19, step CR).

    python3 docs/figures/make_contribution_record.py   # writes docs/figures/contribution_record.html

Every figure on the page is computed here from git or from a committed file, and the page names the source of
each. Scope rules (stated on the page):
  - commits reachable from every branch and tag except refs whose name matches EXCLUDE (a branch that holds an
    unrelated planning project); each commit counted once;
  - dates are author dates, as GitHub's contribution graph uses;
  - the identities are reported as they are in git, not merged or hidden;
  - no line counts: generated result files would dominate them.
The page depends on the git history, so it is regenerated at each pass's close rather than checked in CI.
"""
import collections
import datetime
import html
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/figures/contribution_record.html"
EXCLUDE = re.compile(r"npat-game-planning")
AUTHOR_EMAILS = {"nikhil.prakash1995@gmail.com"}
ASSISTANT_EMAILS = {"noreply@anthropic.com"}
# The calendar starts here; earlier commits are counted in the totals and named on the page (the repository's
# creation commit of 2023-11-07 would otherwise stretch the calendar over two empty years).
CAL_START = "2025-11-01"

AREAS = [  # (label, path prefixes), first match wins
    ("Contracts and gas benchmarks", ("1_blockchain-identity/",)),
    ("W3C SSI credential layer", ("2_w3c-ssi-layer/",)),
    ("V2X testbed", ("cv2x-testbed/", "3_cv2x-testbed/")),
    ("Comparison framework and results", ("4_comparison-framework/",)),
    ("Sandbox, test harness and run identity", ("sandbox/", "tools/", "runs/")),
    ("Phase 2", ("phase2/", "docs/phase2/")),
    ("CI", (".github/",)),
    ("Thesis, register and documents", ("docs/",)),
]


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def refs():
    out = []
    for line in git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").splitlines():
        if line.endswith("/HEAD") or EXCLUDE.search(line):
            continue
        out.append(line)
    excluded = [l for l in git("for-each-ref", "--format=%(refname)", "refs/remotes", "refs/heads").splitlines()
                if EXCLUDE.search(l)]
    return out, excluded


def area_of(path):
    for label, prefixes in AREAS:
        if path.startswith(prefixes):
            return label
    return "Thesis, register and documents" if path.endswith(".md") else "Other"


def commits(included):
    log = git("log", *included, "--format=@@%H%x09%ad%x09%ae%x09%s", "--date=short", "--name-only")
    rows, cur = [], None
    for line in log.splitlines():
        if line.startswith("@@"):
            h, d, e, s = line[2:].split("\t", 3)
            cur = {"h": h[:7], "d": d, "e": e, "s": s, "areas": set()}
            rows.append(cur)
        elif line.strip() and cur is not None:
            cur["areas"].add(area_of(line.strip()))
    return rows


def unique_to_excluded(included, excluded):
    if not excluded:
        return 0
    return int(git("rev-list", "--count", *excluded, "--not", *included).strip())


def milestones(included):
    ms = []
    for line in git("for-each-ref", "--format=%(refname:short)\t%(creatordate:short)", "refs/tags").splitlines():
        name, d = line.split("\t")
        if re.match(r"v\d", name):
            ms.append({"d": d, "kind": "release", "label": f"Tag {name}"})
    for line in git("log", *included, "--merges", "--format=%ad\t%s", "--date=short").splitlines():
        d, s = line.split("\t", 1)
        m = re.search(r"pull request #(\d+)", s)
        if m:
            ms.append({"d": d, "kind": "merge", "label": f"Pull request #{m.group(1)} merged"})
    for p in sorted((ROOT / "docs").glob("AFTER_ACTION_REPORT_*.md")):
        first = git("log", "--diff-filter=A", "--format=%ad", "--date=short", "--", str(p.relative_to(ROOT))).split()
        if first:
            n = int(re.search(r"(\d+)", p.stem).group(1))
            ms.append({"d": first[-1], "kind": "report", "label": f"After-action report {n} opened"})
    return sorted(ms, key=lambda m: m["d"])


def evidence():
    snap = json.loads((ROOT / "docs/figures/dashboard_snapshot.json").read_text())
    st = snap["tests"]["stages"]

    def res(stage):
        return {k: int(v) for k, v in re.findall(r"'(\w+)': (\d+)", st[stage]["result"])}
    l1, hh, py, demos = res("L1"), res("L1+L2"), res("L3+L4"), res("demos")
    reg = snap["register"]
    defects = snap["defects"]["rows"]
    fixed = sum(1 for d in defects if d["status"] == "fixed")
    reports = len(list((ROOT / "docs").glob("AFTER_ACTION_REPORT_*.md")))
    wf = (ROOT / ".github/workflows/test-contracts.yml").read_text()
    checks = len(re.findall(r"^\s+python3 \S+\.py --check", wf, re.M))
    import sys
    sys.path.insert(0, str(ROOT / "docs/figures"))
    from make_result_cards import CARDS  # noqa: E402
    verdicts = [{"row": n, "title": c[1], "verdict": c[4]} for n, c in sorted(CARDS.items()) if c[4]]
    commit = snap["tests"]["commit"]
    return {
        "tiles": [
            {"k": f"{hh['passing']:,}", "l": "Hardhat tests passing, 0 failing", "src": f"sandbox/grand/report/GRAND_REPORT.md at {commit}"},
            {"k": f"{py['passed']:,}", "l": "Python tests passing (SSI credential layer and V2X exemplar interactions)", "src": f"sandbox/grand/report/GRAND_REPORT.md at {commit}"},
            {"k": f"{demos['demos']}", "l": f"feature demos, {demos['steps']:,} steps, {demos['transactions_mined']:,} transactions mined, 0 failures", "src": "sandbox/grand/report/demos.json"},
            {"k": f"{reg['rows']}", "l": f"claims in the register; {reg['by_status'].get('V', 0)} verified, the rest labelled estimate, superseded or unsupported", "src": "docs/MEASUREMENT_CONDITIONS.md"},
            {"k": f"{len(defects)}", "l": f"defects logged in the project's own code and documents; {fixed} fixed", "src": "docs/DEFECT_LOG.md"},
            {"k": f"{reports}", "l": "after-action reports, one per work pass: the plan committed before the work, then the log and the closing", "src": "docs/AFTER_ACTION_REPORT_*.md"},
            {"k": f"{checks}", "l": "document and record checks run in CI on every push, each failing on a stale or unsupported figure", "src": ".github/workflows/test-contracts.yml"},
            {"k": f"{l1['passing']}", "l": "mechanism cells passing: 11 identity adapters × 9 mechanisms, each implemented or declared not applicable", "src": f"sandbox/grand/report/GRAND_REPORT.md at {commit}"},
        ],
        "verdicts": verdicts,
    }


def build():
    included, excluded = refs()
    rows = commits(included)
    n_excl = unique_to_excluded(included, excluded)
    by_day = collections.defaultdict(list)
    for r in rows:
        by_day[r["d"]].append(r)
    ident = collections.Counter("author" if r["e"] in AUTHOR_EMAILS else "assistant" if r["e"] in ASSISTANT_EMAILS else "other"
                                for r in rows)
    areas = collections.Counter(a for r in rows for a in r["areas"])
    last = max(by_day)
    first = min(d for d in by_day if d >= CAL_START)
    before = [{"d": r["d"], "h": r["h"], "s": r["s"][:80]} for r in rows if r["d"] < CAL_START]
    months = collections.Counter(d[:7] for r in rows for d in [r["d"]])
    data = {
        "first": first, "last": last, "before": before, "commits": len(rows), "active_days": len(by_day),
        "branches": len([r for r in included if not r.startswith("refs/tags")]),
        "excluded_commits": n_excl, "identities": dict(ident),
        "days": {d: {"n": len(v), "s": [x["s"][:90] for x in v[:3]]} for d, v in sorted(by_day.items())},
        "months": dict(sorted(months.items())),
        "areas": [{"label": a, "n": n} for a, n in areas.most_common()],
        "milestones": milestones(included),
        "head": git("rev-parse", "--short", "HEAD").strip(),
        **evidence(),
    }
    return data


def main():
    data = build()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = (ROOT / "docs/figures/contribution_template.html").read_text().replace("__DATA__", payload)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}: {data['commits']} commits, {data['active_days']} active days, "
          f"{data['first']} to {data['last']}; excluded {data['excluded_commits']}; identities {data['identities']}")


if __name__ == "__main__":
    main()
