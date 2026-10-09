#!/usr/bin/env python3
"""Render the results dashboard page from the generated snapshot (plan 2026-10-09 P1.3).

    python3 docs/figures/make_dashboard_data.py   # first: the snapshot from committed results
    python3 docs/figures/make_dashboard_page.py   # then: docs/figures/results_dashboard.html

The page embeds the snapshot verbatim; it contains no number of its own.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
snap = json.loads((HERE / "dashboard_snapshot.json").read_text())
# drop the per-row register dump from the page (it is in the snapshot file); keep the page light
snap.pop("register_rows", None)
payload = json.dumps(snap, ensure_ascii=False).replace("</", "<\\/")
# down-sampled trace replay of record (docs/PLAN_SUMO_VISUALISATION.md V3); empty if not yet rendered
REPLAY = HERE.parents[1] / "cv2x-testbed/sumo/results/figures/trace_rsu_seed1_replay.json"
replay = REPLAY.read_text() if REPLAY.exists() else "null"
html = (HERE / "dashboard_template.html").read_text().replace("__SNAPSHOT__", payload).replace("__REPLAY__", replay.replace("</", "<\\/"))
(HERE / "results_dashboard.html").write_text(html)
print("wrote docs/figures/results_dashboard.html", len(html), "bytes")
