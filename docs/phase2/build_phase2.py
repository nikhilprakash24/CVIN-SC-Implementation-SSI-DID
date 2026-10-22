#!/usr/bin/env python3
"""Build and check the Phase 2 idea register (docs/phase2/ideas.yaml -> IDEA_REGISTER.md).

Checks (exit 1 on any): every anchor exists in the Phase 1 artefact it names (claim register row, crux,
defect, deferred item, side paper, scope change, file); every idea cites at least one anchor and one
existing file it builds on; dependencies name existing ideas and form no cycle; every programme names
existing ideas; scores are integers 1-5. The ranking is computed, never typed.

    python3 docs/phase2/build_phase2.py           # write IDEA_REGISTER.md
    python3 docs/phase2/build_phase2.py --check   # CI: stale register or a broken anchor fails
"""
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "IDEA_REGISTER.md"
SOURCES = {  # kind -> (file, regex that finds the id as a table row)
    "row": ("docs/MEASUREMENT_CONDITIONS.md", r"^\| {id} \|"),
    "crux": ("docs/thesis/CRUX_REGISTER.md", r"^\| \*?\*?{id}\b"),
    "defect": ("docs/DEFECT_LOG.md", r"^\| {id} \|"),
    "next": ("docs/MILESTONE_NEXT.md", r"^\| {id} \|"),
    "sp": ("SIDE_PAPERS.md", r"^\| {id}\b"),
    "sc": ("docs/SCOPE_CHANGES.md", r"^\| {id} \|"),
}


def kind_of(anchor):
    a = str(anchor)
    if a.startswith("#"):
        return "row", a[1:]
    for k, pat in (("crux", r"C\d+"), ("defect", r"D\d+"), ("next", r"N-\d+"), ("sp", r"SP-\d+"), ("sc", r"SC-\d+[a-z]?")):
        if re.fullmatch(pat, a):
            return k, a
    return "file", a


def anchor_ok(anchor, cache={}):
    kind, ident = kind_of(anchor)
    if kind == "file":
        return (ROOT / ident).exists()
    path, pat = SOURCES[kind]
    text = cache.setdefault(path, (ROOT / path).read_text(encoding="utf-8"))
    return re.search(pat.format(id=re.escape(ident)), text, re.M) is not None


def score(idea, weights):
    s = dict(idea["scores"], safety=6 - idea["scores"]["risk"])
    return round(sum(weights[k] * s[k] for k in weights), 2)


def problems_of(doc):
    ideas = {i["id"]: i for i in doc["ideas"]}
    out = []
    for i in doc["ideas"]:
        for a in i.get("anchors", []):
            if kind_of(a)[0] == "file":
                out.append(f"{i['id']}: anchor {a} is not an id (put files in builds_on)")
            elif not anchor_ok(a):
                out.append(f"{i['id']}: anchor {a} not found in {SOURCES[kind_of(a)[0]][0]}")
        if not i.get("anchors"):
            out.append(f"{i['id']}: no Phase 1 anchor")
        files = i.get("builds_on", [])
        if not files:
            out.append(f"{i['id']}: builds on no file")
        for f in files:
            if not (ROOT / f).exists():
                out.append(f"{i['id']}: builds_on {f} does not exist")
        for d in i.get("depends", []):
            if d not in ideas:
                out.append(f"{i['id']}: depends on unknown {d}")
        for k in ("value", "novelty", "feasibility", "reuse", "risk"):
            v = i.get("scores", {}).get(k)
            if not isinstance(v, int) or not 1 <= v <= 5:
                out.append(f"{i['id']}: score {k}={v} is not an integer 1-5")
        if i["track"] not in doc["tracks"]:
            out.append(f"{i['id']}: unknown track {i['track']}")
    state = {}

    def visit(n, stack):
        if state.get(n) == 1:
            out.append("dependency cycle: " + " -> ".join(stack + [n]))
            return
        if state.get(n) == 2 or n not in ideas:
            return
        state[n] = 1
        for d in ideas[n].get("depends", []):
            visit(d, stack + [n])
        state[n] = 2
    for n in ideas:
        visit(n, [])
    for p in doc["programmes"]:
        for i in p["ideas"]:
            if i not in ideas:
                out.append(f"{p['id']}: unknown idea {i}")
    return out


def render(doc):
    w = doc["weights"]
    ranked = sorted(doc["ideas"], key=lambda i: (-score(i, w), i["id"]))
    rank = {i["id"]: n + 1 for n, i in enumerate(ranked)}
    used_by = {}
    for i in doc["ideas"]:
        for d in i.get("depends", []):
            used_by.setdefault(d, []).append(i["id"])
    L = ["# Phase 2 Idea Register", "",
         "**Generated** by `docs/phase2/build_phase2.py` from `docs/phase2/ideas.yaml`; do not edit by hand. "
         "**Author:** Nikhil Prakash (MASc, UBC ECE). **Part of:** Phase 2, sub-phase P2.0 (`docs/phase2/README.md`).",
         "",
         f"**Scores:** {doc['scored_by']}. Each idea is scored 1-5 on value, novelty, feasibility, reuse of Phase 1 "
         "assets and risk; the total is " + " + ".join(f"{v:.2f}×{k}" for k, v in w.items()) +
         " (safety = 6 − risk). The ranking orders the conversation; it does not choose. The author chooses (P2-D1).",
         "",
         f"{len(doc['ideas'])} ideas in {len(doc['tracks'])} tracks; {len(doc['programmes'])} candidate programmes. "
         "Every anchor below was checked to exist in the Phase 1 artefact it names.",
         "", "## Ranking", "",
         "| Rank | Idea | Track | Total | value | novelty | feas. | reuse | risk | Phase 1 anchors | Needs |",
         "|---:|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for i in ranked:
        s = i["scores"]
        L.append(f"| {rank[i['id']]} | **{i['id']}** {i['title']} | {i['track']} | {score(i, w):.2f} | {s['value']} | "
                 f"{s['novelty']} | {s['feasibility']} | {s['reuse']} | {s['risk']} | {', '.join(map(str, i['anchors']))} | "
                 f"{', '.join(i.get('depends', [])) or '—'} |")
    L += ["", "## Tracks", "", "| Track | Theme | Ideas |", "|---|---|---|"]
    for t, name in doc["tracks"].items():
        L.append(f"| {t} | {name} | {', '.join(i['id'] for i in doc['ideas'] if i['track'] == t)} |")
    L += ["", "## Candidate programmes (decision P2-D1)", "",
          "| Programme | Ideas | Mean total | Effect on the thesis cruxes |", "|---|---|---:|---|"]
    by = {i["id"]: i for i in doc["ideas"]}
    for p in doc["programmes"]:
        mean = sum(score(by[x], w) for x in p["ideas"]) / len(p["ideas"])
        L.append(f"| **{p['id']}** {p['title']} | {', '.join(p['ideas'])} | {mean:.2f} | {p['thesis_effect']} |")
    L += ["", "## Idea cards", ""]
    for i in sorted(doc["ideas"], key=lambda i: i["id"]):
        L += [f"### {i['id']} — {i['title']}",
              f"*Track {i['track']} · rank {rank[i['id']]} · total {score(i, w):.2f}*", "",
              f"- **Question.** {i['question']}",
              f"- **Why (Phase 1).** {i['why']}",
              f"- **Anchors.** {', '.join(map(str, i['anchors']))}",
              f"- **Builds on.** " + ", ".join(f"`{f}`" for f in i["builds_on"]),
              f"- **First step.** {i['first_step']}",
              f"- **Kill criterion.** {i['kill']}",
              f"- **Needs:** {', '.join(i.get('depends', [])) or 'nothing'} · **needed by:** {', '.join(used_by.get(i['id'], [])) or 'nothing'}"]
        L += [f"- **Status {d}.** {t}" for d, t in i.get("status", [])]  # dated, appended; never edited
        L += [""]
    return "\n".join(L).rstrip() + "\n"


def main():
    doc = yaml.safe_load((HERE / "ideas.yaml").read_text(encoding="utf-8"))
    problems = problems_of(doc)
    for p in problems:
        print("PROBLEM:", p)
    text = render(doc)
    if "--check" in sys.argv:
        stale = not OUT.exists() or OUT.read_text(encoding="utf-8") != text
        if stale:
            print("docs/phase2/IDEA_REGISTER.md is stale: run python3 docs/phase2/build_phase2.py")
        if not (stale or problems):
            print(f"phase 2 register: {len(doc['ideas'])} ideas, every anchor found; IDEA_REGISTER.md current")
        return 1 if (stale or problems) else 0
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(doc['ideas'])} ideas)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
