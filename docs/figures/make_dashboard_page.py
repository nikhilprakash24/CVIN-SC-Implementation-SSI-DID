#!/usr/bin/env python3
"""Render the results dashboard page from the generated snapshot (plan 2026-10-09 P1.3).

    python3 docs/figures/make_dashboard_data.py   # first: the snapshot from committed results
    python3 docs/figures/make_dashboard_page.py   # then: docs/figures/results_dashboard.html

The page embeds the snapshot verbatim and the down-sampled trace replay of record. Every number it
prints comes from the snapshot, including the non-result constants (budget, horizon, bands), which
carry their source (`constants`). `make_dashboard_data.py --check` rebuilds this page in memory and
fails if the committed page differs.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results_dashboard.html"
# down-sampled trace replay of record (docs/PLAN_SUMO_VISUALISATION.md V3); empty if not yet rendered
REPLAY = HERE.parents[1] / "cv2x-testbed/sumo/results/figures/trace_rsu_seed1_replay.json"


def render(snap):
    snap = dict(snap)
    # drop the per-row register dump from the page (it is in the snapshot file); keep the page light
    snap.pop("register_rows", None)
    payload = json.dumps(snap, ensure_ascii=False).replace("</", "<\\/")
    replay = REPLAY.read_text() if REPLAY.exists() else "null"
    return (HERE / "dashboard_template.html").read_text().replace("__SNAPSHOT__", payload).replace("__REPLAY__", replay.replace("</", "<\\/"))


if __name__ == "__main__":
    html = render(json.loads((HERE / "dashboard_snapshot.json").read_text()))
    OUT.write_text(html)
    print("wrote docs/figures/results_dashboard.html", len(html), "bytes")
